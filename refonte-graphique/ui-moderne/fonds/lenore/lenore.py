# Le fond de combat du clan de LENORE (feu), la forteresse des oni au crépuscule, redessiné en VECTORIEL lisse et
# animé (27/11/2026, demande du propriétaire : les 7 autres fonds sur le modèle du volcan de Kael, validé).
#
# Même univers que le fond pixel (refonte-graphique/pixel/fonds/lenore/build.py), recomposé pour le vrai combat
# (le jeu agrandit le fond ×1,4 et coupe les côtés : tout l'important est entre x 84 et 506, sous les pilules du haut,
# au-dessus des cartes). Mêmes mesures et même façon de faire que fonds/kael/kael.py : image de 590 × 1100 pixels du
# fond, plateforme de P0 = 800 à P1 = 1047 ; style des héros vectoriels (grandes formes simples, dégradés doux, une
# seule lumière en haut à droite, un seul contour sombre seulement sur les plans proches, aucun flou SVG), moins
# contrasté que les personnages ; la profondeur vient de la brume (le lointain plus pâle).
#
# Ce qu'on voit, du fond vers le devant : le ciel du crépuscule (indigo en haut, mauve, or près de l'horizon), la
# grosse lune pâle en haut à droite (la seule lumière), quelques étoiles, de longs nuages mauves ; les montagnes
# bleu-mauve dans la brume et un petit pavillon perché ; le DONJON des oni au milieu (soubassement de gros blocs aux
# flancs incurvés, trois étages crème aux poutres de laque rouge et aux fenêtres allumées, trois toits de fer
# bleu-gris aux bouts recourbés, un pignon, et au faîte les deux grandes cornes d'ivoire) ; à gauche la TOUR DE GUET
# (la plaque ronde de laque au signe du clan, deux lanternes de papier, deux petites cornes) et une guirlande de
# lanternes jusqu'au donjon ; à droite un érable rouge ; la MURAILLE basse au chaperon de tuiles, percée au milieu
# d'une PORTE aux piliers de laque (battants ouverts cloutés d'or, une lanterne, des marches) ; deux bannières rouges
# au signe d'or sur la muraille ; deux BRASEROS de fer qui encadrent la porte ; la cour pavée (calme, d'un bord à
# l'autre) ; la terrasse et les douves (sombres, sous les cartes) ; dans les coins du bas, la balustrade de laque.
# Ce qui bouge : les fenêtres du donjon (la lueur respire), les trois lanternes qui se balancent, les bannières, les
# flammes des braseros et leurs étincelles, les feuilles d'érable qui s'envolent, et trois CORBEAUX lointains qui
# traversent le ciel (la touche vivante, comme les dragons de Kael : l'un passe devant la lune, le plus loin finit
# derrière le dernier étage du donjon).
# Le signe du clan (inventé, comme le pixel) : deux cornes dressées en croissant au-dessus d'un clou de kanabō.
#
#   python3 refonte-graphique/ui-moderne/fonds/lenore/lenore.py --fixe     # la vue du combat dans le brouillon
#   python3 refonte-graphique/ui-moderne/fonds/lenore/lenore.py            # images du jeu + calques + test + contrôles
#   python3 refonte-graphique/ui-moderne/fonds/lenore/lenore.py --video    # en plus : anim.gif et anim.mp4
#
# Sorties : public/art/vecto/fonds/lenore.webp (fixe ×2), lenore-anim.webp (planche ×2), fond-lenore.json et
# meta.json (à côté de ce fichier ; meta.json est réuni avec les autres clans dans src/game/fond-vecto.ts par
# fonds/assemble_ts.py) ; pixel/sortie/ui/vecto/fond-lenore/ (fond.png, situation.png, comparaison.png, anim.gif,
# anim.mp4, STATUT.txt).
import base64
import json
import math
import os
import shutil
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'pictos'))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'heros'))
from lib import Shape, blob, ellipse, mix, rpoly, star  # noqa: E402
from atelier import sm, ribbon, bez, resample, sides  # noqa: E402

CLAN = 'lenore'
BROUILLON = os.environ.get('BROUILLON', '/tmp/fonds-brouillon')
TMP = os.path.join(BROUILLON, 'vecto-fond-' + CLAN + '')
SORTIE = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'fond-' + CLAN)
JEU = os.path.join(ROOT, 'public', 'art', 'vecto', 'fonds')
RENDU = os.path.join(ROOT, 'refonte-graphique', 'ui-moderne', 'heros', 'rendu-lot.cjs')

# ------------------------------------------------------------------------------------------------ les mesures
W, H = 590, 1100
UP = 2                          # les images du jeu sont rendues ×2 (vectoriel : plus fin que le pixel)
HZ, P0, P1 = 789, 800, 1047      # P0 avancé (819 → 800) : en combat, le rang du fond a ses pieds à 828
RANGS = (860, 934, 1007)
VISIBLE = {'court': 377, 'moyen': 148, 'long': 50}
PERIODE = 19200                 # toutes les boucles divisent cette période : l'aperçu boucle sans couture
                                # (19,2 s : les corbeaux traversent le ciel lentement, une fois par période)
UNIT = 720 / W
HERO_X_U = {3: 82, 4: 82, 2: 163, 0: 245, 1: 245}
ENEMY_X_U = {0: 475, 1: 475, 2: 557, 3: 638, 4: 638}
ROW_OF = {0: 0, 3: 0, 2: 1, 1: 2, 4: 2}


def place(side, slot):
    xs = HERO_X_U if side == 'heros' else ENEMY_X_U
    return int(round(xs[slot] / UNIT)), RANGS[ROW_OF[slot]]


# Le VRAI combat (src/game/battle-scene.ts, fight-view.ts) : le décor y est agrandi ×1,4 (FOND_ZOOM), centré, son bas
# au bas de l'écran (au-dessus de la barre de geste) ; on n'en voit que x = 84 → 506. Les combattants : spreadX,
# ROW_DY (90 / 180 / 270) + FEET (47) sous le haut du sol (= bas de l'image − 430 × 1,4), dessinés à 1,22 × 0,95.
ZOOM = 1.4
UC = 720 / W * ZOOM                                   # unités de jeu par pixel du fond, en combat
OXC = (720 - W * UC) / 2                              # le bord gauche de l'image (unités, négatif : coupé)
VUE_X = (-OXC / UC, (720 - OXC) / UC)                 # 84,3 → 505,7 : ce qu'on voit en largeur
K_PERSO = 1.22 * 0.95 / UC                            # un pixel d'un personnage = 0,68 pixel du fond en combat
ROW_DY = {0: 90, 3: 90, 2: 180, 1: 270, 4: 270}
RANGS_COMBAT = tuple(1100 - (430 * ZOOM - d - 47) / UC for d in (90, 180, 270))     # 828 / 880 / 933
CARTES = 1100 - (14 + 182) / UC                       # 985 : le haut des cartes des héros (tout ce qui est dessous est caché)


def place_combat(side, slot):
    spread = lambda x: (720 - 288) / 2 + (x - 245) * 0.88
    x = spread(HERO_X_U[slot]) if side == 'heros' else 720 - spread(720 - ENEMY_X_U[slot])
    return (x - OXC) / UC, 1100 - (430 * ZOOM - ROW_DY[slot] - 47) / UC


def telephone(w, h, bas=0):
    """Un téléphone (w × h points, `bas` = la barre de geste) : (haut visible du fond, hauteur du jeu en unités)."""
    hu = max(1280, min(1640, round(720 * h / w)))
    return 1100 - (hu - bas * 720 / w) / UC, hu


# ------------------------------------------------------------------------------------------------ les couleurs
# Reprises de Lenore et de ses monstres vectoriels (peau de laque rouge, crinière indigo, cornes d'ivoire, or, fer
# bleu-gris, papier des lanternes du sorcier) et du fond pixel (crépuscule indigo → or), mais plus sourdes.
INK = '#1f1238'                 # le contour (le raisin de l'interface), seulement sur les plans proches
CIEL = [(0, '#12163a'), (0.22, '#1c2148'), (0.40, '#2c2e5a'), (0.54, '#463e6a'), (0.64, '#664c70'),
        (0.72, '#8e5a6c'), (0.80, '#b46c64'), (0.88, '#d08a5c'), (0.95, '#e2a45e'), (1, '#eab462')]
NUAGE = dict(base='#34345e', light='#40406c', rim='#8a7a9a', sh='#28284e')
NUAGE2 = dict(base='#44406c', light='#524c78', rim='#a08aa4', sh='#34325c')
NUAGE3 = dict(base='#5c4c78', light='#6a5884', rim='#b498a8', sh='#4a3e68')
LOIN1 = dict(base='#7a6890', light='#86749a', rim='#a28eae', sh='#6e5c86')        # la crête la plus lointaine
LOIN2 = dict(base='#64527c', light='#705e88', rim='#8e7aa2', sh='#58486f')
LOIN3 = dict(base='#4e4068', light='#5a4c74', rim='#7e6c94', sh='#433860')
PIERRE = dict(base='#504862', light='#625a72', rim='#8e8298', sh='#3a3350')       # le granite du donjon et de la tour
MUR = dict(base='#433c56', light='#524a64', rim='#83778e', sh='#2f2a40')          # la muraille (plus proche)
ENDUIT = dict(base='#8e7a82', light='#a89090', rim='#cdb8ac', sh='#6c5a6c')       # les murs crème dans le crépuscule
LAQUE = dict(base='#982a32', light='#b43a36', rim='#dc5e40', sh='#641a30')        # la laque rouge (la peau de Lenore)
TUILE = dict(base='#363a58', light='#464c6c', rim='#7c86a8', sh='#24263c')        # les tuiles de fer bleu-gris
FER = dict(base='#2e2c40', light='#423e56', rim='#7a7490', sh='#1e1c2c')
IVOIRE = dict(base='#d2c2a6', light='#e6dabe', rim='#fbf2da', sh='#a08a7a')
OR = dict(base='#d8a03a', light='#f0c45e', hot='#fff0b0', rim='#ffe8a0', sh='#94641e')
BOIS = dict(base='#3e2a34', light='#523844', rim='#866070', sh='#2a1c26')
ERABLE = dict(base='#b03a30', light='#cc5236', rim='#ec8a52', sh='#76222e')
PAPIER = dict(hot='#fff2c4', glow='#ffd27a', mid='#f09a40', deep='#c8562a')
FEU = dict(hot='#fff2c0', glow='#ffd070', mid='#f4963c', deep='#d8582c')
SOL = dict(back='#5d596d', front='#666272')                                         # la cour : valeur moyenne

def fm(v):
    return ('%.2f' % v).rstrip('0').rstrip('.')


# ------------------------------------------------------------------------------------------------ le document SVG
class Doc:
    """Un dessin SVG : collecte les dégradés, masques et symboles (defs) ; chaque fonction de dessin rend du texte."""

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
        self.defs.append('<mask id="%s" maskUnits="userSpaceOnUse" x="-200" y="-200" width="1000" height="1500">'
                         '<path d="%s" fill="#fff"/><path d="%s" fill="#000" transform="translate(%s %s)"/></mask>'
                         % (i, d, d, fm(dx), fm(dy)))
        return 'url(#%s)' % i

    def clip(self, d, evenodd=False):
        i = self.uid('c')
        self.defs.append('<clipPath id="%s"><path d="%s"%s/></clipPath>' % (
            i, d, ' clip-rule="evenodd"' if evenodd else ''))
        return 'url(#%s)' % i

    def svg(self, body, box, size=None):
        x, y, w, h = box
        sz = ' width="%s" height="%s"' % (fm(size[0]), fm(size[1])) if size else ''
        return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="%s %s %s %s"%s><defs>%s</defs>%s</svg>'
                % (fm(x), fm(y), fm(w), fm(h), sz, ''.join(self.defs), body))


EO = ' fill-rule="evenodd"'


def D(s):
    return s if isinstance(s, str) else s.d()


def path(d, fill, op=1.0, extra=''):
    return '<path d="%s" fill="%s"%s%s/>' % (D(d), fill, '' if op == 1 else ' opacity="%g"' % op, extra)


