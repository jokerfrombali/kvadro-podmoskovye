# -*- coding: utf-8 -*-
"""
Аудит привязки текстов к ядру: квадроциклы / снегоходы / багги / вездеход / прокат.
Проверяет H1, title, description, lede, H2 и тело каждого текста + перелинковку.
Запуск из корня репозитория:  python scripts/core_audit.py [--h2] [--links] [--tsv out.tsv]
"""
import sys, os, re, json, glob, collections, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = os.path.join(R, 'site/src')
P = json.load(open(S + '/data/pages.json', encoding='utf-8'))
A = json.load(open(S + '/data/articles.json', encoding='utf-8'))
H = json.load(open(S + '/data/hubs.json', encoding='utf-8'))

# Ядро: техника (главное), прокат (коммерческий маркер), действие (катание)
VEH = re.compile(r'квадроцикл|квадрик|снегоход|багги|вездеход|мотовездеход|cfmoto|cforce|zforce|ski-doo|renegade|tinger', re.I)
RENT = re.compile(r'прокат|аренд', re.I)
ACT = re.compile(r'покатат|катани|заезд|трасс|маршрут', re.I)

URLS = {p['url'] for p in P} | {a['url'] for a in A} | {h['url'] for h in H}
KIND = {}
for p in P: KIND[p['url']] = 'page'
for h in H: KIND[h['url']] = 'hub'
for a in A: KIND[a['url']] = 'art'

def md(path):
    if not os.path.exists(path): return None
    t = open(path, encoding='utf-8').read()
    fm = {}
    m = re.match(r'^---\n(.*?)\n---\n', t, re.S)
    if m:
        for line in m.group(1).split('\n'):
            if ':' in line:
                k, v = line.split(':', 1); fm[k.strip()] = v.strip().strip('"\'')
        t = t[m.end():]
    h2 = re.findall(r'^## +(.+)$', t, re.M)
    h3 = re.findall(r'^### +(.+)$', t, re.M)
    links = re.findall(r'\]\((/[^)\s#]*)', t)
    body = re.sub(r'^#{1,6} .*$', '', t, flags=re.M)
    return dict(fm=fm, h2=h2, h3=h3, links=links, body=body, raw=t)

def cnt(rx, s): return len(rx.findall(s or ''))

rows = []
def audit(rec, kind, path):
    m = md(path)
    r = dict(id=rec['id'], kind=kind, url=rec['url'], h1=rec['h1'], title=rec['title'], desc=rec['description'],
             h1_veh=bool(VEH.search(rec['h1'])), h1_rent=bool(RENT.search(rec['h1'])),
             t_veh=bool(VEH.search(rec['title'])), d_veh=bool(VEH.search(rec['description'])),
             written=m is not None)
    if m:
        body = m['body']
        n = max(len(body), 1)
        r.update(chars=len(body), lede=m['fm'].get('lede', ''),
                 lede_veh=bool(VEH.search(m['fm'].get('lede', ''))),
                 veh=cnt(VEH, body), rent=cnt(RENT, body), act=cnt(ACT, body),
                 veh_per_k=round(cnt(VEH, body) * 1000 / n, 2),
                 h2=m['h2'], h2_n=len(m['h2']), h2_veh=sum(1 for h in m['h2'] if VEH.search(h)),
                 links=m['links'])
        L = [l if l.endswith('/') else l + '/' for l in m['links']]
        r['l_page'] = sum(1 for l in L if KIND.get(l) == 'page')
        r['l_art'] = sum(1 for l in L if KIND.get(l) == 'art')
        r['l_hub'] = sum(1 for l in L if KIND.get(l) == 'hub')
        r['l_broken'] = [l for l in L if l not in URLS]
        r['l_self'] = sum(1 for l in L if l == rec['url'])
    rows.append(r)

for p in P:
    if p['url'] == '/': continue
    audit(p, 'page', f"{S}/content/pages/{p['id']}.md")
for a in A: audit(a, 'art', f"{S}/content/articles/{a['id']}.md")
for h in H: audit(h, 'hub', '/nonexistent')

args = sys.argv[1:]
if '--only' in args:
    # фильтр: --only P10,P11,A07  (префиксы id через запятую)
    pref = tuple(args[args.index('--only') + 1].split(','))
    rows = [r for r in rows if r['id'].startswith(pref)]
