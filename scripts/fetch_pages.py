import subprocess, hashlib, os, re, html, json, sys, time
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36"
os.makedirs('raw/pages', exist_ok=True)
urls=[l.strip() for l in open(sys.argv[1],encoding='utf-8') if l.strip() and not l.startswith('#')]
out=[]
for u in urls:
    cid=hashlib.md5(u.encode()).hexdigest()[:10]
    p=f'raw/pages/{cid}.html'
    if not os.path.exists(p):
        r=subprocess.run(['curl','-sL','--max-time','30','--compressed','-A',UA,u,'-o',p],capture_output=True)
        time.sleep(0.3)
    ok=os.path.exists(p) and os.path.getsize(p)>1500
    out.append((cid,u,'ok' if ok else 'fail', os.path.getsize(p) if os.path.exists(p) else 0))
for c,u,s,z in out: print(f'{c}\t{s}\t{z}\t{u}')
