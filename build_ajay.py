"""Generate Ajaymon's case-study pages (and later the homepage/playground data) into dist/.

Each page keeps the captured Next.js runtime, so interactions still work. For every page we
write two matching representations of the same React tree:
  * the server HTML inside the streamed `S:1` boundary, and
  * the RSC flight payload (`self.__next_f.push`) that React hydrates against.
Text must match exactly between the two; the tree helpers below guarantee that.

Usage: python3 build_ajay.py
"""
import html
import json
import re
import shutil
from signature import PATHS as SIGNATURE_PATHS, VIEWBOX as SIGNATURE_VIEWBOX, STROKE as SIGNATURE_STROKE
from pathlib import Path

from site_content import CONTACT_EMAIL, PLAYGROUND, PROJECTS, SITE

ROOT = Path(__file__).parent
DIST = ROOT / "dist"
TEMPLATES = ROOT / "templates"
ASSETS = ROOT / "assets"  # your source images; copied into dist/profile/work/ at build time

# ---------------------------------------------------------------- tree helpers

class C:
    """A client component reference. `ref` is the payload id (e.g. "$L4c")."""
    def __init__(self, name, ref):
        self.name, self.ref = name, ref


def el(type_, props=None, *children, key=None):
    props = dict(props or {})
    if children:
        props["children"] = children[0] if len(children) == 1 else list(children)
    return {"type": type_, "key": key, "props": props}


def to_rsc(node):
    if node is None or node is False or node is True:
        return node
    if isinstance(node, str):
        return "$" + node if node.startswith("$") else node
    if isinstance(node, (int, float)):
        return node
    if isinstance(node, list):
        return [to_rsc(n) for n in node]
    t = node["type"]
    props = {k: (to_rsc(v) if k == "children" else v) for k, v in node["props"].items()}
    return ["$", t.ref if isinstance(t, C) else t, node["key"], props]


ATTR = {"className": "class", "htmlFor": "for", "viewBox": "viewbox", "pathLength": "pathlength",
        "fetchPriority": "fetchpriority", "srcSet": "srcset", "tabIndex": "tabindex"}
VOID = {"img", "br", "hr", "meta", "link", "input", "source"}


def attrs_html(props):
    out = []
    for k, v in props.items():
        if k in ("children", "dangerouslySetInnerHTML") or v is None or v is False:
            continue
        if k == "style":
            v = ";".join(f"{sk}:{sv}" for sk, sv in v.items())
        name = ATTR.get(k, k)
        out.append(name if v is True else f'{name}="{html.escape(str(v), quote=True)}"')
    return (" " + " ".join(sorted(out))) if out else ""


def children_html(ch, render):
    if ch is None or ch is False or ch is True:
        return ""
    items = ch if isinstance(ch, list) else [ch]
    out, prev_text = [], False
    for c in items:
        if isinstance(c, list):
            out.append(children_html(c, render)); prev_text = False; continue
        is_text = isinstance(c, (str, int, float)) and not isinstance(c, bool)
        if is_text:
            if prev_text:
                out.append("<!-- -->")
            out.append(html.escape(str(c), quote=False))
        else:
            out.append(render(c))
        prev_text = is_text
    return "".join(out)


def to_html(node, components):
    render = lambda n: to_html(n, components)
    if node is None or node is False or node is True:
        return ""
    if isinstance(node, (str, int, float)):
        return html.escape(str(node), quote=False)
    if isinstance(node, list):
        return children_html(node, render)
    t, props = node["type"], node["props"]
    if isinstance(t, C):
        return components[t.name](props, render)
    inner = props.get("dangerouslySetInnerHTML", {}).get("__html") if "dangerouslySetInnerHTML" in props else None
    if t in VOID:
        return f"<{t}{attrs_html(props)}/>"
    body = inner if inner is not None else children_html(props.get("children"), render)
    return f"<{t}{attrs_html(props)}>{body}</{t}>"

# ---------------------------------------------------------------- client component HTML

WIDTHS_PAGE = [640, 750, 828, 1080, 1200, 1920, 2048, 3840]
FILL_STYLE = "position:absolute;height:100%;width:100%;left:0;top:0;right:0;bottom:0;color:transparent"


def image_html(p, render):
    a = {"alt": p.get("alt", ""), "decoding": "async", "sizes": p.get("sizes"), "src": p["src"],
         "srcset": ", ".join(f'{p["src"]} {w}w' for w in WIDTHS_PAGE)}
    if p.get("className"):
        a["class"] = p["className"]
    if p.get("fill"):
        a.update({"data-nimg": "fill", "style": FILL_STYLE})
    else:
        a.update({"data-nimg": "1", "width": p["width"], "height": p["height"], "style": "color:transparent"})
    if not p.get("priority"):
        a["loading"] = "lazy"
    return "<img " + " ".join(f'{k}="{html.escape(str(v), quote=True)}"' for k, v in sorted(a.items()) if v is not None) + "/>"


TICK = ('<svg aria-hidden="true" viewbox="0 0 30 6"><path class="tick-base" d="M1.5 3.2 C6 2.1 11 3.6 16 2.6 S24 2.2 28.5 3" pathlength="1"></path>'
        '<path class="tick-ink" d="M1.5 3.2 C6 2.1 11 3.6 16 2.6 S24 2.2 28.5 3" pathlength="1"></path></svg>')


