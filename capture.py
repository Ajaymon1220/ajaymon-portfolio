"""Capture the reference's public pages and assets for a static replica."""
import concurrent.futures, html, json, re, urllib.request, urllib.parse
from pathlib import Path
ROOT=Path(__file__).parent/'dist'
ORIGIN='https://davemiye.com'
ROUTES=['/','/playground','/work/goals','/work/circa','/work/sidequest','/work/plate','/work/dialme']
seen=set(); failures=[]
def fetch(path):
    url=ORIGIN+path
    target=ROOT/(path.strip('/')+'/index.html' if path in ROUTES and path!='/' else 'index.html' if path=='/' else urllib.parse.urlsplit(path).path.lstrip('/'))
    if target.exists(): return path,target
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
        data=urllib.request.urlopen(req,timeout=60).read()
        target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
        return path,target
    except Exception as e:
        failures.append([path,str(e)]);return path,None
queue=set(ROUTES)
while queue:
    batch=queue-seen;queue=set();seen|=batch
    if not batch:break
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
      for path,target in pool.map(fetch,sorted(batch)):
        if not target or target.suffix not in ['.html','.js','.css']:continue
        s=target.read_text()
        # Public static files and lazily loaded Next.js chunks.
        refs=set(re.findall(r'[/]?(?:_next/)?static/(?:immutable/)?(?:chunks|media)/[a-zA-Z0-9_./-]+\.(?:js|css|woff2|woff|ttf)',s))
        for x in refs:
            queue.add('/'+x.lstrip('/') if x.lstrip('/').startswith('_next/') else '/_next/'+x.lstrip('/'))
        for x in re.findall(r'["\x27(](/[^"\x27\s<>\\?]+\.(?:png|jpg|jpeg|webp|svg|mp3|wav|ogg|mp4|webm|woff2|json))["\x27)?]',s):
            if not x.startswith('//'):queue.add(x)
        for u in re.findall(r'/_next/image\?[^"\s<>\\]+',s):
            src=urllib.parse.parse_qs(urllib.parse.urlsplit(html.unescape(u)).query).get('url',[''])[0]
            if src.startswith('/') and not src.startswith('//'):queue.add(src)
    print('Captured',len(seen),'pending',len(queue-seen),flush=True)
(ROOT.parent/'capture-report.json').write_text(json.dumps({'routes':ROUTES,'assets':sorted(seen),'failures':failures},indent=2))
print('Failures:',failures)
