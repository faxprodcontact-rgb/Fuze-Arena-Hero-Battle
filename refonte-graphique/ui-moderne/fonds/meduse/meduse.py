# Le fond de combat du clan de MÉDUSE (terre), le temple englouti dans la jungle, redessiné en VECTORIEL lisse et
# animé (27/11/2026, demande du propriétaire après le test du volcan de Kael : « les 7 autres fonds »).
#
# Même façon de faire et mêmes mesures que le fond de Kael (ui-moderne/fonds/kael/kael.py, le modèle) : une image de
# 590 × 1100 pixels du fond, plateforme de P0 = 800 à P1 = 1047 ; en combat, le jeu l'agrandit ×1,4 et n'en montre
# que x = 84 → 506, les cartes des héros cachent tout sous y = 985. Le style est celui des héros et monstres
# vectoriels : grandes formes simples, dégradés doux, une seule lumière en haut à droite, un seul contour sombre et
# seulement sur les plans proches, aucun flou SVG. Le lointain plus pâle et plus froid dans la brume de la jungle.
#
# L'identité est celle du fond pixel (refonte-graphique/pixel/fonds/meduse/build.py), recadrée pour le combat :
# un ciel de jungle humide au matin (bleu-vert en haut, voile doré à l'horizon), le soleil pâle en haut à droite,
# des bancs de brume ; des collines de jungle et la grande pyramide à degrés du temple, mangée par la forêt, entre
# deux grands arbres ; à gauche la façade en ruine du temple, où un grand cobra de pierre aux yeux de jade crache une
# cascade ; à droite une terrasse : le guerrier PÉTRIFIÉ (bouclier levé devant le visage) sur son socle au signe du
# clan, deux bannières violettes ; l'eau verte qui inonde le temple passe derrière l'arène (des nénuphars dérivent) ;
# l'arène, un dallage de pierre gris-vert d'un bord à l'autre, très calme ; au premier plan des feuilles et un bloc.
# Ce qui bouge : la cascade et son écume, l'eau, les yeux du cobra et le signe du socle (jade), les lianes, les
# bannières, la brume devant la pyramide, des feuilles qui tombent, des lucioles ; et dans le ciel, trois SERPENTS
# AILÉS lointains (corps qui ondule, ailes de plumes) qui planent lentement, dans la brume (la touche vivante,
# comme les dragons de Kael).
# Le signe du clan (inventé, comme le pixel) : un œil à pupille fendue d'où montent trois petits serpents ondulés.
#
#   python3 refonte-graphique/ui-moderne/fonds/meduse/meduse.py --fixe     # le brouillon (pour composer)
#   python3 refonte-graphique/ui-moderne/fonds/meduse/meduse.py            # images du jeu + calques + contrôles
#   python3 refonte-graphique/ui-moderne/fonds/meduse/meduse.py --video    # en plus : anim.gif et anim.mp4
#
# Sorties : public/art/vecto/fonds/meduse.webp (fixe ×2), meduse-anim.webp (planche ×2), fond-meduse.json et
# meta.json (à côté de ce fichier ; meta.json est réuni aux autres clans par ../assemble_ts.py dans
# src/game/fond-vecto.ts) ; pixel/sortie/ui/vecto/fond-meduse/ (fond.png, situation.png, comparaison.png, anim.gif,
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
from lib import Shape, blob, ellipse, mix, rpoly  # noqa: E402
from atelier import sm, ribbon, bez, resample, sides  # noqa: E402

CLAN = 'meduse'
BROUILLON = os.environ.get('BROUILLON', '/tmp/fonds-brouillon')
TMP = os.path.join(BROUILLON, 'vecto-fond-' + CLAN)
SORTIE = os.path.join(ROOT, 'refonte-graphique', 'pixel', 'sortie', 'ui', 'vecto', 'fond-' + CLAN)
JEU = os.path.join(ROOT, 'public', 'art', 'vecto', 'fonds')
RENDU = os.path.join(ROOT, 'refonte-graphique', 'ui-moderne', 'heros', 'rendu-lot.cjs')

# ------------------------------------------------------------------------------------------------ les mesures
W, H = 590, 1100
UP = 2                          # les images du jeu sont rendues ×2 (vectoriel : plus fin que le pixel)
HZ, P0, P1 = 789, 800, 1047      # comme Kael : en combat, le rang du fond a ses pieds à 828
RANGS = (860, 934, 1007)
VISIBLE = {'court': 377, 'moyen': 148, 'long': 50}
PERIODE = 19200                 # toutes les boucles divisent cette période : l'aperçu boucle sans couture
UNIT = 720 / W
HERO_X_U = {3: 82, 4: 82, 2: 163, 0: 245, 1: 245}
ENEMY_X_U = {0: 475, 1: 475, 2: 557, 3: 638, 4: 638}
ROW_OF = {0: 0, 3: 0, 2: 1, 1: 2, 4: 2}


def place(side, slot):
    xs = HERO_X_U if side == 'heros' else ENEMY_X_U
    return int(round(xs[slot] / UNIT)), RANGS[ROW_OF[slot]]


# Le VRAI combat (src/game/battle-scene.ts, fight-view.ts) : le décor y est agrandi ×1,4 (FOND_ZOOM), centré, son bas
# au bas de l'écran (au-dessus de la barre de geste) ; on n'en voit que x = 84 → 506.
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
# Reprises de Méduse et de ses monstres vectoriels (écailles émeraude, peau de jade, or, violet du pagne et de la robe,
# pierre gris-vert du bouclier), mais plus sourdes ; le ciel et le lointain dans la brume verte de la jungle.
INK = '#1f1238'                 # le contour (le raisin de l'interface), seulement sur les plans proches
CIEL = [(0, '#1b3a4a'), (0.22, '#244e58'), (0.42, '#346668'), (0.58, '#4a7e6e'), (0.72, '#6a9676'),
        (0.86, '#98b080'), (1, '#c2c28c')]
BRUME = '#8eaa8a'               # la couleur de l'air au loin
NUAGE = dict(base='#4c7a72', light='#5c8a78', rim='#9cbc96', sh='#3c6664')
NUAGE_BAS = dict(base='#64907a', light='#749e80', rim='#acc69c', sh='#527c6e')
LOIN1 = dict(base='#86a48a', light='#90ac8e', rim='#aec29c', sh='#7a9a84')         # les collines les plus lointaines
LOIN2 = dict(base='#6c9078', light='#789a7e', rim='#9ab490', sh='#5e846e')
PYR = dict(base='#7e9282', light='#9ea88a', rim='#c8c8a0', sh='#687e72')            # la pyramide, dans la brume
PYR_JUNGLE = dict(base='#5e8a6c', light='#6c9872', rim='#94b88a', sh='#4e7a62')
ARBRE = dict(base='#3e6c58', light='#4a7c5e', rim='#7aa676', sh='#2e5a4e')          # les grands arbres
FORET = dict(base='#2c5644', light='#38684c', rim='#669860', sh='#21463a')          # la forêt proche
RUINE = dict(base='#4e5c56', light='#626e62', rim='#909c84', sh='#38454a')          # la pierre du temple
STATUE = dict(base='#727e70', light='#8a9482', rim='#b8bea0', sh='#55625a')         # la pierre sculptée (plus claire)
MOUSSE = dict(base='#3a7446', light='#4a884c', rim='#8ab86a', sh='#285a3e')
FEUILLE = dict(base='#2c5a40', light='#3a6c46', rim='#6c9c5c', sh='#1e4434')        # le premier plan, dans l'ombre
ROC = dict(base='#3e4a48', light='#525e56', rim='#86907a', sh='#2a3438')
SOL = dict(back='#6a7266', front='#767e70')                                         # l'arène : valeur moyenne
JADE = dict(deep='#138a4a', mid='#2fd070', glow='#7cf0a0', hot='#d4ffe0')
OR = dict(base='#c8963a', light='#e8bc58', rim='#fff0b0', sh='#8a5a26')
VIOLET = dict(base='#6a3a96', light='#8450b0', rim='#b384d8', sh='#46266c')
EAU = dict(far='#6c9c84', mid='#2e6e5e', deep='#21564e', hi='#a6cc9c', dark='#183e3c')
CHUTE = dict(top='#cfe6d6', light='#9cc8b2', mid='#6ea894', deep='#46887a', foam='#eef8ee')


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


# ------------------------------------------------------------------------------------------------ les profils
def interp(pts, x):
    for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
        if xa <= x <= xb:
            return ya + (yb - ya) * (x - xa) / ((xb - xa) or 1)
    return pts[0][1] if x < pts[0][0] else pts[-1][1]


# La falaise de gauche est plus basse que dans le pixel (les dragons passent au-dessus) ; l'éperon de droite est
# avancé de 18 pixels vers le milieu (le combat coupe les bords : on voit x = 84 → 506).
FAL_G_HAUT = [(-14, 536), (14, 530), (44, 526), (72, 530), (96, 538), (110, 544), (126, 545), (142, 540),
              (160, 538), (176, 546)]
FAL_G_FACE = [(184, 572), (182, 612), (190, 650), (186, 690), (196, 730), (214, 776)]
FAL_D_DX = -18
FAL_D_FACE = [(x + FAL_D_DX, y) for x, y in
              [(418, 776), (424, 730), (414, 690), (424, 648), (418, 604), (430, 570)]]
FAL_D_HAUT = [(x + FAL_D_DX, y) for x, y in
              [(442, 556), (468, 551), (494, 547), (520, 545), (548, 540), (576, 543), (604, 538)]] + [(604, 538)]


def sol_g(x):
    return interp(FAL_G_HAUT, x)


def sol_d(x):
    return interp(FAL_D_HAUT, x)

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


def hasard(seed):
    import random
    return random.Random(seed)


def contour(shapes, iw=1.0):
    """Le contour UNIQUE d'un objet fait de plusieurs morceaux : tous les traits d'encre d'abord, les morceaux se
    peignent ensuite par-dessus (on ne voit l'encre qu'au bord extérieur, jamais entre deux morceaux)."""
    return ''.join('<path d="%s" fill="%s" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>' % (
        D(s), INK, INK, fm(2 * iw)) for s in shapes)


def canopee(x0, x1, ybase, ybot, r0, r1, seed, amp=6):
    """Une lisière de jungle : une base pleine et, dessus, une rangée de couronnes rondes (une seule forme)."""
    rnd = hasard(seed)
    yb = ybase if callable(ybase) else (lambda x: ybase)
    s = rpoly([(x0, ybot)] + [(x, yb(x) + 4) for x in range(int(x0), int(x1) + 1, 10)] + [(x1, ybot)], 0)
    x = x0 - r1 * 0.3
    while x < x1 + r1 * 0.3:
        r = rnd.uniform(r0, r1)
        cy = ybase(x) if callable(ybase) else ybase
        s = s + ellipse(x, cy - r * 0.35 + rnd.uniform(-amp, amp) * 0.5, r, r * 0.86)
        x += r * rnd.uniform(1.15, 1.5)
    return s