def vol(doc, shape, m, grad=None, r=1.6, c=2.4, ink=None, iw=1.0, rim_op=0.9, sh_op=0.85):
    """Un volume dans le style des héros : dégradé (clair en haut à droite), bande d'ombre nette en bas à gauche,
    liseré de lumière en haut à droite ; `ink` : le contour (plans proches seulement)."""
    d = D(shape)
    xs = [p[0] for p in shape.pts()] if not isinstance(shape, str) else [0, W]
    ys = [p[1] for p in shape.pts()] if not isinstance(shape, str) else [0, H]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    out = []
    if ink:
        out.append('<path d="%s" fill="%s" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>' % (
            d, ink, ink, fm(2 * iw)))
    g = grad or doc.lin(x1, y0, x0 + (x1 - x0) * 0.25, y1, [(0, m['light']), (0.55, m['base']), (1, m['sh'])])
    out.append(path(d, g))
    if c:
        out.append('<path d="%s" fill="%s" opacity="%g" mask="%s"/>' % (d, m['sh'], sh_op, doc.minus(d, c * 0.8, -c)))
    if r:
        out.append('<path d="%s" fill="%s" opacity="%g" mask="%s"/>' % (d, m['rim'], rim_op, doc.minus(d, -r * 0.75, r)))
    return ''.join(out)


def polyline_d(pts):
    return 'M' + ' L'.join('%s %s' % (fm(x), fm(y)) for x, y in pts)


def length(pts):
    return sum(math.dist(pts[i - 1], pts[i]) for i in range(1, len(pts)))


def lobes_shape(x0, x1, yb, lobes, sag=3):
    """Un banc de fumée : dessous presque plat, dessus en lobes ronds (lobes = [(cx, cy, r)] de droite à gauche)."""
    pts = [(x0, yb - 2), (x0 + (x1 - x0) * 0.3, yb + sag), (x0 + (x1 - x0) * 0.7, yb + sag * 0.6), (x1, yb - 2)]
    sharp = []
    for k, (cx, cy, r) in enumerate(lobes):
        if k > 0:
            sharp.append(len(pts))
        for a in (5, 50, 90, 130, 175):
            ra = math.radians(a)
            pts.append((cx + r * math.cos(ra), cy - r * math.sin(ra)))
    return sm(pts, sharp=tuple(sharp), t=0.9)


# ------------------------------------------------------------------------------------------------ les aides
def catmull(pts, n=6):
    """Une ligne douce passant par les points (Catmull-Rom), n points par segment."""
    out = []
    P = [pts[0]] + list(pts) + [pts[-1]]
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in range(2)))
    out.append(pts[-1])
    return out


def rectd(x0, y0, x1, y1):
    return 'M%s %sH%sV%sH%sZ' % (fm(x0), fm(y0), fm(x1), fm(y1), fm(x0))


def corne(a, b, c, d_, w0, n=14):
    """Une corne (ou une branche) : un ruban le long d'une courbe de Bézier, large au pied, pointu au bout."""
    c_ = resample(bez(a, b, c, d_), n)
    ws = [w0 * (1 - i / n) ** 0.8 + 0.25 for i in range(n + 1)]
    left, right = sides(c_, ws)
    return sm([left[0]] + left[1:] + [c_[-1]] + right[1:][::-1] + [right[0]], sharp=(0, len(left), len(left) * 2), t=0.8)


def toit_forme(cx, yt, ht, ye, he, lift, th):
    """Un toit recourbé vu de face : le haut (yt, demi-largeur ht), les pentes creusées (raides en haut, presque plates
    en bas), les bouts relevés (ye − lift, demi-largeur he), le dessous (épaisseur th au milieu)."""
    def side(sg):
        q1 = (cx + sg * (ht + (he - ht) * 0.42), yt + (ye - yt) * 0.78)
        q2 = (cx + sg * (ht + (he - ht) * 0.80), ye - lift * 0.15)
        tip = (cx + sg * he, ye - lift)
        u1 = (cx + sg * he * 0.86, ye + th * 0.4)
        u2 = (cx + sg * he * 0.52, ye + th)
        return q1, q2, tip, u1, u2
    rq1, rq2, rt, ru1, ru2 = side(1)
    lq1, lq2, lt, lu1, lu2 = side(-1)
    pts = [(cx - ht, yt), (cx + ht, yt), rq1, rq2, rt, ru1, ru2, lu2, lu1, lt, lq2, lq1]
    s = sm(pts, sharp=(0, 1, 4, 9), t=0.8)
    bord = [rt, ru1, ru2, lu2, lu1, lt]
    return s, bord


def toit(doc, cx, yt, ht, ye, he, lift, th, ink=True):
    s, bord = toit_forme(cx, yt, ht, ye, he, lift, th)
    g = doc.lin(cx + he, yt, cx - he * 0.6, ye + th, [(0, TUILE['light']), (0.5, TUILE['base']), (1, TUILE['sh'])])
    out = [vol(doc, s, TUILE, grad=g, r=1.4, c=2.2, ink=INK if ink else None, iw=0.9)]
    # le bord du toit (la planche de rive), un liseré clair le long du dessous, plus clair à droite
    c = resample(catmull(bord, 5), 30)
    out.append(path(ribbon(c, [1.6 * math.sin(math.pi * i / 30) ** 0.3 + 0.2 for i in range(31)]),
                    doc.lin(cx - he, 0, cx + he, 0, [(0, TUILE['light']), (1, TUILE['rim'])]), 0.85))
    return ''.join(out)


def mur(doc, x0, y0, x1, y1, poteaux=(), ink=True):
    """Un étage : le mur crème, ses poutres de laque rouge (en haut, en bas, quelques poteaux), l'ombre de l'avant-toit."""
    out = [vol(doc, rpoly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], 0.6), ENDUIT,
               grad=doc.lin(x1, y0, x0, y1, [(0, ENDUIT['light']), (0.6, ENDUIT['base']), (1, ENDUIT['sh'])]),
               r=1.0, c=1.6, ink=INK if ink else None, iw=0.8)]
    for ya, yb in ((y0, y0 + 3.4), (y1 - 3.4, y1)):
        out.append(path(rpoly([(x0, ya), (x1, ya), (x1, yb), (x0, yb)], 0.4),
                        doc.lin(x0, 0, x1, 0, [(0, LAQUE['sh']), (1, LAQUE['base'])])))
    for x in poteaux:
        out.append(path(rpoly([(x - 1.7, y0), (x + 1.7, y0), (x + 1.7, y1), (x - 1.7, y1)], 0.3), LAQUE['base']))
        out.append(path(rpoly([(x + 0.6, y0 + 3), (x + 1.7, y0 + 3), (x + 1.7, y1 - 3), (x + 0.6, y1 - 3)], 0.2),
                        LAQUE['light'], 0.7))
    # l'ombre douce de l'avant-toit en haut du mur
    out.append(path(rectd(x0, y0, x1, y0 + 9), doc.lin(0, y0, 0, y0 + 9, [(0, '#2a1e34', 0.45), (1, '#2a1e34', 0)])))
    return ''.join(out)


def fenetre(doc, x, y, w, h, k):
    """Une fenêtre allumée (k : la force de la lueur, 0 à 1) : un cadre de laque sombre, le papier éclairé dedans."""
    out = ['<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/>' % (
        fm(x), fm(y), fm(w * 1.25), fm(h * 0.95), doc.rad(x, y, w * 1.25, [
            (0, '#ffb45a', 0.18 + 0.22 * k), (1, '#ffb45a', 0)], ry=h * 0.95))]
    out.append(path(rpoly([(x - w / 2 - 1.2, y - h / 2 - 1.2), (x + w / 2 + 1.2, y - h / 2 - 1.2),
                           (x + w / 2 + 1.2, y + h / 2 + 1.2), (x - w / 2 - 1.2, y + h / 2 + 1.2)], 0.5), '#3a1426'))
    out.append(path(rpoly([(x - w / 2, y - h / 2), (x + w / 2, y - h / 2), (x + w / 2, y + h / 2), (x - w / 2, y + h / 2)],
                          0.3), doc.lin(x + w / 2, y - h / 2, x - w / 2, y + h / 2, [
                              (0, mix('#d88a4a', '#ffe2a0', k)), (0.6, mix('#b8603a', '#ffbe68', k)),
                              (1, mix('#8a3e2e', '#e8843e', k))])))
    return ''.join(out)


def signe_forme(cx, cy, k):
    """Le signe du clan de Lenore (inventé, comme le pixel) : deux cornes dressées en croissant au-dessus d'un clou de
    kanabō (un losange) : la tête cornue de l'oni et sa massue. Aucune lettre."""
    def P(u, v):
        return (cx + u * k, cy + v * k)
    croissant = sm([P(-4.6, -7.0), P(-4.4, -3.4), P(-2.8, -0.6), P(0, 0.6), P(2.8, -0.6), P(4.4, -3.4), P(4.6, -7.0),
                    P(2.9, -3.0), P(0, -1.4), P(-2.9, -3.0)], sharp=(0, 6), t=0.85)
    clou = rpoly([P(0, 1.9), P(2.1, 4.5), P(0, 7.1), P(-2.1, 4.5)], 0.3 * k)
    return croissant + clou


# ================================================================================================ LES ÉLÉMENTS
# Chaque élément : id, profondeur (plans du pixel : ciel −29, derrière −25, paysage −20, devant −15, premier 1300),
# genre ('fixe' : dans l'image fixe seulement ; 'boucle' ; 'morceau' = une boucle d'une image remise par-dessus ;
# 'defile' ; 'particules') et sa fonction de dessin.
ELEMS = []


def element(id, prof, genre, **kw):
    if 'box' in kw:
        kw['box'] = tuple(int(round(v)) for v in kw['box'])
    e = dict(id=id, prof=prof, genre=genre, fn=None, **kw)
    ELEMS.append(e)

    def deco(fn):
        e['fn'] = fn
        return fn
    return deco


# ---------------------------------------------------------------------------------------------------- le ciel
LUNE = (452, 392)            # vue sur tous les téléphones (le court montre le fond à partir de y = 351), à droite des pilules
ETOILES = [(36, 352, 1.0), (104, 410, 0.8), (176, 380, 1.1), (238, 344, 0.8), (268, 422, 0.9), (330, 378, 0.8),
           (376, 446, 1.0), (520, 452, 0.8), (556, 404, 1.1), (60, 470, 0.7), (400, 352, 0.8), (500, 526, 0.7),
           (150, 512, 0.7), (214, 470, 0.8)]


@element('ciel', -29.9, 'fixe')
def ciel(doc):
    out = [path('M-20 -20H610V840H-20Z', doc.lin(0, 0, 0, 800, CIEL))]
    # le couchant (le soleil est déjà passé sous l'horizon) : une lueur d'or basse, derrière le donjon
    out.append('<ellipse cx="300" cy="800" rx="400" ry="200" fill="%s"/>' % doc.rad(
        300, 800, 400, [(0, '#f0b464', 0.42), (0.5, '#d88a5a', 0.18), (1, '#b06a5e', 0)], ry=200))
    # quelques étoiles, petites et douces (aucun rayon)
    for x, y, r in ETOILES:
        out.append('<circle cx="%s" cy="%s" r="%s" fill="#f4ecdc" opacity="%g"/>' % (
            fm(x), fm(y), fm(r), 0.55 - 0.35 * max(0, (y - 340) / 200)))
    # la grosse lune pâle en haut à droite (la seule lumière)
    sx, sy = LUNE
    out.append('<circle cx="%d" cy="%d" r="120" fill="%s"/>' % (sx, sy, doc.rad(
        sx, sy, 120, [(0, '#f6ecd2', 0.30), (0.3, '#c8b4c4', 0.12), (1, '#8a7090', 0)])))
    out.append('<circle cx="%d" cy="%d" r="25" fill="%s"/>' % (sx, sy, doc.rad(
        sx + 7, sy - 7, 32, [(0, '#fffbee'), (0.6, '#f6ead0'), (1, '#dccab0')])))
    # ses mers, deux taches douces côté ombre
    out.append('<ellipse cx="%d" cy="%d" rx="7" ry="5.5" fill="#d6c6aa" opacity="0.55"/>' % (sx - 8, sy + 5))
    out.append('<ellipse cx="%d" cy="%d" rx="4" ry="3" fill="#d6c6aa" opacity="0.5"/>' % (sx + 4, sy + 11))
    out.append('<ellipse cx="%d" cy="%d" rx="3.5" ry="3" fill="#dccdb2" opacity="0.45"/>' % (sx - 3, sy - 9))
    return ''.join(out)