def contents_html(p, render):
    items = []
    for i, s in enumerate(p["sections"]):
        cur = ' aria-current="location" data-state="current"' if i == 0 else ' data-state="ahead"'
        items.append(f'<li><a{cur} data-tick="true" href="#{s["id"]}">{TICK}<span>{html.escape(s["label"], quote=False)}</span></a></li>')
    first = html.escape(p["sections"][0]["label"], quote=False)
    return ('<nav aria-label="Contents" class="project-contents reveal" style="--i:3"><p class="project-contents-heading">Contents</p>'
            f'<ol id="project-contents-list">{"".join(items)}</ol>'
            '<button aria-controls="project-contents-list" aria-expanded="false" class="project-contents-pill" type="button">'
            f'<span data-state="current">{TICK}</span><span class="project-contents-current">{first}</span></button></nav>')


def link_html(p, render):  # Next <Link> renders a plain anchor
    return f'<a{attrs_html(p)}>{children_html(p.get("children"), render)}</a>'


WORK_COMPONENTS = {
    "Image": image_html,
    "Highlight": lambda p, r: f'<mark class="highlight">{children_html(p.get("children"), r)}</mark>',
    "CoverSlides": lambda p, r: '<div aria-hidden="true" class="cover-slides"></div>',
    "ProjectContents": contents_html,
    "Link": link_html,
}

# ---------------------------------------------------------------- payload helpers

PUSH_RE = re.compile(r'<script>self\.__next_f\.push\((\[.*?\])\)</script>', re.S)


def read_payload(doc):
    parts = [json.loads(m.group(1)) for m in PUSH_RE.finditer(doc)]
    return "".join(p[1] for p in parts if len(p) > 1 and isinstance(p[1], str))


def split_rows(payload):
    """Return ordered [(id, body)] respecting length-prefixed text rows (`id:T<hex>,`)."""
    rows, i = [], 0
    while i < len(payload):
        m = re.compile(r'([0-9a-f]*):').match(payload, i)
        if not m:
            raise ValueError(f"bad payload at {i}: {payload[i:i+40]!r}")
        rid, j = m.group(1), m.end()
        t = re.compile(r'T([0-9a-f]+),').match(payload, j)
        if t:
            n = int(t.group(1), 16)
            start = t.end()
            # length is in UTF-8 bytes
            body_bytes = payload[start:].encode("utf-8")[:n]
            text = body_bytes.decode("utf-8")
            rows.append((rid, payload[j:start] + text, True))
            i = start + len(text)
        else:
            k = payload.find("\n", j)
            k = len(payload) if k < 0 else k
            rows.append((rid, payload[j:k], False))
            i = k + 1
    return rows


def join_rows(rows):
    return "".join(f"{rid}:{body}" + ("" if is_text else "\n") for rid, body, is_text in rows)


def write_payload(doc, payload):
    """Replace every flight push with a single push holding the full payload."""
    first = [True]
    def sub(m):
        arr = json.loads(m.group(1))
        if len(arr) > 1 and isinstance(arr[1], str):
            if first[0]:
                first[0] = False
                return "<script>self.__next_f.push(" + json.dumps([1, payload], ensure_ascii=False).replace("</", "<\\/") + ")</script>"
            return ""
        return m.group(0)
    return PUSH_RE.sub(sub, doc)


def rsc(node):
    return json.dumps(to_rsc(node), ensure_ascii=False, separators=(",", ":"))

# ---------------------------------------------------------------- content helpers

def asset_url(slug, rel):
    return f"/profile/work/{slug}/{Path(rel).name}"


def copy_asset(slug, rel):
    dest = DIST / "profile" / "work" / slug / Path(rel).name
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not dest.exists() or dest.stat().st_mtime < (ASSETS / rel).stat().st_mtime:
        shutil.copy2(ASSETS / rel, dest)
    return asset_url(slug, rel)


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower().replace("’", "")).strip("-")


def inline(parts, HL, key_prefix):
    if isinstance(parts, str):
        return [parts]
    out = []
    for i, p in enumerate(parts):
        out.append(el(HL, {}, [p[1]], key=f"{key_prefix}h{i}") if isinstance(p, tuple) else p)
    return out

# ---------------------------------------------------------------- case-study page

def metadata_tree(title, description, image, image_alt):
    m = [el("title", {}, title, key="0"), el("meta", {"name": "description", "content": description}, key="1")]
    if SITE:
        m.append(el("link", {"rel": "canonical", "href": SITE + "/"}, key="c"))
    for k, (attr, name, content) in enumerate([
        ("property", "og:title", title), ("property", "og:description", description), ("property", "og:site_name", "Ajaymon"),
        ("property", "og:image", image), ("property", "og:image:alt", image_alt), ("property", "og:type", "article"),
        ("name", "twitter:card", "summary_large_image"), ("name", "twitter:title", title),
        ("name", "twitter:description", description), ("name", "twitter:image", image), ("name", "twitter:image:alt", image_alt)]):
        m.append(el("meta", {attr: name, "content": content}, key=str(k + 3)))
    m.append(el("link", {"rel": "icon", "href": "/icon.png?icon.1d2tidy8j7kw5.png", "sizes": "256x256", "type": "image/png"}, key="19"))
    m.append(el("link", {"rel": "apple-touch-icon", "href": "/apple-icon.png?apple-icon.0p9rg_xqhc7fo.png", "sizes": "180x180", "type": "image/png"}, key="20"))
    return m