def touffe(cx, cy, r, seed, n=4):
    """Une touffe de feuillage (des boules réunies), dessous à peu près plat, posée en (cx, cy)."""
    rnd = hasard(seed)
    s = rpoly([(cx - r * 1.1, cy), (cx - r * 0.9, cy - r * 0.5), (cx + r * 0.9, cy - r * 0.5), (cx + r * 1.1, cy)], r * 0.3)
    for k in range(n):
        u = (k + 0.5) / n
        x = cx - r * 0.9 + 1.8 * r * u
        rr = r * (0.45 + 0.4 * math.sin(math.pi * u)) * rnd.uniform(0.85, 1.1)
        s = s + ellipse(x, cy - rr * 0.8, rr, rr * 0.9)
    return s


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
SOLEIL = (452, 394)          # vu sur tous les téléphones, à droite des pilules du haut


@element('ciel', -29.9, 'fixe')
def ciel(doc):
    out = [path('M-20 -20H610V840H-20Z', doc.lin(0, 0, 0, 800, CIEL))]
    # le voile doré de l'horizon, derrière la pyramide (le matin humide)
    out.append('<ellipse cx="330" cy="760" rx="380" ry="230" fill="%s"/>' % doc.rad(
        330, 760, 380, [(0, '#d8d096', 0.5), (0.5, '#b8bc8a', 0.22), (1, '#8aa07c', 0)], ry=230))
    # le soleil pâle, en haut à droite (la seule lumière)
    sx, sy = SOLEIL
    out.append('<circle cx="%d" cy="%d" r="130" fill="%s"/>' % (sx, sy, doc.rad(
        sx, sy, 140, [(0, '#f8f0b4', 0.42), (0.35, '#d4d6a0', 0.16), (1, '#7a9a7c', 0)])))
    out.append('<circle cx="%d" cy="%d" r="22" fill="%s"/>' % (sx, sy, doc.rad(
        sx + 6, sy - 6, 27, [(0, '#fffdec'), (0.7, '#f6f0c8'), (1, '#e2dca8')])))
    return ''.join(out)


NUAGES_BAS = {
    # les bancs bas où les serpents lointains se cachent (remis devant eux : morceaux « devant-… »)
    'g': (-20, 122, 474, [(114, 466, 10), (92, 456, 16), (62, 450, 20), (32, 452, 18), (4, 458, 15), (-18, 466, 10)]),
    'm': (300, 408, 410, [(402, 403, 8), (384, 396, 12), (360, 392, 13), (334, 394, 12), (312, 400, 9)]),
}


def nuage_bas(doc, k):
    x0, x1, yb, lobes = NUAGES_BAS[k]
    return vol(doc, lobes_shape(x0, x1, yb, lobes, sag=2), NUAGE_BAS if k == 'g' else
               dict(NUAGE_BAS, base='#5a8a74', light='#68967a', sh='#4a7668'), r=1.8, c=2.6)


@element('nuages', -29.5, 'fixe')
def nuages(doc):
    out = []
    # A : le grand banc de brume en haut à gauche (le haut des téléphones longs)
    a = lobes_shape(-30, 330, 330, [(304, 320, 16), (270, 304, 28), (224, 288, 36), (170, 278, 40), (114, 270, 42),
                                    (60, 274, 40), (10, 284, 36), (-26, 300, 28)], sag=6)
    out.append(vol(doc, a, NUAGE, r=2.2, c=4))
    a2 = lobes_shape(-30, 250, 226, [(232, 216, 14), (198, 202, 24), (152, 190, 30), (100, 186, 32), (50, 190, 30),
                                     (4, 198, 28), (-30, 210, 20)], sag=4)
    out.append(vol(doc, a2, dict(NUAGE, base='#3e6a6e', light='#487474', sh='#30585e'), r=2, c=3.5))
    # B : en haut à droite ; C : un petit banc au-dessus du soleil (il le voile un peu)
    b = lobes_shape(380, 620, 286, [(612, 274, 16), (578, 262, 22), (540, 256, 22), (500, 260, 20), (460, 266, 18),
                                    (414, 274, 14)], sag=3)
    out.append(vol(doc, b, NUAGE, r=2, c=3))
    c = lobes_shape(470, 620, 336, [(610, 328, 12), (580, 318, 16), (544, 316, 15), (508, 322, 12), (482, 328, 8)],
                    sag=2)
    out.append(vol(doc, c, dict(NUAGE, base='#588676', light='#64927c'), r=1.8, c=2.6))
    # E : un petit banc à gauche, sous le banc A
    e = lobes_shape(70, 200, 370, [(190, 364, 9), (162, 356, 13), (126, 354, 14), (92, 360, 11)], sag=2)
    out.append(vol(doc, e, dict(NUAGE, base='#588676', light='#64927c'), r=1.8, c=2.6))
    # les bancs bas
    out.append(nuage_bas(doc, 'g'))
    out.append(nuage_bas(doc, 'm'))
    return ''.join(out)


# ---------------------------------------------------------------------------------------------------- le lointain
@element('lointain', -28.5, 'fixe')
def lointain(doc):
    out = []
    # les collines de jungle les plus lointaines, presque dans la couleur de l'air
    h1 = lambda x: 662 + 14 * math.sin(x / 70) + 10 * math.sin(x / 31 + 1)
    out.append(vol(doc, canopee(-20, 610, h1, 800, 14, 24, 3), LOIN1, r=1.4, c=0))
    h2 = lambda x: 706 + 8 * math.sin(x / 55 + 2) + 6 * math.sin(x / 23)
    out.append(vol(doc, canopee(-20, 610, h2, 800, 11, 18, 7), LOIN2, r=1.4, c=1.2))
    return ''.join(out)


# ---------------------------------------------------------------------------------------------------- la pyramide
PX, PB = 300, 752                 # le milieu et la base de la pyramide (cachée par la forêt)
P_ETAGES = [(752, 150), (712, 126), (672, 104), (632, 84), (594, 66), (560, 50)]   # (y du bas d'un étage, demi-largeur)
P_HAUT = 528                      # le haut du sanctuaire


def pyr_etage(i):
    yb, hw = P_ETAGES[i]
    yt, hw2 = P_ETAGES[i + 1][0], P_ETAGES[i + 1][1] + 8
    return rpoly([(PX - hw, yb), (PX - hw2, yt), (PX + hw2, yt), (PX + hw, yb)], 1.5)


@element('pyramide', -28, 'fixe')
def pyramide(doc):
    out = []
    for i in range(len(P_ETAGES) - 1):
        s = pyr_etage(i)
        yb, hw = P_ETAGES[i]
        yt = P_ETAGES[i + 1][0]
        g = doc.lin(PX + hw, yt, PX - hw * 0.6, yb, [(0, PYR['light']), (0.5, PYR['base']), (1, PYR['sh'])])
        out.append(vol(doc, s, PYR, grad=g, r=1.0, c=2.2, rim_op=0.45))
        # le pan droit de l'étage (tourné vers la lumière) un peu plus clair
        hw2 = P_ETAGES[i + 1][1] + 8
        out.append(path(rpoly([(PX + hw * 0.55, yb), (PX + hw2 * 0.55, yt + 1), (PX + hw2, yt + 1), (PX + hw, yb)], 1),
                        PYR['light'], 0.35))
    # l'escalier du milieu : une large rampe un peu plus claire, ses deux rampes de pierre (aucune marche dessinée)
    yb0, yt0 = PB, P_ETAGES[-1][0]
    esc = rpoly([(PX - 20, yb0), (PX - 12, yt0), (PX + 12, yt0), (PX + 20, yb0)], 1)
    out.append(path(esc, doc.lin(PX + 20, yt0, PX - 20, yb0, [(0, '#a6b49a'), (1, '#8a9c88')])))
    for sg in (-1, 1):
        r_ = rpoly([(PX + sg * 20, yb0), (PX + sg * 12, yt0), (PX + sg * 15, yt0), (PX + sg * 24, yb0)], 0.8)
        out.append(path(r_, PYR['sh'] if sg < 0 else PYR['rim'], 0.7 if sg < 0 else 0.55))
    # le sanctuaire au sommet : un bloc, sa porte sombre, son toit débordant
    yt = P_ETAGES[-1][0]
    sanct = rpoly([(PX - 26, yt + 1), (PX - 24, P_HAUT + 8), (PX + 24, P_HAUT + 8), (PX + 26, yt + 1)], 1.2)
    out.append(vol(doc, sanct, PYR, r=1.4, c=2.0))
    out.append(vol(doc, rpoly([(PX - 31, P_HAUT + 9), (PX - 28, P_HAUT), (PX + 28, P_HAUT), (PX + 31, P_HAUT + 9)], 1.5),
                   PYR, r=1.2, c=1.6))
    porte = sm([(PX - 7, yt + 1), (PX - 7, yt - 13), (PX - 4, yt - 19), (PX, yt - 20.5), (PX + 4, yt - 19),
                (PX + 7, yt - 13), (PX + 7, yt + 1)], sharp=(0, 6), t=0.8)
    out.append(path(porte, doc.lin(0, yt - 20, 0, yt, [(0, '#3e5254'), (1, '#4e6260')])))
    # un fil d'or terni sur le toit (le temple de la reine), vu de loin
    out.append(path(rpoly([(PX - 27, P_HAUT + 0.5), (PX + 27, P_HAUT + 0.5), (PX + 27, P_HAUT + 2.2),
                           (PX - 27, P_HAUT + 2.2)], 0.6), '#c8c08a', 0.75))
    # la jungle qui mange les gradins : des touffes posées sur les rebords (plus nombreuses en bas)
    for cx, cy, r, sd in ((PX - 132, 712, 16, 1), (PX - 96, 712, 9, 2), (PX + 112, 712, 13, 3), (PX + 70, 672, 9, 4),
                          (PX - 86, 672, 12, 5), (PX - 62, 632, 8, 6), (PX + 66, 594, 7, 7), (PX + 140, 752, 18, 8),
                          (PX - 30, 560, 6, 9)):
        out.append(vol(doc, touffe(cx, cy, r, sd), PYR_JUNGLE, r=1.2, c=1.6))
    # deux lianes qui pendent d'un gradin (traits doux, pas de rayures)
    for x, y, ln in ((PX - 70, 672, 22), (PX + 96, 712, 16)):
        c_ = resample([(x, y - 1), (x + 1.5, y + ln * 0.5), (x - 0.5, y + ln)], 8)
        out.append(path(ribbon(c_, [1.6, 1.8, 1.7, 1.6, 1.4, 1.2, 1, 0.7, 0.3]), PYR_JUNGLE['sh'], 0.8))
    return ''.join(out)


@element('brume-loin', -27, 'fixe')
def brume_loin(doc):
    # la brume chaude du matin noie le pied de la pyramide et les collines
    return path('M-10 640H600V800H-10Z', doc.lin(0, 640, 0, 760, [(0, BRUME, 0), (0.6, '#a4b890', 0.35),
                                                                  (1, '#b8c49a', 0.55)]))


# ---------------------------------------------------------------------------------------------------- les arbres
ARBRES = [  # (x du pied, y du pied, hauteur, rayon de la couronne, penche)
    (234, 742, 158, 40, -5),
    (384, 744, 172, 44, 7),
]


