#!/usr/bin/env python3
"""Cut badger.webp and snake.webp out of Badge.Team's konsool_mascots.svg.

Usage: tools/sprites.py path/to/konsool_mascots.svg
(from https://github.com/badgeteam/website, content/en/docs/Badges/Konsool/)

The badger and the snake share one purple outline in the drawing, so each gets the part of
it around its own fills. The badger's foot covers the snake's hoverboard, so the board is
drawn anew here, in the same place and the drawing's colours: a hoverboard as in the films,
square tail, rounded nose, rim, grip dots, stripes, a green zigzag and a foot pad (no
lettering), drawn flat and mapped into place.
Needs inkscape, ImageMagick and Pillow.
"""
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter

# Children of the drawing's main group: 0 confetti, 1 the shared outline, 2 the hoverboard,
# 3 a speck under it, 4 the snake, 5-17 badger, keyboard phone and CRT.
LAYERS = {'outline': [1], 'board': [2], 'snakefill': [4], 'badgerfill': list(range(5, 18))}

# The new board on the 2000 px page: tail top, where the nose arc starts on top, tail bottom.
BOARD_AT = ((1152, 846), (1650, 920), (1155, 1025))


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


S = 4                                   # the flat board is drawn at 4x, then mapped into place
L, R = 500, 100                         # deck length to the nose arc, nose radius (width 2R)
PINK, HOT, DARK = (0xE9, 0x40, 0x76), (0xE7, 0x24, 0x7F), (0xD1, 0x28, 0x6D)
WHITE, YELLOW, GREEN, MINT = (255, 255, 255), (0xFD, 0xC5, 0x49), (0x80, 0xBA, 0x27), (0x7A, 0xC2, 0x9B)
PURPLE = (0x66, 0x24, 0x83)

