# L'ÉCRAN DE CHARGEMENT en style moderne (vectoriel lisse), demande du propriétaire du 27/11/2026 : « Tu peux refaire
# en style moderne l'écran de chargement du début ? Fais-le le plus précis possible. »
#
# Même scène que l'écran pixel du 25/11 (refonte-graphique/pixel/ui/chargement.py, supprimé) : le ciel du soir, le
# soleil en haut à droite (la seule lumière), des bancs de nuages hauts aux bords dorés, des oiseaux au loin, des
# montagnes pâles dans la brume, le COLISÉE sur son piton qui sort d'une MER DE NUAGES (trois rangs à trois vitesses),
# le logo au milieu, la jauge en bas. Le style est celui des fonds de combat vectoriels (fonds/orin, fonds/kael) :
# grandes formes simples, dégradés doux, liseré de lumière en haut à droite, bande d'ombre en bas à gauche, aucun flou
# SVG, un seul contour (le colisée et son piton), pas de rayures.
#
# La scène fait 540 × 1170 unités (la forme d'un grand téléphone) ; index.html l'agrandit pour couvrir l'écran (une
# colonne de 480 px au plus) et coupe ce qui dépasse (un peu de ciel et de nuages sur les petits téléphones).
# Ce qui bouge (CSS seulement, aucun script, rien à redessiner : des images qui glissent) : les nuages hauts, les trois
# rangs de la mer de nuages, la lueur du soleil, trois oiseaux, la lumière qui passe sur la jauge.
#
#   python3 refonte-graphique/ui-moderne/chargement/chargement.py
#     → public/art/chargement/fond.webp      ciel, soleil, montagnes, colisée et piton (fixe)
#       public/art/chargement/ciel.webp      les nuages hauts (une tuile qui se répète, glisse lentement)
#       public/art/chargement/mer-1|2|3.webp les trois rangs de la mer de nuages (tuiles, du fond vers l'avant)
#       public/art/chargement/chargement.webp l'image fixe complète (fond de l'écran du nom au premier lancement)
#       index.html                            style, dessin et logo entre les repères « chargement »
#       refonte-graphique/pixel/sortie/ui/chargement/ (scene.png, aperçu)
# Le logo reste public/art/ui/logo.svg (depuis le 29/11 : refonte-graphique/ui-moderne/logo/logo.py, style moderne), posé tel quel dans la page.
import json
import math
import os
import re
import subprocess
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', 'pictos'))
from lib import blob, ellipse  # noqa: E402

RENDU = os.path.join(ROOT, 'refonte-graphique', 'ui-moderne', 'heros', 'rendu-lot.cjs')
OUT = os.path.join(ROOT, 'public', 'art', 'chargement')
SORTIE = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'chargement')
TMP = os.path.join(os.environ.get('BROUILLON', '/tmp/fonds-brouillon'), 'chargement')

W, H = 540, 1170                # la scène (unités)
K = 1.5                         # pixels d'image par unité (810 × 1755 : net sur un iPhone, léger à télécharger)
ANCRE = 0.62                    # écran moins haut que la scène : on coupe 62 % de ce qui dépasse en haut, 38 % en bas
LOGO = (270, 556, 300)          # le logo : centre x, y et largeur (unités de la scène)

# Les bandes qui glissent : (nom, y du haut, hauteur, durée d'un tour en secondes) ; tuiles de 540 de large
BANDES = [('ciel', 96, 470, 240), ('mer-1', 896, 274, 150), ('mer-2', 970, 200, 95), ('mer-3', 1044, 126, 60)]


# ------------------------------------------------------------------------------------------------ le document SVG
def fm(v):
    return ('%.2f' % v).rstrip('0').rstrip('.')


class Doc:
    """Un dessin SVG : collecte les dégradés et masques (defs) ; chaque fonction de dessin rend du texte."""

    def __init__(self):
        self.defs = []
        self.n = 0

    def uid(self, p):
        self.n += 1
        return '%s%d' % (p, self.n)

    @staticmethod
    def _stops(stops):
        return ''.join('<stop offset="%g" stop-color="%s"%s/>' % (
            s[0], s[1], (' stop-opacity="%g"' % s[2]) if len(s) > 2 else '') for s in stops)

    def lin(self, x1, y1, x2, y2, stops):
        i = self.uid('l')
        self.defs.append('<linearGradient id="%s" gradientUnits="userSpaceOnUse" x1="%s" y1="%s" x2="%s" y2="%s">%s'
                         '</linearGradient>' % (i, fm(x1), fm(y1), fm(x2), fm(y2), self._stops(stops)))
        return 'url(#%s)' % i

    def rad(self, cx, cy, r, stops, ry=None):
        i = self.uid('r')
        tr = ''
        if ry is not None and ry != r:
            tr = ' gradientTransform="translate(%s %s) scale(1 %s) translate(%s %s)"' % (
                fm(cx), fm(cy), fm(ry / r), fm(-cx), fm(-cy))
        self.defs.append('<radialGradient id="%s" gradientUnits="userSpaceOnUse" cx="%s" cy="%s" r="%s"%s>%s'
                         '</radialGradient>' % (i, fm(cx), fm(cy), fm(r), tr, self._stops(stops)))
        return 'url(#%s)' % i

    def minus(self, d, dx, dy):
        """Un masque : la forme moins elle-même décalée de (dx, dy) (une bande le long d'un bord)."""
        i = self.uid('m')
        self.defs.append('<mask id="%s" maskUnits="userSpaceOnUse" x="-600" y="-200" width="1800" height="1600">'
                         '<path d="%s" fill="#fff"/><path d="%s" fill="#000" transform="translate(%s %s)"/></mask>'
                         % (i, d, d, fm(dx), fm(dy)))
        return 'url(#%s)' % i

    def clip(self, d):
        i = self.uid('c')
        self.defs.append('<clipPath id="%s"><path d="%s"/></clipPath>' % (i, d))
        return 'url(#%s)' % i

    def svg(self, body, box):
        x, y, w, h = box
        return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="%s %s %s %s"><defs>%s</defs>%s</svg>'
                % (fm(x), fm(y), fm(w), fm(h), ''.join(self.defs), body))


def D(s):
    return s if isinstance(s, str) else s.d()


def path(d, fill, op=1.0, extra=''):
    return '<path d="%s" fill="%s"%s%s/>' % (D(d), fill, '' if op == 1 else ' opacity="%g"' % op, extra)