@element('nuages', -29.5, 'fixe')
def nuages(doc):
    out = []
    # A : le grand banc en haut à gauche (le haut des téléphones longs)
    a = lobes_shape(-30, 320, 330, [(292, 318, 18), (254, 300, 30), (206, 284, 38), (152, 274, 40), (96, 266, 44),
                                    (42, 270, 40), (-6, 282, 38), (-30, 300, 30)], sag=6)
    out.append(vol(doc, a, NUAGE, r=2.2, c=4))
    a2 = lobes_shape(-30, 250, 232, [(232, 222, 16), (196, 208, 26), (150, 196, 30), (100, 192, 32), (50, 196, 30),
                                     (4, 204, 28), (-30, 216, 20)], sag=4)
    out.append(vol(doc, a2, dict(NUAGE, base='#2c2c56', light='#363462', sh='#222248'), r=2, c=3.5))
    # B : en haut à droite ; C : un petit banc au-dessus de la lune
    b = lobes_shape(380, 620, 292, [(612, 280, 16), (578, 268, 22), (540, 262, 22), (500, 266, 20), (460, 272, 18),
                                    (414, 280, 14)], sag=3)
    out.append(vol(doc, b, NUAGE, r=2, c=3))
    c = lobes_shape(456, 620, 334, [(610, 326, 12), (578, 316, 16), (540, 314, 15), (500, 320, 13), (472, 326, 9)],
                    sag=2)
    out.append(vol(doc, c, NUAGE2, r=1.8, c=2.6))
    # E : un long nuage bas à gauche, au-dessus de la tour (doré dessous par le couchant)
    e = lobes_shape(56, 262, 488, [(252, 482, 8), (226, 474, 12), (190, 468, 15), (150, 470, 14), (112, 474, 12),
                                   (80, 480, 8)], sag=2)
    out.append(vol(doc, e, NUAGE3, r=1.8, c=2.6))
    out.append('<g clip-path="%s">%s</g>' % (doc.clip(e.d()), path(rectd(40, 476, 280, 492), doc.lin(
        0, 478, 0, 490, [(0, '#e0a070', 0), (1, '#e0a070', 0.45)]))))
    return ''.join(out)


# ---------------------------------------------------------------------------------------------------- le lointain
PAVILLON = (206, 551)


@element('lointain', -28.5, 'fixe')
def lointain(doc):
    out = []
    r1 = [(-20, 800), (-20, 652), (30, 640), (80, 620), (128, 592), (168, 568), (196, 554), (206, 551), (218, 556),
          (250, 582), (290, 612), (340, 636), (390, 640), (432, 624), (470, 606), (500, 598), (532, 604), (570, 620),
          (610, 630), (610, 800)]
    out.append(vol(doc, sm(r1, sharp=(0, 1, len(r1) - 2, len(r1) - 1), t=0.7), LOIN1, r=1.4, c=0))
    # le petit pavillon perché sur le pic, sa fenêtre allumée
    x, y = PAVILLON
    out.append(vol(doc, rpoly([(x - 6, y + 2), (x - 6, y - 8), (x + 6, y - 8), (x + 6, y + 2)], 0.6), LOIN2, r=0.8, c=1))
    s, _ = toit_forme(x, y - 14, 3, y - 9, 10, 2.4, 1.6)
    out.append(vol(doc, s, LOIN3, r=0.8, c=1))
    s2, _ = toit_forme(x, y - 20, 1.5, y - 15.5, 6.5, 1.8, 1.4)
    out.append(vol(doc, s2, LOIN3, r=0.8, c=1))
    out.append('<rect x="%s" y="%s" width="3" height="3.4" fill="#f4b464" opacity="0.85"/>' % (fm(x - 1.5), fm(y - 6)))
    out.append('<circle cx="%s" cy="%s" r="7" fill="%s"/>' % (fm(x), fm(y - 4.5), doc.rad(
        x, y - 4.5, 7, [(0, '#f4b464', 0.35), (1, '#f4b464', 0)])))
    r2 = [(-20, 800), (-20, 700), (50, 690), (110, 698), (170, 712), (240, 716), (310, 722), (380, 712), (440, 694),
          (500, 686), (560, 694), (610, 700), (610, 800)]
    out.append(vol(doc, sm(r2, sharp=(0, 1, len(r2) - 2, len(r2) - 1), t=0.7), LOIN2, r=1.4, c=0))
    return ''.join(out)


@element('brume', -27, 'fixe')
def brume(doc):
    # la brume dorée du couchant, au pied des montagnes
    return path('M-10 600H600V800H-10Z', doc.lin(0, 600, 0, 792, [(0, '#b07a78', 0), (0.6, '#c48a6e', 0.3),
                                                                  (1, '#d09468', 0.55)]))


# ---------------------------------------------------------------------------------------------------- le donjon
DX = 318                    # le milieu du donjon (le milieu de ce que montre le combat est x = 295)
SOUB = [(228, 782), (408, 782), (400, 748), (390, 712), (380, 676), (256, 676), (246, 712), (236, 748)]
ETAGES = [  # (x0, y0, x1, y1, poteaux, fenêtres (x), y des fenêtres, w, h)
    (266, 632, 370, 676, (266, 291, 345, 370), (279, 303, 333, 357), 653, 8, 13),
    (284, 576, 352, 610, (284, 352), (298, 318, 338), 591, 7, 11.5),
    (292, 526, 344, 560, (292, 344), (307, 329), 543, 7, 11),
]
TOITS = [  # (yt, ht, ye, he, lift, th)
    (608, 40, 625, 88, 9, 7),
    (558, 30, 573, 66, 8, 6),
    (499, 18, 521, 52, 9, 6),
]


def soubassement(doc):
    s = sm(SOUB, sharp=(0, 1, 4, 5), t=0.75)
    g = doc.lin(408, 676, 240, 782, [(0, PIERRE['light']), (0.5, PIERRE['base']), (1, PIERRE['sh'])])
    out = [vol(doc, s, PIERRE, grad=g, r=1.8, c=3.0, ink=INK, iw=1.0)]
    inner = []
    # de gros blocs, à peine marqués (des joints doux, décalés, pas une grille)
    joints = []
    for y, xs in ((700, (262, 300, 338, 372)), (726, (250, 286, 324, 364, 396)), (752, (244, 278, 318, 352, 390))):
        joints.append('M220 %d H420' % y)
        for x in xs:
            joints.append('M%d %d V%d' % (x, y - 24, y))
    jd = ' '.join(joints)
    inner.append('<path d="%s" fill="none" stroke="#fff4ea" stroke-width="1.1" opacity="0.07" '
                 'transform="translate(0.8 0.8)"/>' % jd)
    inner.append('<path d="%s" fill="none" stroke="#1e1830" stroke-width="1" opacity="0.22"/>' % jd)
    # la face droite (tournée vers la lune) un peu plus claire
    inner.append(path(sm([(352, 676), (382, 676), (392, 712), (402, 748), (410, 782), (372, 782), (362, 730)], t=0.8),
                      PIERRE['light'], 0.35))
    out.append('<g clip-path="%s">%s</g>' % (doc.clip(s.d()), ''.join(inner)))
    return ''.join(out)


def pignon(doc, cx, yb, hw, h):
    """Le petit pignon triangulaire posé sur le premier toit (le chidori), son fronton crème et un clou d'or."""
    s = sm([(cx - hw, yb), (cx - hw * 0.45, yb - h * 0.62), (cx, yb - h), (cx + hw * 0.45, yb - h * 0.62), (cx + hw, yb),
            (cx, yb + 2)], sharp=(0, 2, 4), t=0.7)
    out = [vol(doc, s, TUILE, r=1.2, c=1.8, ink=INK, iw=0.8)]
    f = sm([(cx - hw * 0.62, yb - 2), (cx, yb - h * 0.74), (cx + hw * 0.62, yb - 2)], sharp=(0, 1, 2), t=0.6)
    out.append(vol(doc, f, ENDUIT, r=0.8, c=1.2))
    out.append(path(rpoly([(cx, yb - h * 0.52), (cx + 2.6, yb - h * 0.34), (cx, yb - h * 0.16), (cx - 2.6, yb - h * 0.34)],
                          0.4), doc.lin(cx + 2, yb - h * 0.5, cx - 2, yb - h * 0.2, [(0, OR['light']), (1, OR['sh'])])))
    return ''.join(out)


def cornes_donjon(doc):
    out = []
    for sg in (-1, 1):
        x0 = DX + sg * 15
        s = corne((x0, 498), (x0 + sg * 8, 490), (x0 + sg * 15, 478), (x0 + sg * 9, 462), 5.2)
        out.append(vol(doc, s, IVOIRE, r=1.1, c=1.6, ink=INK, iw=0.8))
    return ''.join(out)


@element('donjon', -22, 'fixe')
def donjon(doc):
    out = [soubassement(doc)]
    # chaque étage puis son toit par-dessus (le toit d'en dessous passe devant le pied de l'étage du dessus)
    order = [('mur', 2), ('toit', 2), ('mur', 1), ('toit', 1), ('mur', 0), ('toit', 0)]
    for kind, k in order:
        if kind == 'mur':
            x0, y0, x1, y1, pot, fx, fy, fw, fh = ETAGES[k]
            out.append(mur(doc, x0, y0, x1, y1, pot))
            out.append(''.join(fenetre(doc, x, fy, fw, fh, 0.5) for x in fx))
        else:
            yt, ht, ye, he, lift, th = TOITS[k]
            out.append(toit(doc, DX, yt, ht, ye, he, lift, th))
            if k == 0:
                out.append(pignon(doc, DX, ye - 1, 19, 22))
            if k == 2:
                # le faîte : une poutre sombre, et les deux grandes cornes d'ivoire de Lenore
                out.append(vol(doc, rpoly([(DX - 21, yt + 2), (DX - 20, yt - 3), (DX + 20, yt - 3), (DX + 21, yt + 2)], 1.2),
                               TUILE, r=0.9, c=1.2, ink=INK, iw=0.8))
                out.append(cornes_donjon(doc))
    return ''.join(out)


def fenetres(k_etage):
    x0, y0, x1, y1, pot, fx, fy, fw, fh = ETAGES[k_etage]

    def fn(doc, ph):
        # la lueur des fenêtres respire doucement (chaque étage un peu décalé)
        k = 0.5 - 0.5 * math.cos(2 * math.pi * (ph + 0.3 * k_etage))
        return ''.join(fenetre(doc, x, fy, fw, fh, 0.25 + 0.75 * k) for x in fx)
    return fn


for _k in range(3):
    _e = ETAGES[_k]
    _fx, _fy, _fw, _fh = _e[5], _e[6], _e[7], _e[8]
    element('fenetres%d' % (_k + 1), -21.6, 'boucle',
            box=(min(_fx) - _fw * 1.3 - 1, _fy - _fh - 1, max(_fx) - min(_fx) + _fw * 2.6 + 2, _fh * 2 + 2),
            n=8, ms=600)(fenetres(_k))


@element('brume-donjon', -21.5, 'fixe')
def brume_donjon(doc):
    # un voile de brume au pied du donjon (il est plus loin que la tour et la muraille)
    return path('M-10 680H600V790H-10Z', doc.lin(0, 680, 0, 760, [(0, '#b88a80', 0), (1, '#c4927a', 0.28)]))


# ---------------------------------------------------------------------------------------------------- la tour de guet
TX = 146


