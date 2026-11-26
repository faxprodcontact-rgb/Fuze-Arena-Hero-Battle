# Les petits signes de l'interface (style moderne) : étoiles des héros, coche, croix, flèches, chevrons, plus / égal,
# lecture / arrêt, pastilles, et les petits boutons ronds (fermer, retour, suivant, acheter).
#   python3 refonte-graphique/ui-moderne/pictos/signes.py
# → src/game/ui/signs-art.ts (SIGN_SVG : nom → texte SVG). px.ts les pose dans le CSS (variables --px-<signe>, mêmes
#   noms qu'avant) ; <Sign> de kit.tsx et les étoiles des héros les affichent. Chaque signe garde les proportions de
#   l'ancien signe en pixels (--sw × --sh de style.css) : la boîte du SVG vaut ces proportions × 20.
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, HERE)

from composants import arrow_shape, plus_shape  # noqa: E402
from lib import Icon, band, circle, col, dark, ellipse, lite, rect, rpoly, star  # noqa: E402
from menus import check_shape  # noqa: E402

OUT = os.path.join(ROOT, 'src', 'game', 'ui', 'signs-art.ts')
SIGNS = {}
OW = 8          # demi-épaisseur du contour des signes (≈ 1 px à leur taille d'affichage)


def sign(name, sw, sh):
    def deco(fn):
        SIGNS[name] = (fn, sw * 20, sh * 20)
        return fn
    return deco


def chevron(w, h, pad, right=True, thick=None):
    """Un chevron (pointe à droite ou à gauche) en trait épais aux bouts ronds."""
    t = thick or min(w, h) * 0.32
    x0, x1 = pad + t / 2, w - pad - t / 2
    pts = [(x0, pad + t / 2), (x1, h / 2), (x0, h - pad - t / 2)]
    if not right:
        pts = [(w - x, y) for x, y in pts]
    return band(pts, t)


def big_star(ic, c):
    o = ic.obj(w=OW)
    o.part(star(70, 76, 60, rr=6), c, gloss=False)
    o.detail(ellipse(84, 50, 9, 5, -30), fill='#ffffff', opacity=0.85, blur=1)


@sign('star', 7, 7)
def _(ic):
    big_star(ic, 'gold')


@sign('star-red', 7, 7)
def _(ic):
    big_star(ic, 'red')


@sign('check', 10, 8)
def _(ic):
    o = ic.obj(w=OW)
    o.part(check_shape(98, 86, 68), 'green', grad='v', gloss=False)


@sign('cross', 8, 8)
def _(ic):
    o = ic.obj(w=OW)
    o.part(plus_shape(80, 80, 62, 0.3).rot(45, 80, 80), 'red', grad='v', gloss=False)


@sign('up', 7, 7)
def _(ic):
    o = ic.obj(w=OW)
    o.part(arrow_shape(70, 70, 56), 'green', grad='v', gloss=False)


@sign('chev', 7, 11)
def _(ic):
    o = ic.obj(w=OW)
    o.part(chevron(140, 220, 14, True, 40), 'gold', gloss=False)


@sign('chev-s', 6, 7)
def _(ic):
    o = ic.obj(w=OW)
    o.part(chevron(120, 140, 14, True, 30), '#8a7cff', gloss=False)


@sign('back-s', 6, 7)
def _(ic):
    o = ic.obj(w=OW)
    o.part(chevron(120, 140, 14, False, 30), 'gold', gloss=False)


@sign('play', 6, 9)
def _(ic):
    o = ic.obj(w=OW)
    o.part(rpoly([(14, 14), (106, 90), (14, 166)], 14), 'white', gloss=False)


@sign('stop', 7, 7)
def _(ic):
    o = ic.obj(w=OW)
    o.part(rect(16, 16, 108, 108, 18), 'white', gloss=False)


@sign('op-plus', 8, 8)
def _(ic):
    o = ic.obj(w=OW)
    o.part(plus_shape(80, 80, 64, 0.3), 'gold', grad='v', gloss=False)


@sign('op-eq', 8, 9)
def _(ic):
    o = ic.obj(w=OW)
    o.part(rect(14, 40, 132, 36, 14), 'gold', grad='v', gloss=False)
    o.part(rect(14, 104, 132, 36, 14), 'gold', grad='v', gloss=False)