def bbox(d):
    v = [float(n) for n in re.findall(r'-?\d+(?:\.\d+)?', D(d))]
    xs, ys = v[0::2], v[1::2]
    return min(xs), min(ys), max(xs), max(ys)


def vol(doc, shape, m, grad=None, r=1.6, c=2.4, rim_op=0.9, sh_op=0.85):
    """Un volume (comme les fonds) : dégradé clair en haut à droite, bande d'ombre nette en bas à gauche, liseré de
    lumière en haut à droite."""
    d = D(shape)
    x0, y0, x1, y1 = bbox(d)
    out = []
    g = grad or doc.lin(x1, y0, x0 + (x1 - x0) * 0.25, y1, [(0, m['light']), (0.55, m['base']), (1, m['sh'])])
    out.append(path(d, g))
    if c:
        out.append('<path d="%s" fill="%s" opacity="%g" mask="%s"/>' % (d, m['sh'], sh_op, doc.minus(d, c * 0.8, -c)))
    if r:
        out.append('<path d="%s" fill="%s" opacity="%g" mask="%s"/>' % (d, m['rim'], rim_op,
                                                                       doc.minus(d, -r * 0.75, r)))
    return ''.join(out)


def poly_d(pts, close=True):
    return 'M' + 'L'.join('%s %s' % (fm(x), fm(y)) for x, y in pts) + ('Z' if close else '')


# ------------------------------------------------------------------------------------------------ les couleurs
# Le soir : le haut du ciel est le raisin de l'interface (--c-bg-1), le bas pêche ; les ombres tirent vers le violet,
# les lumières vers l'or chaud (comme les pictos et les personnages). Le décor reste moins contrasté que le logo.
CIEL = [(0, '#150f36'), (0.2, '#221a55'), (0.4, '#3a2f78'), (0.56, '#5c4590'), (0.68, '#87609c'),
        (0.8, '#b4789c'), (0.9, '#d8929a'), (1, '#efb39a')]
SOLEIL = (412, 300)
NUAGE_HAUT = dict(base='#4e4482', light='#62558f', rim='#f0bf92', sh='#3a3268')     # les plus hauts, bords dorés
NUAGE_MI = dict(base='#7a5f9a', light='#8e6ea4', rim='#ffcf9e', sh='#5e4a86')       # plus bas, plus clairs
NUAGE_BAS = dict(base='#a87aa4', light='#bb8aa8', rim='#ffd8b0', sh='#8a6696')      # près de l'horizon
LOIN1 = dict(base='#a988b4', light='#bd98ba', rim='#f2c6b6', sh='#957aaa')          # les pics lointains
LOIN2 = dict(base='#86699e', light='#9a78a6', rim='#e2b0ae', sh='#705a92')
ROC = dict(base='#5b4a74', light='#715d86', rim='#d6a8a2', sh='#3d3158')            # le piton
HERBE = dict(base='#4f7a5e', light='#69946a', rim='#c8d88e', sh='#355a4c')
INK = '#24163a'                 # le contour du colisée et de son piton
PIERRE = ['#6e4e66', '#9c7076', '#c99a86', '#e8bf98', '#f8dcae']   # le grès du colisée, de l'ombre à la lumière
ARC = '#3a2444'                 # le creux des arcades
MER = [  # les trois rangs de la mer de nuages (du fond vers l'avant) : plus de contraste vers l'avant
    dict(base='#b98fb6', light='#d0a6c0', rim='#ffe2c6', sh='#9a7cac', fond='#a885b0'),
    dict(base='#a680b0', light='#c098bc', rim='#ffdabe', sh='#866aa4', fond='#8f72a8'),
    dict(base='#91709f', light='#ae8ab4', rim='#f8ccb6', sh='#6c5690', fond='#76609a'),
]


# ================================================================================================ LE FOND (fixe)
def ciel(doc):
    out = [path('M0 0H%dV%dH0Z' % (W, H), doc.lin(0, 0, 0, 880, CIEL))]
    # la lueur du couchant sur l'horizon, et le halo du soleil (la seule lumière)
    out.append('<ellipse cx="300" cy="880" rx="420" ry="230" fill="%s"/>' % doc.rad(
        300, 880, 420, [(0, '#ffcfa6', 0.55), (0.5, '#e8a2a0', 0.22), (1, '#c08098', 0)], ry=230))
    sx, sy = SOLEIL
    out.append('<circle cx="%d" cy="%d" r="190" fill="%s"/>' % (sx, sy, doc.rad(
        sx, sy, 190, [(0, '#ffdca0', 0.5), (0.3, '#f6b894', 0.2), (1, '#b07aa0', 0)])))
    out.append('<circle cx="%d" cy="%d" r="31" fill="%s"/>' % (sx, sy, doc.rad(
        sx + 8, sy - 8, 40, [(0, '#fffbe8'), (0.45, '#ffeab0'), (0.85, '#ffc77e'), (1, '#ffb26e')])))
    return ''.join(out)


def pics(pts, base_y=980):
    return poly_d(pts + [(pts[-1][0], base_y), (pts[0][0], base_y)])


def facettes(doc, sommets, m, base_y):
    """La face éclairée de chaque pic (à droite du sommet), un ton plus clair : de grandes facettes, pas de traits."""
    out = []
    for (x, y), (x2, y2), (x3, y3) in sommets:
        out.append(path(poly_d([(x, y), (x2, y2), (x3, y3), (x3 - 4, base_y), (x + (x3 - x) * 0.2, base_y)]),
                        doc.lin(x2, y, x, base_y, [(0, m['rim'], 0.55), (0.35, m['light'], 0.5),
                                                   (1, m['light'], 0)])))
    return ''.join(out)