def tour_brut(doc):
    out = []
    base = sm([(92, 782), (200, 782), (196, 748), (192, 712), (186, 680), (106, 680), (100, 712), (96, 748)],
              sharp=(0, 1, 4, 5), t=0.75)
    g = doc.lin(200, 680, 96, 782, [(0, PIERRE['light']), (0.5, PIERRE['base']), (1, PIERRE['sh'])])
    out.append(vol(doc, base, PIERRE, grad=g, r=1.8, c=3.0, ink=INK, iw=1.0))
    joints = []
    for y, xs in ((706, (124, 160)), (732, (112, 146, 178)), (758, (128, 166)))[:3]:
        joints.append('M80 %d H210' % y)
        for x in xs:
            joints.append('M%d %d V%d' % (x, y - 26, y))
    jd = ' '.join(joints)
    out.append('<g clip-path="%s"><path d="%s" fill="none" stroke="#fff4ea" stroke-width="1.1" opacity="0.07" '
               'transform="translate(0.8 0.8)"/><path d="%s" fill="none" stroke="#1e1830" stroke-width="1" '
               'opacity="0.22"/>%s</g>' % (doc.clip(base.d()), jd, jd, path(sm(
                   [(170, 680), (188, 680), (194, 720), (200, 782), (176, 782), (172, 730)], t=0.8), PIERRE['light'], 0.3)))
    # la salle de guet
    out.append(mur(doc, 110, 640, 182, 680, (110, 182)))
    # la plaque ronde de laque rouge au signe du clan (sur le mur)
    cx, cy = TX, 661
    out.append('<circle cx="%s" cy="%s" r="11" fill="%s" stroke="%s" stroke-width="1.6"/>' % (
        cx, cy, doc.rad(cx + 4, cy - 4, 14, [(0, LAQUE['light']), (0.6, LAQUE['base']), (1, LAQUE['sh'])]), INK))
    out.append('<circle cx="%s" cy="%s" r="9.2" fill="none" stroke="%s" stroke-width="1.4"/>' % (
        cx, cy, doc.lin(cx + 8, cy - 8, cx - 8, cy + 8, [(0, OR['light']), (1, OR['sh'])])))
    out.append(path(signe_forme(cx, cy - 2.4, 0.95), doc.lin(cx + 4, cy - 8, cx - 4, cy + 6,
                                                             [(0, OR['light']), (1, OR['base'])])))
    # le toit recourbé et ses deux petites cornes
    out.append(toit(doc, TX, 616, 22, 634, 62, 9, 6))
    out.append(vol(doc, rpoly([(TX - 24, 618), (TX - 23, 613), (TX + 23, 613), (TX + 24, 618)], 1), TUILE,
                   r=0.9, c=1.2, ink=INK, iw=0.8))
    for sg in (-1, 1):
        x0 = TX + sg * 18
        s = corne((x0, 615), (x0 + sg * 6, 609), (x0 + sg * 11, 600), (x0 + sg * 6, 590), 3.6)
        out.append(vol(doc, s, IVOIRE, r=0.9, c=1.2, ink=INK, iw=0.7))
    return ''.join(out)


@element('tour', -21, 'fixe')
def tour(doc):
    return tour_brut(doc)


# la guirlande de lanternes entre la tour et le donjon (fixe : elles luisent seulement)
GUIRLANDE = [(204, 644), (222, 660), (240, 668), (258, 670)]


@element('guirlande', -20.8, 'fixe')
def guirlande(doc):
    c = resample(catmull(GUIRLANDE, 8), 30)
    out = ['<path d="%s" fill="none" stroke="#2a1a2e" stroke-width="0.9" opacity="0.9"/>' % polyline_d(c)]
    for u in (0.28, 0.62, 0.92):
        x, y = c[round(u * 30)]
        out.append('<circle cx="%s" cy="%s" r="7" fill="%s"/>' % (fm(x), fm(y + 5), doc.rad(
            x, y + 5, 7, [(0, '#ffb45a', 0.4), (1, '#ffb45a', 0)])))
        out.append('<path d="M%s %sV%s" stroke="#2a1a2e" stroke-width="0.7"/>' % (fm(x), fm(y), fm(y + 2)))
        out.append(path(ellipse(x, y + 5, 2.6, 3.4), doc.rad(x + 1, y + 4, 4, [(0, PAPIER['hot']), (0.6, PAPIER['glow']),
                                                                                (1, PAPIER['mid'])])))
    return ''.join(out)


# ---------------------------------------------------------------------------------------------------- l'érable
def erable_feuillage():
    s = None
    for cx, cy, rx, ry in ((448, 662, 21, 17), (474, 648, 25, 21), (496, 666, 18, 15), (430, 680, 14, 11),
                           (466, 676, 20, 14), (492, 638, 14, 12), (452, 640, 15, 12), (486, 684, 13, 9)):
        e = ellipse(cx, cy, rx, ry)
        s = e if s is None else s + e
    return s


@element('erable', -20.5, 'fixe')
def erable(doc):
    out = []
    tronc = corne((472, 752), (470, 724), (462, 700), (454, 674), 4.6, n=16)
    out.append(vol(doc, tronc, BOIS, r=0.9, c=1.4, ink=INK, iw=0.8))
    for a, b, c_, d_, w in (((464, 708), (474, 698), (484, 686), (490, 672), 2.4),
                            ((460, 694), (450, 688), (440, 682), (432, 676), 2.0),
                            ((457, 682), (462, 670), (470, 660), (476, 652), 1.8)):
        out.append(vol(doc, corne(a, b, c_, d_, w, n=10), BOIS, r=0.6, c=0.8, ink=INK, iw=0.7))
    f = erable_feuillage()
    g = doc.lin(514, 626, 424, 694, [(0, ERABLE['light']), (0.5, ERABLE['base']), (1, ERABLE['sh'])])
    out.append(vol(doc, f, ERABLE, grad=g, r=1.8, c=2.8, ink=INK, iw=0.9))
    inner = []
    # des touffes plus claires côté lune, plus sombres dessous (de grandes masses, pas de feuilles une à une)
    for cx, cy, rx, ry, col, op in ((484, 640, 14, 9, ERABLE['rim'], 0.38), (462, 650, 11, 7, ERABLE['light'], 0.45),
                                    (500, 658, 9, 6, ERABLE['light'], 0.4), (446, 676, 16, 7, ERABLE['sh'], 0.4),
                                    (476, 684, 14, 5, ERABLE['sh'], 0.45)):
        inner.append(path(ellipse(cx, cy, rx, ry), col, op))
    out.append('<g clip-path="%s">%s</g>' % (doc.clip(f.d()), ''.join(inner)))
    return ''.join(out)


def feuille_image(doc, i, n):
    """Une feuille d'érable qui s'envole (une image de sa vie) : elle tourne, et s'efface à la fin."""
    t = i / (n - 1)
    op = min(1, 0.3 + 3 * t) if t < 0.3 else (1 - (t - 0.3) / 0.7) ** 0.8
    s = star(7, 7, 4.6, 2.2, n=5, rot=-90 + 52 * i, rr=0.8)
    col = mix(ERABLE['light'], ERABLE['rim'], 0.3 + 0.4 * math.sin(i * 1.3) ** 2)
    return '<g opacity="%g">%s</g>' % (op * 0.95, path(s, col)) if op > 0.02 else ''


element('feuilles', -19.6, 'particules', taille=(14, 14), images=8, dessin=feuille_image, zone=(436, 640, 504, 686),
        nombre=4, vie=(4200, 6000), vx=(-13, -6), vy=(5, 11), ondule=(4, 2400))


# ---------------------------------------------------------------------------------------------------- la muraille
GX = 300                      # la porte, au milieu de ce que montre le combat (entre les deux équipes)
MUR_Y = 744                   # le dessus du chaperon de tuiles


@element('muraille', -18, 'fixe')
def muraille(doc):
    out = []
    body = rectd(-10, MUR_Y + 6, 600, P0)
    out.append(path(body, doc.lin(0, MUR_Y + 6, 0, P0, [(0, MUR['light']), (0.4, MUR['base']), (1, MUR['sh'])])))
    # de grands blocs à peine marqués (une rangée de joints, décalés)
    joints = ['M-10 774 H600']
    x, i = -6, 0
    while x < 600:
        joints.append('M%s %d V774' % (fm(x), MUR_Y + 8))
        joints.append('M%s 774 V%d' % (fm(x + 26 + 6 * math.sin(i)), P0))
        x += 54 + 10 * math.sin(i * 2.3)
        i += 1
    jd = ' '.join(joints)
    out.append('<path d="%s" fill="none" stroke="#fff4ea" stroke-width="1.1" opacity="0.06" '
               'transform="translate(0.8 0.8)"/>' % jd)
    out.append('<path d="%s" fill="none" stroke="#1a1428" stroke-width="1" opacity="0.2"/>' % jd)
    # la lueur du couchant sur le haut du mur, l'ombre au pied
    out.append(path(rectd(-10, P0 - 10, 600, P0), doc.lin(0, P0 - 10, 0, P0, [(0, '#1a1428', 0), (1, '#1a1428', 0.35)])))
    # le chaperon de tuiles : une longue arête, claire dessus, l'ombre dessous sur le mur
    out.append(path(rectd(-10, MUR_Y + 6, 600, MUR_Y + 12), doc.lin(0, MUR_Y + 6, 0, MUR_Y + 12, [
        (0, '#1a1428', 0.5), (1, '#1a1428', 0)])))
    cap = rpoly([(-12, MUR_Y + 7), (-12, MUR_Y + 1), (-4, MUR_Y - 1), (594, MUR_Y - 1), (602, MUR_Y + 1),
                 (602, MUR_Y + 7)], 1.5)
    out.append(vol(doc, cap, TUILE, grad=doc.lin(0, MUR_Y - 1, 0, MUR_Y + 7, [
        (0, TUILE['light']), (0.5, TUILE['base']), (1, TUILE['sh'])]), r=1.2, c=1.4, ink=INK, iw=0.9))
    out.append(porte(doc))
    return ''.join(out)


def porte(doc):
    """La porte de la muraille : deux piliers de laque rouge, les battants ouverts cloutés d'or, le passage sombre
    (des marches qui montent vers le donjon), et son petit toit recourbé."""
    out = []
    x0, x1, yt = GX - 14, GX + 14, 718
    # le passage
    out.append(path(rectd(x0, yt, x1, P0), doc.lin(0, yt, 0, P0, [(0, '#140e20'), (0.6, '#2a1a2a'), (1, '#4a2c30')])))
    for k, y in enumerate((784, 792)):
        out.append(path(rectd(x0, y, x1, y + 2.2), '#8a6a62', 0.3 + 0.12 * k))
    # les battants ouverts, rabattus contre les piliers (vus de biais : étroits)
    for sg in (-1, 1):
        xa, xb = (x0, x0 + 4.5) if sg < 0 else (x1 - 4.5, x1)
        out.append(path(rpoly([(xa, yt + 3), (xb, yt + 3), (xb, P0), (xa, P0)], 0.3),
                        doc.lin(0, yt, 0, P0, [(0, LAQUE['sh']), (1, LAQUE['base'])])))
        for y in (734, 756, 778):
            out.append('<circle cx="%s" cy="%s" r="1" fill="%s"/>' % (fm((xa + xb) / 2), y, OR['light']))
    # les piliers
    for xc in (x0 - 3.6, x1 + 3.6):
        p = rpoly([(xc - 3.6, yt - 2), (xc + 3.6, yt - 2), (xc + 3.6, P0 + 1), (xc - 3.6, P0 + 1)], 0.6)
        out.append(vol(doc, p, LAQUE, grad=doc.lin(xc + 3.6, 0, xc - 3.6, 0, [(0, LAQUE['light']), (1, LAQUE['sh'])]),
                       r=0.9, c=1.2, ink=INK, iw=0.8))
        out.append(vol(doc, rpoly([(xc - 5, P0 + 2), (xc - 4.6, P0 - 5), (xc + 4.6, P0 - 5), (xc + 5, P0 + 2)], 0.8),
                       MUR, r=0.7, c=0.9, ink=INK, iw=0.7))
    # le linteau, et le petit toit
    out.append(vol(doc, rpoly([(x0 - 8, yt + 1), (x0 - 8, yt - 4), (x1 + 8, yt - 4), (x1 + 8, yt + 1)], 0.5), LAQUE,
                   r=0.7, c=0.9, ink=INK, iw=0.7))
    out.append(toit(doc, GX, 700, 14, 712, 38, 6, 4))
    out.append(vol(doc, rpoly([(GX - 15, 702), (GX - 14, 698), (GX + 14, 698), (GX + 15, 702)], 0.8), TUILE,
                   r=0.7, c=0.9, ink=INK, iw=0.7))
    for sg in (-1, 1):
        s = corne((GX + sg * 12, 700), (GX + sg * 15, 696), (GX + sg * 19, 690), (GX + sg * 16, 684), 2.4, n=10)
        out.append(vol(doc, s, IVOIRE, r=0.6, c=0.8, ink=INK, iw=0.6))
    return ''.join(out)


