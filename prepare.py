import concurrent.futures, html, json, re, urllib.request, urllib.parse
from pathlib import Path
ROOT=Path(__file__).parent/'dist'
files=[p for p in ROOT.rglob('*') if p.suffix in ['.html','.js','.css']]
assets={}
for p in files:
 s=html.unescape(p.read_text()).replace('\\"','"')
 for u in re.findall(r'https://cdn\.sanity\.io/(?:images|files)/[A-Za-z0-9_./-]+',s):
  assets[u]=ROOT/'media-cdn'/u.split('cdn.sanity.io/')[1]
 if p.suffix=='.css':
  for u in re.findall(r'url\((\.\./media/[^)]+)\)',s):
   dest=(p.parent/u).resolve();assets['https://davemiye.com'+str(dest.relative_to(ROOT.resolve())).join(['/',''])]=dest

def fetch(item):
 u,p=item
 if p.exists():return
 try:
  data=urllib.request.urlopen(u,timeout=90).read();p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
 except Exception as e:return [u,str(e)]
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
 errors=[e for e in pool.map(fetch,assets.items()) if e]
print('Media',len(assets),'errors',errors,flush=True)
# Replace Next's server image endpoint with each original image source.
for p in files:
 s=p.read_text()
 if p.suffix=='.js':
  s=re.sub(r'return`\$\{e.path\}\?url=\$\{encodeURIComponent\(t\)\}[^;]*?`\}', 'return t}',s)
  s=re.sub(r'async function (\w+)\(e,t,r,([a-z])\)\{try\{return\(await fetch\("/api/contact".*?catch\{return"mail-app"\}\}',r'async function \1(e,t,r,\2){return"mail-app"}',s)
 if p.suffix=='.html':
  def imageurl(m):
   u=html.unescape(m.group(0)).replace('\\u0026','&')
   return html.escape(urllib.parse.parse_qs(urllib.parse.urlsplit(u).query).get('url',[''])[0],quote=True)
  s=re.sub(r'/_next/image\?[^"\s<>\\]+',imageurl,s)
  s=s.replace('<head>','<head><script src="/replica-runtime.js"></script>')
 s=s.replace('https://cdn.sanity.io/','/media-cdn/')
 p.write_text(s)