def montagnes(doc):
    out = []
    # le rang lointain, presque dans le ciel
    r1 = [(-10, 760), (30, 700), (62, 672), (96, 690), (130, 668), (168, 712), (210, 744), (330, 752), (372, 712),
          (410, 686), (446, 652), (478, 676), (512, 664), (550, 700)]
    out.append(vol(doc, pics(r1), LOIN1, grad=doc.lin(0, 650, 0, 900, [(0, LOIN1['light']), (1, '#c89ab0')]),
                   r=1.4, c=0, rim_op=0.8))
    out.append(facettes(doc, [((62, 672), (80, 684), (96, 690)), ((446, 652), (462, 664), (478, 676))], LOIN1, 900))
    # la brume qui monte du fond (le lointain se perd dans la lumière)
    out.append(path('M0 700H%dV900H0Z' % W, doc.lin(0, 690, 0, 860, [(0, '#e6aaa8', 0), (1, '#e6aaa8', 0.55)])))
    # le rang plus proche, sur les côtés (il encadre le colisée)
    r2 = [(-10, 790), (24, 740), (58, 718), (92, 744), (124, 770), (160, 800), (200, 830), (340, 830), (380, 800),
          (414, 772), (444, 742), (476, 720), (506, 734), (550, 760)]
    out.append(vol(doc, pics(r2), LOIN2, grad=doc.lin(0, 720, 0, 900, [(0, LOIN2['light']), (1, '#b48aa8')]),
                   r=1.6, c=0, rim_op=0.85))
    out.append(facettes(doc, [((58, 718), (76, 730), (92, 744)), ((476, 720), (492, 726), (506, 734))], LOIN2, 900))
    out.append(path('M0 760H%dV900H0Z' % W, doc.lin(0, 760, 0, 880, [(0, '#e8b0a8', 0), (1, '#eab4a6', 0.7)])))
    # la mer de nuages tout au fond (sous les rangs qui glissent : jamais de trou)
    out.append(path('M0 858H%dV%dH0Z' % (W, H), doc.lin(0, 858, 0, H, [(0, '#d6aab6'), (0.2, MER[0]['fond']),
                                                                        (1, MER[2]['fond'])])))
    return ''.join(out)


# ------------------------------------------------------------------------------------------------ le colisée
CX, RY_TOP, RX, RY, HAUT = 270, 748, 150, 40, 90       # l'ovale du haut du mur, sa hauteur
EP = 13                                                 # l'épaisseur du mur vue d'en haut


def pt(t, y0, rx=RX, ry=RY):
    """Un point de l'ovale (angle t en degrés : 0 = droite, 90 = devant), à la hauteur y0."""
    a = math.radians(t)
    return CX + rx * math.cos(a), y0 + ry * math.sin(a)


def arc_pts(t0, t1, y0, rx=RX, ry=RY, n=40):
    return [pt(t0 + (t1 - t0) * i / n, y0, rx, ry) for i in range(n + 1)]


def bande_d(t0, t1, ya, yb):
    """La bande du mur de face entre les hauteurs ya (haut) et yb (bas), de l'angle t0 à t1."""
    return poly_d(arc_pts(t0, t1, ya) + arc_pts(t1, t0, yb))


def silhouette():
    """Le contour unique du colisée : l'arrière de l'ovale du haut, puis le bas du mur de face."""
    return poly_d(arc_pts(180, 360, RY_TOP) + arc_pts(0, 180, RY_TOP + HAUT))


def colisee(doc):
    out = []
    yb = RY_TOP + HAUT
    # le contour (un seul, autour de tout le colisée) et une ombre douce sur le plateau, à gauche (la lumière vient
    # d'en haut à droite)
    out.append('<path d="%s" fill="%s" stroke="%s" stroke-width="3.4" stroke-linejoin="round"/>' % (
        silhouette(), INK, INK))
    # le mur de face : le grès, de l'ombre (à gauche) à la lumière (à droite)
    mur = doc.lin(CX - RX, 0, CX + RX, 0, [(0, PIERRE[0]), (0.28, PIERRE[1]), (0.62, PIERRE[2]), (0.86, PIERRE[3]),
                                           (1, PIERRE[2])])
    out.append(path(bande_d(0, 180, RY_TOP, yb), mur))
    # le haut du mur (l'attique) un ton plus clair, une corniche sous chaque étage (avec son ombre dessous)
    clair = doc.lin(CX - RX, 0, CX + RX, 0, [(0, PIERRE[1]), (0.3, PIERRE[2]), (0.7, PIERRE[4]), (1, PIERRE[3])])
    out.append(path(bande_d(0, 180, RY_TOP, RY_TOP + 15), clair, 0.75))
    for ya in (RY_TOP + 15, RY_TOP + 50):
        out.append(path(bande_d(0, 180, ya, ya + 4.5), clair))
        out.append(path(bande_d(0, 180, ya + 4.5, ya + 7), PIERRE[0], 0.55))
    # les fenêtres carrées de l'attique, puis les deux étages d'arcades (l'étage du bas plus haut, la grande porte
    # au milieu)
    out.append(ouvertures(doc, 22, RY_TOP + 5, RY_TOP + 12, carre=True))
    out.append(ouvertures(doc, 16, RY_TOP + 22, RY_TOP + 47))
    out.append(ouvertures(doc, 14, RY_TOP + 57, yb - 1, porte=True))
    # le pied du mur : une bande d'ombre (le mur se pose sur le plateau)
    out.append(path(bande_d(0, 180, yb - 5, yb), PIERRE[0], 0.6))
    # la bande d'ombre du côté gauche (le volume) et le liseré de lumière sur le bord droit
    out.append(path(bande_d(120, 180, RY_TOP, yb), doc.lin(CX - RX, 0, CX - RX * 0.4, 0, [
        (0, '#2c1c40', 0.55), (1, '#2c1c40', 0)])))
    out.append(path(bande_d(0, 14, RY_TOP + 2, yb - 2), '#fff0c8', 0.35))
    # le dessus : le rebord du mur (un anneau), les gradins qui descendent vers l'arène de sable
    out.append(dessus(doc))
    out.append(drapeaux(doc, devant=False))
    return ''.join(out)


def ouvertures(doc, n, ya, yb, carre=False, porte=False):
    """n arcades sur le devant (de 0 à 180°) : le creux sombre, la joue gauche éclairée (la lumière vient de droite),
    une ombre douce en haut du creux. Les arcades des côtés, trop étroites, ne sont pas dessinées."""
    out = []
    step = 180 / n
    for k in range(n):
        t0, t1 = k * step + step * 0.24, (k + 1) * step - step * 0.24
        if porte and k == n // 2 - 1:
            continue
        if porte and k == n // 2:
            t0, t1 = 90 - step * 0.62, 90 + step * 0.62
        (xa, _), (xb, _) = pt(t1, 0), pt(t0, 0)
        w = xb - xa
        if w < 3:
            continue
        tm = (t0 + t1) / 2
        dy = RY * math.sin(math.radians(tm))
        top, bot = ya + dy, yb + dy
        if carre:
            d = poly_d([(xa, top), (xb, top), (xb, bot), (xa, bot)])
        else:
            rr = w / 2
            ry = min(rr * 0.95, (bot - top) * 0.45)
            d = 'M%s %sV%sA%s %s 0 0 1 %s %sV%sZ' % (fm(xa), fm(bot), fm(top + ry), fm(rr), fm(ry), fm(xb),
                                                     fm(top + ry), fm(bot))
        out.append(path(d, doc.lin(0, top, 0, bot, [(0, '#2a1834'), (1, ARC)])))
        if not carre and w > 5:
            # la joue gauche du creux, éclairée ; une lueur chaude au fond (le soleil traverse les couloirs)
            jw = w * 0.2
            out.append(path(poly_d([(xa, bot), (xa, top + ry * 0.9), (xa + jw, top + ry * 1.2), (xa + jw, bot)]),
                            PIERRE[1], 0.85))
            out.append(path(poly_d([(xa + jw, bot), (xa + jw, bot - (bot - top) * 0.3), (xb, bot - (bot - top) * 0.22),
                                    (xb, bot)]), '#c87a62', 0.45))
        if porte and k == n // 2:
            # la grande porte : une grille d'or fermée (le combat attend derrière)
            out.append(grille(doc, xa, xb, top, bot))
    return ''.join(out)


