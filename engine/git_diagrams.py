#!/usr/bin/env python3
"""Editable SVG teaching diagrams. Run through build-git.sh after changing these layouts."""
from pathlib import Path
from html import escape

OUT = Path(__file__).resolve().parents[1] / 'images' / 'git-course'
C = dict(ink='#182230', inkbg='#F0F3F7', muted='#566479', line='#C8D1DD', paper='#FFFFFF',
         teal='#087F8C', tealbg='#EAF7F7', violet='#6654C0', violetbg='#F0EDFA',
         orange='#BA502B', orangebg='#FFF0E9', green='#237759', greenbg='#EAF6F0')
STYLE = '''text{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif;fill:#182230;font-size:26px} .muted{fill:#566479;font-size:23px}.mono{font-family:ui-monospace,"SFMono-Regular",Consolas,monospace;font-size:23px}.heading{font-size:27px;font-weight:650}.small{font-size:21px}.line{fill:none;stroke:#C8D1DD;stroke-width:3;stroke-linecap:round;stroke-linejoin:round}'''

def t(x, y, value, cls='', fill=None, anchor='start'):
    color = f' style="fill:{C.get(fill, fill)}"' if fill else ''
    return f'<text x="{x}" y="{y}" class="{cls}" text-anchor="{anchor}"{color}>{escape(value)}</text>'

def box(x, y, w, h, fill='paper', stroke='line', radius=4):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{C.get(fill,fill)}" stroke="{C.get(stroke,stroke)}" stroke-width="2"/>'

def line(x1, y1, x2, y2, color='line', dashed=False):
    return f'<path d="M{x1} {y1}L{x2} {y2}" fill="none" stroke="{C.get(color,color)}" stroke-width="4" stroke-linecap="round"'+(' stroke-dasharray="8 8"' if dashed else '')+'/>'

def path(d, color='violet'):
    return f'<path d="{d}" fill="none" stroke="{C.get(color,color)}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>'

def arrow(x1, y1, x2, y2, color='teal'):
    return line(x1,y1,x2,y2,color) + f'<path d="M{x2-10 if x2>x1 else x2+10} {y2-7}L{x2} {y2}L{x2-10 if x2>x1 else x2+10} {y2+7}" fill="none" stroke="{C[color]}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>'

def node(x,y,name,color='ink',below=True):
    return f'<circle cx="{x}" cy="{y}" r="12" fill="{C[color]}" stroke="#fff" stroke-width="3"/>'+t(x,y+(43 if below else -28),name,'mono',color,'middle')

def svg(name,title,body,width=1080,height=340,desc=''):
    OUT.mkdir(parents=True,exist_ok=True)
    text=f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc"><title id="title">{escape(title)}</title><desc id="desc">{escape(desc or title)}</desc><style>{STYLE}</style>{body}</svg>\n'
    (OUT/f'{name}.svg').write_text(text)

def tree(x, y, initialized):
    rows = ['my-first-project/', '  README.md', '  index.html', '  style.css']
    if initialized:
        rows.append('  .git/')
    return ''.join(t(x, y + i * 37, value, 'mono', 'violet' if value.strip() == '.git/' else 'ink') for i, value in enumerate(rows))


def area_row(y, label, working, staged, tip, caption):
    b = t(8, y + 25, label, 'muted')
    for x, title in [(0, 'Working directory'), (240, 'Staging area'), (480, 'Local repository')]:
        b += box(x + 2, y + 45, 216, 142) + t(x + 14, y + 76, title, 'small')
    for x, rows in [(16, working), (254, staged)]:
        for i, value in enumerate(rows):
            b += t(x, y + 110 + i * 29, value, 'mono small', 'teal' if x == 254 else 'ink')
    if tip:
        points = [('A', 530)] if tip == 'A' else [('A', 525), ('B', 630)]
        if len(points) > 1:
            b += line(525, y + 127, 630, y + 127, 'violet')
        for name, x in points:
            b += node(x, y + 127, name, 'violet')
        b += t(494, y + 107, 'HEAD → main', 'mono small')
    else:
        b += t(496, y + 122, 'No commits', 'mono small', 'muted')
    b += t(8, y + 218, caption, 'small', 'muted')
    return b


def area_scene(name, before, after, title):
    svg(name, title, area_row(0, 'Before', *before) + area_row(245, 'After', *after), 700, 475)


