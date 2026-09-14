# -*- coding: utf-8 -*-
import re, html, os, json, hashlib, csv, sys

BOILER = r'(?is)<(script|style|noscript|svg|iframe|header|footer|nav|form|select|template)[^>]*>.*?</\1>'

def load(u):
    cid = hashlib.md5(u.encode()).hexdigest()[:10]
    p = f'raw/pages/{cid}.html'
    if not os.path.exists(p) or os.path.getsize(p) < 1500:
        return cid, None
    return cid, open(p, encoding='utf-8', errors='ignore').read()

def strip_tags(s):
    return html.unescape(re.sub(r'(?s)<[^>]+>', ' ', s)).strip()

def norm(s):
    return re.sub(r'\s+', ' ', s).strip()

def analyze(u, raw):
    d = {'url': u}
    m = re.search(r'(?is)<title[^>]*>(.*?)</title>', raw)
    d['title'] = norm(html.unescape(m.group(1))) if m else ''
    m = (re.search(r'(?is)<meta[^>]+name=["\']description["\'][^>]*content=["\'](.*?)["\']', raw)
         or re.search(r'(?is)<meta[^>]+content=["\'](.*?)["\'][^>]*name=["\']description["\']', raw))
    d['description'] = norm(html.unescape(m.group(1))) if m else ''
    # main region: prefer <main> or <article>
    body = raw
    for tag in ('main', 'article'):
        mm = re.search(r'(?is)<%s[^>]*>(.*?)</%s>' % (tag, tag), raw)
        if mm and len(mm.group(1)) > 2000:
            body = mm.group(1); break
    clean = re.sub(BOILER, ' ', body)
    d['h1'] = [norm(strip_tags(x)) for x in re.findall(r'(?is)<h1[^>]*>(.*?)</h1>', clean)]
    d['h2'] = [norm(strip_tags(x)) for x in re.findall(r'(?is)<h2[^>]*>(.*?)</h2>', clean)]
    d['h3'] = [norm(strip_tags(x)) for x in re.findall(r'(?is)<h3[^>]*>(.*?)</h3>', clean)]
    d['h2'] = [x for x in d['h2'] if x]
    d['h3'] = [x for x in d['h3'] if x]
    text = norm(strip_tags(clean))
    d['words'] = len(re.findall(r'[A-Za-zА-Яа-яЁё0-9]+', text))
    d['chars_sp'] = len(text)
    d['chars_nosp'] = len(re.sub(r'\s', '', text))
    d['tables'] = len(re.findall(r'(?is)<table', clean))
    d['imgs'] = len(re.findall(r'(?is)<img', clean))
    d['videos'] = len(re.findall(r'(?is)(youtube|rutube|vk\.com/video|<video)', clean))
    d['lists'] = len(re.findall(r'(?is)<(ul|ol)\b', clean))
    d['faq_schema'] = 1 if re.search(r'FAQPage', raw) else 0
    d['has_price'] = 1 if re.search(r'(?i)(руб|₽|\bот\s*\d{3,})', text) else 0
    d['text'] = text
    return d

if __name__ == '__main__':
    urls = [l.strip() for l in open(sys.argv[1], encoding='utf-8') if l.strip()]
    res = []
    for u in urls:
        cid, raw = load(u)
        if raw is None:
            res.append({'content_id': cid, 'url': u, 'status': 'нет доступа/пустой ответ'}); continue
        a = analyze(u, raw); a['content_id'] = cid; a['status'] = 'ok'
        res.append(a)
    json.dump(res, open('raw/pages_analysis.json', 'w', encoding='utf-8'), ensure_ascii=False)
    ok = [r for r in res if r.get('status') == 'ok']
    print(f'проанализировано {len(ok)} из {len(res)}')
    for r in sorted(ok, key=lambda x: -x['words'])[:60]:
        print(f"{r['words']:6} сл  {r['chars_sp']:7} зн  H2={len(r['h2']):2} H3={len(r['h3']):2} T={r['tables']} IMG={r['imgs']:3}  {r['url'][:78]}")