def grille(doc, xa, xb, top, bot):
    w = xb - xa
    ry = min(w / 2 * 0.95, (bot - top) * 0.45)
    d = 'M%s %sV%sA%s %s 0 0 1 %s %sV%sZ' % (fm(xa + 2), fm(bot), fm(top + ry + 1), fm(w / 2 - 2), fm(ry - 1),
                                             fm(xb - 2), fm(top + ry + 1), fm(bot))
    out = [path(d, doc.lin(xb, top, xa, bot, [(0, '#5a3a3e'), (1, '#3a2232')]))]
    # deux battants de bois, le milieu marqué par un clou d'or ; un seul anneau d'or chacun
    out.append(path(poly_d([((xa + xb) / 2 - 0.7, top + ry * 0.4), ((xa + xb) / 2 + 0.7, top + ry * 0.4),
                            ((xa + xb) / 2 + 0.7, bot), ((xa + xb) / 2 - 0.7, bot)]), '#24142c'))
    for cx in ((xa + xb) / 2 - w * 0.17, (xa + xb) / 2 + w * 0.17):
        out.append('<circle cx="%s" cy="%s" r="1.6" fill="#ffcf5a"/>' % (fm(cx), fm(bot - (bot - top) * 0.42)))
    out.append(path(poly_d([(xa + 2, bot - 2.2), (xb - 2, bot - 2.2), (xb - 2, bot), (xa + 2, bot)]), '#e0a44a', 0.8))
    return ''.join(out)


def dessus(doc):
    out = []
    y = RY_TOP
    # le rebord (l'anneau du haut du mur), éclairé de face et à droite
    bord = ellipse(CX, y, RX, RY)
    out.append(path(bord, doc.lin(CX + RX, y - RY, CX - RX, y + RY, [(0, PIERRE[4]), (0.5, PIERRE[3]),
                                                                       (1, PIERRE[1])])))
    # l'intérieur : le mur du fond (vu de l'intérieur, à l'ombre à droite, éclairé à gauche) qui descend vers les
    # gradins ; les gradins en deux anneaux doux ; l'arène de sable
    rx1, ry1 = RX - EP, RY - EP * 0.32
    out.append(path(ellipse(CX, y + 1, rx1, ry1), doc.lin(CX - rx1, 0, CX + rx1, 0, [
        (0, '#d6a888'), (0.45, '#b88478'), (1, '#7a586c')])))
    # le mur du fond vu de l'intérieur : une bande plus sombre le long de l'arrière de l'ovale (il tourne le dos au
    # soleil), plus claire à gauche où la lumière l'atteint
    back = poly_d(arc_pts(180, 360, y + 1, rx1, ry1) + arc_pts(360, 180, y + 8, rx1 * 0.97, ry1 * 0.86))
    out.append(path(back, doc.lin(CX - rx1, 0, CX + rx1, 0, [(0, '#c08c7a'), (0.5, '#94687a'), (1, '#5e4468')])))
    rx2, ry2 = rx1 * 0.8, ry1 * 0.74
    out.append(path(ellipse(CX, y + 5, rx2, ry2), doc.lin(CX - rx2, 0, CX + rx2, 0, [
        (0, '#c99482'), (0.5, '#a8767a'), (1, '#6e5070')])))
    ledge = ellipse(CX, y + 5, rx2, ry2).d()
    out.append('<path d="%s" fill="#f4d0a8" opacity="0.55" mask="%s"/>' % (ledge, doc.minus(ledge, 0, 1.6)))
    rx3, ry3 = rx1 * 0.56, ry1 * 0.5
    sable = ellipse(CX, y + 10, rx3, ry3)
    out.append(path(sable, doc.lin(CX + rx3, y, CX - rx3, y + 20, [(0, '#ffe2a8'), (0.6, '#f0c286'),
                                                                      (1, '#d8a070')])))
    # l'ombre du mur de droite sur le sable et les gradins (la lumière vient d'en haut à droite)
    inner = ellipse(CX, y + 1, rx1, ry1).d()
    out.append('<path d="%s" fill="#3a2650" opacity="0.4" mask="%s"/>' % (inner, doc.minus(inner, -34, 13)))
    # un signe inventé tracé dans le sable : deux lames croisées dans un losange (le blason de l'arène)
    sx, sy = CX - 4, y + 10
    out.append(path(poly_d([(sx, sy - 6), (sx + 13, sy), (sx, sy + 6), (sx - 13, sy)]), '#c88a5a', 0.55))
    out.append(path(poly_d([(sx, sy - 3.4), (sx + 7.5, sy), (sx, sy + 3.4), (sx - 7.5, sy)]), '#ffe6b0', 0.7))
    # le liseré de lumière sur le bord haut-droit du rebord
    out.append('<path d="%s" fill="#fff6d8" opacity="0.7" mask="%s"/>' % (bord.d(), doc.minus(bord.d(), -1.6, 1.6)))
    return ''.join(out)


DRAPEAUX = [(222, False), (270, False), (318, False), (20, True), (160, True)]


