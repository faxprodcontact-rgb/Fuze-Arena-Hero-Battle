# Le HÉROS JOKER (demande du propriétaire, 29/11/2026) : un petit golem de cristal, trapu, de pierre claire, avec un gros
# cristal au cœur et deux yeux-cristaux de la couleur de son élément (feu orange, eau bleue, vent vert, terre ocre), des
# éclats du même cristal sur les épaules. Il ne combat pas : il se gagne au 20e niveau d'une zone d'Événement et sert de
# héros ★5 à sacrifier dans les fusions (src/core/data/heroes.ts, JOKERS). Un seul dessin, 4 couleurs.
#
#   python3 refonte-graphique/ui-moderne/monstres/golem-joker/golem-joker.py   # → public/art/vecto/joker-<élément>.webp
#                                                                                #   (+ -160) et art/vecto/v/joker-<élément>.webp
#
# Une seule lumière, en haut à droite ; un seul contour (atelier.py) ; pas de rayures ; il regarde vers la droite.
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
HEROS = os.path.abspath(os.path.join(HERE, '..', '..', 'heros'))
sys.path.insert(0, HEROS)
from atelier import Figure, Mat, sm, ellipse  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))

STONE = Mat('#fbf6ff', '#d9d0e6', '#a99fbd', '#766c8e', '#4c4466', glint='#ffffff')
# le cristal de chaque élément : reflet, lumière, base, ombre, creux, et la couleur de sa lueur
CRYSTAL = {
    'feu': (Mat('#fff0d0', '#ffa050', '#ff5a24', '#c42e18', '#7a1a12'), '#ff6a2a'),
    'eau': (Mat('#eafaff', '#8fdcff', '#3fa6f0', '#2a68c4', '#1c3a86'), '#3fb4ff'),
    'vent': (Mat('#f0ffe8', '#a6f08a', '#5ccc5a', '#2e9a4a', '#1c5e3a'), '#6ee06a'),
    'terre': (Mat('#fffbe0', '#f4e08a', '#d8b43c', '#9a8a2a', '#5e5420'), '#e8d050'),
}
FRAME = (0.0, 0.0, 84.0, 92.0)
GRD = 90.0
FEET = (42.0, 90.0)


def gem(cx, cy, w, h):
    """Un cristal à facettes (losange allongé, pointes vives)."""
    return sm([(cx, cy - h / 2), (cx + w / 2, cy - h * 0.12), (cx + w * 0.32, cy + h / 2), (cx - w * 0.32, cy + h / 2),
               (cx - w / 2, cy - h * 0.12)], sharp=(0, 1, 2, 3, 4), t=0.6)


def facets(cx, cy, w, h, m):
    """Les facettes d'un cristal : la face éclairée (haut-droit), la face dans l'ombre (bas-gauche), un éclat."""
    return [
        (sm([(cx, cy - h / 2), (cx + w / 2, cy - h * 0.12), (cx + w * 0.1, cy + h * 0.05)], sharp=(0, 1, 2), t=0.6), m.hi, 0.85),
        (sm([(cx - w / 2, cy - h * 0.12), (cx - w * 0.32, cy + h / 2), (cx - w * 0.05, cy + h / 2), (cx + w * 0.1, cy + h * 0.05)],
            sharp=(0, 1, 2, 3), t=0.6), m.shadow, 0.7),
        (ellipse(cx + w * 0.14, cy - h * 0.22, w * 0.09, h * 0.07), '#ffffff', 0.95),
    ]