def graph_row(y, label, mode, head, main, feature=None, file=''):
    b = t(8, y + 25, label, 'muted')
    if mode in ('AB', 'ABC'):
        points = [('A', 50, 135), ('B', 185, 135)]
        if mode == 'ABC':
            points.append(('C', 325, 135))
        b += line(points[0][1], y + 135, points[-1][1], y + 135, 'ink')
    else:
        points = [('A', 35, 135), ('B', 125, 135), ('C', 215, 135), ('D', 305, 65)]
        b += line(35, y + 135, 215, y + 135, 'ink')
        b += path(f'M215 {y+135} C260 {y+135} 260 {y+65} 305 {y+65}')
        if mode in ('ABCDE', 'MERGE'):
            points.append(('E', 305, 135))
            b += line(215, y + 135, 305, y + 135, 'ink')
        if mode == 'MERGE':
            points.append(('M', 405, 135))
            b += line(305, y + 135, 405, y + 135, 'ink')
            b += path(f'M305 {y+65} C350 {y+65} 350 {y+135} 405 {y+135}')
    for n, x, yy in points:
        b += node(x, y + yy, n, 'green' if n == 'M' else ('violet' if n == 'D' or (n == 'C' and mode == 'ABC') else 'ink'))
    refs = [(f'HEAD → {head}', 'teal'), (f'main → {main}', 'ink')]
    if feature:
        refs.append((f'{feature[0]} → {feature[1]}', 'violet'))
    for i, (ref, color) in enumerate(refs):
        b += t(450, y + 76 + i * 36, ref, 'mono small', color)
    b += t(8, y + 209, file, 'mono small', 'muted')
    return b


def graph_scene(name, title, before, after):
    svg(name, title, graph_row(0, 'Before', *before) + graph_row(235, 'After', *after), 700, 465)


def remote_panel(x, y, label, state, local):
    b = t(x + 10, y + 32, label, 'heading')
    if state == 'empty':
        return b + t(x + 12, y + 128, 'No commits', 'muted')
    head, main, tracking, feature = state
    refs = []
    if local:
        tip = main if head == 'main' else feature
        refs.append((f'HEAD → {head} → {tip}', 'teal'))
    if not local or head != 'main':
        refs.append((f'main → {main}', 'ink'))
    if tracking:
        refs.append((f'origin/main → {tracking}', 'orange'))
    elif feature and not local:
        refs.append((f'improve-readme → {feature}', 'violet'))
    for i, (value, color) in enumerate(refs):
        b += t(x + 10, y + 65 + i * 29, value, 'mono small', color)
    if feature:
        if main != 'Q':
            b += line(x + 65, y + 162, x + 245, y + 162, 'violet')
            b += node(x + 65, y + 162, 'N') + node(x + 245, y + 162, 'P', 'violet')
        if main == 'Q':
            # A GitHub merge commit has N and P as parents, even when a fast-forward was possible.
            pass
            b += line(x + 50, y + 163, x + 285, y + 163, 'ink')
            b += path(f'M{x+50} {y+163} C{x+100} {y+163} {x+130} {y+115} {x+180} {y+115} C{x+235} {y+115} {x+235} {y+163} {x+285} {y+163}')
            b += node(x + 50, y + 163, 'N') + node(x + 180, y + 115, 'P', 'violet') + node(x + 285, y + 163, 'Q', 'green')
    else:
        sequence = ['M'] if main == 'M' and tracking != 'N' else (['N', 'Q'] if main == 'Q' else ['M', 'N'])
        b += t(x + 12, y + 170, '…', 'mono', 'muted') + line(x + 45, y + 162, x + (240 if len(sequence) == 2 else 160), y + 162, 'ink')
        for i, value in enumerate(sequence):
            b += node(x + (105 + i * 135 if len(sequence) == 2 else 160), y + 162, value, 'green' if value == 'Q' else 'ink')
    return b


def remote_scene(name, title, before, after, direction=None):
    b = ''
    for y, label, pair in [(0, 'Before', before), (235, 'After', after)]:
        b += t(350, y + 25, label, 'muted', None, 'middle')
        b += remote_panel(0, y, 'Local', pair[0], True) + remote_panel(380, y, 'GitHub', pair[1], False)
        if y and direction:
            b += arrow(333 if direction == 'push' else 367, y + 162, 367 if direction == 'push' else 333, y + 162, 'orange' if direction == 'push' else 'teal')
    if name == 'remote-add':
        b += t(10, 123, 'origin: not configured', 'mono small', 'muted')
        b += t(10, 358, 'origin: GitHub URL', 'mono small', 'teal')
    svg(name, title, b, 700, 465, title + '. Earlier history is abbreviated by an ellipsis. HEAD names the current local branch. GitHub has its own branch references.')