def drapeaux(doc, devant):
    """Des oriflammes rouge et or sur le rebord, qui flottent vers la gauche (le vent du soir)."""
    out = []
    for t, dv in DRAPEAUX:
        if dv != devant:
            continue
        x, y = pt(t, RY_TOP)
        y -= 1
        hm = 30
        out.append(path(poly_d([(x - 1.1, y), (x - 1.1, y - hm), (x + 1.1, y - hm), (x + 1.1, y)]), '#3a2638'))
        out.append('<circle cx="%s" cy="%s" r="1.9" fill="#ffd36a"/>' % (fm(x), fm(y - hm - 1)))
        fl = blob([(x - 1, y - hm + 1), (x - 10, y - hm - 1), (x - 21, y - hm + 1), (x - 15, y - hm + 6.5),
                   (x - 21, y - hm + 12), (x - 9, y - hm + 11.5), (x - 1, y - hm + 13)], sharp=(0, 2, 3, 4, 6))
        out.append(vol(doc, fl, dict(base='#c8364a', light='#e85460', rim='#ffd27a', sh='#8a1e3e'), r=1.1, c=1.4))
    return ''.join(out)


# ------------------------------------------------------------------------------------------------ le piton
def piton(doc):
    out = []
    # la roche : un plateau ovale sous le colisée, des falaises qui s'évasent et plongent dans les nuages
    py = RY_TOP + HAUT + 8
    roche = blob([(CX - 182, py - 4), (CX - 120, py + 36), (CX, py + 50), (CX + 120, py + 36), (CX + 184, py - 6),
                  (CX + 200, py + 40), (CX + 226, py + 120), (CX + 120, py + 170), (CX - 130, py + 170),
                  (CX - 226, py + 120), (CX - 200, py + 40)], sharp=(0, 4), t=0.9)
    out.append('<path d="%s" fill="%s" stroke="%s" stroke-width="3.4" stroke-linejoin="round"/>' % (
        roche.d(), INK, INK))
    out.append(vol(doc, roche, ROC, grad=doc.lin(CX + 200, py, CX - 160, py + 150, [
        (0, ROC['light']), (0.5, ROC['base']), (1, ROC['sh'])]), r=2, c=3.2))
    # deux grandes facettes éclairées à droite (la roche taillée), une ombre sous le plateau
    out.append(path(blob([(CX + 120, py + 40), (CX + 186, py - 2), (CX + 202, py + 44), (CX + 222, py + 118),
                          (CX + 150, py + 150), (CX + 132, py + 96)], sharp=(1,), t=0.8), ROC['light'], 0.6))
    out.append(path(blob([(CX + 40, py + 50), (CX + 112, py + 42), (CX + 124, py + 100), (CX + 70, py + 160),
                          (CX + 28, py + 120)], t=0.8), ROC['light'], 0.3))
    out.append(path(blob([(CX - 178, py + 4), (CX - 100, py + 40), (CX - 108, py + 110), (CX - 196, py + 112),
                          (CX - 204, py + 50)], t=0.8), ROC['sh'], 0.5))
    # le dessus du plateau : un tapis d'herbe autour du mur, plus clair à droite
    herbe = blob([(CX - 184, py - 6), (CX - 120, py + 28), (CX, py + 40), (CX + 122, py + 28), (CX + 186, py - 8),
                  (CX + 150, py - 4), (CX, py + 4), (CX - 150, py - 2)], sharp=(0, 4), t=0.8)
    out.append(vol(doc, herbe, HERBE, grad=doc.lin(CX + 180, py, CX - 180, py + 30, [
        (0, HERBE['light']), (0.6, HERBE['base']), (1, HERBE['sh'])]), r=1.4, c=0))
    # le chemin dallé qui descend de la grande porte vers les nuages
    gx = CX
    che = blob([(gx - 9, py - 8), (gx + 9, py - 8), (gx + 13, py + 40), (gx + 20, py + 120), (gx - 18, py + 120),
                (gx - 12, py + 40)], sharp=(0, 1), t=0.6)
    out.append(vol(doc, che, dict(base='#c8a088', light='#e6c09c', rim='#fff0c8', sh='#9a7478'),
                   grad=doc.lin(gx + 20, py, gx - 20, py + 120, [(0, '#ecc8a0'), (0.5, '#c8a088'), (1, '#8e6a76')]),
                   r=1, c=1.4))
    # des buissons ronds et des petits sapins sombres sur le plateau (posés, avec leur ombre)
    for x, y, s in [(CX - 160, py + 2, 1.1), (CX - 130, py + 16, 0.8), (CX + 150, py + 4, 1.0),
                    (CX + 120, py + 18, 0.75), (CX - 60, py + 30, 0.6), (CX + 64, py + 30, 0.65)]:
        out.append(buisson(doc, x, y, s))
    for x, y, s in [(CX - 176, py - 4, 1.0), (CX + 172, py - 6, 0.9)]:
        out.append(sapin(doc, x, y, s))
    return ''.join(out)


def buisson(doc, x, y, s):
    b = blob([(x - 9 * s, y), (x - 8 * s, y - 6 * s), (x - 2 * s, y - 10 * s), (x + 5 * s, y - 9 * s),
              (x + 9 * s, y - 4 * s), (x + 9 * s, y)], sharp=(0, 5), t=0.9)
    return ('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="#24163a" opacity="0.28"/>' % (
        fm(x - 2 * s), fm(y + 0.5), fm(11 * s), fm(2.4 * s))) + vol(doc, b, HERBE, r=1.1, c=1.6)


def sapin(doc, x, y, s):
    t = blob([(x, y - 30 * s), (x + 8 * s, y - 14 * s), (x + 11 * s, y - 2 * s), (x, y + 1), (x - 11 * s, y - 2 * s),
              (x - 8 * s, y - 14 * s)], sharp=(0,), t=0.8)
    return ('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="#24163a" opacity="0.3"/>' % (
        fm(x - 3 * s), fm(y + 1), fm(12 * s), fm(2.6 * s))) + vol(
        doc, t, dict(base='#2f5a4c', light='#43745c', rim='#b4d28e', sh='#1f3e3a'), r=1.2, c=2)


def fond():
    doc = Doc()
    body = ciel(doc) + montagnes(doc) + piton(doc) + colisee(doc) + drapeaux(doc, devant=True)
    return doc.svg(body, (0, 0, W, H))


# ================================================================================================ LES BANDES (tuiles)
APLATI = 0.8                    # les bosses de la mer de nuages, plus larges que hautes


def profil(lobes, x0, x1, step=1.5):
    """Le dessus d'un rang de nuages : le plus haut des lobes (cercles) en chaque x, la tuile répétée de chaque côté."""
    pts = []
    x = x0
    while x <= x1 + 0.01:
        best = None
        for cx, cy, r in lobes:
            for o in (-W, 0, W):
                dx = x - (cx + o)
                if abs(dx) < r:
                    yy = cy - APLATI * math.sqrt(r * r - dx * dx)
                    best = yy if best is None else min(best, yy)
        pts.append((x, best if best is not None else 9999))
        x += step
    return pts


