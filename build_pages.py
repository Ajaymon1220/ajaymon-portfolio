"""Dedicated Work and About routes sharing the portfolio's existing React shell."""
import json,re
import build_ajay as b
from site_content import PROJECTS

def work_tree():
    cards=[]
    for p in PROJECTS:
        src=b.asset_url(p['slug'],p['cover'][0])
        cards.append(b.el('article',{'className':'work-index-card'},
            b.el('a',{'href':'/work/'+p['slug'],'className':'work-index-link','data-cursor':'View project'},
                b.el('div',{'className':'work-index-image'},b.el('img',{'src':src,'alt':p['cover'][3],'loading':'lazy','width':p['cover'][1],'height':p['cover'][2]})),
                b.el('div',{'className':'work-index-meta'},b.el('h2',{},p['title']),b.el('span',{'aria-hidden':'true'},'↗')),
                b.el('p',{'className':'text-muted'},' · '.join(p['services'])))))
    return b.el('section',{'id':'work','className':'work-index px-5 md:px-8','aria-labelledby':'work-title'},
        b.el('div',{'className':'work-index-inner'},
            b.el('header',{'className':'page-intro reveal','style':{'--i':1}},
                b.el('p',{'className':'text-sm text-muted'},'Designing for clarity'),
                b.el('h1',{'id':'work-title','className':'page-heading'},'My selected works'),
                b.el('p',{'className':'page-description text-muted'},'A selection of product design work across fintech, workflows, and design systems.')),
            b.el('div',{'className':'work-index-grid reveal','style':{'--i':2}},cards)))

def write_pages(home):
    for route in ['work','about']:
        doc=home
        # Streamed server markup and Flight data must describe the same page.
        for sid in (['intro','experience','clients','testimonials','playground'] if route=='work' else ['work','playground']):
            doc=re.sub(r'<section\b[^>]*\bid="'+sid+r'"[^>]*>.*?</section>','',doc,flags=re.S)
        doc=re.sub(r'<nav aria-label="Sections".*?</nav>','',doc,flags=re.S)
        if route=='work':
            doc=re.sub(r'<section\b[^>]*\bid="work"[^>]*>.*?</section>',lambda _:b.to_html(work_tree(),{}),doc,flags=re.S)
        else:
            doc=re.sub(r'<h1 class="sr-only">.*?</h1>','<h1 class="page-heading about-heading">About me</h1>',doc,count=1,flags=re.S)
            doc=re.sub(r'<a class="hero-bio-link" href="/#work">.*?</a>','<a class="hero-bio-link" href="/work">Explore my selected work</a>',doc,count=1,flags=re.S)
        rows=[]
        for rid,body,t in b.split_rows(b.read_payload(doc)):
            if rid=='42':
                obj=json.loads(body)
                main=obj[1][3]
                main['children']=['$L66'] if route=='work' else [main['children'][0],'$L67','$L68','$L69']
                obj=[x for x in obj if x!='$L6c']
                if route=='about':
                    def heading(x):
                        if isinstance(x,list):
                            if len(x)==4 and x[1]=='h1':x[3].update(className='page-heading about-heading',children='About me')
                            else:
                                for v in x:heading(v)
                        elif isinstance(x,dict):
                            for v in x.values():heading(v)
                    heading(obj)
                body=json.dumps(obj,ensure_ascii=False,separators=(',',':'))
            elif rid=='66' and route=='work':body=b.rsc(work_tree())
            elif rid=='61' and route=='about':
                obj=json.loads(body);obj[3].update(href='/work',children='Explore my selected work');body=json.dumps(obj,ensure_ascii=False,separators=(',',':'))
            rows.append((rid,body,t))
        def active_link(x):
            if isinstance(x,dict):
                if x.get('href')=='/'+route and x.get('children')==route.title():x['aria-current']='page'
                for v in x.values():active_link(v)
            elif isinstance(x,list):
                for v in x:active_link(v)
        for i,(rid,body,t) in enumerate(rows):
            if not t and body.startswith(('[','{')):
                obj=json.loads(body);active_link(obj);rows[i]=(rid,json.dumps(obj,ensure_ascii=False,separators=(',',':')),t)
        doc=b.write_payload(doc,b.join_rows(rows))
        doc=doc.replace('href="/'+route+'">'+route.title()+'</a>', 'href="/'+route+'" aria-current="page">'+route.title()+'</a>')
        doc=doc.replace('/#contact','#contact')
        title=('My selected works' if route=='work' else 'About me')+' — Ajaymon'
        doc=doc.replace('Ajaymon — Product Designer',title)
        out=b.DIST/route/'index.html';out.parent.mkdir(parents=True,exist_ok=True);out.write_text(doc)
        print('wrote',out.relative_to(b.ROOT))
