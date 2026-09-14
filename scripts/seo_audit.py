# -*- coding: utf-8 -*-
import os, re, glob, collections, json, html
D='site/dist'
files=[f for f in glob.glob(D+'/**/index.html',recursive=True)]
rows=[]
for f in files:
    s=open(f,encoding='utf-8').read()
    url='/'+os.path.relpath(f,D).replace('/index.html','').replace('index.html','')
    url=('/' if url in ('/.','/') else url.rstrip('/')+'/')
    t=re.search(r'<title>(.*?)</title>',s,re.S)
    d=re.search(r'<meta name="description" content="(.*?)"',s,re.S)
    c=re.search(r'<link rel="canonical" href="(.*?)"',s)
    h1=re.findall(r'<h1[^>]*>(.*?)</h1>',s,re.S)
    h2=re.findall(r'<h2[^>]*>(.*?)</h2>',s,re.S)
    ld=len(re.findall(r'application/ld\+json',s))
    links=set(re.findall(r'href="(/[^"#?]*)"',s))
    rows.append(dict(url=url,title=html.unescape(t.group(1)) if t else '',
        desc=html.unescape(d.group(1)) if d else '', canon=c.group(1) if c else '',
        h1=[html.unescape(re.sub('<[^>]+>','',x)).strip() for x in h1],
        nh2=len(h2), ld=ld, links=links, size=len(s)))
print(f'СТРАНИЦ В СБОРКЕ: {len(rows)}\n')
def bad(name, items):
    print(f'{name}: {len(items)}')
    for x in list(items)[:6]: print('   ', x)
    if len(items)>6: print(f'    … ещё {len(items)-6}')
    print()
bad('без title', [r['url'] for r in rows if not r['title']])
bad('без description', [r['url'] for r in rows if not r['desc']])
bad('без canonical', [r['url'] for r in rows if not r['canon']])
bad('не ровно один H1', [r['url'] for r in rows if len(r['h1'])!=1])
bad('без структурированных данных', [r['url'] for r in rows if r['ld']<2])
dt=collections.Counter(r['title'] for r in rows)
bad('дубли title', [f'{k}  ×{v}' for k,v in dt.items() if v>1])
dd=collections.Counter(r['desc'] for r in rows)
bad('дубли description', [f'{k[:70]}…  ×{v}' for k,v in dd.items() if v>1])
lt=[r for r in rows if len(r['title'])>75]
bad('title длиннее 75 знаков', [f"{len(r['title'])} — {r['title'][:70]}" for r in lt])
ld_=[r for r in rows if len(r['desc'])>180]
bad('description длиннее 180 знаков', [f"{len(r['desc'])} — {r['url']}" for r in ld_])
# битые внутренние ссылки и сироты
have={r['url'] for r in rows}
allref=set()
for r in rows: allref |= {l if l.endswith('/') else l+'/' for l in r['links']}
broken=sorted(l for l in allref if l not in have and not l.startswith(('/robots','/sitemap','/favicon','/_')))
bad('битые внутренние ссылки', broken)
inbound=collections.Counter()
for r in rows:
    for l in r['links']:
        u=l if l.endswith('/') else l+'/'
        if u!=r['url']: inbound[u]+=1
orphans=sorted(u for u in have if inbound[u]==0 and u!='/')
bad('страницы без входящих ссылок', orphans)
print(f"средний вес страницы: {sum(r['size'] for r in rows)//len(rows)//1024} КБ")
print(f"среднее число H2: {sum(r['nh2'] for r in rows)/len(rows):.1f}")
print(f"страниц с 8+ H2: {sum(1 for r in rows if r['nh2']>=8)}")