def build_case(project, nxt, template):
    L, HL, IMG, CS, PC = C("Link", "$La"), C("Highlight", "$L4b"), C("Image", "$L4c"), C("CoverSlides", "$L4d"), C("ProjectContents", "$L4a")
    slug = project["slug"]
    sizes = "(min-width: 640px) 38rem, 100vw"
    cover_rel, cw, ch, calt = project["cover"]
    cover = copy_asset(slug, cover_rel)
    slides = [copy_asset(slug, s) for s in project["slides"]]

    sections, toc = [], [{"id": "overview", "label": "Overview"}]
    for si, (heading, blocks) in enumerate(project["sections"]):
        sid = slugify(heading)
        toc.append({"id": sid, "label": heading})
        kids = [el("h2", {"className": "project-h2"}, [heading], key=f"s{si}h")]
        for bi, b in enumerate(blocks):
            if isinstance(b, tuple) and b[0] == "figure":
                _, rel, w, h, alt, cap = b
                kids.append(el("figure", {"className": "project-figure"},
                               el(IMG, {"src": copy_asset(slug, rel), "alt": alt, "width": w, "height": h, "sizes": sizes}),
                               el("figcaption", {}, cap) if cap else None, key=f"s{si}f{bi}"))
            else:
                kids.append(el("p", {}, inline(b, HL, f"s{si}p{bi}"), key=f"s{si}p{bi}"))
        sections.append(el("section", {"id": sid, "className": "project-section project-body"}, kids, key=sid))

    details = [el("div", {}, el("dt", {}, k), el("dd", {}, v), key=k) for k, v in project["details"]]
    overview = el("section", {"id": "overview", "className": "project-section"},
        el(L, {"href": "/#work", "className": "reveal link-underline project-back", "style": {"--i": 1}},
           el("span", {"aria-hidden": "true"}, "←"), " Featured projects"),
        el("h1", {"className": "reveal project-title", "style": {"--i": 2}}, project["title"]),
        el("p", {"className": "reveal project-summary", "style": {"--i": 3}}, project["summary"]),
        el("dl", {"className": "reveal project-details", "style": {"--i": 4}}, [details]),
        el("figure", {"className": "project-cover reveal", "style": {"--i": 5}},
           el(IMG, {"src": cover, "alt": calt, "fill": True, "priority": True, "sizes": sizes, "className": "object-cover"}),
           el(CS, {"slides": slides, "alt": calt})),
        False)

    ncover = asset_url(nxt["slug"], nxt["cover"][0])
    next_section = el("section", {"aria-label": "Next project", "className": "project-next"},
        el(L, {"href": f"/work/{nxt['slug']}", "className": "project-next-link", "data-cursor": "Next"},
           el("p", {"className": "project-next-label"}, "Next project"),
           el("p", {"className": "project-next-title"}, nxt["title"], " ", el("span", {"aria-hidden": "true"}, "→")),
           el("div", {"className": "project-next-thumb"},
              el(IMG, {"src": ncover, "alt": nxt["cover"][3], "fill": True, "sizes": sizes, "className": "object-cover"}))))

    ld = json.dumps({"@context": "https://schema.org", "@type": "CreativeWork", "name": project["title"],
                     "description": project["summary"], "image": cover,
                     "creator": {"@type": "Person", "name": "Ajaymon"}}, ensure_ascii=False)
    main = el("main", {"className": "project-page px-5 pt-28 md:px-8"},
        el("div", {"className": "project-layout"},
           el(PC, {"sections": toc}),
           el("div", {"className": "project-column"}, el("article", {}, overview, sections), next_section)))
    script = el("script", {"type": "application/ld+json", "dangerouslySetInnerHTML": {"__html": ld}})

    # --- payload
    rows = split_rows(read_payload(template))
    title = f'{project["title"]} — Ajaymon'
    meta = metadata_tree(title, project["summary"], cover, calt)
    content_ids = {f"{n:x}" for n in range(0x4e, 0x57)}
    new_rows = []
    for rid, body, is_text in rows:
        if rid == "46":
            body = json.dumps([to_rsc(script), to_rsc(main), "$L57"], ensure_ascii=False, separators=(",", ":"))
        elif rid == "3f":
            body = rsc(meta)
        elif rid in content_ids:
            body = "null"
        else:
            body = body.replace('"k":"goals"', f'"k":"{slug}"').replace('["","work","goals"]', f'["","work","{slug}"]')
            for old in [p["slug"] for p in PROJECTS]:
                body = body.replace(f'"k":"{old}"', f'"k":"{slug}"').replace(f'["","work","{old}"]', f'["","work","{slug}"]')
        new_rows.append((rid, body, is_text))
    doc = write_payload(template, join_rows(new_rows))

    # --- server HTML
    s1 = doc.index('<div hidden="" id="S:1">') + len('<div hidden="" id="S:1">')
    end = doc.index("<footer", s1)
    doc = doc[:s1] + to_html(script, WORK_COMPONENTS) + to_html(main, WORK_COMPONENTS) + doc[end:]

    head_start, head_end = doc.index("<title>"), doc.index('<link href="/icon.png')
    doc = doc[:head_start] + "".join(to_html(m, {}) for m in meta[:-2]) + doc[head_end:]
    doc = re.sub(r'<link as="image" imagesizes="[^"]*" imagesrcset="[^"]*" rel="preload"/>',
                 lambda _: f'<link as="image" imagesizes="{sizes}" imagesrcset="{", ".join(f"{cover} {w}w" for w in WIDTHS_PAGE)}" rel="preload"/>', doc, count=1)

    out = DIST / "work" / slug / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc)
    return out