@element('arbres', -24, 'fixe')
def arbres(doc):
    out = []
    for k, (x, y, h_, r, pen) in enumerate(ARBRES):
        top = (x + pen, y - h_)
        # le tronc monte jusque dans la couronne (son bout est caché par le feuillage)
        tronc = resample(bez((x, y), (x + pen * 0.1, y - h_ * 0.4), (x + pen * 0.7, y - h_ * 0.75),
                             (top[0], top[1] - 22)), 14)
        out.append(vol(doc, ribbon(tronc, [12, 11, 10.4, 10, 9.6, 9.3, 9, 8.8, 8.6, 8.4, 8.2, 8, 7.8, 7.6, 7],
                                   sharp_ends=False), dict(base='#4e5e54', light='#5e6e60', rim='#8a9a84', sh='#3e4c48'),
                       r=1.0, c=1.4))
        # deux branches qui partent sous la couronne
        for sg in (-1, 1):
            b = resample(bez(top, (top[0] + sg * r * 0.3, top[1] - 4), (top[0] + sg * r * 0.6, top[1] - 10),
                             (top[0] + sg * r * 0.8, top[1] - 16)), 8)
            out.append(path(ribbon(b, [2.6, 2.4, 2.2, 2, 1.8, 1.5, 1.2, 0.9, 0.5]), '#4a5a50'))
        # la couronne : un parasol de boules (la plus haute à droite, vers la lumière)
        cx, cy = top[0], top[1] - 18
        s = sm([(cx - r * 1.15, cy + r * 0.35), (cx - r * 0.95, cy - r * 0.05), (cx - r * 0.55, cy - r * 0.38),
                (cx - r * 0.1, cy - r * 0.5), (cx + r * 0.35, cy - r * 0.55), (cx + r * 0.8, cy - r * 0.32),
                (cx + r * 1.15, cy + r * 0.05), (cx + r * 1.2, cy + r * 0.36), (cx + r * 0.6, cy + r * 0.5),
                (cx, cy + r * 0.44), (cx - r * 0.6, cy + r * 0.52)], t=0.9)
        for dx, dy, rr in ((-0.7, -0.05, 0.42), (-0.25, -0.32, 0.45), (0.25, -0.36, 0.46), (0.72, -0.12, 0.42)):
            s = s + ellipse(cx + dx * r, cy + dy * r, rr * r, rr * r * 0.82)
        out.append(vol(doc, s, ARBRE, grad=doc.lin(cx + r, cy - r * 0.6, cx - r * 0.6, cy + r * 0.5, [
            (0, ARBRE['light']), (0.5, ARBRE['base']), (1, ARBRE['sh'])]), r=2.0, c=3.0))
        # le dessous de la couronne dans l'ombre
        out.append('<g clip-path="%s">%s</g>' % (doc.clip(s.d()), path(
            'M%s %sH%sV%sH%sZ' % (fm(cx - r * 1.5), fm(cy + r * 0.2), fm(cx + r * 1.5), fm(cy + r), fm(cx - r * 1.5)),
            ARBRE['sh'], 0.6)))
    return ''.join(out)


# ---------------------------------------------------------------------------------------------------- la forêt proche
@element('foret', -22, 'fixe')
def foret(doc):
    h = lambda x: 722 + 6 * math.sin(x / 40) + 5 * math.sin(x / 17 + 1)
    s = canopee(150, 440, h, 770, 12, 20, 11, amp=4)
    out = [vol(doc, s, FORET, r=1.8, c=2.6)]
    # quelques grandes feuilles plus claires (lumière à droite) sur le dessus
    for x, y, a in ((236, 712, -30), (318, 716, 20), (372, 712, -10)):
        f = feuille_forme(x, y, 9, a)
        out.append(path(f, FORET['light'], 0.8))
    return ''.join(out)


def feuille_forme(x, y, L, ang, w=0.42):
    """Une feuille (pointe en haut, tournée de `ang` degrés), son pied en (x, y)."""
    a = math.radians(ang)
    P = lambda u, v: (x + (u * math.cos(a) - v * math.sin(a)) * L, y + (u * math.sin(a) + v * math.cos(a)) * L)
    return sm([P(0, 0), P(-w, -0.45), P(-w * 0.6, -0.8), P(0, -1.15), P(w * 0.6, -0.8), P(w, -0.45)], sharp=(0, 3), t=0.8)


# ---------------------------------------------------------------------------------------------------- la ruine (gauche)
R_HAUT = 574                       # le dessus de la façade (la corniche), où est posé le cobra
R_X1 = 206                         # le bord droit de la façade
COBRA_X = 160
PORTE = (112, 700, 15)             # la porte noyée : milieu, haut de l'arc, demi-largeur


def ruine_forme():
    pts = [(-14, 790), (-14, 548), (20, 545), (46, 548), (60, 552), (64, R_HAUT), (194, R_HAUT), (202, R_HAUT + 3),
           (R_X1, R_HAUT + 12), (R_X1 + 2, 660), (R_X1 + 4, 790)]
    return sm(pts, sharp=(0, 1, 4, 5, 6, len(pts) - 1), t=0.6)


def porte_forme():
    x, y, w_ = PORTE
    return sm([(x - w_, 790), (x - w_, y + w_ * 0.7), (x - w_ * 0.72, y + w_ * 0.2), (x, y), (x + w_ * 0.72, y + w_ * 0.2),
               (x + w_, y + w_ * 0.7), (x + w_, 790)], sharp=(0, 6), t=0.85)


@element('ruine', -20, 'fixe')
def ruine(doc):
    out = []
    forme = ruine_forme()
    g = doc.lin(R_X1, 560, -10, 780, [(0, RUINE['light']), (0.45, RUINE['base']), (1, RUINE['sh'])])
    out.append(vol(doc, forme, RUINE, grad=g, r=2.4, c=4.0, ink=INK, iw=1.0))
    inner = []
    # la partie haute de gauche, plus en retrait : un peu plus sombre
    inner.append(path(sm([(-14, 548), (62, 552), (64, 600), (-14, 600)], sharp=(0, 1, 2, 3), t=0.5), RUINE['sh'], 0.35))
    # la corniche : un dessus éclairé, une ombre douce dessous
    inner.append(path(rpoly([(60, R_HAUT), (R_X1 + 2, R_HAUT), (R_X1 + 2, R_HAUT + 3), (60, R_HAUT + 3)], 0.5),
                      RUINE['rim'], 0.55))
    inner.append(path(rpoly([(-14, R_HAUT + 12), (R_X1 + 4, R_HAUT + 12), (R_X1 + 4, R_HAUT + 19), (-14, R_HAUT + 19)], 2),
                      doc.lin(0, R_HAUT + 12, 0, R_HAUT + 19, [(0, RUINE['sh'], 0.85), (1, RUINE['sh'], 0)])))
    # la frise : un bandeau en saillie où ondule un serpent incrusté de jade (un seul, sans motif répété)
    fy = 636
    inner.append(path(rpoly([(-14, fy - 7), (R_X1 + 4, fy - 7), (R_X1 + 4, fy + 8), (-14, fy + 8)], 1),
                      RUINE['light'], 0.35))
    inner.append(path(rpoly([(-14, fy + 8), (R_X1 + 4, fy + 8), (R_X1 + 4, fy + 13), (-14, fy + 13)], 1),
                      doc.lin(0, fy + 8, 0, fy + 13, [(0, RUINE['sh'], 0.8), (1, RUINE['sh'], 0)])))
    c = [(x, fy + 0.5 + 3 * math.sin(x / 15 + 0.6)) for x in range(-14, 168, 4)]
    ws = [0.6 + 1.3 * min(1, i / 6) for i in range(len(c))]
    inner.append(path(ribbon([(x + 0.6, y + 0.8) for x, y in c], ws), RUINE['sh'], 0.7))
    inner.append(path(ribbon(c, ws), '#4e9a6a', 0.75))
    hx_, hy_ = c[-1]
    inner.append(path(sm([(hx_ - 2, hy_ - 2.4), (hx_ + 5, hy_ - 1.6), (hx_ + 7, hy_), (hx_ + 5, hy_ + 1.6),
                          (hx_ - 2, hy_ + 2.4)], t=0.8), '#4e9a6a', 0.8))
    # quelques grands blocs (des joints doux, irréguliers, pas des rangées)
    for pts, ws_ in (([(-14, 684), (30, 686), (70, 683)], 1.2), ([(134, 686), (170, 684), (206, 686)], 1.2),
                     ([(-14, 612), (40, 610)], 1.0), ([(120, 606), (176, 608)], 1.0), ([(40, 612), (42, 628)], 0.9),
                     ([(176, 608), (178, 628)], 0.9), ([(24, 686), (22, 736)], 1.0), ([(178, 688), (180, 740)], 1.0)):
        cc = resample(pts, 8)
        wl = [ws_ * (0.3 + 0.7 * math.sin(math.pi * i / 8) ** 0.5) for i in range(9)]
        inner.append(path(ribbon(cc, wl), RUINE['sh'], 0.6))
        inner.append(path(ribbon([(x - 0.8, y - 1) for x, y in cc], [w * 0.5 for w in wl]), RUINE['rim'], 0.25))
    # la porte noyée : l'arc de pierre taillée (une seule pièce claire), le noir de l'intérieur, la clé de jade
    pf = porte_forme()
    x, y, w_ = PORTE
    arc = sm([(x - w_ - 6, 790), (x - w_ - 6, y + w_ * 0.6), (x - w_ * 0.8, y - 3), (x, y - 9), (x + w_ * 0.8, y - 3),
              (x + w_ + 6, y + w_ * 0.6), (x + w_ + 6, 790)], sharp=(0, 6), t=0.85)
    inner.append(vol(doc, arc, STATUE, r=1.4, c=2.0))
    inner.append(path(pf, doc.lin(0, y, 0, 760, [(0, '#0e1a1e'), (1, '#18282a')])))
    inner.append(path(sm([(x + w_ - 4, y + 10), (x + w_, y + w_ * 0.7), (x + w_, 760), (x + w_ - 5, 760)], t=0.8),
                      '#2a3c3c', 0.6))
    inner.append(path(rpoly([(x - 3.2, y - 10), (x + 3.2, y - 10), (x + 2.4, y + 0.5), (x - 2.4, y + 0.5)], 0.8),
                      doc.lin(x + 3, y - 10, x - 3, y, [(0, JADE['glow']), (1, JADE['deep'])])))
    # la lumière en haut à droite : le bord droit de la façade accroche la lumière
    inner.append(path(sm([(R_X1 - 14, R_HAUT + 20), (R_X1 + 4, R_HAUT + 16), (R_X1 + 6, 790), (R_X1 - 10, 790)], t=0.8),
                      RUINE['light'], 0.4))
    # la mousse du pied (l'eau monte et descend) et la brume chaude du bas
    inner.append(path('M-20 718H230V800H-20Z', doc.lin(0, 718, 0, 760, [(0, MOUSSE['sh'], 0), (1, MOUSSE['sh'], 0.55)])))
    out.append('<g clip-path="%s">%s</g>' % (doc.clip(forme.d()), ''.join(inner)))
    # la mousse posée sur les dessus, qui coule un peu par-dessus la corniche
    for pts in ([(62, R_HAUT + 1), (66, R_HAUT - 2), (96, R_HAUT - 2.5), (110, R_HAUT + 1), (104, R_HAUT + 8),
                 (90, R_HAUT + 5), (80, R_HAUT + 11), (70, R_HAUT + 6)],
                [(176, R_HAUT + 1), (182, R_HAUT - 2), (200, R_HAUT - 1), (206, R_HAUT + 6), (204, R_HAUT + 15),
                 (198, R_HAUT + 9), (188, R_HAUT + 6)],
                [(-14, 549), (10, 543), (36, 544), (58, 549), (62, 556), (48, 560), (38, 556), (24, 562), (8, 556),
                 (-14, 558)]):
        out.append(vol(doc, sm(pts, t=0.85), MOUSSE, r=1.0, c=1.4))
    # un buisson sur la partie haute de gauche
    out.append(vol(doc, touffe(28, 548, 26, 21, 5), dict(FORET, base='#305c46', light='#3c6c4c'), r=1.6, c=2.4,
                   ink=INK, iw=0.9))
    out.append(cobra(doc))
    return ''.join(out)