def rang(doc, lobes, m, y_bas, prof=70):
    """Un rang de nuages en tuile : UNE masse (le dessus en lobes ronds), le liseré doré sur les pentes tournées vers
    la lumière (en haut à droite), la bande d'ombre sur les pentes de gauche ; une lueur douce au sommet de chaque
    lobe (sans bord) : le volume sans aucun trait ni bulle."""
    top = [(x, min(y, y_bas)) for x, y in profil(lobes, -6, W + 6)]
    ymin = min(y for _, y in top)
    masse = poly_d(top + [(W + 6, y_bas), (-6, y_bas)])
    ymoy = sum(y for _, y in top) / len(top)
    g = doc.lin(0, ymin, 0, ymoy + prof, [(0, m['light']), (0.3, m['base']), (0.75, m['sh']), (1, m['fond'])])
    out = [vol(doc, masse, m, grad=g, r=2.2, c=3.4, rim_op=0.9, sh_op=0.55)]
    for cx, cy, r in lobes:
        for o in (-W, 0, W):
            x = cx + o + r * 0.22
            if x + r < -6 or x - r > W + 6:
                continue
            y = cy - r * APLATI * 0.5
            out.append('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/>' % (
                fm(x), fm(y), fm(r * 0.7), fm(r * 0.4), doc.rad(x, y, r * 0.7, [
                    (0, m['rim'], 0.38), (0.6, m['light'], 0.12), (1, m['light'], 0)], ry=r * 0.4)))
    return ''.join(out)


def lobes_rang(seed, y, n, dy, k=(0.72, 1.08)):
    """n lobes serrés sur la tuile (ils se chevauchent : jamais de creux jusqu'en bas) ; la même graine donne
    toujours le même rang. y = la hauteur moyenne des sommets."""
    import random
    rnd = random.Random(seed)
    pas = W / n
    out = []
    for i in range(n):
        x = (i + rnd.uniform(0.3, 0.7)) * pas
        r = pas * rnd.uniform(*k)
        out.append((x, y + APLATI * r + rnd.uniform(-dy, dy), r))
    return out


def mer_svg(i):
    nom, y0, h, _ = BANDES[1 + i]
    doc = Doc()
    m = MER[i]
    arriere = dict(m, base=MER[max(0, i - 1)]['light'], light=MER[max(0, i - 1)]['light'], fond=m['base'])
    if i == 0:
        rangs = [(lobes_rang(11, y0 + 8, 13, 5), arriere, 40), (lobes_rang(12, y0 + 26, 10, 8, (0.8, 1.2)), m, 55)]
    elif i == 1:
        rangs = [(lobes_rang(23, y0 + 10, 10, 6), arriere, 50), (lobes_rang(24, y0 + 34, 8, 10, (0.8, 1.25)), m, 70)]
    else:
        rangs = [(lobes_rang(37, y0 + 12, 8, 7), arriere, 60), (lobes_rang(38, y0 + 42, 6, 12, (0.85, 1.3)), m, 90)]
    body = ''.join(rang(doc, lobes, mm, y0 + h + 10, pr) for lobes, mm, pr in rangs)
    return doc.svg('<g clip-path="%s">%s</g>' % (doc.clip('M0 %dH%dV%dH0Z' % (y0, W, y0 + h)), body),
                   (0, y0, W, h))


# Les nuages hauts : des bancs plats dessous, en lobes dessus, aux bords dorés ; les plus hauts plus sombres.
BANCS = [  # x0, x1, y du dessous, lobes (cx, cy, r) de droite à gauche, matière
    (-40, 210, 236, [(196, 226, 14), (164, 210, 22), (120, 198, 28), (72, 196, 26), (26, 204, 22), (-14, 216, 16)],
     NUAGE_HAUT),
    (300, 520, 170, [(508, 162, 12), (474, 150, 18), (430, 142, 20), (386, 146, 18), (344, 156, 14),
                     (314, 164, 9)], NUAGE_HAUT),
    (236, 470, 386, [(456, 378, 12), (424, 364, 18), (384, 356, 22), (338, 360, 20), (294, 370, 15), (258, 378, 10)],
     NUAGE_MI),
    (-10, 150, 452, [(138, 446, 9), (112, 436, 14), (78, 430, 16), (42, 434, 14), (10, 442, 10)], NUAGE_MI),
    (380, 560, 530, [(546, 524, 9), (516, 514, 13), (484, 510, 13), (450, 514, 11), (412, 520, 8)], NUAGE_BAS),
]


def banc(doc, x0, x1, yb, lobes, m, o):
    pts = [(x0 + o, yb - 2), (x0 + o + (x1 - x0) * 0.3, yb + 4), (x0 + o + (x1 - x0) * 0.7, yb + 3), (x1 + o, yb - 2)]
    sharp = []
    for k, (cx, cy, r) in enumerate(lobes):
        if k > 0:
            sharp.append(len(pts))
        for a in (5, 50, 90, 130, 175):
            ra = math.radians(a)
            pts.append((cx + o + r * math.cos(ra), cy - r * math.sin(ra)))
    s = blob(pts, sharp=tuple(sharp), t=0.9)
    return vol(doc, s, m, r=2.4, c=3.6, rim_op=0.85)


def ciel_svg():
    nom, y0, h, _ = BANDES[0]
    doc = Doc()
    body = ''.join(banc(doc, *b, o) for b in BANCS for o in (-W, 0, W))
    return doc.svg('<g clip-path="%s">%s</g>' % (doc.clip('M0 %dH%dV%dH0Z' % (y0, W, y0 + h)), body),
                   (0, y0, W, h))


# ================================================================================================ LA PAGE
OISEAUX = [(150, 420, 1.0, 0), (166, 412, 0.8, 0.35), (138, 410, 0.7, 0.7)]   # x, y, taille, décalage du battement


def oiseau_svg():
    """Un oiseau lointain : deux ailes en arc (signe simple, sombre), pour un petit SVG en ligne."""
    return ('<svg viewBox="-12 -6 24 10"><path d="M-11 -1Q-6 -6 0 1Q6 -6 11 -1Q6 -3 0 4Q-6 -3 -11 -1Z" '
            'fill="#2a1f52"/></svg>')