# ---------------------------------------------------------------- shared data

def jsnum(x):
    """Format a number the way JavaScript's String(n) does for these values."""
    if isinstance(x, float) and x.is_integer():
        return str(int(x))
    return repr(x) if isinstance(x, float) else str(x)


def js_round(x):
    import math
    return math.floor(x + 0.5)


def pieces():
    """Playground/dial pieces in the shape the site's components expect."""
    out = []
    for i, (rel, w, h, alt, slug) in enumerate(PLAYGROUND):
        out.append({"alt": alt, "frames": None, "height": h, "id": f"ajaymon-{i + 1:02d}", "kind": "image", "lqip": None,
                    "onDial": rel in DIAL, "src": copy_asset(slug or "karbon-forex", rel), "video": None, "width": w})
    return out


# Ten pieces shown on the homepage dial (the component shows at most ten).
DIAL = ["invoice/overview.png", "taxos/overview.png", "project-4-0.png", "project-3-0.png", "project-2-0.png",
        "invoice/flow.png", "taxos/dashboard.png", "project-1-0.png", "project-4-2.png", "project-3-1.png"]


def dial_selection(items):
    """Port of the site's dial picker (module 141362, export k)."""
    t = [e for e in items if e.get("onDial")]
    r = t if t else [e for e in items if e["kind"] == "image"]
    a = [e for e in r if e["kind"] != "image"][:10]
    n = [e for e in r if e["kind"] == "image"][:10 - len(a)]
    i = len(n) + len(a)
    for idx, e in enumerate(a):
        n.insert(js_round(idx * i / len(a)), e)
    return n


def grid_layout(items):
    """Port of the playground row packer (module 141362, export I)."""
    ratio = lambda p: p["width"] / p["height"]
    t = [e for e in items if e["kind"] != "image"]
    r = [e for e in items if e["kind"] == "image"]
    rows, n, pattern = [], 0, [0, 2, 1]

    def pick(e, pool, extra):
        a = pool[:12]
        combos = []
        for x in range(len(a)):
            combos.append([x])
            combos.extend([x, y] for y in range(x + 1, len(a)))
        best, cost = [], float("inf")
        for o in combos:
            if len(pool) + extra - len(o) == 1:
                continue
            c = abs(ratio(e) + sum(ratio(a[k]) for k in o) - 3) + 0.01 * sum(o)
            if c < cost:
                best, cost = o, c
        return best

    while t or r:
        lead_is_media = len(t) > 0 and (len(rows) % 2 == 0 or not r)
        lead = (t if lead_is_media else r).pop(0)
        pool = r if r else t
        chosen = pick(lead, pool, len(t) if r else 0)
        row = [pool[k] for k in chosen]
        for k in reversed(chosen):
            pool.pop(k)
        if lead_is_media:
            row.insert(min(pattern[n % 3], len(row)), lead); n += 1
        else:
            row.insert(0, lead)
        rows.append(row)
    flat = [p for row in rows for p in row]
    out = []
    for row in rows:
        total = sum(ratio(p) for p in row)
        for p in row:
            k = flat.index(p)
            if len(flat) % 2 == 1 and k >= len(flat) - 3:
                pair = flat[-3:]
            elif k % 2 == 0:
                pair = flat[k:k + 2]
            else:
                pair = flat[k - 1:k + 1]
            out.append({"piece": p, "ratio": ratio(p), "wide": (ratio(p) / total, len(row)),
                        "phone": (ratio(p) / sum(ratio(q) for q in pair), len(pair))})
    return out


def vw(x):
    return f"{jsnum(js_round(1000 * x) / 10)}vw"

# ---------------------------------------------------------------- whole-site sanitising

TRACKERS = {"$L17", "$L18", "$L19"}  # Clarity <Script>, Vercel Analytics, SanityLive (same ids on every page)
ART = {"avatar": ("/profile/art/avatar.svg", 400, 400), "footer": ("/profile/art/footer-scene.svg?v=2", 620, 322)}