# ---------------------------------------------------------------------------------------------------- le cobra
YEUX = ((COBRA_X - 7.5, 498.5), (COBRA_X + 7.5, 498.5))


def cobra_formes():
    x = COBRA_X
    y0 = R_HAUT
    anneau1 = sm([(x - 40, y0 + 0.5), (x - 42, y0 - 7), (x - 30, y0 - 14), (x, y0 - 16), (x + 30, y0 - 14),
                  (x + 42, y0 - 7), (x + 40, y0 + 0.5)], sharp=(0, 6), t=0.85)
    anneau2 = sm([(x - 30, y0 - 12), (x - 32, y0 - 20), (x - 20, y0 - 27), (x + 2, y0 - 29), (x + 24, y0 - 26),
                  (x + 33, y0 - 19), (x + 30, y0 - 12), (x, y0 - 10)], t=0.85)
    cou = sm([(x - 11, y0 - 22), (x - 10, 540), (x - 8, 524), (x + 8, 524), (x + 10, 540), (x + 11, y0 - 22)],
             sharp=(0, 5), t=0.8)
    capuchon = sm([(x, 467), (x - 13, 472), (x - 24, 484), (x - 30, 502), (x - 27, 522), (x - 17, 540), (x - 9, 552),
                   (x, 556), (x + 9, 552), (x + 17, 540), (x + 27, 522), (x + 30, 502), (x + 24, 484), (x + 13, 472)],
                  t=0.85)
    tete = sm([(x - 16, 495), (x - 12, 485), (x, 481), (x + 12, 485), (x + 16, 495), (x + 13, 507), (x + 7, 516),
               (x, 519), (x - 7, 516), (x - 13, 507)], t=0.85)
    return anneau1, anneau2, cou, capuchon, tete


def cobra(doc):
    """Le grand cobra de pierre, dressé de face sur la corniche, capuchon ouvert : il crache la cascade."""
    x = COBRA_X
    a1, a2, cou, cap, tete = cobra_formes()
    out = [contour((a1, a2, cap, tete), 1.0)]
    out.append(vol(doc, cap, STATUE, r=2.0, c=3.0))
    # le fil de jade qui borde le capuchon (incrusté : un sillon sombre, puis le jade)
    bord = [(x - 19, 548), (x - 24, 530), (x - 25, 506), (x - 20, 488), (x - 10, 477), (x, 474), (x + 10, 477),
            (x + 20, 488), (x + 25, 506), (x + 24, 530), (x + 19, 548)]
    cb = resample(catmull(bord), 30)
    wl = [0.4 + 1.2 * math.sin(math.pi * i / 30) ** 0.4 for i in range(31)]
    out.append(path(ribbon([(px + 0.5, py + 0.8) for px, py in cb], [w * 1.3 for w in wl]), STATUE['sh'], 0.8))
    out.append(path(ribbon(cb, wl), JADE['deep'], 0.95))
    out.append(path(ribbon([(px + 0.3, py - 0.3) for px, py in cb[16:]], [w * 0.5 for w in wl[16:]]), JADE['mid'], 0.6))
    # le dessin du capuchon : deux grandes écailles en larmes, de chaque côté (pas de motif répété)
    for sg in (-1, 1):
        s = sm([(x + sg * 9, 530), (x + sg * 15, 518), (x + sg * 19, 528), (x + sg * 16, 540)], t=0.9)
        out.append(path(s, STATUE['sh'] if sg < 0 else STATUE['light'], 0.5))
    out.append(vol(doc, a2, STATUE, r=1.6, c=2.6))
    out.append(vol(doc, a1, STATUE, r=1.6, c=2.6))
    out.append(path(ribbon(resample([(x - 28, R_HAUT - 12), (x, R_HAUT - 9.5), (x + 28, R_HAUT - 12)], 10),
                           [0.3, 1, 1.6, 1.8, 1.8, 1.8, 1.8, 1.6, 1.2, 0.8, 0.3]), STATUE['sh'], 0.6))
    out.append(vol(doc, tete, STATUE, r=1.6, c=2.4))
    # les arcades froncées au-dessus des yeux (ombre douce), le diadème d'or et son émeraude
    for sg in (-1, 1):
        out.append(path(sm([(x + sg * 2, 492), (x + sg * 12, 491), (x + sg * 14, 494), (x + sg * 4, 495)], t=0.8),
                        STATUE['sh'], 0.7))
    dia = sm([(x - 9, 488), (x - 5, 485.5), (x, 482.5), (x + 5, 485.5), (x + 9, 488), (x, 488.8)], sharp=(0, 2, 4), t=0.7)
    out.append(vol(doc, dia, OR, r=0.8, c=0.8))
    out.append(path(sm([(x - 1.8, 486.5), (x, 484), (x + 1.8, 486.5), (x, 488.4)], t=0.9),
                    doc.lin(x + 2, 484, x - 2, 488, [(0, JADE['glow']), (1, JADE['deep'])])))
    # les orbites (le jade des yeux est un calque qui luit doucement)
    for ex, ey in YEUX:
        out.append(path(sm([(ex - 4.6, ey + 0.6), (ex - 1.6, ey - 2.2), (ex + 3.6, ey - 1.4), (ex + 4.6, ey + 0.8),
                            (ex + 1, ey + 2.6)], t=0.9), '#2a3434'))
    # le museau, les narines, la gueule ouverte (sombre) et les crochets d'ivoire
    out.append(path(sm([(x - 7, 507), (x, 505.5), (x + 7, 507), (x + 6, 515), (x, 517.5), (x - 6, 515)], t=0.9),
                    '#1a2426'))
    for sg in (-1, 1):
        out.append(path(rpoly([(x + sg * 4.6, 507.4), (x + sg * 2.8, 507.6), (x + sg * 3.9, 512.5)], 0.3), '#e8e2c4'))
        out.append('<circle cx="%s" cy="503" r="0.9" fill="#2a3434"/>' % fm(x + sg * 2.6))
    # de la mousse sur le haut du capuchon et sur l'anneau du haut
    for pts in ([(x - 14, 474), (x - 6, 469.5), (x + 4, 469), (x + 10, 471), (x + 4, 473), (x - 4, 476)],
                [(x - 30, R_HAUT - 22), (x - 22, R_HAUT - 28), (x - 10, R_HAUT - 28), (x - 14, R_HAUT - 24)],
                [(x + 18, R_HAUT - 26), (x + 30, R_HAUT - 22), (x + 34, R_HAUT - 17), (x + 26, R_HAUT - 20)]):
        out.append(vol(doc, sm(pts, t=0.9), MOUSSE, r=0.8, c=1.0))
    return ''.join(out)


def yeux(doc, ph):
    """Les yeux de jade du cobra : ils luisent doucement (une montée et une descente par boucle)."""
    k = 0.5 - 0.5 * math.cos(2 * math.pi * ph)
    out = []
    for ex, ey in YEUX:
        out.append('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/>' % (fm(ex), fm(ey), fm(7 + k), fm(5 + k * 0.6),
                   doc.rad(ex, ey, 7 + k, [(0, JADE['glow'], 0.25 + 0.3 * k), (1, JADE['mid'], 0)], ry=5 + k * 0.6)))
        eye = sm([(ex - 3.6, ey + 0.6), (ex - 1.2, ey - 1.6), (ex + 2.8, ey - 1.0), (ex + 3.6, ey + 0.6),
                  (ex + 0.8, ey + 1.9)], t=0.9)
        out.append(path(eye, doc.lin(ex + 3, ey - 2, ex - 3, ey + 2, [
            (0, mix(JADE['glow'], JADE['hot'], 0.5 * k)), (0.6, JADE['mid']), (1, JADE['deep'])])))
        out.append(path(rpoly([(ex - 0.5, ey - 1.5), (ex + 0.5, ey - 1.5), (ex + 0.4, ey + 1.6), (ex - 0.4, ey + 1.6)],
                              0.4), '#0c2418', 0.9))
    return ''.join(out)


element('yeux', -19, 'boucle', box=(COBRA_X - 16, 491, 32, 15), n=12, ms=400)(yeux)


# ---------------------------------------------------------------------------------------------------- les lianes
LIANES = [(34, R_HAUT + 16, 58), (74, R_HAUT + 16, 84), (192, R_HAUT + 18, 66)]   # (x, y d'attache, longueur)


def liane(k):
    x0, y0, ln = LIANES[k]

    def fn(doc, ph):
        a = 2 * math.pi * ph
        pts = []
        for i in range(13):
            v = i / 12
            sway = (3.2 * math.sin(a + k * 1.7) + 1.0 * math.sin(2 * a + v * 2)) * v ** 1.4
            pts.append((x0 + sway + 1.5 * math.sin(v * 5 + k), y0 + v * ln))
        ws = [1.8 - 0.9 * i / 12 for i in range(13)]
        out = [path(ribbon(pts, ws), '#2e5a3e')]
        # quelques feuilles le long (pas régulières)
        for j, (u, sg, L) in enumerate(((0.22, 1, 6), (0.45, -1, 5.5), (0.63, 1, 5), (0.86, -1, 4.5))):
            i = int(u * 12)
            px, py = pts[i]
            f = feuille_forme(px, py + 1, L, sg * 120 + 10 * math.sin(a + j), w=0.45)
            out.append(path(f, MOUSSE['base']))
            out.append(path(feuille_forme(px, py + 1, L * 0.7, sg * 120 + 10 * math.sin(a + j), w=0.22),
                            MOUSSE['light'], 0.6))
        return ''.join(out)
    return fn


for _k, (_x, _y, _l) in enumerate(LIANES):
    element('liane%d' % (_k + 1), -19, 'boucle', box=(_x - 12, _y - 2, 24, _l + 10), n=8, ms=300)(liane(_k))


# ---------------------------------------------------------------------------------------------------- la cascade
CASC = ((COBRA_X, 514), (COBRA_X + 1, 764), 8, 24)       # (haut, bas, largeur en haut, en bas)