# Des lucioles d'or qui montent lentement de la mer de nuages et s'éteignent : x, y de départ, taille, durée, retard
LUCIOLES = [(96, 930, 5, 9, 0), (180, 980, 4, 11, 3.5), (402, 950, 5, 10, 1.6), (468, 1010, 4, 12, 6),
            (330, 1000, 3.5, 9.5, 4.8), (54, 1040, 4, 11, 7.6), (240, 1060, 3, 10, 2.4)]


def html():
    svg = open(os.path.join(ROOT, 'public', 'art', 'ui', 'logo.svg'), encoding='utf-8').read()
    vw, vh = [float(v) for v in re.search(r'viewBox="[\d.-]+ [\d.-]+ ([\d.]+) ([\d.]+)"', svg).groups()]
    svg = svg.replace('<svg ', '<svg class="logo" ', 1)
    lx, ly, lw = LOGO
    lh = lw * vh / vw
    pc = lambda v, tot: '%.3f%%' % (v / tot * 100)
    bandes_css = []
    bandes_html = []
    for nom, y0, h, dur in BANDES:
        bandes_css.append('#splash .b-%s { top: %s; height: %s; animation-duration: %ds; }' % (
            nom, pc(y0, H), pc(h, H), dur))
        # l'adresse de l'image dans le style de l'élément (pas dans le CSS : Vite le laisse tel quel, relatif à la page)
        bandes_html.append('<i class="bd b-%s" style="background-image:url(art/chargement/%s.webp)"></i>' % (nom, nom))
    # les oiseaux : un petit vol (aller vers la droite, très lent) et un battement d'ailes
    ois_css = []
    ois_html = []
    for k, (x, y, s, ph) in enumerate(OISEAUX):
        ois_css.append('#splash .o%d { left: %s; top: %s; width: %s; animation-delay: -%.2fs; }' % (
            k, pc(x, W), pc(y, H), pc(24 * s, W), ph))
        ois_html.append('<i class="oi o%d">%s</i>' % (k, oiseau_svg()))
    luc_css = []
    for k, (x, y, sz, dur, dl) in enumerate(LUCIOLES):
        luc_css.append('#splash .l%d { left: %s; top: %s; width: %s; animation-duration: %gs; animation-delay: %gs; }'
                       % (k, pc(x, W), pc(y, H), pc(sz * 3, W), dur, dl))
    luc_html = ''.join('<i class="lu l%d"></i>' % k for k in range(len(LUCIOLES)))
    pts = [(0, 0), (8, 0.30), (20, 0.52), (40, 0.70), (65, 0.82), (100, 0.92)]
    kf = ' '.join('%d%%{width:%.0f%%}' % (p, v * 100) for p, v in pts)
    style = f"""<style>
      /* écran de chargement en style moderne (fabriqué par refonte-graphique/ui-moderne/chargement/chargement.py) :
         visible pendant le téléchargement du jeu, retiré par main.tsx. La scène ({W} × {H} unités) est agrandie pour
         couvrir l'écran (une colonne de 480 px au plus) : --u = la taille d'une unité ; ce qui dépasse est coupé
         ({ANCRE * 100:.0f} % en haut). Tout ce qui bouge glisse en CSS (aucun dessin à refaire, léger pour le téléphone). */
      #splash {{ position: fixed; inset: 0; z-index: 9999; background: #150f36; transition: opacity .5s; }}
      #splash.gone {{ opacity: 0; pointer-events: none; }}
      #splash .sp {{ position: absolute; top: 0; bottom: 0; left: 50%; width: min(100%, 480px); transform: translateX(-50%); overflow: hidden;
        --u: max(calc(min(100vw, 480px) / {W}), calc(100vh / {H})); background: #3a2f78; }}
      @supports (height: 100dvh) {{ #splash .sp {{ --u: max(calc(min(100vw, 480px) / {W}), calc(100dvh / {H})); }} }}
      #splash .sc {{ position: absolute; width: calc(var(--u) * {W}); height: calc(var(--u) * {H}); left: calc(50% - var(--u) * {W / 2:g});
        top: calc((100% - var(--u) * {H}) * {ANCRE}); background: 0 0 / 100% 100% no-repeat; }}
      #splash .bd {{ position: absolute; left: 0; width: 200%; background-size: 50% 100%; background-repeat: repeat-x;
        animation: splash-glisse linear infinite; will-change: transform; }}
      {' '.join(bandes_css)}
      @keyframes splash-glisse {{ from {{ transform: translateX(0) }} to {{ transform: translateX(-50%) }} }}
      /* la lueur du soleil respire */
      #splash .sol {{ position: absolute; left: {pc(SOLEIL[0] - 110, W)}; top: {pc(SOLEIL[1] - 110, H)}; width: {pc(220, W)}; height: {pc(220, H)};
        border-radius: 50%; background: radial-gradient(closest-side, #fff2d0a0, #ffd8b044 45%, #ffd8b000);
        animation: splash-sol 5s ease-in-out infinite alternate; }}
      @keyframes splash-sol {{ from {{ opacity: .35; transform: scale(.9) }} to {{ opacity: 1; transform: scale(1.08) }} }}
      #splash .oi {{ position: absolute; display: block; animation: splash-vol 26s ease-in-out infinite alternate; }}
      #splash .oi svg {{ display: block; width: 100%; height: auto; animation: splash-aile .9s ease-in-out infinite alternate; transform-origin: 50% 40%; }}
      {' '.join(ois_css)}
      @keyframes splash-vol {{ from {{ transform: translate(0, 0) }} 50% {{ transform: translate(calc(var(--u) * 50), calc(var(--u) * -8)) }} to {{ transform: translate(calc(var(--u) * 96), calc(var(--u) * 4)) }} }}
      @keyframes splash-aile {{ from {{ transform: scaleY(1) }} to {{ transform: scaleY(-.55) }} }}
      /* les lucioles : un point d'or (dégradé, sans flou) qui monte, ondule et s'éteint */
      #splash .lu {{ position: absolute; aspect-ratio: 1; border-radius: 50%; opacity: 0;
        background: radial-gradient(closest-side, #fffbe6, #ffd86a 40%, #ffb53a00); animation: splash-luciole linear infinite; }}
      {' '.join(luc_css)}
      @keyframes splash-luciole {{ 0% {{ opacity: 0; transform: translate(0, 0) }} 15% {{ opacity: 1 }}
        50% {{ transform: translate(calc(var(--u) * 10), calc(var(--u) * -70)) }} 80% {{ opacity: .8 }}
        100% {{ opacity: 0; transform: translate(calc(var(--u) * -4), calc(var(--u) * -150)) }} }}
      /* le logo (vectoriel, net à toutes les tailles) : posé dans le ciel, au-dessus du colisée */
      #splash .logo {{ position: absolute; left: {pc(lx - lw / 2, W)}; top: {pc(ly - lh / 2, H)}; width: {pc(lw, W)}; height: auto;
        aspect-ratio: {vw:.0f} / {vh:.0f}; overflow: visible; animation: splash-logo .8s cubic-bezier(.2, 1.4, .4, 1) both; }}
      @keyframes splash-logo {{ from {{ opacity: 0; transform: translateY(calc(var(--u) * 14)) scale(.92) }} to {{ opacity: 1; transform: none }} }}
      /* la jauge : une pilule creusée dans la pierre, cerclée d'or fin ; l'or la remplit (vite au début, puis de plus en
         plus lentement, jusqu'à 92 %) ; une lumière passe dessus */
      #splash .load {{ position: absolute; left: 50%; bottom: calc(env(safe-area-inset-bottom, 0px) + 34px); width: min(64%, 250px); height: 18px;
        transform: translateX(-50%); padding: 4px; border-radius: 999px; box-sizing: border-box;
        background: linear-gradient(180deg, #1f1d33, #2e2c47); box-shadow: inset 0 0 0 1.5px #ffc94d8c, inset 0 2px 3px #05021a99, 0 4px 12px #1a0f3a80; }}
      #splash .load i {{ display: block; height: 100%; border-radius: 999px; overflow: hidden; }}
      #splash .load b {{ position: relative; display: block; height: 100%; width: 0; border-radius: 999px; overflow: hidden; animation: splash-load 6s ease-out forwards;
        background: linear-gradient(180deg, #ffe27a, #ffc22e 55%, #e08a1a); box-shadow: inset 0 1.5px 0 #fff6c8, 0 0 8px #ffc22e80; }}
      #splash .load b::after {{ content: ''; position: absolute; top: 0; bottom: 0; width: 40px; left: -40px;
        background: linear-gradient(90deg, #fff0, #fffbe6b0, #fff0); animation: splash-reflet 1.8s ease-in-out .6s infinite; }}
      @keyframes splash-load {{ {kf} }}
      @keyframes splash-reflet {{ from {{ left: -40px }} to {{ left: 100% }} }}
      #splash.done .load b {{ width: 100%; animation: none; transition: width .25s; }}
      @media (prefers-reduced-motion: reduce) {{ #splash .bd, #splash .oi, #splash .oi svg, #splash .sol, #splash .load b::after {{ animation: none; }} #splash .lu {{ display: none; }} }}
    </style>"""
    body = ('<div id="splash"><div class="sp"><div class="sc" style="background-image:url(art/chargement/fond.webp)">' + ''.join(bandes_html[:1]) + '<i class="sol"></i>'
            + ''.join(ois_html) + ''.join(bandes_html[1:]) + luc_html + svg + '</div><div class="load"><i><b></b></i></div>'
            '</div></div>')
    pre = '\n    '.join('<link rel="preload" as="image" type="image/webp" href="art/chargement/%s.webp" />' % n
                        for n in ['fond'] + [b[0] for b in BANDES])
    return style, body, pre


