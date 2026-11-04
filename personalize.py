from pathlib import Path
import re
from urllib.parse import quote
root=Path(__file__).parent/'dist'
greetings='[{word:"Hello",language:"English"},{word:"வணக்கம்",language:"தமிழ்"},{word:"നമസ്കാരം",language:"മലയാളം"},{word:"こんにちは",language:"日本語"}]'
count=0
for p in root.rglob('*'):
 if p.suffix not in ['.html','.js','.css']:continue
 s=p.read_text();old=s
 s=s.replace('Dave Miye (David Fayeye on LinkedIn)','Ajaymon, based in Bangalore,')
 s=s.replace('Dave Miye<!-- -->, or <!-- -->David Fayeye<!-- --> on LinkedIn','Ajaymon<!-- --> — based in <!-- -->Bangalore<!-- -->, India')
 s=s.replace(r'\"Dave Miye\",\", or \",\"David Fayeye\",\" on LinkedIn\"',r'\"Ajaymon\",\" — based in \",\"Bangalore\",\", India\"')
 s=s.replace('Dave Miye','Ajaymon').replace('David Fayeye','Ajaymon')
 s=re.sub(r'\bDave\b','Ajaymon',s)
 s=s.replace('Africa/Lagos','Asia/Kolkata').replace('GMT+1','Bangalore · IST')
 s=s.replace('location:"Based in —"','location:"Based in Bangalore, India"')
 s,n=re.subn(r'\[\{word:"Hello",language:"English"\},.*?\{word:"你好",language:"中文"\}\]',lambda _:greetings,s);count+=n
 if p.suffix=='.html':s=s.replace('</head>','<link rel="stylesheet" href="/personalize.css"/></head>')
 if s!=old:p.write_text(s)
# The original signature is an outlined drawing; replace its appearance with the new name.
svg='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 70"><text x="8" y="52" font-family="cursive" font-style="italic" font-size="56" fill="black">Ajaymon</text></svg>'
mask='url("data:image/svg+xml,'+quote(svg)+'")'
(root/'personalize.css').write_text('.header-signature,.preloader-signature{background:currentColor;mask:'+mask+' center/contain no-repeat;-webkit-mask:'+mask+' center/contain no-repeat}.header-signature>*,.preloader-signature>*{visibility:hidden}.hello-word{line-height:1.35!important}.hello-language{white-space:nowrap}\n')
print('Updated greeting lists:',count)
assert count==3