def cascade(doc, ph):
    (xt, yt), (xb, yb), wt, wb = CASC
    c = resample(bez((xt, yt), (xt, yt + 30), (xb, yb - (yb - yt) * 0.6), (xb, yb)), 20)
    ws = [(wt + (wb - wt) * (i / 20) ** 0.8) * (1 + 0.05 * math.sin(i * 1.35) + 0.04 * math.sin(i * 2.9))
          for i in range(21)]
    left, right = sides(c, ws)
    body = sm([(xt - wt * 0.4, yt - 1), (xt + wt * 0.4, yt - 1)] + right[1:] +
              [(xb + wb * 0.62, yb + 2), (xb, yb + 4), (xb - wb * 0.62, yb + 2)] + left[1:][::-1], t=0.8)
    out = [path(body, doc.lin(xt + wt / 2, yt, xt - wt / 2, yb,
                              [(0, CHUTE['top']), (0.2, CHUTE['light']), (0.8, CHUTE['mid']), (1, CHUTE['light'])]))]
    cl = doc.clip(body.d())
    inner = []
    # le bord gauche (à l'ombre de la façade) plus foncé, le bord droit éclairé
    inner.append('<path d="%s" fill="%s" opacity="0.55" mask="%s"/>' % (body.d(), CHUTE['deep'],
                                                                          doc.minus(body.d(), wt * 0.35, 0)))
    inner.append('<path d="%s" fill="%s" opacity="0.5" mask="%s"/>' % (body.d(), CHUTE['top'],
                                                                         doc.minus(body.d(), -wt * 0.18, 0)))
    # des paquets d'eau qui descendent : taches allongées et douces, claires ou plus foncées, à des places et des
    # tailles différentes ; chacune fait un tour entier par boucle : sans couture
    span = yb - yt
    for j, (u, s0, ln, col, op) in enumerate((
            (-0.2, 0.00, 0.18, CHUTE['foam'], 0.55), (0.18, 0.14, 0.12, CHUTE['foam'], 0.45),
            (0.02, 0.33, 0.22, CHUTE['top'], 0.6), (-0.12, 0.52, 0.15, CHUTE['foam'], 0.5),
            (0.22, 0.67, 0.18, CHUTE['top'], 0.5), (-0.24, 0.81, 0.12, CHUTE['foam'], 0.45),
            (0.08, 0.9, 0.16, CHUTE['foam'], 0.4),
            (0.12, 0.24, 0.15, CHUTE['deep'], 0.3), (-0.16, 0.72, 0.13, CHUTE['deep'], 0.26))):
        v = (s0 + ph) % 1
        y = yt - span * ln * 0.5 + v * span * (1 + ln)
        f = min(1, max(0, (y - yt) / span))
        w = wt + (wb - wt) * f ** 0.8
        x = xt + (xb - xt) * f + u * w
        rx, ry = w * (0.16 + 0.05 * (j % 3)), span * ln * 0.5
        inner.append('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/>' % (
            fm(x), fm(y), fm(rx), fm(ry), doc.rad(x, y, rx, [(0, col, op), (0.6, col, op * 0.5), (1, col, 0)], ry=ry)))
    out.append('<g clip-path="%s">%s</g>' % (cl, ''.join(inner)))
    # la bouche : l'eau sort de la gueule, plus claire
    out.append('<ellipse cx="%s" cy="%s" rx="5" ry="3" fill="%s"/>' % (fm(xt), fm(yt + 2), doc.rad(
        xt, yt + 2, 5, [(0, CHUTE['foam'], 0.9), (1, CHUTE['top'], 0)], ry=3)))
    # le pied : l'écume qui bouillonne (des bosses qui gonflent et retombent, décalées) et le voile d'embruns
    out.append('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/>' % (fm(xb), fm(yb - 6), fm(wb * 1.6), fm(16),
               doc.rad(xb, yb - 6, wb * 1.6, [(0, '#e8f6e8', 0.45), (0.6, '#cfe6d4', 0.15), (1, '#b0d0c0', 0)], ry=16)))
    a = 2 * math.pi * ph
    bos = []
    for j, (dx, r) in enumerate(((-0.75, 4.2), (-0.35, 5.2), (0.05, 6.0), (0.45, 5.0), (0.85, 3.8))):
        rr = r * (0.85 + 0.2 * math.sin(a * 2 + j * 1.9))
        bos.append((xb + dx * wb, yb + 1 - rr * 0.6, rr))
    foot = sm([(xb - wb * 1.15, yb + 3)] + [(bx, by - rr * 0.6) for bx, by, rr in bos] + [(xb + wb * 1.15, yb + 3),
                                                                                         (xb, yb + 5)], t=0.9)
    out.append(vol(doc, foot, dict(base='#dcefe0', light='#f6fff6', rim='#ffffff', sh='#a8ccbc'), r=0.8, c=1.2))
    return ''.join(out)


element('cascade', -17, 'boucle', box=(COBRA_X - 32, 510, 66, 262), n=16, ms=150)(cascade)


# ---------------------------------------------------------------------------------------------------- la terrasse (droite)
T_HAUT = 700
SOCLE = (445, T_HAUT)
STATUE_PIED = (445, T_HAUT - 30)


def terrasse_forme():
    pts = [(390, 790), (389, 716), (394, 706), (400, T_HAUT), (604, T_HAUT), (604, 790)]
    return sm(pts, sharp=(0, 3, 4, 5), t=0.6)


def socle_formes():
    x, y = SOCLE
    pied = rpoly([(x - 26, y + 1), (x - 26, y - 5), (x + 26, y - 5), (x + 26, y + 1)], 1)
    corps = rpoly([(x - 22, y - 4), (x - 21, y - 25), (x + 21, y - 25), (x + 22, y - 4)], 1)
    dessus = rpoly([(x - 26, y - 24), (x - 25, y - 30), (x + 25, y - 30), (x + 26, y - 24)], 1.2)
    return pied, corps, dessus


def statue_formes():
    """Le guerrier pétrifié (tourné vers la gauche, vers l'arène), pied en STATUE_PIED : jambes en marche, pagne,
    torse, tête casquée à crête, le bouclier rond levé devant le visage, l'épée basse derrière lui."""
    X, Y = STATUE_PIED
    P = lambda pts: [(X + u, Y + v) for u, v in pts]
    jambe_d = rpoly(P([(1, -31), (9, -31), (12, -2), (17, 0), (4, 0), (2, -15)]), 1.5)
    jambe_g = rpoly(P([(-8, -31), (1, -31), (-5, -15), (-7, -2), (-18, 0), (-14, -3), (-12, -16)]), 1.5)
    pagne = rpoly(P([(-12, -26), (12, -26), (10, -39), (-10, -39)]), 2)
    torse = sm(P([(-10, -38), (10, -38), (13, -52), (9, -58), (-7, -58), (-12, -52)]), t=0.8)
    bras_epee = ribbon(resample(P([(8, -54), (13, -47), (16, -40)]), 6), [3.4, 3.4, 3.2, 3, 2.8, 2.8, 2.6])
    epee = rpoly(P([(15, -41), (18, -42), (27, -22), (25.5, -20.5)]), 0.5)
    tete = sm(P([(-6, -58), (-7, -65), (-3, -71), (3, -71), (6, -66), (5, -59)]), t=0.9)
    crete = sm(P([(-3, -70), (2, -76), (9, -76), (14, -70), (10, -71), (4, -71)]), t=0.8)
    bras_bouclier = ribbon(resample(P([(-6, -54), (-12, -58), (-16, -62)]), 6), [3.6, 3.6, 3.4, 3.2, 3, 3, 2.8])
    bouclier = ellipse(X - 18, Y - 63, 9, 12.5)
    return jambe_d, jambe_g, pagne, torse, bras_epee, epee, tete, crete, bras_bouclier, bouclier


def signe_forme(cx, cy, k):
    """Le signe de Méduse : un œil en amande à pupille fendue, d'où montent trois petits serpents ondulés
    (le regard qui pétrifie, couronné des serpents de la reine). Aucune lettre ; la pupille est un creux."""
    def P(u, v):
        return (cx + u * k, cy + v * k)
    oeil = sm([P(-5, 1.4), P(-2.6, -1.2), P(0, -1.9), P(2.6, -1.2), P(5, 1.4), P(2.6, 3.6), P(0, 4.2), P(-2.6, 3.6)],
              sharp=(0, 4), t=0.9)
    pupille = sm([P(0, -0.9), P(0.75, 1.1), P(0, 3.2), P(-0.75, 1.1)], t=0.8).rev()
    s = oeil + pupille
    for dx, h_, sg in ((-2.8, 4.8, -1), (0, 6.0, 1), (2.8, 4.8, 1)):
        c = [(cx + (dx + 0.7 * sg * math.sin(i * 1.4)) * k, cy + (-2.0 - h_ * i / 6) * k) for i in range(7)]
        s = s + ribbon(c, [0.75 * k, 0.8 * k, 0.75 * k, 0.65 * k, 0.55 * k, 0.75 * k, 0.15 * k])
    return s