def build():
    b = t(20, 35, 'Before', 'muted') + t(400, 35, 'After git init', 'muted')
    b += tree(20, 100, False) + tree(400, 100, True) + arrow(330, 160, 380, 160, 'teal')
    svg('init', 'git init adds .git without changing the project files', b, 700, 330)
    b = ''
    for i, (title, desc) in enumerate([('Working directory', 'Files you edit'), ('Staging area', 'Next snapshot'), ('Local repository', 'Saved commits')]):
        x = i * 370
        b += box(x + 2, 70, 300, 185) + t(x + 20, 110, title, 'heading') + t(x + 20, 155, desc, 'muted')
        b += t(x + 20, 215, 'index.html' if i < 2 else 'A — B', 'mono', 'violet' if i == 2 else 'ink')
    b += t(335, 40, 'git add', 'mono', 'teal', 'middle') + arrow(312, 170, 358, 170, 'teal')
    b += t(705, 40, 'git commit', 'mono', 'violet', 'middle') + arrow(682, 170, 728, 170, 'violet')
    svg('areas', 'The three local areas', b, 1080, 290)
    files = ['README.md', 'index.html', 'style.css']
    empty = ['Empty']
    area_scene('initial-stage', (files, empty, None, 'All three files are untracked.'), (files, files, None, 'All three file contents are staged. The files stay in place.'), 'git add . stages the three initial project files')
    area_scene('initial-commit', (files, files, None, 'The staged snapshot contains all three files.'), (files, files, 'A', 'A: Add project files. All three files are now tracked.'), 'The first commit saves the three project files')
    v1 = ['index.html: v1', 'Hello']
    v2 = ['index.html: v2', 'My homepage']
    area_scene('edit', (v1, v1, 'A', 'README.md and style.css are unchanged.'), (v2, v1, 'A', 'Only the working copy of index.html changed.'), 'Editing index.html changes only the working directory')
    area_scene('stage', (v2, v1, 'A', 'The homepage edit is not staged yet.'), (v2, v2, 'A', 'The new homepage is staged. No new commit yet.'), 'git add index.html stages its current contents')
    area_scene('commit', (v2, v2, 'A', 'The staged snapshot is ready.'), (v2, v2, 'B', 'B: Add homepage. README.md and style.css are still included.'), 'git commit records the homepage snapshot as B')
    b = ''
    for x, title, version in [(0, 'Working directory', 'v3'), (370, 'Staging area', 'v2'), (740, 'Next commit', 'v2')]:
        b += box(x + 2, 30, 300, 175) + t(x + 20, 70, title, 'heading') + t(x + 20, 120, 'index.html', 'mono') + t(x + 20, 170, version, 'heading', 'teal' if x else 'ink')
    svg('staging-versions', 'The next commit uses staged v2 even if the working file has become v3', b, 1080, 240)
    b = line(120, 125, 960, 125, 'ink')
    for x, name, message in [(120, 'A', 'Add project files'), (540, 'B', 'Add homepage'), (960, 'C', 'Use navy text')]:
        b += node(x, 125, name) + t(x, 220, message, '', None, 'middle')
    svg('history', 'Commit snapshots of the same project', b, 1080, 270)
    base = ('AB', 'main', 'B', None, 'style.css: color #222')
    branched = ('AB', 'main', 'B', ('add-style', 'B'), 'style.css: color #222')
    selected = ('AB', 'add-style', 'B', ('add-style', 'B'), 'The files are unchanged: both names point to B.')
    feature = ('ABC', 'add-style', 'B', ('add-style', 'C'), 'style.css: color navy')
    on_main = ('ABC', 'main', 'B', ('add-style', 'C'), 'style.css: color #222')
    merged = ('ABC', 'main', 'C', ('add-style', 'C'), 'style.css: color navy')
    graph_scene('branch-start', 'Creating a branch adds a name at B and leaves HEAD on main', base, branched)
    graph_scene('switch', 'Switch changes HEAD to add-style; both branches still point at B', branched, selected)
    graph_scene('branch-work', 'Committing the style change advances add-style to C', selected, feature)
    graph_scene('switch-main', 'Switching to main restores its files at B', feature, on_main)
    graph_scene('fast-forward', 'Merging add-style fast-forwards main from B to C', on_main, merged)
    footer = ('ABCD', 'add-footer', 'C', ('add-footer', 'D'), 'D adds a footer to index.html. main stays at C.')
    changed_main = ('ABCDE', 'main', 'E', ('add-footer', 'D'), 'E adds a description to README.md. The footer is on D.')
    final = ('MERGE', 'main', 'M', ('add-footer', 'D'), 'M contains both edits. Its parents are E and D.')
    graph_scene('footer-branch', 'A second feature branch adds a footer at D', ('ABC', 'main', 'C', None, 'Start from the shared history through C.'), footer)
    graph_scene('main-change', 'main gains E while add-footer stays at D', footer, changed_main)
    graph_scene('merge', 'A merge commit joins the two histories at M', changed_main, final)
    local_m = ('main', 'M', None, None)
    tracking_m = ('main', 'M', 'M', None)
    remote_m = ('main', 'M', None, None)
    remote_n = ('main', 'N', None, None)
    fetched = ('main', 'M', 'N', None)
    local_n = ('main', 'N', 'N', None)
    pr_local = ('improve-readme', 'N', 'N', 'P')
    pr_remote = ('main', 'N', None, 'P')
    merged_remote = ('main', 'Q', None, 'P')
    remote_scene('remote-add', 'Adding origin records the remote URL; it uploads no commits', (local_m, 'empty'), (local_m, 'empty'))
    remote_scene('push', 'Pushing main uploads its history through M', (local_m, 'empty'), (tracking_m, remote_m), 'push')
    b = t(20, 35, 'New local folder', 'heading') + tree(20, 100, True)
    b += t(395, 35, 'GitHub', 'heading') + t(395, 105, 'main → M', 'mono') + node(535, 160, 'M', 'violet')
    b += arrow(390, 245, 275, 245, 'teal') + t(540, 280, 'clone', 'mono', 'teal', 'middle')
    b += t(20, 335, 'HEAD → main → M', 'mono') + t(20, 375, 'origin/main → M', 'mono', 'orange')
    svg('clone', 'Clone creates a new folder with working files, Git history and origin', b, 700, 410)
    remote_scene('fetch', 'A teammate added N on GitHub; fetch updates origin/main but leaves local main at M', (tracking_m, remote_n), (fetched, remote_n), 'fetch')
    remote_scene('pull', 'Pull fetches and then fast-forwards local main to N', (fetched, remote_n), (local_n, remote_n), 'fetch')
    remote_scene('pr-branch', 'A local README commit P is on improve-readme; main stays at N', (local_n, remote_n), (pr_local, remote_n))
    remote_scene('pr-push', 'Push shares improve-readme at P without merging main', (pr_local, remote_n), (pr_local, pr_remote), 'push')
    remote_scene('pr-merge', 'The GitHub merge-commit option creates Q with parents N and P; local branches have not moved', (pr_local, pr_remote), (pr_local, merged_remote))
    remote_scene('sync', 'After switching to main, pull advances local main from N to Q', (local_n, merged_remote), (('main', 'Q', 'Q', 'P'), merged_remote), 'fetch')
    b = ''
    for i, label in enumerate(['Branch', 'Commit', 'Push', 'Open PR', 'Review', 'Merge']):
        x = i * 182
        b += t(x + 10, 90, label, 'heading')
        if i < 5:
            b += arrow(x + 140, 82, x + 173, 82, 'teal')
    svg('collaboration', 'Branch, commit, push, open a pull request, review, merge', b, 1080, 160)
    b = line(60, 170, 1020, 170, 'ink') + path('M300 170 C410 170 410 55 520 55 L680 55 C820 55 820 170 1020 170')
    for x, y in [(60, 170), (300, 170), (660, 170), (680, 55), (1020, 170)]:
        b += f'<circle cx="{x}" cy="{y}" r="14" fill="{C["violet"] if y == 55 else C["ink"]}"/>'
    svg('cover', 'A Git history branches and merges', b, 1080, 215)


if __name__ == '__main__':
    build()
    print(f'Generated course diagrams in {OUT}')