def scrub_tree(x):
    if isinstance(x, list):
        if len(x) == 4 and x[0] == "$" and isinstance(x[1], str):
            props = x[3] if isinstance(x[3], dict) else {}
            if x[1] == "svg" and "signature" in props.get("className", ""):
                props.update({"viewBox": SIGNATURE_VIEWBOX, "strokeWidth": SIGNATURE_STROKE,
                              "children": [["$", "path", str(i), {"d": d}] for i, d in enumerate(SIGNATURE_PATHS)]})
            if x[1] == "$L18":  # Vercel Analytics sits in a Suspense boundary; keep the boundary so hydration matches
                return ["$", "$Sreact.suspense", None, {"children": None}]
            if x[1] in TRACKERS and (x[1] != "$L17" or props.get("id") == "clarity"):
                return None
            if x[1] == "link" and props.get("rel") == "canonical" and "davemiye" in str(props.get("href")):
                return None
            if x[1] == "meta" and props.get("property") == "og:url":
                return None
        return [scrub_tree(v) for v in x]
    if isinstance(x, dict):
        return {k: scrub_tree(v) for k, v in x.items()}
    return x


TEXT_FIXES = [
    ("I take apps from the first flow to the App Store listing. Open to full-time product design roles.",
     "Product designer in Bangalore turning complex fintech workflows into clear, intuitive experiences. Open to full-time roles."),
    ("Ajaymon, Product Designer & Engineer, with the mascot saying hello in Japanese and a classical figure drawing",
     "Portrait of Ajaymon, product designer in Bangalore"),
]
# React keys on the logo grid still carried the original site's client names
LOGO_KEYS = dict(zip(["Studio Hemis", "Goals", "SimpliRide", "Circa", "Carril", "Talent360", "Workas", "Dialme", "Plate"],
                     ["Karbon Business", "FlowTax", "Karbon Forex", "AI Accountant", "Skillto", "MBRDI", "Figma", "Webflow", "Adobe"]))


def sanitize(doc):
    rows = []
    for rid, body, is_text in split_rows(read_payload(doc)):
        if not is_text and body[:1] in "[{":
            body = json.dumps(scrub_tree(json.loads(body)), ensure_ascii=False, separators=(",", ":"))
        if body.startswith('HC"https://x667x4mo.api.sanity.io"'):
            continue
        body = body.replace("https://davemiye.com/opengraph-image.jpg?opengraph-image.2ovl3d9tkf34i.jpg", "/profile/ajaymon-portrait.png")
        rows.append((rid, body, is_text))
    doc = write_payload(doc, join_rows(rows))
    for old, new in TEXT_FIXES:
        doc = doc.replace(old, new).replace(html.escape(old), html.escape(new))
    doc = re.sub(r'https://davemiye\.com/(?:opengraph|twitter)-image\.jpg(?:\?[^"\\]*)?', "/profile/ajaymon-portrait.png", doc)
    doc = re.sub(r'<link href="https://davemiye\.com[^"]*" rel="canonical"/>', "", doc)
    doc = re.sub(r'<meta content="https://davemiye\.com[^"]*" property="og:url"/>', "", doc)
    doc = re.sub(r'<link[^>]*x667x4mo\.api\.sanity\.io[^>]*>', "", doc)

    def art(m, kind):
        cls = re.search(r'class="([^"]*)"', m.group(1)).group(1)
        cur = re.search(r'data-cursor="([^"]*)"', m.group(1))
        src, w, h = ART[kind]
        extra = f' data-cursor="{cur.group(1)}"' if cur else ""
        if kind == 'avatar':
            return f'<ajay-mascot class="{cls}"></ajay-mascot>'
        return f'<img alt="" aria-hidden="true" class="{cls}"{extra} draggable="false" height="{h}" src="{src}" width="{w}"/>'
    # every render of the mascot drawing (preloader, hero, playground perch): 400x400 viewBox with a crayon- filter
    def mascot(m):
        return art(m, "avatar") if 'id="crayon-' in m.group(0) else m.group(0)
    doc = re.sub(r'<svg([^>]*viewbox="0 0 400 400"[^>]*)>.*?</svg>', mascot, doc, flags=re.S)
    doc = re.sub(r'<svg([^>]*class="footer-scene[^"]*"[^>]*)>.*?</svg>', lambda m: art(m, "footer"), doc, flags=re.S)
    doc = re.sub(r'<img[^>]*src="/profile/art/avatar.svg"[^>]*>', lambda m: '<ajay-mascot class="' + re.search(r'class="([^"]*)"', m.group(0)).group(1) + '"></ajay-mascot>', doc)
    def signature_markup(m):
        attrs = re.sub(r'viewbox="[^"]*"', 'viewbox="' + SIGNATURE_VIEWBOX + '"', m.group(1))
        attrs = re.sub(r'stroke-width="[^"]*"', 'stroke-width="' + str(SIGNATURE_STROKE) + '"', attrs)
        return '<svg' + attrs + '>' + ''.join('<path d="' + d + '"></path>' for d in SIGNATURE_PATHS) + '</svg>'
    doc = re.sub(r'<svg([^>]*class="(?:header|preloader)-signature"[^>]*)>.*?</svg>', signature_markup, doc, flags=re.S)
    doc = doc.replace('/personalize.css', '/personalize.css?v=3')
    doc = re.sub(r"/profile/art/footer-scene\.svg(?:\?v=\d+)?", "/profile/art/footer-scene.svg?v=2", doc)
    doc = doc.replace('</head>', '<style>ajay-mascot{display:block;aspect-ratio:1;height:auto}</style><script src="/mascot.js?v=2"></script></head>')
    return doc