# ---------------------------------------------------------------------------------------------------- les lanternes
def lanterne(doc, x, yh, ph, k=0, taille=1.0, corde=8):
    """Une lanterne de papier pendue en (x, yh) : elle se balance doucement (ph : la phase de la boucle)."""
    a = 5.0 * math.sin(2 * math.pi * ph + k)
    s = taille
    yb = yh + corde
    body = []
    body.append('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fm(x), fm(yb + 8 * s), fm(15 * s), doc.rad(
        x, yb + 8 * s, 15 * s, [(0, '#ffc060', 0.38), (0.5, '#ffa040', 0.14), (1, '#ff9030', 0)])))
    body.append('<path d="M%s %sV%s" stroke="#2a1a2e" stroke-width="0.8"/>' % (fm(x), fm(yh), fm(yb)))
    body.append(vol(doc, rpoly([(x - 3 * s, yb), (x + 3 * s, yb), (x + 3 * s, yb + 1.8 * s), (x - 3 * s, yb + 1.8 * s)],
                               0.4), FER, r=0.5, c=0.6, ink=INK, iw=0.6))
    corps = ellipse(x, yb + 8 * s, 5.4 * s, 6.6 * s)
    body.append('<path d="%s" fill="%s" stroke="%s" stroke-width="1.2"/>' % (corps.d(), doc.rad(
        x + 1.6 * s, yb + 6.6 * s, 7.4 * s, [(0, PAPIER['hot']), (0.45, PAPIER['glow']), (0.85, PAPIER['mid']),
                                             (1, PAPIER['deep'])], ry=8.6 * s), INK))
    body.append(vol(doc, rpoly([(x - 3 * s, yb + 14.2 * s), (x + 3 * s, yb + 14.2 * s), (x + 3 * s, yb + 16 * s),
                                (x - 3 * s, yb + 16 * s)], 0.4), FER, r=0.5, c=0.6, ink=INK, iw=0.6))
    body.append(path(ribbon([(x, yb + 16 * s), (x + 0.3, yb + 18.5 * s), (x + 0.6, yb + 21 * s)], [1.2, 0.9, 0.2]),
                     LAQUE['base']))
    return '<g transform="rotate(%s %s %s)">%s</g>' % (fm(a), fm(x), fm(yh), ''.join(body))


LANTERNES = [  # id, x, crochet, déphasage, taille, corde
    ('lanterne-tour1', TX - 52, 636, 0.0, 1.0, 7),
    ('lanterne-tour2', TX + 52, 636, 1.9, 1.0, 7),
    ('lanterne-porte', GX, 718, 3.6, 0.9, 6),
]


def lanterne_fn(x, yh, k, s, corde):
    def fn(doc, ph):
        return lanterne(doc, x, yh, ph, k, s, corde)
    return fn


for _id, _x, _yh, _k, _s, _c in LANTERNES:
    element(_id, -17.6, 'boucle', box=(_x - 17 * _s, _yh - 2, 34 * _s, 34 * _s + _c - 2), n=12, ms=200)(
        lanterne_fn(_x, _yh, _k, _s, _c))


# ---------------------------------------------------------------------------------------------------- les bannières
MATS = [(218, MUR_Y), (418, MUR_Y)]
MAT_H = 54


def mat(doc, x, y):
    m = dict(base='#3a3446', light='#544c60', rim='#8a7e92', sh='#262234')
    out = [vol(doc, rpoly([(x - 1.4, y + 1), (x - 1.4, y - MAT_H), (x + 1.4, y - MAT_H), (x + 1.4, y + 1)], 0.6),
               m, r=0.7, c=0.8, ink=INK, iw=0.7)]
    out.append(vol(doc, rpoly([(x - 12, y - MAT_H + 2), (x + 12, y - MAT_H + 2), (x + 12, y - MAT_H + 5),
                               (x - 12, y - MAT_H + 5)], 1.2), m, r=0.7, c=0.8, ink=INK, iw=0.7))
    out.append('<circle cx="%s" cy="%s" r="2.6" fill="%s" stroke="%s" stroke-width="1.2"/>' % (
        x, y - MAT_H - 1, doc.rad(x + 1, y - MAT_H - 2, 3, [(0, OR['hot']), (1, OR['base'])]), INK))
    out.append(vol(doc, rpoly([(x - 5, y + 2), (x - 4, y - 3), (x + 4, y - 3.5), (x + 5, y + 2)], 1), MUR,
                   r=0.8, c=1.0, ink=INK, iw=0.8))
    return ''.join(out)


def banniere(k):
    x, y = MATS[k]
    top = y - MAT_H + 5

    def fn(doc, ph):
        # la toile pend sous la traverse ; elle ondule doucement (plus en bas qu'en haut), le vent vient de la droite
        L, w_ = 36, 21
        a = 2 * math.pi * ph

        def P(u, v):          # u : −1..1 en travers, v : 0..1 en descendant
            sway = v ** 1.5 * (2.4 * math.sin(a + v * 2.2 + k * 2) - 1.2)
            return (x + u * w_ / 2 * (1 - 0.08 * v) + sway, top + v * L + 0.8 * math.sin(a + u * 1.5 + k) * v)
        pts = [P(-1, 0), P(1, 0)]
        for v in (0.33, 0.66, 0.92):
            pts.append(P(1, v))
        pts += [P(1, 1.04), P(0, 0.86), P(-1, 1.04)]
        for v in (0.92, 0.66, 0.33):
            pts.append(P(-1, v))
        s = sm(pts, sharp=(0, 1, 5, 6, 7), t=0.6)
        out = [mat(doc, x, y), vol(doc, s, LAQUE, r=1.3, c=2.0, ink=INK, iw=0.9)]
        sx, sy = P(0, 0.42)
        out.append(path(signe_forme(sx, sy - 1, 1.25), OR['base']))
        return ''.join(out)
    return fn


for _k in range(2):
    _x, _y = MATS[_k]
    element('banniere%d' % (_k + 1), -17, 'boucle', box=(_x - 20, _y - MAT_H - 5, 40, MAT_H + 10), n=12,
            ms=200)(banniere(_k))


# ---------------------------------------------------------------------------------------------------- les braseros
BRASEROS = [(262, P0 + 6), (338, P0 + 6)]


def brasero_socle(doc, x, y):
    out = [vol(doc, rpoly([(x - 9, y), (x - 8, y - 9), (x + 8, y - 9), (x + 9, y)], 1), MUR, r=1.0, c=1.4, ink=INK, iw=0.9)]
    out.append(vol(doc, rpoly([(x - 2.2, y - 9), (x - 2.2, y - 19), (x + 2.2, y - 19), (x + 2.2, y - 9)], 0.4), FER,
                   r=0.6, c=0.8, ink=INK, iw=0.7))
    out.append(vol(doc, rpoly([(x - 12, y - 30), (x + 12, y - 30), (x + 7, y - 19), (x - 7, y - 19)], 1.2), FER,
                   r=1.0, c=1.4, ink=INK, iw=0.9))
    out.append(path(rpoly([(x - 10.6, y - 27), (x + 10.6, y - 27), (x + 10, y - 25.6), (x - 10, y - 25.6)], 0.3),
                    OR['base'], 0.85))
    return ''.join(out)


@element('braseros', -16.5, 'fixe')
def braseros(doc):
    return ''.join(brasero_socle(doc, x, y) for x, y in BRASEROS)


def flamme(k):
    x, y = BRASEROS[k]
    yb = y - 30

    def fn(doc, ph):
        a = 2 * math.pi * ph
        out = ['<circle cx="%s" cy="%s" r="16" fill="%s"/>' % (fm(x), fm(yb - 9), doc.rad(
            x, yb - 9, 16, [(0, '#ffb050', 0.32 + 0.06 * math.sin(a * 2 + k)), (1, '#ff8a30', 0)]))]
        # trois langues de feu qui dansent (chaque bout fait un tour entier par boucle : sans couture)
        for j, (dx, h, w, col, sp) in enumerate(((-4.5, 13, 4.2, FEU['deep'], 1), (4.2, 15, 4.4, FEU['deep'], 2),
                                                 (0, 22, 6.4, FEU['mid'], 1), (0.4, 14, 3.8, FEU['glow'], 2),
                                                 (0.2, 7.5, 2.2, FEU['hot'], 1))):
            hh = h * (1 + 0.14 * math.sin(a * sp + j * 1.7 + k))
            sw = 2.2 * math.sin(a * sp + j * 2.1 + k * 0.7)
            xb = x + dx
            pts = [(xb - w, yb + 1), (xb - w * 0.8, yb - hh * 0.35), (xb - w * 0.3 + sw * 0.4, yb - hh * 0.7),
                   (xb + sw, yb - hh), (xb + w * 0.4 + sw * 0.4, yb - hh * 0.62), (xb + w * 0.85, yb - hh * 0.3),
                   (xb + w, yb + 1)]
            out.append(path(sm(pts, sharp=(0, 3, 6), t=0.85), col, 0.95))
        # les braises au bord du bol
        out.append(path(rpoly([(x - 10, yb + 1.5), (x - 9, yb - 1.4), (x + 9, yb - 1.6), (x + 10, yb + 1.5)], 1),
                        doc.lin(x - 10, 0, x + 10, 0, [(0, FEU['deep']), (0.5, FEU['glow']), (1, FEU['mid'])])))
        return ''.join(out)
    return fn


for _k in range(2):
    _x, _y = BRASEROS[_k]
    element('flamme%d' % (_k + 1), -16, 'boucle', box=(_x - 17, _y - 64, 34, 36), n=8, ms=120)(flamme(_k))


def etincelle_image(doc, i, n):
    t = i / (n - 1)
    r = 1.3 - 0.6 * t
    op = 1 - 0.8 * t
    return ('<circle cx="6" cy="6" r="5" fill="%s"/><circle cx="6" cy="6" r="%s" fill="%s"/>' % (
        doc.rad(6, 6, 5, [(0, '#ffa040', 0.5 * op), (1, '#ff8030', 0)]), fm(r), mix('#fff0b0', '#ffb060', t)))


for _k in range(2):
    _x, _y = BRASEROS[_k]
    element('etincelles%d' % (_k + 1), -15.9, 'particules', taille=(12, 12), images=4, dessin=etincelle_image,
            zone=(_x - 5, _y - 50, _x + 5, _y - 44), nombre=2, vie=(1500, 2300), vx=(-5, 4), vy=(-17, -10),
            ondule=(2, 1600))


# ---------------------------------------------------------------------------------------------------- la cour
def sol_x(g, y):
    """Le dallage en perspective : la coordonnée au sol g → x à l'écran (les joints filent vers le centre)."""
    k = (y - 600) / (P1 - 600)
    return 295 + g * k