W = [r for r in rows if r['written']]
print(f"страниц {sum(1 for r in rows if r['kind']=='page')}, статей {sum(1 for r in rows if r['kind']=='art')}, хабов {len(H)}; написано текстов: {len(W)}\n")

def sec(name, items, fmt):
    print(f"## {name}: {len(items)}")
    for x in items: print('   ' + fmt(x))
    print()

sec('H1 без техники (квадроцикл/снегоход/багги/вездеход)', [r for r in rows if not r['h1_veh']],
    lambda r: f"{r['id']} {r['url']}  H1: {r['h1']}")
sec('title без техники', [r for r in rows if not r['t_veh']],
    lambda r: f"{r['id']} {r['url']}  T: {r['title']}")
sec('description без техники', [r for r in rows if not r['d_veh']],
    lambda r: f"{r['id']} {r['url']}  D: {r['desc'][:110]}")
sec('lede без техники (написанные)', [r for r in W if not r['lede_veh']],
    lambda r: f"{r['id']} {r['url']}  L: {(r['lede'] or '—')[:110]}")
sec('тело: техника реже 2 упоминаний на 1000 знаков', sorted([r for r in W if r['veh_per_k'] < 2], key=lambda r: r['veh_per_k']),
    lambda r: f"{r['id']} {r['url']}  {r['veh_per_k']}/1000  veh={r['veh']} rent={r['rent']} chars={r['chars']}")
sec('тело: ни одного слова прокат/аренда', [r for r in W if r['rent'] == 0],
    lambda r: f"{r['id']} {r['url']}")
sec('H2: меньше трети заголовков с техникой', [r for r in W if r['h2_n'] and r['h2_veh'] * 3 < r['h2_n']],
    lambda r: f"{r['id']} {r['url']}  {r['h2_veh']}/{r['h2_n']}")
sec('ссылки: битые', [r for r in W if r['l_broken']],
    lambda r: f"{r['id']} {r['url']}  {r['l_broken']}")
sec('ссылки: ни одной на коммерческую страницу', [r for r in W if r['l_page'] == 0],
    lambda r: f"{r['id']} {r['url']}  page={r['l_page']} art={r['l_art']} hub={r['l_hub']}")
sec('ссылки: статья без ссылок на другие статьи/хаб', [r for r in W if r['kind'] == 'art' and r['l_art'] + r['l_hub'] == 0],
    lambda r: f"{r['id']} {r['url']}")
sec('ссылки: меньше 3 внутренних всего', [r for r in W if len(r['links']) < 3],
    lambda r: f"{r['id']} {r['url']}  {len(r['links'])}")

# входящие ссылки из текстов (не из шаблона)
inb = collections.Counter()
for r in W:
    for l in r['links']:
        l = l if l.endswith('/') else l + '/'
        if l != r['url']: inb[l] += 1
key_pages = [p for p in P if p['queue'] in ('1', 1)]
sec('входящие из текстов на страницы очереди 1 (меньше 3)', [p for p in key_pages if inb[p['url']] < 3],
    lambda p: f"{p['id']} {p['url']}  inbound={inb[p['url']]}  H1: {p['h1']}")

if '--h2' in args:
    print('## Все H2 написанных текстов')
    for r in W:
        print(f"\n{r['id']} [{r['kind']}] {r['url']}\n   H1: {r['h1']}")
        for h in r['h2']: print(f"   {'✓' if VEH.search(h) else '·'} {h}")
if '--links' in args:
    print('## Ссылки написанных текстов')
    for r in W: print(f"{r['id']} {r['url']}\n   " + '\n   '.join(r['links']))
if '--tsv' in args:
    out = args[args.index('--tsv') + 1]
    with open(out, 'w', encoding='utf-8') as f:
        cols = ['id','kind','url','written','h1_veh','t_veh','d_veh','lede_veh','chars','veh','rent','veh_per_k','h2_n','h2_veh','l_page','l_art','l_hub','h1','title']
        f.write('\t'.join(cols) + '\n')
        for r in rows: f.write('\t'.join(str(r.get(c, '')) for c in cols) + '\n')
    print('tsv →', out)