MASCOT_MODULE = (',482852,e=>{"use strict";var t=e.i(843476);e.s(["f",0,function(e){let{viewBox:a,fill:n,...r}=e;'
                 'return(0,t.jsx)("ajay-mascot",{...r})}])}')
FOOTER_MODULE = (',345545,e=>{"use strict";var t=e.i(843476);e.s(["FooterScene",0,function({className:e}){'
                 'return(0,t.jsx)("img",{src:"/profile/art/footer-scene.svg?v=2",alt:"",draggable:!1,width:620,height:322,"aria-hidden":"true",className:e})}])}')


def send_note_js(fn, note, sender, trap, started):
    """Deliver a contact note by email through FormSubmit. Returns "delivered" or "mail-app" (fallback)."""
    endpoint = "https://formsubmit.co/ajax/" + CONTACT_EMAIL
    return (f'async function {fn}({note},{sender},{trap},{started}){{'
            f'if({trap}||Date.now()-({started}||0)<3e3)return"delivered";'
            f'try{{let __res=await fetch({json.dumps(endpoint)},{{method:"POST",headers:{{"Content-Type":"application/json",Accept:"application/json"}},'
            f'body:JSON.stringify({{email:{sender},message:{note},_replyto:{sender},_subject:"New note from your portfolio",_template:"table",_captcha:"false"}})}}),'
            f'__dat=await __res.json().catch(()=>({{}}));return __res.ok&&String(__dat.success)==="true"?"delivered":"mail-app"}}'
            f'catch(e){{return"mail-app"}}}}')


SIGNATURE_MODULE = (',291390,e=>{"use strict";var t=e.i(843476);let r=' + json.dumps(SIGNATURE_PATHS) +
    ';e.s(["f",0,function(e){return(0,t.jsx)("svg",{viewBox:' + json.dumps(SIGNATURE_VIEWBOX) +
    ',fill:"none",stroke:"currentColor",strokeWidth:' + str(SIGNATURE_STROKE) +
    ',strokeLinecap:"round",strokeLinejoin:"round",role:"img","aria-label":"Ajaymon",...e,children:r.map((e,i)=>(0,t.jsx)("path",{d:e},i))})}])}')


def patch_chunks():
    """Swap Dave Miye's drawn mascot and footer scene for image slots holding Ajaymon's own art."""
    for f in (DIST / "_next/static/immutable/chunks").glob("*.js"):
        s = original = f.read_text()
        for mod, replacement in (("482852", MASCOT_MODULE), ("345545", FOOTER_MODULE), ("291390", SIGNATURE_MODULE)):
            start = s.find(f",{mod},e=>{{")
            if start < 0 or s.startswith(replacement, start):
                continue
            end = re.compile(r'\}\]\)\}(?=,\d+(?:,\d+)*,e=>\{|\]\))').search(s, start)
            s = s[:start] + replacement + s[end.end():]
        # A failed/cancelled animation must never leave the page covered or scroll locked.
        s = s.replace('})().catch(e=>{if(!r)throw e}),', '})().catch(e=>{if(!r){u();delete t.dataset.preloader;p(!0);(0,i.i)()}}),')
        # The contact note's send step was a stub that always fell back to the visitor's mail app.
        s = re.sub(r'async function (\w+)\((\w+),(\w+),(\w+),(\w+)\)\{return"mail-app"\}',
                   lambda m: send_note_js(*m.groups()), s)
        if s != original:
            f.write_text(s)
            print("patched", f.name)


ART_SVG = {
    "avatar.svg": ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400"><circle cx="200" cy="200" r="150" fill="none" '
                   'stroke="#8d8a84" stroke-width="4" stroke-dasharray="14 12"/><text x="200" y="196" text-anchor="middle" '
                   'font-family="system-ui,sans-serif" font-size="26" fill="#8d8a84">your</text><text x="200" y="228" text-anchor="middle" '
                   'font-family="system-ui,sans-serif" font-size="26" fill="#8d8a84">avatar</text></svg>'),

}


def write_art_placeholders():
    d = DIST / "profile" / "art"
    d.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ASSETS / "art/footer-scene.svg", d / "footer-scene.svg")
    for name, svg in ART_SVG.items():
        if not (d / name).exists():  # never overwrite art you've dropped in
            (d / name).write_text(svg)

# ---------------------------------------------------------------- homepage

def find_row(rows, needle):
    for i, (rid, body, is_text) in enumerate(rows):
        if needle in body:
            return i
    raise KeyError(needle)


WIDTHS_ALL = [32, 48, 64, 96, 128, 256, 384, 640, 750, 828, 1080, 1200, 1920, 2048, 3840]


