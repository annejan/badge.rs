#!/usr/bin/env python3
"""Cut badger.webp and snake.webp out of Badge.Team's konsool_mascots.svg.

Usage: tools/sprites.py path/to/konsool_mascots.svg
(from https://github.com/badgeteam/website, content/en/docs/Badges/Konsool/)

The badger and the snake share one purple outline in the drawing, so each gets the part of
it around its own fills. The badger's foot covers the left end of the snake's hoverboard;
that end is drawn in here: square, like the tail of a real hoverboard (the nose is the
rounded end), in the board's pink with a purple rim.
Needs inkscape, ImageMagick and Pillow.
"""
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

# Children of the drawing's main group: 0 confetti, 1 the shared outline, 2-4 board and
# snake, 5-17 badger, keyboard phone and CRT.
LAYERS = {'outline': [1], 'snakefill': [2, 3, 4], 'badgerfill': list(range(5, 18))}


def render(svg, keep, png):
    ET.register_namespace('', 'http://www.w3.org/2000/svg')
    tree = ET.parse(svg)
    group = tree.getroot()[3]
    for i, child in enumerate(list(group)):
        if i not in keep:
            group.remove(child)
    part = png.with_suffix('.svg')
    tree.write(part)
    subprocess.run(['inkscape', str(part), '--export-type=png', '--export-area-page',
                    '--export-width=2000', '-o', str(png)], check=True, capture_output=True)


def cut(tmp, name):
    """The fills over their own share of the outline, trimmed."""
    run = lambda *a: subprocess.run(['magick', *map(str, a)], check=True)
    run(tmp / f'{name}fill.png', '-alpha', 'extract', '-threshold', '10%', '-morphology', 'Close', 'Disk:30',
        '-morphology', 'Dilate', 'Disk:16', tmp / f'{name}mask.png')
    run(tmp / 'outline.png', '(', tmp / 'outline.png', '-alpha', 'extract', tmp / f'{name}mask.png',
        '-compose', 'Multiply', '-composite', ')', '-alpha', 'off', '-compose', 'CopyOpacity', '-composite',
        tmp / f'{name}line.png')
    run(tmp / f'{name}line.png', tmp / f'{name}fill.png', '-compose', 'Over', '-composite', '-trim', '+repage',
        tmp / f'{name}.png')


def board_end(src, dst):
    s = Image.open(src).convert('RGBA')
    px = s.load()
    for y in range(250, 305):              # a stray bit of the badger's outline
        for x in range(0, 40):
            px[x, y] = (0, 0, 0, 0)
    # Clear what's left of the cut beyond the new tail, a line from (50, 205) to (80, 398).
    for y in range(185, 445):
        edge = 50 + (80 - 50) * (min(max(y, 205), 398) - 205) / (398 - 205)
        for x in range(0, int(edge)):
            px[x, y] = (0, 0, 0, 0)
    pad = 30
    bez = lambda p0, p1, p2, p3, n=30: [tuple((1 - t) ** 3 * a + 3 * (1 - t) ** 2 * t * b + 3 * (1 - t) * t ** 2 * c + t ** 3 * e
                                              for a, b, c, e in zip(p0, p1, p2, p3)) for t in (i / n for i in range(n + 1))]
    o = lambda x, y: (x + pad, y)
    pts = ([o(88, 203), o(64, 205)] + bez(o(64, 205), o(50, 206), o(50, 206), o(52, 220))
           + [o(78, 384)] + bez(o(78, 384), o(80, 398), o(80, 398), o(95, 401))
           + [o(125, 408), o(195, 432), o(230, 330), o(200, 215)])
    mask = Image.new('L', (s.width + pad, s.height), 0)
    ImageDraw.Draw(mask).polygon(pts, fill=255)
    out = Image.new('RGBA', mask.size, (0, 0, 0, 0))
    rim = Image.new('RGBA', mask.size, (0x66, 0x24, 0x83, 255))
    rim.putalpha(mask.filter(ImageFilter.MaxFilter(19)))
    out.alpha_composite(rim)
    pink = Image.new('RGBA', mask.size, (0xE9, 0x40, 0x76, 255))
    pink.putalpha(mask)
    out.alpha_composite(pink)
    out.alpha_composite(s, (pad, 0))
    out.save(dst)


def main(svg):
    root = Path(__file__).resolve().parent.parent
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        for name, keep in LAYERS.items():
            render(svg, keep, tmp / f'{name}.png')
        cut(tmp, 'badger')
        cut(tmp, 'snake')
        board_end(tmp / 'snake.png', tmp / 'snake2.png')
        webp = ['-quality', '88', '-define', 'webp:alpha-quality=100']
        subprocess.run(['magick', tmp / 'badger.png', '-resize', '560x', *webp, root / 'badger.webp'], check=True)
        subprocess.run(['magick', tmp / 'snake2.png', '-resize', '520x', *webp, root / 'snake.webp'], check=True)


if __name__ == '__main__':
    main(sys.argv[1])