@element('terrasse', -20, 'fixe')
def terrasse(doc):
    out = []
    forme = terrasse_forme()
    g = doc.lin(604, 690, 380, 790, [(0, RUINE['light']), (0.45, RUINE['base']), (1, RUINE['sh'])])
    out.append(vol(doc, forme, RUINE, grad=g, r=2.4, c=4.0, ink=INK, iw=1.0))
    inner = []
    inner.append(path(rpoly([(388, T_HAUT), (606, T_HAUT), (606, T_HAUT + 3), (388, T_HAUT + 3)], 0.5), RUINE['rim'], 0.5))
    inner.append(path(rpoly([(386, T_HAUT + 9), (606, T_HAUT + 9), (606, T_HAUT + 16), (386, T_HAUT + 16)], 2),
                      doc.lin(0, T_HAUT + 9, 0, T_HAUT + 16, [(0, RUINE['sh'], 0.8), (1, RUINE['sh'], 0)])))
    for pts in (([(404, 728), (450, 726), (500, 729)]), ([(520, 726), (604, 728)]), ([(470, 728), (472, 760)]),
                ([(560, 728), (558, 760)])):
        cc = resample(pts, 8)
        wl = [1.1 * (0.3 + 0.7 * math.sin(math.pi * i / 8) ** 0.5) for i in range(9)]
        inner.append(path(ribbon(cc, wl), RUINE['sh'], 0.6))
        inner.append(path(ribbon([(x - 0.8, y - 1) for x, y in cc], [w * 0.5 for w in wl]), RUINE['rim'], 0.25))
    inner.append(path('M380 718H610V800H380Z', doc.lin(0, 718, 0, 760, [(0, MOUSSE['sh'], 0), (1, MOUSSE['sh'], 0.5)])))
    out.append('<g clip-path="%s">%s</g>' % (doc.clip(forme.d()), ''.join(inner)))
    # la mousse sur le rebord
    for pts in ([(398, T_HAUT + 1), (404, T_HAUT - 2), (424, T_HAUT - 2.5), (434, T_HAUT + 1), (424, T_HAUT + 7),
                 (412, T_HAUT + 4), (404, T_HAUT + 9)],
                [(530, T_HAUT + 1), (540, T_HAUT - 2), (566, T_HAUT - 2), (574, T_HAUT + 1), (562, T_HAUT + 6),
                 (548, T_HAUT + 4)]):
        out.append(vol(doc, sm(pts, t=0.85), MOUSSE, r=1.0, c=1.4))
    # la colonne brisée (vue seulement à l'accueil : le combat coupe à x = 506)
    cx = 548
    col = sm([(cx - 9, T_HAUT + 1), (cx - 9, 640), (cx - 6, 634), (cx - 1, 638), (cx + 3, 630), (cx + 9, 636),
              (cx + 9, T_HAUT + 1)], sharp=(0, 6), t=0.7)
    base = rpoly([(cx - 13, T_HAUT + 1), (cx - 12, T_HAUT - 6), (cx + 12, T_HAUT - 6), (cx + 13, T_HAUT + 1)], 1)
    out.append(contour((col, base), 0.9))
    out.append(vol(doc, col, STATUE, r=1.4, c=2.2))
    out.append(vol(doc, base, STATUE, r=1.0, c=1.4))
    out.append(vol(doc, sm([(cx - 9, 662), (cx - 4, 656), (cx + 4, 658), (cx + 9, 654), (cx + 9, 662), (cx - 2, 666)],
                           t=0.9), MOUSSE, r=0.8, c=1.0))
    # le socle, le guerrier pétrifié
    pied, corps, dessus = socle_formes()
    parts = statue_formes()
    out.append(contour((pied, corps, dessus) + parts, 1.0))
    for s in (pied, corps, dessus):
        out.append(vol(doc, s, RUINE, r=1.4, c=2.0))
    x, y = SOCLE
    out.append(path(rpoly([(x - 26, y - 24), (x + 26, y - 24), (x + 26, y - 22), (x - 26, y - 22)], 0.5), OR['sh'], 0.7))
    out.append(path(rpoly([(x - 10, y - 21), (x + 10, y - 21), (x + 10, y - 7), (x - 10, y - 7)], 1.2), '#2e3a3a'))
    jd, jg, pagne, torse, be, epee, tete, crete, bb, bouc = parts
    # derrière : la jambe et le bras de l'épée (un peu plus sombres) ; devant : le reste
    for s, m in ((jd, dict(STATUE, base='#66726a', light='#7a8678')), (be, dict(STATUE, base='#66726a', light='#7a8678')),
                 (epee, STATUE), (jg, STATUE), (pagne, STATUE), (torse, STATUE), (crete, STATUE), (tete, STATUE),
                 (bb, STATUE), (bouc, STATUE)):
        out.append(vol(doc, s, m, r=1.2, c=1.8))
    X, Y = STATUE_PIED
    # le bouclier : sa bosse au milieu, son bord en relief (côté lumière)
    out.append(path(ellipse(X - 18, Y - 63, 3.2, 4.4), STATUE['light'], 0.8))
    out.append(path(ellipse(X - 18.6, Y - 62.4, 2.0, 2.8), STATUE['sh'], 0.35))
    # l'ombre douce entre le pagne et les jambes, entre le bouclier et le torse
    out.append(path(rpoly([(X - 11, Y - 27), (X + 11, Y - 27), (X + 9, Y - 24), (X - 9, Y - 24)], 1), STATUE['sh'], 0.45))
    # une fêlure qui se tord sur le torse, une sur la jambe (la pierre du regard de Méduse)
    for pts in ([(X + 2, Y - 56), (X - 1, Y - 50), (X + 3, Y - 45), (X + 1, Y - 40)], [(X - 5, Y - 24), (X - 8, Y - 17),
                                                                                         (X - 7, Y - 10)]):
        cc = resample(pts, 8)
        out.append(path(ribbon(cc, [0.2, 0.6, 0.8, 0.8, 0.7, 0.6, 0.5, 0.4, 0.1]), STATUE['sh'], 0.85))
    # de la mousse posée sur l'épaule, le casque et le haut du socle
    for pts in ([(X + 2, Y - 58), (X + 8, Y - 60), (X + 13, Y - 54), (X + 8, Y - 55)],
                [(X - 4, Y - 71), (X + 1, Y - 73), (X + 5, Y - 71), (X, Y - 69.5)],
                [(x + 6, y - 29.5), (x + 14, y - 32), (x + 24, y - 31), (x + 26, y - 28), (x + 16, y - 28.5)]):
        out.append(vol(doc, sm(pts, t=0.9), MOUSSE, r=0.7, c=0.9))
    return ''.join(out)


def signe(doc, ph):
    x, y = SOCLE
    k = 0.5 - 0.5 * math.cos(2 * math.pi * ph)
    cy = y - 14
    out = ['<ellipse cx="%s" cy="%s" rx="11" ry="9" fill="%s"/>' % (x, cy, doc.rad(
        x, cy, 11, [(0, JADE['glow'], 0.2 + 0.3 * k), (1, JADE['mid'], 0)], ry=9))]
    out.append(path(signe_forme(x, cy + 1.6, 1.05), mix(JADE['deep'], JADE['glow'], 0.35 + 0.55 * k), extra=EO))
    return ''.join(out)


element('signe', -19, 'boucle', box=(SOCLE[0] - 12, SOCLE[1] - 24, 24, 20), n=12, ms=400)(signe)


# ---------------------------------------------------------------------------------------------------- les bannières
MATS = [(102, R_HAUT), (404, T_HAUT), (486, T_HAUT)]
MAT_H = 52


def mat(doc, x, y):
    bois = dict(base='#5a4632', light='#76603e', rim='#b09a6a', sh='#3a2c24')
    hampe = rpoly([(x - 1.4, y + 1), (x - 1.4, y - MAT_H), (x + 1.4, y - MAT_H), (x + 1.4, y + 1)], 0.6)
    trav = rpoly([(x - 13, y - MAT_H + 2), (x + 13, y - MAT_H + 2), (x + 13, y - MAT_H + 5), (x - 13, y - MAT_H + 5)], 1.2)
    pied = rpoly([(x - 6, y + 2), (x - 5, y - 3), (x + 5, y - 3.5), (x + 7, y + 2)], 1.2)
    out = [contour((hampe, trav, pied), 0.7), vol(doc, hampe, bois, r=0.7, c=0.8), vol(doc, trav, bois, r=0.7, c=0.8),
           vol(doc, pied, ROC, r=0.8, c=1.0)]
    out.append('<circle cx="%s" cy="%s" r="2.6" fill="%s" stroke="%s" stroke-width="1.2"/>' % (
        x, y - MAT_H - 1, doc.rad(x + 1, y - MAT_H - 2, 3, [(0, '#fff0b0'), (1, '#c8963a')]), INK))
    return ''.join(out)


def banniere(k):
    x, y = MATS[k]
    top = y - MAT_H + 5

    def fn(doc, ph):
        # la toile pend sous la traverse ; elle ondule doucement (plus en bas qu'en haut), le vent vient de la droite
        L, w_ = 34, 22
        a = 2 * math.pi * ph

        def P(u, v):          # u : -1..1 en travers, v : 0..1 en descendant
            sway = v ** 1.5 * (2.2 * math.sin(a + v * 2.2 + k) - 1.1)
            return (x + u * w_ / 2 * (1 - 0.08 * v) + sway, top + v * L + 0.8 * math.sin(a + u * 1.5 + k) * v)
        pts = [P(-1, 0), P(1, 0)]
        for v in (0.33, 0.66, 0.92):
            pts.append(P(1, v))
        pts += [P(1, 1.04), P(0.5, 0.9), P(0, 1.08), P(-0.5, 0.9), P(-1, 1.04)]
        for v in (0.92, 0.66, 0.33):
            pts.append(P(-1, v))
        s = sm(pts, sharp=(0, 1, 5, 7, 9), t=0.6)
        out = [mat(doc, x, y), vol(doc, s, VIOLET, r=1.3, c=2.0, ink=INK, iw=0.9)]
        sx, sy = P(0, 0.42)
        out.append(path(signe_forme(sx, sy + 2, 1.15), '#e8c060', extra=EO))
        return ''.join(out)
    return fn


for _k in range(3):
    _x, _y = MATS[_k]
    element('banniere%d' % (_k + 1), -16, 'boucle', box=(_x - 20, _y - MAT_H - 5, 40, MAT_H + 10), n=12,
            ms=200)(banniere(_k))


# ---------------------------------------------------------------------------------------------------- l'eau
EAU_BOX = (0, 744, 590, 44)
EAU_T = (192, 44)


def nenuphar(doc, cx, cy, r, rot, fleur=False):
    """Une feuille de nénuphar vue de biais (aplatie), son encoche ; parfois une fleur pâle posée dessus."""
    s = []
    for i in range(14):
        a = math.radians(rot + 22 + i * (316 / 13))
        s.append((cx + r * math.cos(a), cy + r * 0.38 * math.sin(a)))
    s.append((cx, cy))
    f = sm(s, sharp=(0, 13, 14), t=0.9)
    out = [path(f.move(0, 1.2), EAU['dark'], 0.55),
           path(f, doc.lin(cx + r, cy - r * 0.4, cx - r, cy + r * 0.4, [(0, '#5e9a5a'), (1, '#3c744a')]))]
    if fleur:
        for dx, h_ in ((-1.6, 3.2), (1.6, 3.2), (0, 4.4)):
            out.append(path(sm([(cx + dx - 1.4, cy - 0.5), (cx + dx, cy - h_), (cx + dx + 1.4, cy - 0.5)], sharp=(1,),
                               t=0.8), '#f2e6ee' if dx >= 0 else '#d8c4d6'))
        out.append('<circle cx="%s" cy="%s" r="0.9" fill="#f0d070"/>' % (fm(cx), fm(cy - 1)))
    return ''.join(out)


def eau_tuile(doc):
    """La tuile de l'eau verte (192 × 44), qui se répète exactement en x : le lointain plus clair (le ciel s'y
    reflète), des reflets doux allongés, des nénuphars."""
    tw, th = EAU_T
    out = [path('M0 0H%dV%dH0Z' % (tw, th), doc.lin(0, 0, 0, th, [
        (0, '#7aa88c'), (0.25, '#4a8a74'), (0.6, EAU['mid']), (1, EAU['deep'])]))]
    rnd = hasard(5)
    for x, y, w_, op in ((20, 9, 40, 0.35), (110, 6, 52, 0.3), (70, 18, 30, 0.22), (160, 20, 36, 0.24),
                         (36, 31, 28, 0.16), (128, 34, 40, 0.15)):
        for dx in (-tw, 0, tw):
            out.append('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/>' % (
                fm(x + dx), fm(y), fm(w_ / 2), fm(1.2 + y / 30), doc.rad(x + dx, y, w_ / 2, [
                    (0, EAU['hi'], op), (1, EAU['hi'], 0)], ry=1.2 + y / 30)))
    for x, y, r, rot, fl in ((46, 22, 7, 10, False), (138, 30, 9, 200, True), (98, 38, 6, 120, False),
                             (176, 14, 5, 60, False)):
        for dx in (-tw, 0, tw):
            out.append(nenuphar(doc, x + dx, y, r, rot, fl))
    return ''.join(out)