def build_home(template):
    rows = split_rows(read_payload(template))
    items = pieces()

    # Featured projects (WorkSection)
    i = find_row(rows, '{"projects":[')
    rid, body, t = rows[i]
    k = body.index('"projects":') + len('"projects":')
    old_projects, end = json.JSONDecoder().raw_decode(body, k)
    new_projects = [{"slug": p["slug"], "title": p["title"], "client": next((v for kk, v in p["details"] if kk == "Client"), ""),
                     "services": p["services"], "year": None, "summary": p["summary"],
                     "cover": {"alt": p["cover"][3], "src": asset_url(p["slug"], p["cover"][0])},
                     "slides": [asset_url(p["slug"], s) for s in p["slides"]]} for p in PROJECTS]
    rows[i] = (rid, body[:k] + json.dumps(new_projects, ensure_ascii=False, separators=(",", ":")) + body[end:], t)

    # Structured data
    person = json.dumps({"@context": "https://schema.org", "@type": "Person", "name": "Ajaymon", "jobTitle": "Product Designer",
                         "image": "/profile/ajaymon-portrait.png", "address": "Bangalore, India",
                         "sameAs": ["https://www.linkedin.com/in/ajaymon/"]}, ensure_ascii=False)
    i = find_row(rows, '"application/ld+json"')
    rid, body, t = rows[i]
    tree = json.loads(body)
    old_ld = tree[0][3]["dangerouslySetInnerHTML"]["__html"]
    tree[0][3]["dangerouslySetInnerHTML"]["__html"] = person
    rows[i] = (rid, json.dumps(tree, ensure_ascii=False, separators=(",", ":")), t)

    # Playground dial
    i = find_row(rows, '{"images":[')
    rid, body, t = rows[i]
    k = body.index('"images":') + len('"images":')
    old_images, end = json.JSONDecoder().raw_decode(body, k)
    rows[i] = (rid, body[:k] + json.dumps(items, ensure_ascii=False, separators=(",", ":")) + body[end:], t)

    for old, new in LOGO_KEYS.items():
        rows = [(r, b.replace(f'["$","li","{old}",{{"className":"clients-cell"', f'["$","li","{new}",{{"className":"clients-cell"'), t) for r, b, t in rows]
    doc = write_payload(template, join_rows(rows))

    # --- head preloads: hero photo and the dial's current piece
    def preload(m):
        tag = m.group(0)
        if "/media-cdn/" not in tag:
            return tag
        src = "/profile/ajaymon-portrait.png" if "112px, 88px" in tag else dial_selection(items)[2]["src"]
        widths = re.findall(r" (\d+)w", tag)
        return re.sub(r'imagesrcset="[^"]*"', f'imagesrcset="{", ".join(f"{src} {w}w" for w in widths)}"', tag)
    doc = re.sub(r'<link as="image"[^>]*rel="preload"/>', preload, doc)

    # --- server HTML: project rail
    def card(p):
        src = asset_url(p["slug"], p["cover"][0])
        srcset = ", ".join(f"{src} {w}w" for w in [384, 640, 750, 828, 1080, 1200, 1920, 2048, 3840])
        return (f'<article class="projects-card" data-card="true"><a class="projects-link" data-cursor="View project" draggable="false" href="/work/{p["slug"]}">'
                f'<div class="projects-thumb"><img alt="{html.escape(p["cover"][3])}" class="object-cover" data-nimg="fill" decoding="async" draggable="false" loading="lazy" '
                f'sizes="(min-width: 768px) 52vw, 82vw" src="{src}" srcset="{srcset}" style="{FILL_STYLE}"/><div aria-hidden="true" class="cover-slides"></div></div>'
                f'<div class="projects-meta"><h3 class="text-sm font-medium">{html.escape(p["title"], quote=False)}</h3>'
                f'<p class="text-sm text-muted">{html.escape(" · ".join(p["services"]), quote=False)}</p></div></a></article>')
    rail_start = doc.index('<div aria-label="Projects — scroll sideways" class="projects-rail"')
    first = doc.index("<article", rail_start)
    last = doc.rindex("</article>", rail_start, doc.index("</section>", rail_start)) + len("</article>")
    doc = doc[:first] + "".join(card(p) for p in PROJECTS) + doc[last:]

    # --- server HTML: structured data
    assert old_ld in doc
    doc = doc.replace(old_ld, person, 1)

    # --- server HTML: photo stack + client logos use local files only
    def fix_img(m):
        tag = m.group(0)
        src = re.search(r' src="([^"]*)"', tag).group(1)
        if 'class="client-logo' in tag:
            return re.sub(r' srcset="[^"]*"', "", tag)
        if src.startswith("/profile/"):
            widths = re.findall(r" (\d+)w", re.search(r' srcset="([^"]*)"', tag).group(1)) if " srcset=" in tag else []
            return re.sub(r' srcset="[^"]*"', f' srcset="{", ".join(f"{src} {w}w" for w in widths)}"', tag) if widths else tag
        return tag
    doc = re.sub(r"<img [^>]*>", fix_img, doc)

    # --- server HTML: experience ranges are three text nodes in the payload (start, " – ", end)
    doc = re.sub(r'(<span class="experience-time">)([^<]*?) – ([^<]*?)(</span>)', r'\1\2<!-- --> – <!-- -->\3\4', doc)

    # --- server HTML: each "How I work" note has one photo in the payload; drop leftover second prints
    doc = re.sub(r'(<div aria-hidden="true" class="kind-note-prints"><span class="kind-note-print"[^>]*><img [^>]*/></span>)(?:<span class="kind-note-print"[^>]*><img [^>]*/></span>)+</div>',
                 r'\1</div>', doc)

    # --- server HTML: dial (map old pieces to new by position; the structure is identical)
    old_sel, new_sel = dial_selection(old_images), dial_selection(items)
    assert len(old_sel) == len(new_sel) == 10, (len(old_sel), len(new_sel))
    ds = doc.index('<section aria-labelledby="playground-dial-title"')
    de = doc.index("</section>", ds)
    seg = doc[ds:de]
    src_map = {o["src"]: n["src"] for o, n in zip(old_sel, new_sel)}
    def remap_url(u):
        base = html.unescape(u).split("?")[0]
        return src_map.get(base, u)
    seg = re.sub(r' src="([^"]*)"', lambda m: f' src="{remap_url(m.group(1))}"', seg)
    seg = re.sub(r' srcset="([^"]*)"', lambda m: ' srcset="' + ", ".join(
        f"{remap_url(part.rsplit(' ', 1)[0])} {part.rsplit(' ', 1)[1]}" for part in m.group(1).split(", ")) + '"', seg)
    for o, n in zip(old_sel, new_sel):
        seg = seg.replace(html.escape(o["alt"]), html.escape(n["alt"])).replace(f'#view-{o["id"]}', f'#view-{n["id"]}')
    doc = doc[:ds] + seg + doc[de:]
    return doc

