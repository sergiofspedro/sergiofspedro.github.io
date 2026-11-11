"""Generate one static page per project (/<slug>/index.html) from the master index.html.

GitHub Pages only serves real files, so each project URL needs its own index.html. Each copy is the
master page with that project preselected and its own title, so links such as
https://sergiofspedro.github.io/fundingaicopilot/ open straight on the project.

Run after any change to index.html:   python tools/build_pages.py
The slugs live in PROJECT_SLUGS inside index.html; this script reads them from there.
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://sergiofspedro.github.io/'


def read(p):
    return open(os.path.join(ROOT, p), encoding='utf8', newline='').read()


master = read('index.html')
block = re.search(r'var PROJECT_SLUGS = \{(.*?)\};', master, re.S).group(1)
slugs = dict(re.findall(r"(\w+): '([^']*)'", block))
slugs['about'] = 'aboutme'  # the root already shows About; /aboutme/ is the explicit address

names = {}
for m in re.finditer(r'<button class="sidebar-project-link[^"]*" data-id="(\w+)"[^>]*>([^<]*)', master):
    names[m.group(1)] = m.group(2).strip()

taken = {d for d in os.listdir(ROOT) if os.path.isdir(os.path.join(ROOT, d))} - set(slugs.values())
clash = [s for s in slugs.values() if s in taken]
if clash:
    sys.exit('slug clashes with an existing folder: %s' % clash)


def build(pid, slug):
    h = master
    # visible section
    h = re.sub(r'<section id="project-about"( style="display:none")?>', '<section id="project-about" style="display:none">', h)
    h = re.sub(r'<section id="project-%s"( style="display:none")?>' % pid, '<section id="project-%s">' % pid, h)
    # active button
    def active(m):
        tag = m.group(0).replace(' active"', '"')
        if 'data-id="%s"' % pid in tag:
            tag = tag.replace('" data-id=', ' active" data-id=', 1)
        return tag
    h = re.sub(r'<button class="(?:mobile-nav-link|sidebar-project-link)[^"]*" data-id="\w+"', active, h)
    url = SITE + slug + '/'
    title = '%s - Sérgio Pedro' % names[pid]
    h = h.replace('<title>Sérgio Pedro - Portfolio</title>', '<title>%s</title>\n  <link rel="canonical" href="%s" />' % (title, url), 1)
    h = h.replace('<meta property="og:title" content="Sérgio Pedro - Portfolio" />', '<meta property="og:title" content="%s" />' % title, 1)
    h = h.replace('<meta property="og:url" content="%s" />' % SITE, '<meta property="og:url" content="%s" />' % url, 1)
    out = os.path.join(ROOT, slug)
    os.makedirs(out, exist_ok=True)
    open(os.path.join(out, 'index.html'), 'w', encoding='utf8', newline='').write(h)


for pid, slug in slugs.items():
    build(pid, slug)
print('built %d pages: %s' % (len(slugs), ', '.join(slugs.values())))