def eau(doc, off):
    x, y, w, h = EAU_BOX
    tw, th = EAU_T
    out = []
    for k in range(-1, w // tw + 2):
        out.append('<g transform="translate(%s %s)">%s</g>' % (fm(x + k * tw + off), fm(y), eau_tuile(doc)))
    return '<g clip-path="%s">%s</g>' % (doc.clip('M%d %dH%dV%dH%dZ' % (x, y, x + w, y + h, x)), ''.join(out))


element('eau', -18, 'defile', box=EAU_BOX, tuile=EAU_T, vx=10.0, vy=0.0, dessin=eau, tuile_dessin=eau_tuile)


@element('rives', -17.5, 'morceau', box=(0, 740, 590, P0 - 740))
def rives(doc):
    """La rive d'en face (le pied des ruines dans l'eau, un fil sombre) et la rive proche : les marches à demi noyées
    qui montent à l'arène."""
    out = []
    loin = sm([(-10, 740), (600, 740), (600, 745), (520, 746), (430, 744), (330, 746), (240, 745), (150, 747),
               (60, 745), (-10, 746)], sharp=(0, 1), t=0.7)
    out.append(path(loin, '#2a4a46', 0.7))
    # la marche basse, à fleur d'eau
    pts = [(-10, P0 + 4), (-10, 784), (40, 782), (110, 784), (190, 781), (270, 783), (350, 781), (430, 783),
           (510, 781), (600, 783), (600, P0 + 4)]
    s = sm(pts, sharp=(0, 1, len(pts) - 2, len(pts) - 1), t=0.7)
    out.append(vol(doc, s, RUINE, grad=doc.lin(0, 781, 0, P0, [(0, '#76806c'), (0.4, '#56625a'), (1, '#3e4a48')]),
                   r=1.2, c=0))
    out.append(path(rpoly([(-10, 789), (600, 789), (600, 792), (-10, 792)], 1), doc.lin(0, 789, 0, 792, [
        (0, '#2e3a3a', 0.5), (1, '#2e3a3a', 0)])))
    # l'eau qui lèche la marche (un liseré clair irrégulier)
    lis = [(x, 783.4 + 0.8 * math.sin(x / 13) + 0.5 * math.sin(x / 5.3)) for x in range(-10, 604, 6)]
    out.append(path(ribbon(lis, [0.3] + [0.9 + 0.4 * math.sin(i * 0.7) for i in range(len(lis) - 2)] + [0.3]),
                    '#c4dcb8', 0.5))
    # la corniche de l'arène et quelques touffes de mousse et pierres posées
    out.append(path('M-10 %dH600V%dH-10Z' % (P0 - 2, P0), '#26302e', 0.8))
    for x, w_, h_ in ((22, 24, 7), (250, 16, 5), (548, 28, 8)):
        y = P0 - 1
        s = sm([(x - w_ / 2, y), (x - w_ * 0.3, y - h_), (x + w_ * 0.2, y - h_ * 1.05), (x + w_ / 2, y)],
               sharp=(0, 3), t=0.8)
        out.append(vol(doc, s, ROC, r=1.0, c=1.4))
    for x, w_ in ((60, 18), (330, 14), (470, 20)):
        y = P0 - 0.5
        s = sm([(x - w_ / 2, y), (x - w_ * 0.25, y - 4.5), (x + w_ * 0.1, y - 5.5), (x + w_ * 0.4, y - 3.5),
                (x + w_ / 2, y)], sharp=(0, 4), t=0.9)
        out.append(vol(doc, s, MOUSSE, r=0.8, c=1.0))
    return ''.join(out)


# ---------------------------------------------------------------------------------------------------- l'arène
def sol_x(g, y):
    """Le dallage en perspective : la coordonnée au sol g → x à l'écran (les joints filent vers le centre)."""
    k = (y - 600) / (P1 - 600)
    return 295 + g * k


@element('arene', -15.5, 'fixe')
def arene(doc):
    out = []
    # le dessus : un rectangle d'un bord à l'autre, une seule valeur moyenne qui s'éclaire à peine vers l'avant et
    # vers la droite (la lumière)
    out.append(path('M-10 %dH600V%dH-10Z' % (P0, P1), doc.lin(0, P0, 0, P1, [(0, SOL['back']), (1, SOL['front'])])))
    out.append(path('M-10 %dH600V%dH-10Z' % (P0, P1), doc.lin(0, 0, 590, 0, [(0, '#16262a', 0.06),
                                                                              (1, '#f6f8e0', 0.04)])))
    # les dalles : des joints à peine marqués (rangs plus hauts devant), décalés d'un rang à l'autre
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
    out.append('<path d="%s" fill="none" stroke="#f6faea" stroke-width="1.2" opacity="0.05" '
               'transform="translate(0.8 0.8)"/>' % jd)
    out.append('<path d="%s" fill="none" stroke="#1e2c2c" stroke-width="1" opacity="0.11"/>' % jd)
    # quelques dalles un peu plus claires ou plus sombres, un peu de mousse vers les bords (très peu)
    for (g0, i, col, op) in ((-220, 1, '#f6f8e6', 0.035), (60, 3, '#1e2c2c', 0.04), (300, 2, '#f6f8e6', 0.03),
                             (-90, 4, '#1e2c2c', 0.035), (180, 5, '#f6f8e6', 0.03), (-420, 2, '#3a7446', 0.06),
                             (380, 4, '#3a7446', 0.05)):
        ya, yb = rows[i] + 1, rows[i + 1] - 1
        pts = [(sol_x(g0, ya), ya), (sol_x(g0 + 140, ya), ya), (sol_x(g0 + 140, yb), yb), (sol_x(g0, yb), yb)]
        out.append(path(rpoly(pts, 2), col, op))
    # le bord arrière : l'arête éclairée
    out.append(path('M-10 %dH600V%dH-10Z' % (P0, P0 + 1.6), '#9aa48e', 0.7))
    # le reflet vert de l'eau sur le fond du dallage (doux)
    out.append(path('M-10 %dH600V%dH-10Z' % (P0, P0 + 24), doc.lin(0, P0, 0, P0 + 24, [(0, '#2e6e5e', 0.10),
                                                                                       (1, '#2e6e5e', 0)])))
    # l'arête avant éclairée, puis le flanc de pierre (sa frise en vague a disparu : sous les cartes, rien qui bouge)
    out.append(path('M-10 %dH600V%dH-10Z' % (P1, 1064), doc.lin(0, P1, 0, 1064, [
        (0, '#4e5a54'), (0.6, '#46524e'), (1, '#33433e')])))
    out.append(path('M-10 %dH600V%dH-10Z' % (P1 - 1, P1 + 1.6), '#a8b098', 0.85))
    for g in range(-600, 700, 160):
        x = sol_x(g, P1)
        out.append(path(rpoly([(x - 0.6, P1 + 2), (x + 0.6, P1 + 2), (x + 0.6, 1060), (x - 0.6, 1060)], 0.3),
                        '#1e2c2c', 0.35))
    return ''.join(out)


@element('dessous', -15.4, 'fixe')
def dessous(doc):
    """Sous le flanc de l'arène : en combat, c'est sous les cartes des héros (y > 985) ; donc simple et sombre, l'eau
    profonde du temple, sans détail (l'accueil, qui la montre, garde un bas calme)."""
    out = [path('M-10 1062H600V1104H-10Z', doc.lin(0, 1062, 0, 1100, [(0, '#24504a'), (0.35, '#1a3c3a'),
                                                                     (1, '#132c2e')]))]
    pts = [(-10, 1058), (600, 1058), (600, 1064)]
    x, i = 600, 0
    while x > -10:
        x -= 22 + 9 * math.sin(i * 1.7)
        pts.append((x, 1064 + 2 * math.sin(i * 2.3) + 1.2 * math.cos(i * 1.1)))
        i += 1
    pts.append((-10, 1064))
    out.append(path(sm(pts, sharp=(0, 1), t=0.7), doc.lin(0, 1058, 0, 1068, [(0, '#3a4a46'), (1, '#2c3c3a')])))
    return ''.join(out)


# ---------------------------------------------------------------------------------------------------- particules
def luciole_image(doc, i, n):
    t = i / (n - 1)
    op = math.sin(math.pi * (0.08 + 0.84 * t))
    return ('<circle cx="6" cy="6" r="5" fill="%s"/><circle cx="6" cy="6" r="1.2" fill="%s" opacity="%g"/>' % (
        doc.rad(6, 6, 5, [(0, '#f4f4a0', 0.6 * op), (1, '#d8e870', 0)]), '#fffde0', op))


element('lucioles', -14, 'particules', taille=(12, 12), images=6, dessin=luciole_image, zone=(110, 704, 480, 772),
        nombre=6, vie=(2600, 3800), vx=(-4, 4), vy=(-6, -2), ondule=(3, 2200))


def feuille_image(doc, i, n):
    """Une feuille qui tombe en tournoyant (une image de sa vie : elle se retourne, et s'efface à la fin)."""
    t = i / (n - 1)
    a = 360 * t * 1.5
    sq = math.cos(math.radians(a))
    op = min(1, 4 * t) if t < 0.25 else (1 if t < 0.8 else (1 - t) / 0.2 * 0.9 + 0.1)
    col = MOUSSE['light'] if sq > 0 else MOUSSE['sh']
    f = feuille_forme(0, 3.5, 7, 0, w=0.42)
    return '<g opacity="%g" transform="translate(7 7) rotate(%s) scale(%s 1)">%s</g>' % (
        op, fm(30 * math.sin(2 * math.pi * t)), fm(max(0.15, abs(sq))), path(f, col))


element('feuilles', -14, 'particules', taille=(14, 14), images=10, dessin=feuille_image, zone=(130, 590, 460, 640),
        nombre=3, vie=(5200, 6400), vx=(-5, 5), vy=(18, 21), ondule=(6, 2400))


def brume_image(doc, i, n):
    """Une écharpe de brume (une image de sa vie : elle apparaît, s'étire et s'efface)."""
    t = i / (n - 1)
    op = math.sin(math.pi * (0.05 + 0.9 * t)) ** 1.2
    w_, h_ = 70 + 20 * t, 9
    out = []
    for dx, dy, k in ((-0.35, 0.2, 0.6), (0.1, -0.1, 1.0), (0.42, 0.15, 0.7)):
        cx, cy = 60 + dx * w_, 15 + dy * h_
        out.append('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/>' % (
            fm(cx), fm(cy), fm(w_ * 0.5 * k), fm(h_ * k), doc.rad(cx, cy, w_ * 0.5 * k, [
                (0, '#c8d6b0', 0.32 * op), (0.6, '#b4c8a4', 0.14 * op), (1, '#a4bc98', 0)], ry=h_ * k)))
    return ''.join(out)


element('brume', -23, 'particules', taille=(120, 30), images=8, dessin=brume_image, zone=(220, 640, 380, 690),
        nombre=3, vie=(9000, 12000), vx=(3, 6), vy=(-0.4, 0.2), ondule=(0, 9000))


# ---------------------------------------------------------------------------------------------------- premier plan
@element('feuilles-gauche', 1300, 'morceau', box=(0, 1012, 92, 88))
def feuilles_g(doc):
    """Dans le coin bas gauche (caché en combat par les cartes) : de grandes feuilles sombres de la jungle."""
    fs = [feuille_forme(8, 1104, 70, 28, w=0.36), feuille_forme(-4, 1104, 62, 52, w=0.34),
          feuille_forme(26, 1104, 52, 12, w=0.38)]
    out = [contour(fs, 1.1)]
    for k, f in enumerate(fs):
        out.append(vol(doc, f, FEUILLE if k != 2 else dict(FEUILLE, base='#356848', light='#447a50'), r=1.6, c=2.4))
    return ''.join(out)


@element('bloc-droite', 1300, 'morceau', box=(516, 1026, 74, 74))
def bloc_d(doc):
    """Dans le coin bas droit : un bloc du temple tombé, couvert de mousse."""
    s = rpoly([(522, 1104), (528, 1046), (586, 1036), (606, 1042), (606, 1104)], 5)
    m = sm([(526, 1052), (546, 1040), (576, 1034), (600, 1036), (606, 1046), (590, 1050), (566, 1047), (548, 1056),
            (534, 1060)], t=0.85)
    out = [contour((s, m), 1.1), vol(doc, s, RUINE, r=2.0, c=3.0), vol(doc, m, MOUSSE, r=1.2, c=1.6)]
    return ''.join(out)


# ---------------------------------------------------------------------------------------------------- les serpents ailés
# La touche vivante (comme les dragons de Kael) : trois grands serpents ailés lointains, aux ailes de plumes, qui
# planent dans la brume du ciel ; plus loin = plus petit, plus pâle et plus lent. Chacun est une particule seule qui
# vit une période entière : il naît caché (hors de l'image, ou derrière un banc de brume) et finit caché ; son corps
# ondule et ses ailes battent lentement (12 images en boucle). Les bancs où ils se cachent sont remis devant eux
# (morceaux « devant-… »). Ils restent au-dessus de y = 470 : ni devant les personnages, ni sur l'arène.
SERPENTS = [
    # id, y, échelle, x de départ, x d'arrivée, montée (px/s), couleur, opacité, profondeur
    ('serpent1', 420, 0.52, -70, 660, -0.4, '#1a3640', 0.9, -29.73),       # le plus proche : de bord à bord
    ('serpent2', 452, 0.28, 640, 48, 0.0, '#284a52', 0.78, -29.74),        # entre à droite, va se cacher dans la brume
    ('serpent3', 397, 0.18, 352, -40, 0.0, '#30545a', 0.7, -29.75),       # le plus loin : sort d'un petit banc
]
SERP_N, SERP_MS = 12, 160
T_VUE = 17600                                   # l'instant des images fixes : les trois serpents bien séparés                       # un battement d'ailes = 1,92 s
SERP_BOITE = (-98, -84, 172, 122)               # la silhouette (repère local, tête à droite) : x, y, w, h


def serp_aile(ph, near=True):
    """Une aile de plumes (repère local, tête à droite) : le bras (épaule, coude, poignet) et les grandes plumes
    arrondies au bout ; ph : le battement (0 = en haut, 0,5 = en bas)."""
    a = 2 * math.pi * ph
    f = 0.3 + 0.7 * math.cos(a)
    sx = 0.85 + 0.15 * abs(f)
    S = (2, -2) if near else (8, -3)
    k = 1.3 if near else 1.1

    def P(dx, dy):
        return (S[0] + dx * sx * k, S[1] + dy * f * k)
    loc = [(0, 0), (-2, -18), (8, -38), (7, -60),               # le bord d'attaque jusqu'à la pointe
           (1, -57), (-6, -60), (-11, -54), (-18, -56), (-23, -48), (-31, -48), (-33, -39), (-40, -36), (-37, -26),
           (-32, -12), (-22, -3)]
    return sm([P(x, y) for x, y in loc], sharp=(0, 3, 4, 6, 8, 10, 12), t=0.9)


def serp_corps(ph):
    """Le corps qui ondule (une vague qui court de la tête à la queue), la tête à crête et l'éventail de la queue."""
    a = 2 * math.pi * ph
    c = []
    for i in range(29):
        u = i / 28                                   # 0 : la queue, 1 : le cou
        x = -76 + 126 * u
        amp = 1.5 + 6.5 * (1 - u) ** 1.2
        c.append((x, amp * math.sin(2 * math.pi * 1.25 * u + a) - 1.5 * u))
    ws = []
    for i in range(29):
        u = i / 28
        ws.append(1.2 + 9.0 * math.sin(math.pi * min(1, u / 0.62)) ** 0.8 if u < 0.62 else 10.2 - 3.4 * (u - 0.62) / 0.38)
    corps = ribbon(c, ws)
    hx, hy = c[-1]
    tete = sm([(hx - 3, hy - 4.6), (hx + 7, hy - 5.4), (hx + 15, hy - 1.6), (hx + 19, hy + 1), (hx + 10, hy + 3.4),
               (hx - 2, hy + 4.6)], sharp=(3,), t=0.8)
    cretes = [ribbon([(hx + 2, hy - 3.2), (hx - 5, hy - 9), (hx - 13, hy - 11)], [1.6, 1.0, 0.2]),
              ribbon([(hx + 5, hy - 3.6), (hx + 1, hy - 11), (hx - 4, hy - 15)], [1.4, 0.9, 0.2])]
    tx, ty = c[0]
    queue = [sm([(tx + 2, ty - 1), (tx - 8, ty - 8 + dy), (tx - 16, ty - 9 + dy * 1.4), (tx - 14, ty - 5 + dy),
                 (tx - 6, ty + 1)], sharp=(0, 4), t=0.8) for dy in (0, 6, 12)]
    return [corps, tete] + cretes + queue


def serpent_image(id_):
    _, y, k, x0, x1, vy, col, op, _ = next(d for d in SERPENTS if d[0] == id_)
    sg = 1 if x1 > x0 else -1
    bx, by, bw, bh = SERP_BOITE
    w, h = bw * k + 4, bh * k + 4

    def fn(doc, i, n):
        ph = i / n
        loin = mix(col, '#4e7672', 0.35)                   # l'aile lointaine, plus dans la brume
        ox = w / 2 - (bx + bw / 2) * k * sg
        oy = h / 2 - (by + bh / 2) * k
        out = ['<g transform="translate(%s %s) scale(%s %s)">' % (fm(ox), fm(oy), fm(k * sg), fm(k))]
        out.append(path(serp_aile(ph, False), loin, 0.9))
        out.extend(path(p_, col) for p_ in serp_corps(ph))
        out.append(path(serp_aile(ph, True), col, 0.95))
        out.append('</g>')
        return '<g opacity="%g">%s</g>' % (op, ''.join(out))
    return fn, (round(w), round(h))


for _d in SERPENTS:
    _fn, _t = serpent_image(_d[0])
    _vx = (_d[4] - _d[3]) * 1000 / PERIODE
    element(_d[0], _d[8], 'particules', taille=_t, images=SERP_N, ms=SERP_MS, dessin=_fn,
            zone=(_d[3], _d[1], _d[3], _d[1]), nombre=1, vie=(PERIODE, PERIODE), vx=(_vx, _vx), vy=(_d[5], _d[5]),
            ondule=(0, PERIODE))


def devant_nuage(k):
    """Un banc de brume remis devant les serpents (dans le jeu, les particules se posent sur l'image fixe)."""
    x0, x1, yb, lobes = NUAGES_BAS[k]
    top = min(cy - r for _, cy, r in lobes) - 4
    box = (x0 - 4, top, x1 - x0 + 8, yb + 6 - top)

    def fn(doc):
        return nuage_bas(doc, k)
    return box, fn


for _k in NUAGES_BAS:
    _box, _fn = devant_nuage(_k)
    element('devant-nuage-' + _k, -29.4, 'morceau', box=_box)(_fn)


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
# Côté héros : Méduse (myths-4, la générale du clan) au fond, Rocvar (dragon-terre) au milieu, Aurelle (angels-10)
# devant ; en face, les trois monstres du clan de Méduse (guerrier serpent, naga au bouclier, prêtresse), retournés.
PERSOS = [('myths-4', 'heros', 0), ('dragon-terre', 'heros', 2), ('angels-10', 'heros', 4),
          ('mon-meduse-rapide', 'ennemis', 0), ('mon-meduse-costaud', 'ennemis', 2), ('mon-meduse-sorts', 'ennemis', 4)]


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
    # le fond entier pour le propriétaire (les dragons en vol)
    rendre([(scene(T_VUE), os.path.join(SORTIE, 'fond.png'))], W * UP, H * UP)
    planche, meta = calques()
    planche.save(os.path.join(JEU, CLAN + '-anim.webp'), quality=90, alpha_quality=100, method=6)
    planche.save(os.path.join(TMP, 'planche.png'))
    doc = {
        'clan': CLAN, 'style': 'vecto', 'w': W, 'h': H, 'up': UP, 'unite': round(UNIT, 5),
        'image': 'art/vecto/fonds/%s.webp' % CLAN, 'planche': 'art/vecto/fonds/%s-anim.webp' % CLAN,
        'note': ('Coordonnées x, y, w, h, zone en pixels du fond (590 × 1100) ; cases et tuiles en pixels de la '
                 'planche (×up). L\'image fixe ne contient que ce qui ne bouge pas : chaque calque animé se pose '
                 'dessus, entier (transparent autour). Images lisses : agrandir en LINÉAIRE. Boucle : images changées '
                 'toutes les ms (ms 0 = un morceau remis devant). Défilé : la tuile coule à vx, vy px du fond par '
                 'seconde. Particules : la règle de fond-px.ts (hasard rng("' + CLAN + '-" + id)), centre en (x, y), images '
                 'sur la vie ou en boucle toutes les ms. Branché dans le jeu derrière ?vecto=1 (src/game/fond-vecto.ts).'),
        'reperes': {'hz': HZ, 'p0': P0, 'p1': P1, 'rangs_combat': [round(r, 1) for r in RANGS_COMBAT],
                    'rangs_accueil': list(RANGS), 'cartes': round(CARTES, 1), 'vue_x': [round(v, 1) for v in VUE_X]},
        'periode_ms': PERIODE, 'planche_taille': list(planche.size), 'calques': meta}
    json.dump(doc, open(os.path.join(HERE, 'fond-%s.json' % CLAN), 'w'), indent=1, ensure_ascii=False)
    ecrire_ts(doc)
    print(('  jeu : public/art/vecto/fonds/' + CLAN + '.webp %d Ko, ' + CLAN + '-anim.webp %d Ko (%d × %d), %d calques') % (
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
        vue_combat(T_VUE, 780).convert('RGB').save(os.path.join(TMP, 'brouillon-390.png'))
        vue_combat(T_VUE, 720, phone=(360, 640, 0)).convert('RGB').save(os.path.join(TMP, 'brouillon-360.png'))
        rendre([(scene(T_VUE), os.path.join(TMP, 'brouillon-fond.png'))], W, H)
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
    vue_combat(T_VUE, 780).convert('RGB').save(os.path.join(SORTIE, 'situation.png'))
    # la comparaison : ancien fond pixel | nouveau fond vectoriel, mêmes personnages, même cadrage
    pix = Image.open(os.path.join(ROOT, 'public', 'art', 'px', 'fonds', CLAN + '.webp')).convert('RGBA')
    a = vue_combat(0, 780, fond=pix)
    b = vue_combat(T_VUE, 780)
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
