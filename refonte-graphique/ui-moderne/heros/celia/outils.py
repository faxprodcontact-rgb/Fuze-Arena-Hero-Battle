# Outils en plus de l'atelier commun (atelier.py, qu'on ne touche pas), pour Célia :
# - poly / from_poly / inter : passer d'une forme (Shape) à un polygone (shapely) et retour, pour peindre une bande
#   (obi, ourlet) exactement DANS la forme qu'elle entoure (liste de contrôle, point 3) ;
# - crpath, taper : repris d'Eldra (../eldra/outils.py) : une ligne souple, un ruban effilé (mèche, pan d'obi) ;
# - crystal : un cristal de glace (bipyramide taillée) en plusieurs facettes, à n'importe quel angle.
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
from atelier import sm, sides, resample  # noqa: E402,F401
from lib import Shape  # noqa: E402
import importlib.util  # noqa: E402
_sp = importlib.util.spec_from_file_location('eldra_outils', os.path.join(HERE, '..', 'eldra', 'outils.py'))
_eo = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(_eo)
crpath, taper, bent = _eo.crpath, _eo.taper, _eo.bent

from shapely.geometry import Polygon  # noqa: E402


def poly(shape, n=6):
    """Les points d'une forme (chaque segment de Bézier découpé en n)."""
    s, segs = shape.subs[0]
    out = [s]
    p = s
    for c1, c2, q in segs:
        for k in range(1, n + 1):
            t = k / n
            a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3
            out.append((a * p[0] + b * c1[0] + c * c2[0] + d * q[0], a * p[1] + b * c1[1] + c * c2[1] + d * q[1]))
        p = q
    return out


def from_poly(pts):
    """Un polygone (liste de points) → une forme à côtés droits (assez de points pour paraître lisse)."""
    pts = list(pts)
    segs = []
    for i in range(1, len(pts) + 1):
        a, b = pts[i - 1], pts[i % len(pts)]
        segs.append(((a[0] + (b[0] - a[0]) / 3, a[1] + (b[1] - a[1]) / 3), (a[0] + 2 * (b[0] - a[0]) / 3, a[1] + 2 * (b[1] - a[1]) / 3), b))
    return Shape([(pts[0], segs)])


def inter(a, b):
    """La partie de la forme a qui est dans la forme b (le plus grand morceau)."""
    g = Polygon(poly(a)).buffer(0).intersection(Polygon(poly(b)).buffer(0))
    if g.is_empty:
        return None
    if g.geom_type != 'Polygon':
        g = max(g.geoms, key=lambda x: x.area)
    return from_poly(list(g.exterior.coords)[:-1])


def crystal_shapes(c, L, W, ang, tip=0.3, tail=0.36):
    """Un cristal (bipyramide hexagonale vue de biais) de centre c, longueur L, largeur W, angle ang (degrés depuis
    la verticale, + = penché vers la droite). Rend (silhouette, facette gauche ombrée, facette droite claire, arête,
    facette du bas)."""
    a = math.radians(ang)
    u = (math.sin(a), -math.cos(a))           # vers la pointe du haut
    v = (math.cos(a), math.sin(a))            # vers la droite

    def P(s, t):
        return (c[0] + u[0] * s + v[0] * t, c[1] + u[1] * s + v[1] * t)
    top = P(L / 2, 0)
    bot = P(-L / 2, 0)
    hs = L / 2 - L * tip                       # le haut du fût
    ls = -L / 2 + L * tail                     # le bas du fût
    w = W / 2
    sil = sm([top, P(hs, w), P(ls, w), bot, P(ls, -w), P(hs, -w)], sharp=(0, 1, 2, 3, 4, 5), t=0.3)
    left = sm([top, P(hs, -w), P(ls, -w), bot, P(ls, -w * 0.2), P(hs, -w * 0.15)], sharp=(0, 1, 2, 3, 4, 5), t=0.3)
    right = sm([top, P(hs, w * 0.15), P(ls, w * 0.2), bot, P(ls, w), P(hs, w)], sharp=(0, 1, 2, 3, 4, 5), t=0.3)
    ridge = sm([top, P(hs, w * 0.32), P(ls, w * 0.36), bot, P(ls, w * 0.12), P(hs, w * 0.08)], sharp=(0, 1, 2, 3, 4, 5), t=0.3)
    low = sm([P(ls, -w), P(ls, w), bot], sharp=(0, 1, 2), t=0.3)
    return sil, left, right, ridge, low, top, bot