# ---------------------------------------------------------------- playground

def build_playground(template):
    rows = split_rows(read_payload(template))
    items = pieces()
    i = find_row(rows, '{"pieces":[')
    rid, body, t = rows[i]
    k = body.index('"pieces":') + len('"pieces":')
    _, end = json.JSONDecoder().raw_decode(body, k)
    rows[i] = (rid, body[:k] + json.dumps(items, ensure_ascii=False, separators=(",", ":")) + body[end:], t)
    doc = write_payload(template, join_rows(rows))

    tiles = []
    for n, e in enumerate(grid_layout(items)):
        p = e["piece"]
        (ws, wc), (ps, pc) = e["wide"], e["phone"]
        style = (f'--i:{5 + n % 6};--lean:{"0.8" if n % 2 else "-0.8"}deg;--ratio:{jsnum(e["ratio"])};--wide-share:{jsnum(ws)};'
                 f'--wide-count:{wc};--phone-share:{jsnum(ps)};--phone-count:{pc}')
        sizes = f"(min-width: 1216px) {js_round(1152 * ws)}px, (min-width: 640px) {vw(ws)}, {vw(ps)}"
        srcset = ", ".join(f'{p["src"]} {w}w' for w in WIDTHS_ALL)
        alt = html.escape(p["alt"])
        tiles.append(f'<li class="playground-tile reveal" style="{style}"><button aria-label="View {alt} larger" data-cursor="View" type="button">'
                     f'<img alt="{alt}" data-nimg="1" decoding="async" draggable="false" height="{p["height"]}" loading="lazy" sizes="{sizes}" '
                     f'src="{p["src"]}" srcset="{srcset}" style="color:transparent" width="{p["width"]}"/></button></li>')
    gs = doc.index('<ul class="playground-grid">')
    ge = doc.index("</ul>", gs) + len("</ul>")
    doc = doc[:gs] + '<ul class="playground-grid">' + "".join(tiles) + "</ul>" + doc[ge:]
    return doc

# ---------------------------------------------------------------- mobile-only styles

MOBILE_CSS = """/* ajaymon-mobile: phone-only refinements; desktop (768px+) is untouched */
@media (max-width:767px){
  html[data-revealed] body::before{content:"";position:fixed;inset:0 0 auto;height:4.25rem;z-index:49;pointer-events:none;
    background:linear-gradient(to bottom,var(--paper) 62%,transparent)}
  main section.py-28{padding-top:5rem;padding-bottom:5rem}
  footer#contact{padding-top:5rem}
  .projects-meta p{white-space:normal}
}
"""


def write_mobile_css():
    f = DIST / "personalize.css"
    css = f.read_text()
    css = css.split("/* ajaymon-mobile:")[0].rstrip() + "\n" + MOBILE_CSS
    f.write_text(css)

# ---------------------------------------------------------------- main

def main():
    write_art_placeholders()
    write_mobile_css()
    patch_chunks()
    work = (TEMPLATES / "work.html").read_text()
    for i, p in enumerate(PROJECTS):
        out = build_case(p, PROJECTS[(i + 1) % len(PROJECTS)], work)
        out.write_text(sanitize(out.read_text()))
        print("wrote", out.relative_to(ROOT))
    (DIST / "index.html").write_text(sanitize(build_home((TEMPLATES / "home.html").read_text())))
    print("wrote dist/index.html")
    (DIST / "playground" / "index.html").write_text(sanitize(build_playground((TEMPLATES / "playground.html").read_text())))
    print("wrote dist/playground/index.html")


if __name__ == "__main__":
    main()
