#!/usr/bin/env python3
"""Build one crawlable page per video at work/<slug>/index.html, plus sitemap.xml and robots.txt.

Each page is a copy of index.html with its own title, description, preview image, canonical URL
and VideoObject data, so Google and link previews see every project. Re-run after editing index.html:
    python3 build_pages.py
"""
import html, json, os, re, shutil, subprocess

SITE = "https://samcahillproductions.com"
src = open("index.html", encoding="utf-8").read()
script = src[src.index("<script>") + 8:src.index("const url = v =>")]  # data block only
# Evaluate the data block (W, YT_TITLES, PRESS) without a browser
data = json.loads(subprocess.run(
    ["node", "-e", script[script.index("const W = ["):script.index("// Sam's picks lead the grid")] + ";console.log(JSON.stringify(W))"],
    capture_output=True, text=True, check=True).stdout)
press = json.loads(src[src.index("const PRESS = ") + 14:src.index("\n};", src.index("const PRESS = ")) + 2])

def meta(s, prop, val):
    return re.sub(r'(<meta (?:property|name)="%s" content=")[^"]*(")' % re.escape(prop), lambda m: m.group(1) + val + m.group(2), s)

shutil.rmtree("work", ignore_errors=True)
urls = [SITE + "/"]
for w in data:
    slug, name, v = w["slug"], w["name"], w["v"]
    first = v[0] if isinstance(v, list) else v
    vid = None if first.startswith("ig:") else first.replace("short:", "")
    info = press.get(slug, {})
    desc = info.get("blurb") or f"{name}. {info.get('credit', 'A Sam Cahill project')}."
    if info.get("credit"):
        desc = f"{info['credit']}. {desc}"
    image = f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg" if vid else f"{SITE}/images/jxdn-thumb.jpg"
    url = f"{SITE}/work/{slug}/"
    e = lambda t: html.escape(t, quote=True)
    ld = {"@context": "https://schema.org", "@type": "VideoObject", "name": name, "description": desc,
          "thumbnailUrl": image, "url": url, "creator": {"@type": "Person", "name": "Sam Cahill", "url": SITE + "/"}}
    if vid:
        ld["embedUrl"] = f"https://www.youtube.com/embed/{vid}"
    page = src.replace('<meta charset="utf-8">', '<meta charset="utf-8">\n<base href="/">', 1)
    page = re.sub(r"<title>.*?</title>", f"<title>{e(name)} | Sam Cahill</title>", page, count=1)
    page = meta(page, "description", e(desc))
    page = meta(page, "og:title", e(f"{name} | Sam Cahill"))
    page = meta(page, "og:description", e(desc))
    page = meta(page, "og:image", e(image))
    page = meta(page, "og:url", e(url))
    page = meta(page, "og:type", "video.other")
    page = page.replace(f'<link rel="canonical" href="{SITE}/">', f'<link rel="canonical" href="{url}">', 1)
    page = re.sub(r'<script type="application/ld\+json">.*?</script>',
                  lambda m: '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False).replace("</", "<\\/") + "</script>", page, count=1, flags=re.S)
    os.makedirs(f"work/{slug}", exist_ok=True)
    open(f"work/{slug}/index.html", "w", encoding="utf-8").write(page)
    urls.append(url)

open("sitemap.xml", "w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                               + "".join(f"  <url><loc>{u}</loc></url>\n" for u in urls) + "</urlset>\n")
open("robots.txt", "w").write(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")
print(f"built {len(urls) - 1} pages")
