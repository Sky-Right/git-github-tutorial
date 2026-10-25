#!/usr/bin/env python3
"""Crop real VS Code captures; preserve native labels and colors.

Raw desktop captures stay local. Pass their directory with --raw when replacing
the screenshots. The manifest records the exact crops and source hashes.
"""
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
CAPTURES = {
    'init': ('init.png', (500, 105, 1120, 215), [], 'Git: Initialize Repository; default branch main'),
    'changes': ('diff.png', (125, 400, 705, 520), [], 'Changes lists the unstaged index.html edit; opening this list is read-only'),
    'diff': ('diff.png', (735, 160, 1650, 355), [], 'Click index.html in Changes; inline diff compares working file with index'),
    'stage': ('diff.png', (125, 400, 705, 520), [(603, 454, 639, 498)], 'Stage Changes (+) copies v2 into the index; HEAD remains A'),
    'unstage': ('staged.png', (125, 400, 705, 520), [(603, 454, 639, 498)], 'Unstage Changes (-) restores the index from A; working v2 is kept'),
    'commit': ('commit.png', (160, 225, 700, 390), [(170, 238, 689, 305), (170, 322, 689, 386)], 'Enter Add homepage, then Commit; staged v2 becomes B locally'),
    'history': ('history.png', (125, 827, 705, 1010), [], 'Built-in Source Control Graph displays B then A; inspection does not check out a commit'),
    'switch': ('switch.png', (500, 105, 1250, 215), [], 'Status Bar branch selector: choose existing add-style; HEAD changes, both tips stay at B'),
    'merge': ('merge.png', (500, 105, 1300, 215), [], 'Git: Merge... on main, select add-style; fast-forward from B to C'),
    'publish': ('publish.png', (160, 315, 700, 390), [], 'Publish Branch with origin configured pushes main and sets origin/main as upstream'),
}


def prepare(raw, out):
    out.mkdir(parents=True, exist_ok=True)
    manifest = {'version': '1.137.0', 'commit': '645f29cc3176500b4b5762ba887cf2a7f0ffdf2c',
                'captured': '2026-10-25', 'platform': 'macOS', 'theme': 'Dark Modern',
                'locale': 'zh-cn', 'extensions': 'Built-in Git only; empty temporary profile',
                'editing': 'Crops and thin blue outlines only; no UI text or colors replaced', 'images': []}
    for name, (source, bounds, highlights, operation) in CAPTURES.items():
        data = (raw / source).read_bytes()
        im = Image.open(raw / source).convert('RGB')
        assert im.size == (2400, 1600), (source, im.size)
        im = im.crop(bounds)
        draw = ImageDraw.Draw(im)
        for x1, y1, x2, y2 in highlights:
            draw.rounded_rectangle((x1-bounds[0], y1-bounds[1], x2-bounds[0], y2-bounds[1]), radius=5, outline='#67b7f7', width=3)
        im.save(out / f'{name}.png', optimize=True)
        manifest['images'].append({'file': f'{name}.png', 'source': source, 'sourceSHA256': hashlib.sha256(data).hexdigest(),
                                   'crop': bounds, 'highlights': highlights, 'operation': operation})
    # Real inputs before choosing a side, then the result after choosing Current.
    # Omit empty editor space and the unrelated footer line, which is unchanged.
    source = 'conflict-result.png'
    im = Image.open(raw / source).convert('RGB')
    before = Image.open(raw / 'conflict.png').convert('RGB')
    canvas = Image.new('RGB', (1640, 466), 'white')
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.truetype(str(ROOT / 'theme/fonts/DroidSerif-400.ttf'), 27)
    draw.text((0, 0), 'Incoming', font=font, fill='#1a1a1a')
    draw.text((830, 0), 'Current: Accept Current', font=font, fill='#1a1a1a')
    canvas.paste(before.crop((735, 223, 2375, 410)), (0, 36))
    draw.text((0, 243), 'Result — after choosing Current', font=font, fill='#1a1a1a')
    canvas.paste(im.crop((735, 710, 2375, 905)), (0, 271))
    canvas.save(out / 'conflict.png', optimize=True)
    manifest['images'].append({'file': 'conflict.png', 'source': source,
                              'sourceSHA256': hashlib.sha256((raw/source).read_bytes()).hexdigest(),
                              'inputSource': 'conflict.png', 'inputSourceSHA256': hashlib.sha256((raw/'conflict.png').read_bytes()).hexdigest(),
                              'crops': [[735, 223, 2375, 410], [735, 710, 2375, 905]],
                              'operation': 'Actual Merge Editor inputs before choosing Current, then Result afterward: Our homepage. Complete Merge saves/resolves the file; the merge still needs a commit.'})
    (out / 'captures.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(f'Prepared {len(manifest["images"])} real VS Code excerpts in {out}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw', type=Path, required=True)
    parser.add_argument('--out', type=Path, default=ROOT/'images/vscode')
    args = parser.parse_args()
    prepare(args.raw, args.out)