@element('arene', -15.5, 'fixe')
def arene(doc):
    out = []
    # la cour : un rectangle d'un bord à l'autre, une seule valeur moyenne qui s'éclaire à peine vers l'avant et vers
    # la droite (la lune)
    out.append(path(rectd(-10, P0, 600, P1), doc.lin(0, P0, 0, P1, [(0, SOL['back']), (1, SOL['front'])])))
    out.append(path(rectd(-10, P0, 600, P1), doc.lin(0, 0, 590, 0, [(0, '#1a1630', 0.06), (1, '#f4ecff', 0.04)])))
    rows = [P0, 824, 852, 886, 928, 980, P1]
    joints = []
    for i in range(len(rows) - 1):
        ya, yb = rows[i], rows[i + 1]
        if i > 0:
            joints.append('M-10 %s H600' % fm(ya))
        step = 150
        off = (i % 2) * step / 2 + (i * 37) % 40
        g = -900 + off
        while g < 900:
            xa, xb = sol_x(g, ya), sol_x(g, yb)
            if -10 < min(xa, xb) and max(xa, xb) < 600:
                joints.append('M%s %s L%s %s' % (fm(xa), fm(ya + 1), fm(xb), fm(yb - 1)))
            g += step + 20 * math.sin(i * 3.1 + g)
    jd = ' '.join(joints)
    out.append('<path d="%s" fill="none" stroke="#f6f0ff" stroke-width="1.2" opacity="0.05" '
               'transform="translate(0.8 0.8)"/>' % jd)
    out.append('<path d="%s" fill="none" stroke="#1c1830" stroke-width="1" opacity="0.12"/>' % jd)
    for (g0, i, col, op) in ((-220, 1, '#f6f0ff', 0.035), (60, 3, '#1c1830', 0.04), (300, 2, '#f6f0ff', 0.03),
                             (-90, 4, '#1c1830', 0.035), (180, 5, '#f6f0ff', 0.03)):
        ya, yb = rows[i] + 1, rows[i + 1] - 1
        pts = [(sol_x(g0, ya), ya), (sol_x(g0 + 140, ya), ya), (sol_x(g0 + 140, yb), yb), (sol_x(g0, yb), yb)]
        out.append(path(rpoly(pts, 2), col, op))
    # le pied de la muraille : un fil d'ombre, l'ombre douce de la muraille sur le fond de la cour
    out.append(path(rectd(-10, P0, 600, P0 + 1.4), '#221c32', 0.8))
    out.append(path(rectd(-10, P0, 600, P0 + 20), doc.lin(0, P0, 0, P0 + 20, [(0, '#221c32', 0.14),
                                                                              (1, '#221c32', 0)])))
    # l'arête avant éclairée, puis le flanc de la terrasse
    out.append(path(rectd(-10, P1, 600, 1066), doc.lin(0, P1, 0, 1066, [(0, '#463e56'), (1, '#34304a')])))
    out.append(path(rectd(-10, P1 - 1, 600, P1 + 1.6), '#a49cb0', 0.85))
    for g in range(-600, 700, 160):
        x = sol_x(g, P1)
        out.append(path(rpoly([(x - 0.6, P1 + 2), (x + 0.6, P1 + 2), (x + 0.6, 1064), (x - 0.6, 1064)], 0.3),
                        '#1c1830', 0.35))
    return ''.join(out)


@element('douves', -15.4, 'fixe')
def douves(doc):
    """Sous la terrasse : les douves (en combat, sous les cartes des héros, y > 985) : simples et sombres, à peine
    dorées en haut par le reflet du couchant ; aucun détail, aucune animation."""
    out = [path(rectd(-10, 1064, 600, 1104), doc.lin(0, 1064, 0, 1100, [(0, '#4a3448'), (0.25, '#2a2440'),
                                                                     (1, '#1a1830')]))]
    out.append(path(rectd(-10, 1063, 600, 1067), '#120f22', 0.6))
    return ''.join(out)


def balustrade(doc, x0, x1, posts):
    out = []
    for y0, y1 in ((1014, 1018.5), (1030, 1033.5)):
        out.append(vol(doc, rpoly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], 1), LAQUE, r=0.8, c=1.0, ink=INK, iw=0.9))
    for x in posts:
        out.append(vol(doc, rpoly([(x - 3.2, 1006), (x + 3.2, 1006), (x + 3.4, 1052), (x - 3.4, 1052)], 0.8), LAQUE,
                       grad=doc.lin(x + 3, 0, x - 3, 0, [(0, LAQUE['light']), (1, LAQUE['sh'])]), r=0.9, c=1.2,
                       ink=INK, iw=0.9))
        out.append(vol(doc, rpoly([(x - 4.6, 1008), (x - 4.2, 1004), (x + 4.2, 1004), (x + 4.6, 1008)], 0.8), OR,
                       r=0.6, c=0.8, ink=INK, iw=0.8))
        out.append('<circle cx="%s" cy="%s" r="4" fill="%s" stroke="%s" stroke-width="1.6"/>' % (
            fm(x), 1000, doc.rad(x + 1.4, 998.6, 5, [(0, OR['hot']), (0.5, OR['light']), (1, OR['sh'])]), INK))
    return ''.join(out)


@element('balustrade-gauche', 1300, 'morceau', box=(0, 992, 66, 64))
def balustrade_g(doc):
    return balustrade(doc, -12, 52, (12, 50))


@element('balustrade-droite', 1300, 'morceau', box=(524, 992, 66, 64))
def balustrade_d(doc):
    return balustrade(doc, 538, 602, (540, 578))


# ---------------------------------------------------------------------------------------------------- les corbeaux
# La touche vivante du ciel (comme les dragons de Kael) : trois corbeaux lointains, silhouettes dans la couleur de la
# brume du crépuscule ; plus loin = plus petit, plus pâle et plus lent. Le plus proche passe devant la lune ; le plus
# loin passe derrière le donjon (un « morceau » remet le dernier étage devant lui). Ils ne descendent jamais vers la
# cour. Chacun est une particule seule : il naît caché (hors de l'image, ou derrière le donjon) et finit caché ; ses
# ailes battent (12 images en boucle).
CORBEAUX = [
    # id, y, échelle, x de départ, x d'arrivée, montée (px/s), couleur, opacité, profondeur
    ('corbeau1', 382, 0.95, -40, 640, -0.4, '#1c1838', 0.9, -29.75),      # le plus proche : devant la lune
    ('corbeau2', 428, 0.62, 640, -40, 0.0, '#2c284c', 0.78, -29.74),      # de droite à gauche, au-dessus des cornes
    ('corbeau3', 544, 0.38, 622, DX, 0.0, '#3e3660', 0.66, -29.73),       # le plus loin : finit derrière le donjon
]
CORBEAU_N, CORBEAU_MS = 12, 80                   # un battement d'ailes = 0,96 s
CORBEAU_BOITE = (-27, -28, 46, 46)


def aile_corbeau(ph, near=True):
    """Une aile de corbeau (repère local, tête à droite) : le bord d'attaque, quatre rémiges écartées en doigts au bout,
    le bord de fuite. ph : le battement (0 = en haut, 0,5 = en bas)."""
    f = 0.15 + 0.85 * math.cos(2 * math.pi * ph)       # 1 : en haut, −0,7 : en bas
    sx = 0.85 + 0.15 * abs(f)
    S = (2, -1) if near else (5, -2)
    k = 1 if near else 0.86

    def P(dx, dy):
        return (S[0] + dx * sx * k, S[1] + dy * f * k)
    loc = [(0, 0), (1, -7), (0, -14), (-2, -20), (-4, -25.5), (-5.6, -22.8), (-7.8, -26), (-9, -22.6), (-11.4, -25),
           (-12.2, -21), (-14.6, -22.4), (-14.6, -17.6), (-16.8, -17.2), (-15.4, -11), (-13, -5), (-9, -1.2),
           (-4, 0.4)]
    return [P(x, y) for x, y in loc]


def corbeau_corps(ph):
    b = -0.8 * math.sin(2 * math.pi * ph)
    corps = sm([(-13, -0.2 + b * 0.3), (-6, -3 + b), (2, -3.6 + b), (8, -3.2 + b), (11.5, -4.6 + b), (14.8, -3.4 + b),
                (19, -2.4 + b), (14.6, -1.4 + b), (11, 0.6 + b), (4, 2.2 + b), (-4, 2.4 + b), (-12, 1.6 + b)],
               sharp=(6,), t=0.85)
    queue = sm([(-11, -0.8 + b * 0.3), (-20, -3.2), (-22.4, -0.6), (-21.6, 2.6), (-11, 1.6 + b * 0.3)],
               sharp=(1, 3), t=0.7)
    return [corps, queue]


def corbeau_image(id_):
    _, y, k, x0, x1, vy, col, op, _ = next(d for d in CORBEAUX if d[0] == id_)
    sg = 1 if x1 > x0 else -1
    bx, by, bw, bh = CORBEAU_BOITE
    w, h = bw * k + 4, bh * k + 4

    def fn(doc, i, n):
        ph = i / n
        loin = mix(col, '#5a4a78', 0.3)                   # l'aile lointaine, plus dans la brume
        ox = w / 2 - (bx + bw / 2) * k * sg
        oy = h / 2 - (by + bh / 2) * k
        out = ['<g transform="translate(%s %s) scale(%s %s)">' % (fm(ox), fm(oy), fm(k * sg), fm(k))]
        out.append(path(sm(aile_corbeau(ph, False), sharp=(0, 4, 6, 8, 10, 12), t=0.6), loin))
        out.extend(path(p_, col) for p_ in corbeau_corps(ph))
        out.append(path(sm(aile_corbeau(ph, True), sharp=(0, 4, 6, 8, 10, 12), t=0.6), col))
        out.append('</g>')
        return '<g opacity="%g">%s</g>' % (op, ''.join(out))
    return fn, (round(w), round(h))


for _d in CORBEAUX:
    _fn, _t = corbeau_image(_d[0])
    _vx = (_d[4] - _d[3]) * 1000 / PERIODE
    element(_d[0], _d[8], 'particules', taille=_t, images=CORBEAU_N, ms=CORBEAU_MS, dessin=_fn,
            zone=(_d[3], _d[1], _d[3], _d[1]), nombre=1, vie=(PERIODE, PERIODE), vx=(_vx, _vx), vy=(_d[5], _d[5]),
            ondule=(0, PERIODE))


def devant(ids, box):
    """Un morceau du paysage remis devant les corbeaux : ces éléments seuls (sans le ciel), coupés à la boîte."""
    def fn(doc):
        x, y, w, h = box
        body = ''.join(e['fn'](doc) for e in sorted(ELEMS, key=lambda e: e['prof']) if e['id'] in ids)
        return '<g clip-path="%s">%s</g>' % (doc.clip(rectd(x, y, x + w, y + h)), body)
    return fn


DEVANT_DONJON = (286, 522, 64, 42)
element('devant-donjon', -21.9, 'morceau', box=DEVANT_DONJON)(devant(('donjon',), DEVANT_DONJON))



# ================================================================================================ LE TEMPS
def rng(seed):
    """Le hasard à graine du jeu (src/game/bg/fond-px.ts), recopié à l'identique : mêmes particules qu'en combat."""
    M = 0xffffffff
    a = 991
    for ch in seed:
        a = ((a * 31) + ord(ch)) & M

    def imul(x, y):
        return ((x & M) * (y & M)) & M

    def r(lo=0.0, hi=1.0):
        nonlocal a
        a = (a + 0x6d2b79f5) & M
        t = a
        t = imul(t ^ (t >> 15), t | 1)
        t = (t ^ ((t + imul(t ^ (t >> 7), t | 61)) & M)) & M
        return lo + (((t ^ (t >> 14)) & M) / 4294967296) * (hi - lo)
    return r


_PART_CACHE = {}