def flat():
    """The board seen from above, tail left, nose right, in local units (x 0..600, y 0..200)."""
    w, h = (L + R) * S, 2 * R * S
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    shape = Image.new('L', (w, h), 0)
    d = ImageDraw.Draw(shape)
    d.rounded_rectangle([0, 0, L * S, h - 1], radius=14 * S, fill=255)
    d.pieslice([(L - R) * S, 0, (L + R) * S - 1, h - 1], -90, 90, fill=255)
    d.rectangle([(L - R) * S, 0, L * S, h - 1], fill=255)
    deck = Image.new('RGBA', (w, h), HOT + (255,))
    inner = shape.filter(ImageFilter.MinFilter(2 * 9 * S + 1))      # a 9-unit hot-pink rim
    body = Image.new('RGBA', (w, h), PINK + (255,))
    dd = ImageDraw.Draw(body)
    for y in range(4, 200, 9):                                       # the grip dots
        for x in range(4 + (y // 9 % 2) * 4, 600, 9):
            dd.ellipse([(x - 1.6) * S, (y - 1.6) * S, (x + 1.6) * S, (y + 1.6) * S], fill=DARK)
    band = lambda u0, u1, slope, colour: dd.polygon([(u0 * S, 0), (u1 * S, 0), ((u1 + slope * 200) * S, h), ((u0 + slope * 200) * S, h)], fill=colour)
    line = lambda pts, colour, width: dd.line([(x * S, y * S) for x, y in pts], fill=colour, width=width * S, joint='curve')
    # Nose: two hot-pink bands edged in white, slanting back.
    for u in (330, 375):
        band(u - 4, u + 30, 0.35, WHITE)
        band(u, u + 26, 0.35, HOT)
    band(420, 428, 0.35, WHITE)
    # White chevrons and a yellow band across the middle, the other way.
    band(200, 245, -0.25, YELLOW)
    band(196, 200, -0.25, WHITE)
    band(245, 249, -0.25, WHITE)
    # The green zigzag, nose to tail.
    line([(15, 150), (70, 60), (135, 145), (210, 55), (290, 150), (360, 70), (440, 120), (500, 60)], GREEN, 7)
    # Yellow corners at the tail, and where the nose starts to curve.
    dd.polygon([(0, 0), (45 * S, 0), (0, 40 * S)], fill=YELLOW)
    dd.polygon([(0, h), (45 * S, h), (0, h - 40 * S)], fill=YELLOW)
    dd.polygon([(440 * S, 0), (500 * S, 0), (500 * S, 45 * S)], fill=YELLOW)
    dd.polygon([(440 * S, h), (500 * S, h), (500 * S, h - 45 * S)], fill=YELLOW)
    # The foot pad near the tail, with its strap.
    dd.ellipse([(95 - 52) * S, (100 - 52) * S, (95 + 52) * S, (100 + 52) * S], fill=PURPLE)
    dd.ellipse([(95 - 48) * S, (100 - 48) * S, (95 + 48) * S, (100 + 48) * S], fill=MINT)
    dd.polygon([(70 * S, 40 * S), (100 * S, 30 * S), (122 * S, 160 * S), (92 * S, 170 * S)], fill=HOT)
    deck.paste(body, (0, 0), inner)
    img.paste(deck, (0, 0), shape)
    return img

def place(page_size, A, B, D, thickness=14):
    """Map the flat board onto the page: A tail-top, B where the nose arc starts on top,
    D tail-bottom (page pixels); then give it a side and a purple outline."""
    board = flat()
    # page = A + x/L*(B-A) + y/(2R)*(D-A), x, y in local units; PIL wants page -> source.
    ax, ay = (B[0] - A[0]) / (L * S), (B[1] - A[1]) / (L * S)
    bx, by = (D[0] - A[0]) / (2 * R * S), (D[1] - A[1]) / (2 * R * S)
    det = ax * by - ay * bx
    ia, ib, ic, id_ = by / det, -bx / det, -ay / det, ax / det
    coeffs = (ia, ib, -(ia * A[0] + ib * A[1]), ic, id_, -(ic * A[0] + id_ * A[1]))
    top = board.transform(page_size, Image.AFFINE, coeffs, resample=Image.BICUBIC)
    alpha = top.getchannel('A')
    out = Image.new('RGBA', page_size, (0, 0, 0, 0))
    side = Image.new('RGBA', page_size, DARK + (255,))
    side_alpha = Image.new('L', page_size, 0)
    for dy in range(1, thickness + 1):                               # the board's edge, below the deck
        side_alpha.paste(alpha, (0, dy), alpha)
    side.putalpha(side_alpha)
    full = ImageChops.lighter(alpha, side_alpha)
    rim = Image.new('RGBA', page_size, PURPLE + (255,))
    rim.putalpha(full.point(lambda v: 255 if v > 40 else 0).filter(ImageFilter.MaxFilter(21)))
    out.alpha_composite(rim)
    out.alpha_composite(side)
    # a purple line where the deck meets the side
    edge = Image.new('RGBA', page_size, PURPLE + (255,))
    edge.putalpha(alpha.point(lambda v: 255 if v > 40 else 0).filter(ImageFilter.MaxFilter(7)))
    out.alpha_composite(edge)
    out.alpha_composite(top)
    return out


def snake(tmp):
    """The new board, the snake's share of the outline, the snake."""
    run = lambda *a: subprocess.run(['magick', *map(str, a)], check=True)
    run(tmp / 'snakefill.png', '-alpha', 'extract', '-threshold', '10%', '-morphology', 'Close', 'Disk:30',
        '-morphology', 'Dilate', 'Disk:16', tmp / 'snakemask.png')
    # Where the old board showed (closed over its stripes), but not right next to the snake:
    # the shared outline there is the old board's.
    run(tmp / 'board.png', '-alpha', 'extract', '-threshold', '10%', '-morphology', 'Close', 'Disk:14', tmp / 'oldboard.png')
    run(tmp / 'snakefill.png', '-alpha', 'extract', '-threshold', '10%', '-morphology', 'Dilate', 'Disk:11', tmp / 'snakenear.png')
    outline = Image.open(tmp / 'outline.png').convert('RGBA')
    old = ImageChops.subtract(Image.open(tmp / 'oldboard.png').convert('L'), Image.open(tmp / 'snakenear.png').convert('L'))
    mine = ImageChops.multiply(outline.getchannel('A'), Image.open(tmp / 'snakemask.png').convert('L'))
    outline.putalpha(ImageChops.subtract(mine, old))
    out = place(outline.size, *BOARD_AT)
    out.alpha_composite(outline)
    out.alpha_composite(Image.open(tmp / 'snakefill.png').convert('RGBA'))
    out.crop(out.getbbox()).save(tmp / 'snake.png')


def main(svg):
    root = Path(__file__).resolve().parent.parent
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        for name, keep in LAYERS.items():
            render(svg, keep, tmp / f'{name}.png')
        cut(tmp, 'badger')
        snake(tmp)
        webp = ['-quality', '88', '-define', 'webp:alpha-quality=100']
        subprocess.run(['magick', tmp / 'badger.png', '-resize', '560x', *webp, root / 'badger.webp'], check=True)
        subprocess.run(['magick', tmp / 'snake.png', '-resize', '520x', *webp, root / 'snake.webp'], check=True)


if __name__ == '__main__':
    main(sys.argv[1])