def build(element, ow=1.0):
    cm, glow = CRYSTAL[element]
    fig = Figure(*FRAME, ow=ow)
    # la lueur du cristal du cœur, derrière lui (un dégradé radial, aucun flou)
    fig.glow(44, 56, 30, 26, glow, 0.28)

    # ---- le bras lointain (à droite, derrière le corps) ----
    far_arm = sm([(60, 44), (70, 47), (75, 58), (74, 68), (68, 72), (63, 66), (64, 56), (58, 52)], t=0.9)
    fig.part('far_arm', far_arm, STONE, cel=1.6, rim=0.5, cast=0.8,
             grad=(76, 44, 58, 72, [(0, STONE.base), (0.6, STONE.shadow), (1, STONE.deep)]))
    # ---- les jambes courtes, en piliers ----
    for name, x in (('leg_far', 53.0), ('leg_near', 31.0)):
        leg = sm([(x - 8, 70), (x + 8, 70), (x + 9, 84), (x + 10, GRD), (x - 10, GRD), (x - 9, 84)], sharp=(3, 4), t=0.85)
        fig.part(name, leg, STONE, cel=1.8, rim=0.6, cast=1.0,
                 details=[(sm([(x - 10, GRD - 3), (x + 10, GRD - 3), (x + 10, GRD), (x - 10, GRD)], sharp=(0, 1, 2, 3)), STONE.shadow, 0.55)])
    # ---- le corps : un gros bloc arrondi ----
    body = sm([(22, 44), (34, 34), (52, 32), (64, 38), (69, 50), (68, 66), (60, 76), (44, 79), (28, 76), (19, 66), (18, 54)], t=1.0)
    cx, cy = 44.0, 57.0
    heart = gem(cx, cy, 17, 22)
    bd = [
        # le cœur rayonne sur la pierre autour de lui (un dégradé radial, aucun flou)
        (ellipse(cx, cy, 19, 20), ('rad', cx, cy, 19, 20, [(0, cm.light, 0.65), (0.6, cm.base, 0.18), (1, cm.base, 0)]), 1),
        # le creux où le cristal est serti (une ombre douce autour)
        (heart.scale(1.28, 1.2, cx, cy + 1), STONE.deep, 0.55),
        (heart, ('rad', cx + 2, cy - 4, 14, 16, [(0, cm.hi), (0.3, cm.light), (0.75, cm.base), (1, cm.shadow)]), 1),
        *facets(cx, cy, 17, 22, cm),
        # un grand pan éclairé en haut à droite, un pan dans l'ombre en bas à gauche (la pierre taillée)
        (sm([(52, 33), (64, 38), (68.6, 49), (61, 45), (54, 40)], t=0.8), STONE.hi, 0.6),
        (sm([(19, 64), (22, 71), (30, 77), (36, 78.6), (29, 72), (24, 64)], t=0.8), STONE.deep, 0.35),
        # deux fêlures douces dans la pierre (courbes, jamais des rayures)
        (sm([(25, 50), (28, 47), (29.4, 48.2), (26.4, 51.4)], t=0.8), STONE.shadow, 0.6),
        (sm([(56, 70), (60, 67), (61, 68.4), (57.2, 71.6)], t=0.8), STONE.shadow, 0.5),
    ]
    fig.part('body', body, STONE, cel=2.4, rim=0.9, cast=1.6, details=bd,
             grad=(70, 32, 22, 78, [(0, STONE.light), (0.5, STONE.base), (1, STONE.shadow)]))
    # ---- la tête : un bloc plus petit, posé sans cou, tourné vers la droite ----
    head = sm([(32, 22), (38, 13), (50, 10), (60, 14), (64, 22), (62, 31), (54, 36), (42, 36), (34, 32)], t=1.0)
    hd = []
    for (ex, ey, ew, eh) in ((44.0, 24.0, 6.4, 7.0), (56.4, 23.0, 5.6, 6.4)):
        e = ellipse(ex, ey, ew / 2, eh / 2)
        hd += [(ellipse(ex, ey, ew * 1.3, eh * 1.2), ('rad', ex, ey, ew * 1.3, eh * 1.2, [(0, cm.light, 0.7), (1, cm.light, 0)]), 1),
               (e.scale(1.35, 1.3, ex, ey), STONE.deep, 0.8),
               (e, ('rad', ex + 0.5, ey - 0.8, ew * 0.7, eh * 0.7, [(0, '#ffffff'), (0.35, cm.hi), (0.8, cm.light), (1, cm.base)]), 1),
               (ellipse(ex + 0.7, ey - 1.0, ew * 0.16, eh * 0.13), '#ffffff', 1)]
    # le front : une avancée de pierre (le dessus éclairé)
    hd += [(sm([(35, 18), (42, 14.5), (52, 13.5), (60, 16), (58, 17.8), (50, 16.4), (42, 17.4), (36, 20)], t=0.9), STONE.hi, 0.7)]
    fig.part('head', head, STONE, cel=1.8, rim=0.8, cast=1.4, details=hd,
             grad=(64, 10, 34, 36, [(0, STONE.hi), (0.45, STONE.light), (1, STONE.base)]))
    # ---- les éclats de cristal : la couronne sur la tête, les épaules (ils sortent de la pierre) ----
    for name, (gx, gy, gw, gh) in (('crown_far', (55, 8, 6, 11)), ('crown_mid', (47.5, 5.5, 7.5, 14)), ('crown_near', (40, 9.5, 5.5, 9)),
                                   ('shard_far', (64, 34, 8, 15)), ('shard_near', (26, 35, 9, 17))):
        sh = gem(gx, gy, gw, gh)
        fig.part(name, sh, cm, cel=0.8, rim=0.4, cast=0.8, details=facets(gx, gy, gw, gh, cm),
                 grad=(gx + gw / 2, gy - gh / 2, gx - gw / 2, gy + gh / 2, [(0, cm.hi), (0.4, cm.light), (1, cm.shadow)]))
    # ---- le bras proche (à gauche, devant), le poing posé près du sol ----
    near_arm = sm([(20, 44), (28, 46), (30, 56), (27, 68), (26, 78), (16, 80), (10, 74), (13, 62), (14, 52)], t=0.9)
    fig.part('near_arm', near_arm, STONE, cel=2.0, rim=0.8, cast=1.4,
             details=[(sm([(10, 74), (16, 80), (26, 78), (25, 81), (15, 83), (9, 77)], t=0.9), STONE.shadow, 0.5)],
             grad=(30, 44, 10, 80, [(0, STONE.light), (0.5, STONE.base), (1, STONE.shadow)]))
    # deux petits cristaux sur le poing
    for name, (gx, gy, gw, gh) in (('knuckle_a', (22.5, 69, 5, 8)), ('knuckle_b', (17, 72.5, 4.4, 7))):
        sh = gem(gx, gy, gw, gh)
        fig.part(name, sh, cm, cel=0.5, rim=0.3, cast=0.6, details=facets(gx, gy, gw, gh, cm),
                 grad=(gx + gw / 2, gy - gh / 2, gx - gw / 2, gy + gh / 2, [(0, cm.hi), (0.4, cm.light), (1, cm.shadow)]))
    return fig