def remplace(texte, nom, contenu):
    a, b = f'<!-- {nom}:debut -->', f'<!-- {nom}:fin -->'
    i, j = texte.index(a), texte.index(b)
    return texte[:i + len(a)] + '\n    ' + contenu + '\n    ' + texte[j:]


def rendre(jobs):
    """jobs = [(svg, sortie.png, w, h)] rendus par le moteur des héros (Chromium, rendu-lot.cjs), groupés par taille."""
    os.makedirs(TMP, exist_ok=True)
    par_taille = {}
    for k, (svg, out, w, h) in enumerate(jobs):
        p = os.path.join(TMP, '%d.svg' % k)
        open(p, 'w').write(svg)
        par_taille.setdefault((w, h), []).append([p, out])
    for (w, h), frames in par_taille.items():
        jp = os.path.join(TMP, 'job-%d-%d.json' % (w, h))
        json.dump({'w': w, 'h': h, 'frames': frames}, open(jp, 'w'))
        subprocess.run(['node', RENDU, jp], check=True)


def main():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(SORTIE, exist_ok=True)
    jobs = [(fond(), os.path.join(TMP, 'fond.png'), round(W * K), round(H * K)),
            (ciel_svg(), os.path.join(TMP, 'ciel.png'), round(W * K), round(BANDES[0][2] * K))]
    for i in range(3):
        nom, y0, h, _ = BANDES[1 + i]
        jobs.append((mer_svg(i), os.path.join(TMP, nom + '.png'), round(W * K), round(h * K)))
    rendre(jobs)
    tailles = {}
    for nom in ['fond'] + [b[0] for b in BANDES]:
        im = Image.open(os.path.join(TMP, nom + '.png'))
        im = im.convert('RGB') if nom == 'fond' else im.convert('RGBA')
        p = os.path.join(OUT, nom + '.webp')
        im.save(p, 'WEBP', quality=86 if nom == 'fond' else 84, method=6)
        tailles[nom] = os.path.getsize(p)
    # l'image fixe complète (écran du nom au premier lancement) et l'aperçu
    scene = Image.open(os.path.join(TMP, 'fond.png')).convert('RGBA')
    for nom, y0, h, _ in BANDES:
        scene.alpha_composite(Image.open(os.path.join(TMP, nom + '.png')).convert('RGBA'), (0, round(y0 * K)))
    scene.convert('RGB').save(os.path.join(SORTIE, 'scene.png'))
    fixe = scene.convert('RGB').resize((W, H), Image.LANCZOS)
    fixe.save(os.path.join(OUT, 'chargement.webp'), 'WEBP', quality=80, method=6)
    tailles['chargement'] = os.path.getsize(os.path.join(OUT, 'chargement.webp'))
    print('images :', ', '.join('%s %d ko' % (n, v // 1024) for n, v in tailles.items()),
          '— total chargement %d ko' % (sum(v for n, v in tailles.items() if n != 'chargement') // 1024))
    style, body, pre = html()
    p = os.path.join(ROOT, 'index.html')
    t = open(p, encoding='utf-8').read()
    t = remplace(t, 'chargement-style', style)
    t = remplace(t, 'chargement-precharge', pre)
    t = remplace(t, 'chargement', body)
    open(p, 'w', encoding='utf-8').write(t)
    print('index.html mis à jour')


if __name__ == '__main__':
    main()