@sign('op-arrow', 10, 9)
def _(ic):
    o = ic.obj(w=OW)
    o.part(arrow_shape(100, 90, 74).rot(90, 100, 90), 'gold', grad='h', gloss=False)


# ---------- Pastilles et petits boutons ----------

@sign('badge', 7, 7)
def _(ic):
    o = ic.obj(w=OW * 0.8)
    o.part(circle(70, 70, 60), '#ffffff', gloss=False, bevel=0.4)
    o.part(circle(70, 70, 46), 'red', gloss=False, cast=False)


@sign('badge-gold', 7, 7)
def _(ic):
    o = ic.obj(w=OW * 0.8)
    o.part(circle(70, 70, 60), '#ffffff', gloss=False, bevel=0.4)
    o.part(circle(70, 70, 46), 'gold', gloss=False, cast=False)


def round_btn(ic, w, h, c):
    o = ic.obj(w=OW * 1.3)
    r = min(w, h) / 2 - 22
    o.part(circle(w / 2, h / 2 - 6, r), c, grad='v', gloss=False)
    return o, w / 2, h / 2 - 6, r


@sign('btn-close', 15, 16)
def _(ic):
    o, cx, cy, r = round_btn(ic, 300, 320, 'red')
    o.detail(plus_shape(cx, cy, r * 0.5, 0.3).rot(45, cx, cy), fill='#ffffff')


@sign('btn-back', 15, 16)
def _(ic):
    o, cx, cy, r = round_btn(ic, 300, 320, 'azure')
    o.detail(chevron(r * 0.9, r * 1.1, 0, False, r * 0.26).move(cx - r * 0.5, cy - r * 0.55), fill='#ffffff')


@sign('btn-next', 15, 16)
def _(ic):
    o, cx, cy, r = round_btn(ic, 300, 320, 'violet')
    o.detail(chevron(r * 0.9, r * 1.1, 0, True, r * 0.26).move(cx - r * 0.4, cy - r * 0.55), fill='#ffffff')


@sign('btn-plus', 9, 10)
def _(ic):
    o = ic.obj(w=OW)
    o.part(rect(12, 12, 156, 160, 44), 'green', grad='v', gloss=False)
    o.detail(plus_shape(90, 92, 46, 0.3), fill='#ffffff')


def vchevron(w, h, pad, down=True, t=40):
    """Un chevron vers le bas (déplier) ou vers le haut (replier)."""
    y0, y1 = pad + t / 2, h - pad - t / 2
    pts = [(pad + t / 2, y0), (w / 2, y1), (w - pad - t / 2, y0)]
    if not down:
        pts = [(x, h - y) for x, y in pts]
    return band(pts, t)


@sign('chevron-down', 11, 7)
def _(ic):
    o = ic.obj(w=OW)
    o.part(vchevron(220, 140, 14, True, 38), 'gold', gloss=False)


@sign('chevron-up', 11, 7)
def _(ic):
    o = ic.obj(w=OW)
    o.part(vchevron(220, 140, 14, False, 38), 'gold', gloss=False)


def build():
    out = {}
    for name, (fn, w, h) in SIGNS.items():
        ic = Icon(w=w, h=h)
        fn(ic)
        out[name] = ic.svg()
    return out


def main():
    svgs = build()
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('// Fabriqué par refonte-graphique/ui-moderne/pictos/signes.py — ne pas modifier à la main.\n'
                '// Les petits signes de l\'interface (style moderne, lisses) : nom → texte SVG. px.ts les pose dans le CSS\n'
                '// (variables --px-<nom>) ; leurs proportions sont celles des anciens signes en pixels (style.css : --sw × --sh).\n'
                'export const SIGN_SVG: Readonly<Record<string, string>> = '
                + json.dumps(svgs, ensure_ascii=False, indent=0, separators=(',', ':')) + ';\n')
    print(len(svgs), 'signes →', os.path.relpath(OUT, ROOT), '(%d Ko)' % (os.path.getsize(OUT) // 1024))


if __name__ == '__main__':
    main()