def particules_a(e, t):
    """Où sont les particules à l'instant t (la règle du jeu : chaque place renaît au même endroit à chaque période ;
    images jouées sur la vie, ou en boucle toutes les `ms`)."""
    if e['id'] not in _PART_CACHE:
        r = rng(CLAN + '-' + e['id'])
        P = PERIODE
        life0 = (e['vie'][0] + e['vie'][1]) / 2
        slots = max(e['nombre'], math.ceil(e['nombre'] * P / life0))
        lst = []
        for s in range(slots):
            life = min(P, r(*e['vie']))
            born = (s + r()) * P / slots
            x0, y0 = r(e['zone'][0], e['zone'][2]), r(e['zone'][1], e['zone'][3])
            vx, vy = r(*e['vx']), r(*e['vy'])
            ph = r(0, 6.283)
            lst.append((life, born, x0, y0, vx, vy, ph))
        _PART_CACHE[e['id']] = lst
    out = []
    amp, per = e['ondule']
    ms = e.get('ms', 0)
    for life, born, x0, y0, vx, vy, ph in _PART_CACHE[e['id']]:
        age = ((t - born) % PERIODE + PERIODE) % PERIODE
        if age >= life:
            continue
        s = age / 1000
        x = x0 + vx * s + amp * math.sin(ph + 2 * math.pi * age / max(1, per))
        y = y0 + vy * s
        i = int((age + ph * 100) // ms) % e['images'] if ms else min(e['images'] - 1, int(age / life * e['images']))
        out.append((x, y, i))
    return out


def phase(e, t, override=None):
    if override and e['id'] in override:
        return override[e['id']]
    if e['genre'] == 'boucle':
        return (int(t // e['ms']) % e['n']) / e['n']
    return 0


def scene(t=0, box=(0, 0, W, H), particules=True, base=False):
    """Tout le fond à l'instant t, en SVG (sans les personnages). base : seulement l'image fixe du jeu (ce qui ne
    bouge pas : les boucles, défilés et particules sont des calques posés par-dessus)."""
    doc = Doc()
    body = []
    for e in sorted(ELEMS, key=lambda e: e['prof']):
        g = e['genre']
        if base and g not in ('fixe', 'morceau'):
            continue
        if g in ('fixe', 'morceau'):
            body.append(e['fn'](doc))
        elif g == 'boucle':
            body.append(e['fn'](doc, phase(e, t)))
        elif g == 'defile':
            tw = e['tuile'][0]
            off = (t / 1000 * e['vx']) % tw
            body.append(e['dessin'](doc, off))
        elif g == 'particules' and particules:
            ids = []
            for i in range(e['images']):
                sid = doc.uid('s')
                doc.defs.append('<g id="%s">%s</g>' % (sid, e['dessin'](doc, i, e['images'])))
                ids.append(sid)
            w_, h_ = e['taille']
            for x, y, i in particules_a(e, t):
                body.append('<use href="#%s" x="%s" y="%s"/>' % (ids[i], fm(x - w_ / 2), fm(y - h_ / 2)))
    return doc.svg(''.join(body), box)


# ================================================================================================ LE RENDU
def rendre(jobs, w, h):
    """jobs = [(svg, sortie.png)] tous rendus à w × h par le moteur des héros (Chromium, rendu-lot.cjs)."""
    os.makedirs(os.path.join(TMP, 'svg'), exist_ok=True)
    frames = []
    for k, (svg, out) in enumerate(jobs):
        p = os.path.join(TMP, 'svg', '%d-%d-%d.svg' % (w, h, k))
        open(p, 'w').write(svg)
        frames.append([p, out])
    jp = os.path.join(TMP, 'svg', 'job-%d-%d.json' % (w, h))
    json.dump({'w': w, 'h': h, 'frames': frames}, open(jp, 'w'))
    subprocess.run(['node', RENDU, jp], check=True)
    return [f[1] for f in frames]


# ------------------------------------------------------------------------------------------------ les personnages
# Côté héros : Aurelle (angels-10) au fond, Kael (assassins-2) au milieu, Lenore (knights-9, la générale du clan)
# devant ; en face, les trois monstres du clan de Lenore (diablotin, oni-brute, sorcier-oni), retournés vers la gauche.
PERSOS = [('angels-10', 'heros', 0), ('assassins-2', 'heros', 2), ('knights-9', 'heros', 4),
          ('mon-lenore-rapide', 'ennemis', 0), ('mon-lenore-costaud', 'ennemis', 2), ('mon-lenore-sorts', 'ennemis', 4)]


def vecto_table():
    import re
    s = open(os.path.join(ROOT, 'src', 'game', 'vecto.ts')).read()
    out = {}
    for m in re.finditer(r"'([\w-]+)': \[([\d.]+), ([\d.]+), ([\d.]+), ([\d.]+)\]", s):
        out[m.group(1)] = tuple(float(m.group(i)) for i in range(2, 6))
    return out


def poser(im, s, x0, y0, persos=PERSOS):
    """Pose les personnages vectoriels (public/art/vecto/<id>.webp) comme le combat : places de place_combat(),
    taille K_PERSO (un pixel de mesure = 0,68 pixel du fond), l'ombre du jeu (ovale noir à 30 %). L'image `im` est le
    fond rendu à l'échelle s (pixels d'image par pixel du fond), son coin haut-gauche en (x0, y0) du fond."""
    tab = vecto_table()
    acts = sorted([(place_combat(side, slot)[1], cid, side, slot) for cid, side, slot in persos])
    ss = 4
    sh = Image.new('L', (im.width * ss, im.height * ss), 0)
    d = ImageDraw.Draw(sh)
    for fy, cid, side, slot in acts:
        fx, fy = place_combat(side, slot)
        w_ = min(160, tab[cid][0] * 0.6 * 1.22 * 0.95 * 1.1) / UC
        hh = 10 / UC
        d.ellipse(((fx - x0 - w_ / 2) * s * ss, (fy - y0 - hh) * s * ss, (fx - x0 + w_ / 2) * s * ss,
                   (fy - y0 + hh) * s * ss), fill=77)
    sh = sh.resize(im.size, Image.LANCZOS)
    black = Image.new('RGBA', im.size, (0, 0, 0, 255))
    black.putalpha(sh)
    im.alpha_composite(black)
    for fy, cid, side, slot in acts:
        fx, fy = place_combat(side, slot)
        w_, h_, ax, ay = tab[cid]
        k = K_PERSO * s
        sp = Image.open(os.path.join(ROOT, 'public', 'art', 'vecto', cid + '.webp')).convert('RGBA')
        sp = sp.resize((round(w_ * k), round(h_ * k)), Image.LANCZOS)
        if side == 'heros':
            x = (fx - x0) * s - ax * k
        else:
            sp = sp.transpose(Image.FLIP_LEFT_RIGHT)
            x = (fx - x0) * s - (w_ - ax) * k
        y = (fy - y0) * s - ay * k
        im.paste(sp, (round(x), round(y)), sp) if x < 0 or y < 0 else im.alpha_composite(sp, (round(x), round(y)))
    return im


def vue_combat(t, largeur, phone=(390, 844, 34), fond=None):
    """Ce que montre le combat sur un téléphone (sans l'interface) : le fond (vectoriel à l'instant t, ou l'image
    `fond` donnée), les personnages, et sous le terrain la bande de la barre de geste (fond du jeu)."""
    top, hu = telephone(*phone)
    x0 = VUE_X[0]
    s = largeur / (VUE_X[1] - VUE_X[0])
    hh = round((H - top) * s)
    if fond is None:
        p = os.path.join(TMP, 'vue-%d.png' % largeur)
        rendre([(scene(t, (x0, top, VUE_X[1] - x0, H - top)), p)], largeur, hh)
        im = Image.open(p).convert('RGBA')
    else:
        im = fond.crop((round(x0 * fond.width / W), round(top * fond.height / H), round(VUE_X[1] * fond.width / W),
                        fond.height)).resize((largeur, hh), Image.NEAREST).convert('RGBA')
    im = poser(im, s, x0, top)
    return geste(im, s, phone)


def geste(im, s, phone):
    bas = round(phone[2] * 720 / phone[0] / UC * s)
    out = Image.new('RGBA', (im.width, im.height + bas), (21, 15, 54, 255))
    out.alpha_composite(im, (0, 0))
    return out


# ================================================================================================ LES EXPORTS
def calques():
    """Rend les images de chaque calque (×UP), les range dans une planche et écrit la description JSON."""
    os.makedirs(os.path.join(TMP, 'calques'), exist_ok=True)
    groupes = {}        # (w, h) → [(svg, png, (id, i))]
    for e in sorted(ELEMS, key=lambda e: e['prof']):
        g = e['genre']
        if g in ('boucle', 'morceau'):
            x, y, w_, h_ = e['box']
            n = e.get('n', 1)
            for i in range(n):
                doc = Doc()
                body = e['fn'](doc, i / n) if g == 'boucle' else e['fn'](doc)
                svg = doc.svg(body, (x, y, w_, h_))
                png = os.path.join(TMP, 'calques', '%s-%02d.png' % (e['id'], i))
                groupes.setdefault((w_ * UP, h_ * UP), []).append((svg, png, (e['id'], i)))
        elif g == 'defile':
            tw, th = e['tuile']
            doc = Doc()
            svg = doc.svg(e['tuile_dessin'](doc), (0, 0, tw, th))
            png = os.path.join(TMP, 'calques', '%s-tuile.png' % e['id'])
            groupes.setdefault((tw * UP, th * UP), []).append((svg, png, (e['id'], 0)))
        elif g == 'particules':
            w_, h_ = e['taille']
            for i in range(e['images']):
                doc = Doc()
                svg = doc.svg(e['dessin'](doc, i, e['images']), (0, 0, w_, h_))
                png = os.path.join(TMP, 'calques', '%s-%02d.png' % (e['id'], i))
                groupes.setdefault((w_ * UP, h_ * UP), []).append((svg, png, (e['id'], i)))
    images = {}
    for (w_, h_), lst in groupes.items():
        rendre([(s_, p_) for s_, p_, _ in lst], w_, h_)
        for _, p_, key in lst:
            images[key] = Image.open(p_).convert('RGBA')
    # la planche : des étagères, les plus hautes d'abord, 2048 px de large au plus. Chaque image est « étirée » de 2 px
    # tout autour (ses bords recopiés) : le jeu agrandit en lissant, et sans cela un liseré sombre apparaît au bord
    # des morceaux remis devant (vu dans le vrai combat).
    keys = sorted(images, key=lambda k: (-images[k].height, k))
    PW, EX = 2048, 2
    pos = {}
    x = y = EX
    rowh = 0
    for k in keys:
        im = images[k]
        if x + im.width + EX > PW:
            x, y, rowh = EX, y + rowh + 2 * EX + 1, 0
        pos[k] = (x, y)
        x += im.width + 2 * EX + 1
        rowh = max(rowh, im.height)
    ph = y + rowh + EX
    planche = Image.new('RGBA', (PW, ph), (0, 0, 0, 0))
    for k, (px_, py_) in pos.items():
        im = images[k]
        w_, h_ = im.size
        big = Image.new('RGBA', (w_ + 2 * EX, h_ + 2 * EX))
        big.paste(im.resize((w_ + 2 * EX, h_ + 2 * EX), Image.NEAREST), (0, 0))   # les bords, étirés
        big.paste(im, (EX, EX))
        for i in range(EX):
            big.paste(im.crop((0, 0, w_, 1)), (EX, i))
            big.paste(im.crop((0, h_ - 1, w_, h_)), (EX, h_ + EX + i))
            big.paste(im.crop((0, 0, 1, h_)), (i, EX))
            big.paste(im.crop((w_ - 1, 0, w_, h_)), (w_ + EX + i, EX))
        planche.paste(big, (px_ - EX, py_ - EX))
    used = max(px_ + images[k].width + EX for k, (px_, py_) in pos.items())
    planche = planche.crop((0, 0, used, ph))
    meta = []
    for e in sorted(ELEMS, key=lambda e: e['prof']):
        g = e['genre']
        c = dict(id=e['id'], prof=e['prof'])
        if g in ('boucle', 'morceau'):
            x_, y_, w_, h_ = e['box']
            n = e.get('n', 1)
            c.update(genre='boucle', x=x_, y=y_, w=w_, h=h_, ms=e.get('ms', 0) if n > 1 else 0,
                     cases=[list(pos[(e['id'], i)]) for i in range(n)])
        elif g == 'defile':
            x_, y_, w_, h_ = e['box']
            sx, sy = pos[(e['id'], 0)]
            c.update(genre='defile', x=x_, y=y_, w=w_, h=h_, case=[sx, sy, e['tuile'][0] * UP, e['tuile'][1] * UP],
                     vx=e['vx'], vy=e['vy'])
        elif g == 'particules':
            w_, h_ = e['taille']
            c.update(genre='particules', cases=[list(pos[(e['id'], i)]) + [w_ * UP, h_ * UP] for i in range(e['images'])],
                     zone=list(e['zone']), nombre=e['nombre'], vie=list(e['vie']), vx=list(e['vx']), vy=list(e['vy']),
                     ondule=list(e['ondule']), images='boucle' if e.get('ms') else 'vie', ms=e.get('ms', 0),
                     graine=CLAN + '-' + e['id'])
        else:
            continue
        meta.append(c)
    return planche, meta


def exporter():
    os.makedirs(JEU, exist_ok=True)
    os.makedirs(SORTIE, exist_ok=True)
    # l'image fixe du jeu ×UP : seulement ce qui ne bouge pas (les calques animés se posent dessus, entiers)
    fixe = os.path.join(TMP, 'fixe-x2.png')
    rendre([(scene(0, particules=False, base=True), fixe)], W * UP, H * UP)
    Image.open(fixe).convert('RGB').save(os.path.join(JEU, CLAN + '.webp'), quality=95, method=6)
    # le fond entier pour le propriétaire (les corbeaux en vol)
    rendre([(scene(5200), os.path.join(SORTIE, 'fond.png'))], W * UP, H * UP)
    planche, meta = calques()
    planche.save(os.path.join(JEU, CLAN + '-anim.webp'), quality=90, alpha_quality=100, method=6)
    planche.save(os.path.join(TMP, 'planche.png'))
    doc = {
        'clan': CLAN, 'style': 'vecto', 'w': W, 'h': H, 'up': UP, 'unite': round(UNIT, 5),
        'image': 'art/vecto/fonds/' + CLAN + '.webp', 'planche': 'art/vecto/fonds/' + CLAN + '-anim.webp',
        'note': ('Coordonnées x, y, w, h, zone en pixels du fond (590 × 1100) ; cases et tuiles en pixels de la '
                 'planche (×up). L\'image fixe ne contient que ce qui ne bouge pas : chaque calque animé se pose '
                 'dessus, entier (transparent autour). Images lisses : agrandir en LINÉAIRE. Boucle : images changées '
                 'toutes les ms (ms 0 = un morceau remis devant). Défilé : la tuile coule à vx, vy px du fond par '
                 'seconde. Particules : la règle de fond-px.ts (hasard rng("lenore-" + id)), centre en (x, y), images '
                 'sur la vie ou en boucle toutes les ms. Branché dans le jeu derrière ?vecto=1 (src/game/fond-vecto.ts).'),
        'reperes': {'hz': HZ, 'p0': P0, 'p1': P1, 'rangs_combat': [round(r, 1) for r in RANGS_COMBAT],
                    'rangs_accueil': list(RANGS), 'cartes': round(CARTES, 1), 'vue_x': [round(v, 1) for v in VUE_X]},
        'periode_ms': PERIODE, 'planche_taille': list(planche.size), 'calques': meta}
    json.dump(doc, open(os.path.join(HERE, 'fond-' + CLAN + '.json'), 'w'), indent=1, ensure_ascii=False)
    ecrire_ts(doc)
    print('  jeu : public/art/vecto/fonds/lenore.webp %d Ko, lenore-anim.webp %d Ko (%d × %d), %d calques' % (
        os.path.getsize(os.path.join(JEU, CLAN + '.webp')) // 1024,
        os.path.getsize(os.path.join(JEU, CLAN + '-anim.webp')) // 1024, planche.size[0], planche.size[1], len(meta)))
    return doc


def ecrire_ts(doc):
    """src/game/fond-vecto.ts : les calques au format de FOND_META (lu par bg/fond-px.ts derrière ?vecto=1)."""
    out = []
    for c in doc['calques']:
        z = c['prof']
        if c['genre'] == 'boucle':
            out.append(dict(id=c['id'], g='b', z=z, x=c['x'], y=c['y'], w=c['w'], h=c['h'], ms=c['ms'], f=c['cases']))
        elif c['genre'] == 'defile':
            out.append(dict(id=c['id'], g='d', z=z, x=c['x'], y=c['y'], w=c['w'], h=c['h'], f=c['case'], vx=c['vx'],
                            vy=c['vy']))
        else:
            out.append(dict(id=c['id'], g='p', z=z, f=c['cases'], zone=c['zone'], n=c['nombre'], vie=c['vie'],
                            vx=[round(v, 4) for v in c['vx']], vy=c['vy'], ondule=c['ondule'], ms=c['ms']))
    meta = {'w': W, 'h': H, 'up': UP, 'periode': PERIODE, 'calques': out}
    json.dump(meta, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'meta.json'), 'w'), separators=(',', ':'))
    import sys as _sys
    _sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
    from assemble_ts import assemble
    assemble()


def composer_jeu(doc, t):
    """Contrôle : l'image à l'instant t refaite comme le jeu la ferait (fixe + calques de la planche), à ×UP."""
    base = Image.open(os.path.join(JEU, CLAN + '.webp')).convert('RGBA')
    pl = Image.open(os.path.join(TMP, 'planche.png')).convert('RGBA')
    for c in sorted(doc['calques'], key=lambda c: c['prof']):
        if c['genre'] == 'boucle':
            i = 0 if c['ms'] == 0 else int(t // c['ms']) % len(c['cases'])
            sx, sy = c['cases'][i]
            base.alpha_composite(pl.crop((sx, sy, sx + c['w'] * UP, sy + c['h'] * UP)), (c['x'] * UP, c['y'] * UP))
        elif c['genre'] == 'defile':
            sx, sy, tw, th = c['case']
            tile = pl.crop((sx, sy, sx + tw, sy + th))
            off = round((t / 1000 * c['vx']) % (tw / UP) * UP)
            strip = Image.new('RGBA', (c['w'] * UP + 2 * tw, th))
            for k in range(c['w'] * UP // tw + 3):
                strip.alpha_composite(tile, (k * tw, 0))
            base.alpha_composite(strip.crop((tw - off, 0, tw - off + c['w'] * UP, th)), (c['x'] * UP, c['y'] * UP))
    return base


def contrôles(img_x1):
    """Mesures du sol de combat (comme le contrôle du pixel) : là où sont les pieds en combat, au-dessus des cartes."""
    a = np.asarray(img_x1.convert('RGB'), float)
    zone = a[P0 + 6:int(CARTES), int(VUE_X[0]):int(VUE_X[1])]
    L = zone[..., 0] * 0.3 + zone[..., 1] * 0.59 + zone[..., 2] * 0.11
    edges = (np.abs(np.diff(L, axis=1)) > 28).mean()
    print('  sol de combat (y %d → %d, x %d → %d) : luminosité moyenne %.0f, écart %.1f, %.2f %% de bords durs' % (
        P0 + 6, CARTES, VUE_X[0], VUE_X[1], L.mean(), L.std(), edges * 100))
    return L.mean(), L.std(), edges


def main():
    args = sys.argv[1:]
    os.makedirs(TMP, exist_ok=True)
    if '--fixe' in args:
        # le brouillon : la vue du combat sur un téléphone 390 × 844 (avec les personnages) et sur un court
        vue_combat(5200, 780).convert('RGB').save(os.path.join(TMP, 'brouillon-390.png'))
        vue_combat(5200, 720, phone=(360, 640, 0)).convert('RGB').save(os.path.join(TMP, 'brouillon-360.png'))
        print('  ', TMP)
        return
    os.makedirs(SORTIE, exist_ok=True)
    doc = exporter()
    # contrôle : le jeu (fixe + calques) donne bien la même image que le dessin entier
    for t in (0, 1650, 5100):
        ref = os.path.join(TMP, 'ref-%d.png' % t)
        rendre([(scene(t, particules=False), ref)], W * UP, H * UP)
        a = np.asarray(Image.open(ref).convert('RGB'), float)
        b = np.asarray(composer_jeu(doc, t).convert('RGB'), float)
        diff = np.abs(a - b).max(2)
        print('  jeu = dessin à t = %d ms : écart moyen %.2f, %.2f %% des pixels à plus de 24' % (
            t, diff.mean(), (diff > 24).mean() * 100))
        if t == 1650:
            Image.fromarray(np.clip(diff * 4, 0, 255).astype(np.uint8)).save(os.path.join(TMP, 'diff-jeu.png'))
    contrôles(Image.open(os.path.join(TMP, 'ref-0.png')).resize((W, H), Image.LANCZOS))
    # la situation : un téléphone 390 × 844 (×2), cadré comme le vrai combat, sans l'interface
    vue_combat(5200, 780).convert('RGB').save(os.path.join(SORTIE, 'situation.png'))
    # la comparaison : ancien fond pixel | nouveau fond vectoriel, mêmes personnages, même cadrage
    pix = Image.open(os.path.join(ROOT, 'public', 'art', 'px', 'fonds', CLAN + '.webp')).convert('RGBA')
    a = vue_combat(0, 780, fond=pix)
    b = vue_combat(5200, 780)
    comp = Image.new('RGB', (780 * 2 + 12, a.height), (31, 18, 56))
    comp.paste(a.convert('RGB'), (0, 0))
    comp.paste(b.convert('RGB'), (792, 0))
    comp.save(os.path.join(SORTIE, 'comparaison.png'))
    print('  test : fond.png, situation.png, comparaison.png')
    if '--video' in args:
        video()


def video():
    """L'animation en situation, cadrée comme le combat d'un téléphone 390 × 844 : une période entière (19,2 s),
    25 images par seconde, sans couture. Le mp4 à 720 de large (= les unités du jeu), le gif à 400 (une image sur
    deux)."""
    fps = 25
    n = PERIODE * fps // 1000
    phone = (390, 844, 34)
    top, hu = telephone(*phone)
    x0 = VUE_X[0]
    s = 720 / (VUE_X[1] - x0)
    hh = round((H - top) * s)
    d = os.path.join(TMP, 'video')
    os.makedirs(d, exist_ok=True)
    for f in os.listdir(d):
        os.unlink(os.path.join(d, f))
    jobs = [(scene(i * 1000 / fps, (x0, top, VUE_X[1] - x0, H - top)), os.path.join(d, 'f%04d.png' % i))
            for i in range(n)]
    rendre(jobs, 720, hh)
    gif = []
    for i in range(n):
        im = geste(poser(Image.open(jobs[i][1]).convert('RGBA'), s, x0, top), s, phone).convert('RGB')
        if im.height % 2:
            im = im.crop((0, 0, im.width, im.height - 1))
        im.save(os.path.join(d, 'v%04d.png' % i))
        if i % 2 == 0:
            gif.append(im.resize((400, round(im.height * 400 / 720)), Image.LANCZOS))
    mp4 = os.path.join(SORTIE, 'anim.mp4')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(fps), '-i', os.path.join(d, 'v%04d.png'),
                    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', '-preset', 'slow', '-movflags',
                    '+faststart', mp4], check=True)
    sample = Image.new('RGB', (400, gif[0].height * 4))
    for k in range(4):
        sample.paste(gif[k * len(gif) // 4], (0, k * gif[0].height))
    pal = sample.quantize(255, method=Image.Quantize.MEDIANCUT)
    q = [g.quantize(palette=pal, dither=Image.Dither.NONE) for g in gif]          # sans tramage : ≤ 3 Mo
    gp = os.path.join(SORTIE, 'anim.gif')
    q[0].save(gp, save_all=True, append_images=q[1:], duration=2000 // fps, loop=0, optimize=True)
    print('  vidéo : anim.mp4 %d Ko, anim.gif %d Ko (%d images)' % (
        os.path.getsize(mp4) // 1024, os.path.getsize(gp) // 1024, len(q)))


if __name__ == '__main__':
    main()
