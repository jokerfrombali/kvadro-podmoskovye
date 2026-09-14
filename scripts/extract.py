import re,html,sys,os,json
def text_of(path):
    h=open(path,encoding='utf-8',errors='ignore').read()
    return h
def clean(h):
    h=re.sub(r'(?is)<(script|style|noscript|svg|header|footer|nav)[^>]*>.*?</\1>',' ',h)
    t=re.sub(r'(?s)<[^>]+>','\n',h)
    t=html.unescape(t)
    lines=[l.strip() for l in t.split('\n')]
    lines=[l for l in lines if l]
    out=[];prev=None
    for l in lines:
        if l!=prev: out.append(l)
        prev=l
    return '\n'.join(out)
def meta(h):
    d={}
    m=re.search(r'(?is)<title[^>]*>(.*?)</title>',h); d['title']=html.unescape(m.group(1).strip()) if m else ''
    m=re.search(r'(?is)<meta[^>]+name=["\']description["\'][^>]*content=["\'](.*?)["\']',h)
    if not m: m=re.search(r'(?is)<meta[^>]+content=["\'](.*?)["\'][^>]*name=["\']description["\']',h)
    d['description']=html.unescape(m.group(1).strip()) if m else ''
    for lvl in (1,2,3):
        d['h%d'%lvl]=[html.unescape(re.sub(r'(?s)<[^>]+>','',x)).strip() for x in re.findall(r'(?is)<h%d[^>]*>(.*?)</h%d>'%(lvl,lvl),h)]
    return d
if __name__=='__main__':
    for p in sys.argv[1:]:
        h=text_of(p); d=meta(h); body=clean(h)
        words=len(re.findall(r'\w+',body))
        print(json.dumps({'file':os.path.basename(p),'title':d['title'],'description':d['description'],
            'h1':d['h1'],'h2':d['h2'],'h3':d['h3'],'words':words,'chars':len(body)},ensure_ascii=False))
