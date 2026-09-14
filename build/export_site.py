# -*- coding: utf-8 -*-
import sys, os, json, re, csv, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import d_config as C, d_arch as AR
import d_art_01,d_art_02,d_art_03,d_art_04,d_art_05,d_art_06,d_art_07
import d_blocks_01,d_blocks_02,d_blocks_03,d_blocks_04,d_blocks_05,d_blocks_06
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT=os.path.join(ROOT,'site/src/data')
ARTS=[]
for m in (d_art_01,d_art_02,d_art_03,d_art_04,d_art_05,d_art_06,d_art_07): ARTS+=m.ART
BLOCKS={}
for m in (d_blocks_01,d_blocks_02,d_blocks_03,d_blocks_04,d_blocks_05,d_blocks_06): BLOCKS.update(m.B)
SEM=json.load(open(os.path.join(ROOT,'build/semantics.json'),encoding='utf-8'))['SEM']
NARROW={}
for i,l in enumerate(open(os.path.join(ROOT,'raw/wordstat/narrow.tsv'),encoding='utf-8')):
    if i==0 or '\t' not in l: continue
    a,b=l.rstrip('\n').rsplit('\t',1)
    try: NARROW[re.sub(r'\s+',' ',a.lower().replace('ё','е')).strip()]=int(b)
    except: pass
byp=collections.defaultdict(list)
for r in SEM:
    if r['status']=='принято': byp[r['page']].append(r)

def keys(pid, lim=12):
    rows=sorted(byp.get(pid,[]), key=lambda x:-x['freq'])[:lim]
    return [{'q':r['raw'],'broad':r['freq'],'exact':NARROW.get(r['norm'])} for r in rows]

pages=[]
for c in AR.COMMERCIAL:
    pid,url,parent,typ,cl,h1,title,desc,why,isnew,queue,status = c
    pages.append(dict(id=pid,url=url,parent=parent,type=typ,cluster=cl,h1=h1,title=title,
                      description=desc,rationale=why,queue=queue,keys=keys(pid)))
hubs=[]
for h in AR.HUBS:
    hid,url,name,h1,title,desc,pq,pf,n = h
    hubs.append(dict(id=hid,url=url,parent='/baza-znaniy/',name=name,h1=h1,title=title,
                     description=desc,primary=pq,freq=pf,count=n,keys=keys(hid)))
HUB={h[0]:h for h in AR.HUBS}
articles=[]
for a in ARTS:
    aid,hub,slug,h1,title,desc,pq,pf,sup,task,differ,prio,vmin,vmax,own,media,facts,cta = a
    blocks=[]
    for raw in BLOCKS[aid]:
        lvl,head,thesis=(raw.split('|',2)+['',''])[:3]
        blocks.append({'level':int(lvl),'h':head,'note':thesis})
    supl=[]
    for part in (sup or '').split(';'):
        part=part.strip()
        if not part or ':' not in part: continue
        q,f=part.rsplit(':',1)
        supl.append({'q':q.strip(),'f':f.strip()})
    hb=HUB[hub]
    articles.append(dict(id=aid,hub=hub,hubName=hb[2],hubUrl=hb[1],url=hb[1]+slug+'/',slug=slug,
                         h1=h1,title=title,description=desc,primary=pq,freq=pf,
                         exact=NARROW.get(re.sub(r'\s+',' ',pq.lower().replace('ё','е')).strip()),
                         support=supl,task=task,differ=differ,queue=prio,vmin=vmin,vmax=vmax,
                         own=own,media=media,facts=facts,cta=cta,blocks=blocks,keys=keys(aid)))
json.dump(pages,open(OUT+'/pages.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
json.dump(hubs,open(OUT+'/hubs.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
json.dump(articles,open(OUT+'/articles.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
print('pages',len(pages),'| hubs',len(hubs),'| articles',len(articles))
print('всего маршрутов:',len(pages)+len(hubs)+len(articles)+1)