ELEMENT_ID = {'feu': 'fire', 'eau': 'water', 'vent': 'wind', 'terre': 'earth'}


def main():
    from PIL import Image
    rendu = os.path.join(HEROS, 'rendu.cjs')
    pub = os.path.join(ROOT, 'public', 'art', 'vecto')
    for el in CRYSTAL:
        gid = 'joker-' + ELEMENT_ID[el]
        for suffix, ow, h, out in (('', 0.95, 512, gid), ('-petit', 1.35, 160, gid + '-160'), ('-tete', 1.2, 160, None)):
            fig = build(el, ow=ow)
            if out is None:
                # la tête (cartes et visages des menus, art/vecto/v/) : le haut du golem, carré
                fig.x0, fig.y0, fig.w, fig.h = 14.0, 2.0, 58.0, 58.0
            svg = fig.svg()
            path = os.path.join(HERE, 'golem-joker-%s%s.svg' % (el, suffix))
            open(path, 'w').write(svg)
            png = path[:-4] + '.png'
            subprocess.run(['node', rendu, path, png, str(h)], check=True)
            dest = os.path.join(pub, 'v', gid + '.webp') if out is None else os.path.join(pub, out + '.webp')
            Image.open(png).save(dest, 'WEBP', quality=90, method=6)
            print('écrit', os.path.relpath(dest, ROOT))
    x0, y0, w, h = FRAME
    print('mesures pour src/game/vecto.ts : [largeur, hauteur, x et y des pieds] =', [w, h, FEET[0] - x0, FEET[1] - y0])


if __name__ == '__main__':
    main()
