# -*- coding: utf-8 -*-
import json,os,glob,re
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A=json.load(open(R+'/site/src/data/articles.json',encoding='utf-8'))
P=json.load(open(R+'/site/src/data/pages.json',encoding='utf-8'))
ad={os.path.basename(f)[:-3] for f in glob.glob(R+'/site/src/content/articles/*.md')}
pd={os.path.basename(f)[:-3] for f in glob.glob(R+'/site/src/content/pages/*.md')}
print(f'СТАТЬИ:   {len(ad):3} из {len(A)}  ({len(ad)/len(A)*100:.0f}%)')
print(f'СТРАНИЦЫ: {len(pd):3} из {len(P)}  ({len(pd)/len(P)*100:.0f}%)')
tot=0
for f in glob.glob(R+'/site/src/content/**/*.md',recursive=True): tot+=len(open(f,encoding='utf-8').read())
print(f'написано знаков: {tot:,}'.replace(',',' '))
import collections
print('\nстатьи по очередям (осталось):')
c=collections.Counter(a['queue'] for a in A if a['id'] not in ad)
for k in sorted(c, key=str): print(f'   очередь {k}: {c[k]}')
print('\nстраницы по очередям (осталось):')
c=collections.Counter(p['queue'] for p in P if p['id'] not in pd)
for k in sorted(c, key=str): print(f'   очередь {k}: {c[k]}')
