# Le fond de combat du clan d'ARACHNÉ (terre), le repaire des araignées, redessiné en VECTORIEL lisse et animé
# (27/11/2026, demande du propriétaire après le test du volcan de Kael : « les 7 autres fonds »).
#
# Même façon de faire et mêmes mesures que le fond de Kael (refonte-graphique/ui-moderne/fonds/kael/kael.py) :
# une image de 590 × 1100 pixels du fond, plateforme de P0 = 800 à P1 = 1047 ; en combat, le jeu l'agrandit ×1,4 et
# coupe les côtés (on voit x = 84 → 506), les pieds des rangs sont à 828 / 880 / 933, les cartes des héros cachent
# tout ce qui est sous y = 985. Le style est celui des héros et monstres vectoriels : grandes formes simples, dégradés
# doux, une seule lumière en haut à droite, un seul contour sombre seulement sur les plans proches, aucun flou SVG.
# Le fond reste moins contrasté que les personnages ; le lointain est plus pâle, dans la brume rosée du soir.
#
# Ce qu'on voit (la composition du fond pixel, refonte-graphique/pixel/fonds/arachne/build.py, recadrée pour le
# combat), du fond vers le devant : on est DANS une ancienne carrière creusée sous la montagne. Par la grande bouche
# de la grotte, un ciel de soir (lavande, puis rose et or vers la lumière en haut à droite, un soleil pâle), deux
# nuages doux ; au loin la carrière à ciel ouvert (des gradins taillés, pâles dans la brume) et des blocs abandonnés.
# Un pilier de roche laissé par les carriers soutient la voûte ; entre lui et la paroi de gauche, la grande toile
# (un cocon pris dedans, la petite araignée qui descend et remonte) ; une seconde toile dans le coin haut-droit de la
# bouche, à contre-jour ; deux cocons pendus à la voûte. À droite, un replat porte la pierre levée du clan (chitine
# noire, signe de grenat) entre deux bannières de soie ; à gauche, un replat plus bas et sa bannière ; des grappes de
# cristaux grenat. L'arène : les grandes dalles taillées de la carrière, d'un bord à l'autre, calmes ; dessous, le
# gouffre sombre ; deux rochers dans les coins du bas.
# Ce qui bouge : TROIS CHAUVES-SOURIS lointaines traversent la bouche (la touche vivante, comme les dragons de Kael :
# elles sortent de derrière une paroi ou le pilier et y rentrent), les toiles ondulent, les cocons se balancent,
# l'araignée descend au bout de son fil, les cristaux et le signe respirent, les bannières ondulent, des poussières
# dorées flottent dans la lumière, des éclats grenat montent des cristaux.
# Le signe du clan (inventé, comme le pixel) : un losange (le corps) entre deux crochets courbes qui se rejoignent
# dessous (les chélicères), deux points au-dessus (les yeux).
#
#   python3 refonte-graphique/ui-moderne/fonds/arachne/arachne.py --fixe   # la vue du combat dans le brouillon
#   python3 refonte-graphique/ui-moderne/fonds/arachne/arachne.py          # images du jeu + calques + contrôles
#   python3 refonte-graphique/ui-moderne/fonds/arachne/arachne.py --video  # en plus : anim.gif et anim.mp4
#
# Sorties : public/art/vecto/fonds/arachne.webp (fixe ×2), arachne-anim.webp (planche ×2), fond-arachne.json et
# meta.json (à côté de ce fichier ; meta.json est réuni avec les autres clans dans src/game/fond-vecto.ts par
# ../assemble_ts.py) ; pixel/sortie/ui/vecto/fond-arachne/ (fond.png, situation.png, comparaison.png, anim.gif,
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

CLAN = 'arachne'
BROUILLON = os.environ.get('BROUILLON', '/tmp/fonds-brouillon')
TMP = os.path.join(BROUILLON, 'vecto-fond-' + CLAN)
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
                                # (19,2 s : les chauves-souris traversent la bouche lentement, une fois par période)
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
# Reprises d'Arachné et de ses araignées vectorielles (chitine indigo, rouge des anneaux, grenat des cristaux, pierre
# brun-gris de la cuirassée, soie lavande) et du ciel du fond pixel (lavande → rose → or), mais plus sourdes.
INK = '#1f1238'                 # le contour (le raisin de l'interface), seulement sur les plans proches
CIEL = [(0, '#3e3460'), (0.2, '#4e406c'), (0.4, '#6a5280'), (0.58, '#8e6a8a'), (0.74, '#b0848c'), (0.88, '#cfa08e'),
        (1, '#dcb898')]
NUAGE = dict(base='#b8929a', light='#cfa8a4', rim='#ecccb4', sh='#9a7890')
MONT = dict(base='#a88a9c', light='#b4949e', rim='#c8aca6', sh='#9a7e94')          # les montagnes, tout au loin
LOIN = dict(base='#8e767e', light='#b69c92', rim='#d2b6a0', sh='#7a6474')          # les gradins de la carrière
LOIN2 = dict(base='#806a74', light='#aa908a', rim='#c8ac98', sh='#6c5868')         # les gradins plus proches
BLOC = dict(base='#857278', light='#9a8482', rim='#b89e8c', sh='#6c5c68')          # les blocs abandonnés
PAROI = dict(base='#342a3c', light='#43374a', rim='#8e7868', sh='#231c2a')         # la voûte et les parois (ombre)
PILIER = dict(base='#3e3344', light='#54454f', rim='#9a8270', sh='#2a2131')
ROC = dict(base='#41353e', light='#56474e', rim='#9a8270', sh='#2a2230')          # les replats, rochers proches
SOL = dict(back='#6c5e62', front='#7a6a66')                                         # l'arène : valeur moyenne
SOIE = dict(base='#b4b0d2', light='#cecbe6', rim='#f0ecf2', sh='#8c88b4')          # les cocons
FIL = '#e6e2f4'                                                                     # les fils de soie
TISSU = dict(base='#7e7aa8', light='#9894c0', rim='#c8c4e2', sh='#58547e')         # les bannières de soie
CHITINE = dict(base='#2a2540', light='#3c365a', rim='#8682b4', sh='#1c1830')       # la pierre levée, les mâts
GRENAT = dict(base='#a8284a', light='#d24c62', rim='#ff9eaa', sh='#6e1838')
ROUGE = '#c0343a'                                                                   # le signe sur la soie
CHAUVE = '#3a2c4a'                                                                  # les chauves-souris

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



def stroke(d, col, w, op=1.0, extra=''):
    """Un fil (trait rond, sans remplissage)."""
    return '<path d="%s" fill="none" stroke="%s" stroke-width="%s" stroke-linecap="round" stroke-linejoin="round"%s%s/>' % (
        d, col, fm(w), '' if op == 1 else ' opacity="%g"' % op, extra)


def quad(a, c, b):
    return 'M%s %s Q%s %s %s %s' % (fm(a[0]), fm(a[1]), fm(c[0]), fm(c[1]), fm(b[0]), fm(b[1]))


def qpt(a, c, b, t):
    return tuple((1 - t) ** 2 * a[j] + 2 * (1 - t) * t * c[j] + t * t * b[j] for j in range(2))


# ------------------------------------------------------------------------------------------------ la grotte
# La bouche de la grotte (le trou dans la voûte et les parois) : bord gauche de bas en haut, le bas de la voûte de
# gauche à droite (plus haut à droite), bord droit de haut en bas. Les parois sont rapprochées du milieu par rapport
# au pixel (le combat coupe les bords : on voit x = 84 → 506) ; la voûte reste au-dessus de y ≈ 300 (les pilules du
# haut ne cachent que la voûte calme et le ciel).
BOUCHE_G = [(150, 798), (153, 760), (146, 712), (151, 664), (143, 612), (149, 560), (141, 506), (147, 452),
            (139, 398), (145, 350)]
VOUTE_PTS = [(152, 318), (168, 302), (196, 297), (222, 300), (240, 304), (256, 306), (272, 302), (290, 292),
             (316, 284), (346, 279), (372, 272), (398, 268), (424, 262), (444, 266)]
BOUCHE_D = [(452, 284), (456, 330), (451, 384), (459, 440), (453, 500), (461, 560), (455, 620), (460, 680),
            (454, 740), (458, 798)]


def voute_y(x):
    return interp(VOUTE_PTS, x)


def paroi_g(y):
    return interp(sorted((b, a) for a, b in BOUCHE_G + [VOUTE_PTS[0]]), y)


def paroi_d(y):
    return interp(sorted((b, a) for a, b in [VOUTE_PTS[-1]] + BOUCHE_D), y)


def bouche_forme():
    pts = BOUCHE_G + VOUTE_PTS + BOUCHE_D
    return sm(pts, sharp=(0, len(pts) - 1), t=0.75)


def grotte_forme():
    return rpoly([(-20, -20), (610, -20), (610, 800), (-20, 800)], 0).hole(bouche_forme())


# Le pilier laissé debout par les carriers (il monte se perdre derrière la voûte ; son pied est posé au sol).
PIL_G = [(226, 790), (232, 762), (236, 704), (234, 640), (238, 580), (236, 520), (239, 460), (237, 400), (236, 350),
         (230, 318), (222, 290)]
PIL_D = [(290, 284), (278, 312), (272, 350), (273, 400), (271, 460), (274, 520), (272, 580), (275, 640), (273, 704),
         (277, 762), (286, 790)]


def pilier_g(y):
    return interp(sorted((b, a) for a, b in PIL_G), y)


def pilier_d(y):
    return interp(sorted((b, a) for a, b in PIL_D), y)


@element('ciel', -29.9, 'fixe')
def ciel(doc):
    out = [path('M-20 -20H610V820H-20Z', doc.lin(0, 250, 0, 640, CIEL))]
    sx, sy = SOLEIL
    # la lumière du soir en haut à droite (la seule lumière), un soleil pâle voilé
    out.append('<circle cx="%d" cy="%d" r="190" fill="%s"/>' % (sx, sy, doc.rad(
        sx, sy, 190, [(0, '#ffcf94', 0.46), (0.3, '#eaa88a', 0.24), (0.7, '#c08a8c', 0.08), (1, '#b0848c', 0)])))
    out.append('<circle cx="%d" cy="%d" r="18" fill="%s"/>' % (sx, sy, doc.rad(
        sx + 5, sy - 5, 23, [(0, '#fff4d4'), (0.6, '#ffdca0'), (1, '#f4b27a')])))
    return ''.join(out)


SOLEIL = (404, 392)


@element('nuages', -29.5, 'fixe')
def nuages(doc):
    out = []
    a = lobes_shape(150, 262, 418, [(254, 410, 9), (232, 400, 15), (204, 396, 17), (176, 402, 13), (156, 410, 8)],
                    sag=2)
    out.append(vol(doc, a, NUAGE, r=1.6, c=2.4))
    b = lobes_shape(282, 392, 452, [(384, 446, 7), (364, 438, 12), (336, 432, 15), (308, 438, 12), (288, 446, 7)],
                    sag=2)
    out.append(vol(doc, b, dict(NUAGE, base='#c49c9e', light='#d8b2a8'), r=1.6, c=2.2))
    return ''.join(out)


# ---------------------------------------------------------------------------------------------------- le lointain
@element('montagnes', -29.2, 'fixe')
def montagnes(doc):
    pts = [(110, 700), (110, 584), (150, 570), (186, 560), (214, 566), (246, 552), (282, 546), (318, 556),
           (350, 548), (388, 556), (420, 544), (452, 552), (490, 560), (490, 700)]
    out = [vol(doc, sm(pts, sharp=(0, 1, len(pts) - 2, len(pts) - 1), t=0.7), MONT, r=1.2, c=0)]
    # la brume du soir monte du pied des montagnes
    out.append(path('M100 560H500V700H100Z', doc.lin(0, 556, 0, 640, [(0, '#c8a49c', 0), (1, '#d0aa9c', 0.5)])))
    # plus près, le rebord de la carrière (un peu plus sombre, sa crête éclairée)
    pts = [(110, 700), (110, 600), (160, 592), (200, 598), (250, 588), (300, 594), (340, 584), (380, 590),
           (430, 580), (470, 586), (490, 590), (490, 700)]
    out.append(vol(doc, sm(pts, sharp=(0, 1, len(pts) - 2, len(pts) - 1), t=0.7),
                   dict(base='#9c8090', light='#a68894', rim='#c6a8a2', sh='#8c7286'), r=1.4, c=0))
    out.append(path('M100 590H500V700H100Z', doc.lin(0, 590, 0, 660, [(0, '#c8a49c', 0), (1, '#cca69c', 0.45)])))
    return ''.join(out)


def gradin(doc, x0, x1, y_top, y_bot, m, sens, k=1.0):
    """Un gradin taillé : un dessus plat éclairé (bord un peu irrégulier) et sa face verticale, côté `sens`
    (+1 : la face regarde à gauche, à l'ombre ; −1 : elle regarde à droite, vers la lumière)."""
    out = []
    face_x = x0 if sens > 0 else x1
    top = [(x0, y_top + 1), (x0 + (x1 - x0) * 0.3, y_top - 0.6), (x0 + (x1 - x0) * 0.62, y_top + 0.6), (x1, y_top)]
    s = sm(top + [(x1, y_bot), (x0, y_bot)], sharp=(0, 3, 4, 5), t=0.6)
    out.append(path(s, m['base']))
    # le dessus (une bande plus claire, épaisse de quelques pixels)
    out.append(path(sm(top + [(x1, y_top + 5 * k), (x0, y_top + 5.6 * k)], sharp=(0, 3, 4, 5), t=0.6), m['light']))
    out.append(path(ribbon(resample(top, 10), [0.2] + [0.9 * k] * 9 + [0.2]), m['rim'], 0.7))
    # la face qui regarde le côté de l'ombre : plus sombre
    fw = 9 * k
    fx = face_x if sens > 0 else face_x - fw
    out.append(path(rpoly([(fx, y_top + 1), (fx + fw, y_top + 2), (fx + fw, y_bot), (fx, y_bot)], 1.5),
                    m['sh'] if sens > 0 else m['light'], 0.55 if sens > 0 else 0.4))
    return ''.join(out)


@element('carriere', -28.5, 'fixe')
def carriere(doc):
    """La carrière à ciel ouvert, au loin : des gradins taillés qui montent vers la droite (les dessus éclairés, les
    faces à l'ombre), d'autres plus bas à gauche ; le fond de la carrière ; la brume rosée devant."""
    out = []
    # à droite, la grande paroi taillée en gradins (du plus haut, derrière, au plus bas, devant)
    for k, (x0, y0) in enumerate([(430, 600), (392, 628), (352, 656), (318, 684), (288, 708)]):
        m = LOIN if k < 3 else LOIN2
        out.append(gradin(doc, x0, 500, y0, 760, m, +1, k=1.0))
    # à gauche, des gradins plus bas, qui montent vers la gauche
    for k, (x1, y0) in enumerate([(176, 640), (206, 666), (236, 690), (262, 712)]):
        m = LOIN if k < 2 else LOIN2
        out.append(gradin(doc, 100, x1, y0, 760, m, -1, k=0.9))
    # le fond de la carrière, poussiéreux
    out.append(path('M100 728H500V770H100Z', doc.lin(0, 728, 0, 760, [(0, '#a48c8a'), (1, '#94807e')])))
    # la brume rosée qui traîne au fond (une bande douce, pas de rond)
    out.append(path('M100 600H500V760H100Z', doc.lin(0, 600, 0, 748, [(0, '#c8a49c', 0), (0.6, '#c8a49c', 0.1),
                                                                      (1, '#cfaa9e', 0.45)])))
    # deux blocs abandonnés, tout petits, sur le fond de la carrière
    for x, y, w_, h_ in ((300, 744, 16, 9), (382, 740, 22, 11)):
        s = rpoly([(x - w_ / 2, y), (x - w_ / 2, y - h_), (x + w_ / 2, y - h_ - 1), (x + w_ / 2, y)], 1.5)
        out.append(vol(doc, s, dict(BLOC, base='#9a8486', light='#ac9690', rim='#c4aa98', sh='#88727c'), r=0.9, c=1.2))
    return ''.join(out)


# ---------------------------------------------------------------------------------------------------- le sol de la grotte
def bloc_taille(doc, x, y, w_, h_, m=BLOC, ink=None):
    """Un bloc taillé abandonné, posé au sol en (x, y) (milieu du bas) : face avant, dessus éclairé, côté droit."""
    out = []
    d = h_ * 0.32
    face = rpoly([(x - w_ / 2, y), (x - w_ / 2, y - h_), (x + w_ / 2 - d * 0.6, y - h_), (x + w_ / 2 - d * 0.6, y)], 1.5)
    top = rpoly([(x - w_ / 2, y - h_), (x - w_ / 2 + d * 0.7, y - h_ - d * 0.55), (x + w_ / 2 + d * 0.1, y - h_ - d * 0.55),
                 (x + w_ / 2 - d * 0.6, y - h_)], 1.2)
    side = rpoly([(x + w_ / 2 - d * 0.6, y), (x + w_ / 2 - d * 0.6, y - h_), (x + w_ / 2 + d * 0.1, y - h_ - d * 0.55),
                  (x + w_ / 2 + d * 0.1, y - d * 0.4)], 1.2)
    whole = sm([(x - w_ / 2, y), (x - w_ / 2, y - h_), (x - w_ / 2 + d * 0.7, y - h_ - d * 0.55),
                (x + w_ / 2 + d * 0.1, y - h_ - d * 0.55), (x + w_ / 2 + d * 0.1, y - d * 0.4), (x + w_ / 2 - d * 0.6, y)],
               sharp=(0, 1, 2, 3, 4, 5), t=0.5)
    if ink:
        out.append('<path d="%s" fill="%s" stroke="%s" stroke-width="1.6" stroke-linejoin="round"/>' % (
            whole.d(), ink, ink))
    out.append(path(face, doc.lin(x + w_ / 2, y - h_, x - w_ / 2, y, [(0, m['base']), (1, m['sh'])])))
    out.append(path(side, m['light']))
    out.append(path(top, m['rim'], 0.85))
    return ''.join(out)


@element('sol-grotte', -21, 'fixe')
def sol_grotte(doc):
    """Le sol de la grotte, entre la bouche et l'arène : la poussière claire éclairée par le soir, des blocs taillés."""
    out = [path('M-10 746H600V802H-10Z', doc.lin(0, 746, 0, 800, [(0, '#8e7a78'), (0.5, '#7a6a6c'), (1, '#64565c')]))]
    # la lumière de la bouche tombe au sol (une nappe douce, allongée, pas un rond)
    out.append(path(sm([(170, 756), (260, 750), (380, 752), (446, 760), (420, 780), (300, 786), (190, 778)], t=0.9),
                    '#c8a08e', 0.16))
    out.append(bloc_taille(doc, 200, 788, 34, 18, ink=INK))
    out.append(bloc_taille(doc, 324, 780, 40, 22, ink=INK))
    out.append(bloc_taille(doc, 356, 795, 16, 9, ink=INK))
    return ''.join(out)


@element('pilier', -20.5, 'fixe')
def pilier(doc):
    pts = PIL_G + PIL_D
    s = sm(pts, sharp=(0, len(PIL_G) - 1, len(PIL_G), len(pts) - 1), t=0.75)
    g = doc.lin(282, 300, 228, 780, [(0, PILIER['light']), (0.5, PILIER['base']), (1, PILIER['sh'])])
    out = [vol(doc, s, PILIER, grad=g, r=2.2, c=3.6, ink=INK, iw=1.0)]
    inner = []
    # la face droite, tournée vers la lumière ; quelques entailles des carriers (peu, de grandes marques)
    inner.append(path(sm([(262, 330), (276, 320), (274, 460), (276, 600), (280, 760), (264, 760), (262, 600),
                          (260, 450)], t=0.8), PILIER['light'], 0.55))
    for y0, w0 in ((420, 18), (566, 22), (690, 16)):
        c = [(238 + 2, y0), (238 + w0 * 0.5, y0 + 2.5), (238 + w0, y0 + 1)]
        inner.append(path(ribbon(resample(c, 8), [0.2, 1.2, 1.8, 2, 2, 1.8, 1.4, 0.8, 0.2]), PILIER['sh'], 0.55))
        inner.append(path(ribbon(resample([(x, y - 2.4) for x, y in c], 8), [0.1, 0.5, 0.8, 0.9, 0.9, 0.8, 0.6, 0.4, 0.1]),
                          PILIER['rim'], 0.35))
    # le haut se perd dans l'ombre de la voûte
    inner.append(path('M200 270H300V360H200Z', doc.lin(0, 290, 0, 356, [(0, '#1a1422', 0.75), (1, '#1a1422', 0)])))
    out.append('<g clip-path="%s">%s</g>' % (doc.clip(s.d()), ''.join(inner)))
    return ''.join(out)


@element('grotte', -20, 'fixe')
def grotte(doc):
    """La voûte et les deux parois : une seule forme percée de la bouche ; dans l'ombre, sauf le bord de la bouche
    (le soir l'éclaire en haut à droite des arêtes)."""
    s = grotte_forme()
    g = doc.lin(0, 0, 0, 800, [(0, '#1c1624'), (0.3, PAROI['sh']), (0.7, PAROI['base']), (1, PAROI['light'])])
    out = [vol(doc, s, PAROI, grad=g, r=2.6, c=4.2, ink=INK, iw=1.1)]
    inner = []
    # de grandes pierres taillées dans la voûte et les parois (peu, anguleuses, à peine marquées : un liseré clair en
    # haut à droite, une ombre douce en bas à gauche)
    pierres = []
    for pts in ([(-20, 60), (70, 40), (120, 90), (100, 170), (20, 190), (-20, 160)],
                [(140, 40), (250, 24), (300, 70), (270, 150), (170, 160), (130, 110)],
                [(320, 20), (430, 30), (470, 90), (420, 150), (330, 140), (300, 80)],
                [(490, 50), (610, 40), (610, 170), (530, 180), (480, 120)],
                [(30, 222), (128, 204), (156, 256), (112, 296), (40, 290)],
                [(196, 182), (298, 172), (326, 228), (288, 262), (200, 258)],
                [(360, 172), (468, 162), (498, 218), (448, 246), (372, 238)],
                [(-20, 340), (70, 322), (110, 380), (92, 468), (10, 490), (-20, 450)],
                [(0, 522), (90, 502), (118, 560), (100, 648), (20, 660), (-20, 600)],
                [(500, 322), (600, 300), (610, 420), (560, 450), (492, 410)],
                [(482, 472), (580, 452), (610, 560), (540, 600), (478, 560)],
                [(490, 624), (600, 612), (610, 720), (520, 740), (472, 700)],
                [(10, 692), (100, 682), (128, 740), (60, 790), (-20, 760)]):
        pierres.append(vol(doc, rpoly(pts, 7), dict(base='#3a3044', light='#463a4e', rim='#806e72', sh='#241d2c'),
                           r=1.8, c=3.0, rim_op=0.8, sh_op=0.7))
    inner.append('<g opacity="0.6">%s</g>' % ''.join(pierres))
    # quelques fentes douces (de grandes marques, pas des rayures)
    for pts, ws in (([(116, 120), (126, 170), (118, 210)], 2.2), ([(470, 380), (480, 430), (472, 470)], 2.2),
                    ([(110, 590), (118, 640), (112, 690)], 2.0)):
        c = resample(catmull(pts), 14)
        wl = [0.3 + ws * math.sin(math.pi * i / 14) ** 0.8 for i in range(15)]
        inner.append(path(ribbon(c, wl), PAROI['sh'], 0.6))
    # la lumière du soir qui entre par la bouche réchauffe un peu la pierre tout autour
    inner.append('<ellipse cx="300" cy="520" rx="330" ry="360" fill="%s"/>' % doc.rad(
        300, 520, 330, [(0, '#b08478', 0.0), (0.42, '#a07a76', 0.24), (0.62, '#8a6a70', 0.1), (1, '#6a5060', 0)],
        ry=360))
    # le haut de la voûte, plus sombre (loin de la lumière)
    inner.append(path('M-20 -20H610V200H-20Z', doc.lin(0, 0, 0, 200, [(0, '#120e18', 0.55), (1, '#120e18', 0)])))
    out.append('<g clip-path="%s">%s</g>' % (doc.clip(s.d()), ''.join(inner)))
    return ''.join(out)


# ---------------------------------------------------------------------------------------------------- la soie
def tri_angle(hub, pts):
    return sorted(pts, key=lambda p: math.atan2(p[1] - hub[1], p[0] - hub[0]))


def toile(doc, hub, ancres, cadre, ph, amp=(1.6, 1.0), tours=9, t0=0.1, t1=0.86, graine=0.0, op=0.55, cocon=None):
    """Une toile : les rayons (du moyeu aux ancres, ils ploient un peu), la spirale en festons (creusés vers le
    moyeu), les fils du cadre (ancre à ancre). Elle ondule : le moyeu bouge doucement (ph : 0..1, sans couture).
    Les fils sont plus clairs vers la lumière (en haut à droite)."""
    a = 2 * math.pi * ph
    hx, hy = hub[0] + amp[0] * math.sin(a + graine), hub[1] + amp[1] * math.sin(a + graine + 0.9)
    H_ = (hx, hy)
    anc = tri_angle(hub, ancres)
    rayons = []
    for i, (ax, ay) in enumerate(anc):
        mx, my = (hx + ax) / 2, (hy + ay) / 2
        L = math.dist(H_, (ax, ay))
        c = (mx + 0.4 * math.sin(a + i * 1.3), my + 0.025 * L + 0.8 * math.sin(a + i * 0.7 + graine))
        rayons.append(((hx, hy), c, (ax, ay)))
    d_r = ' '.join(quad(*r_) for r_ in rayons)
    d_s = []
    n = len(rayons)
    for j in range(tours):
        t = t0 + (t1 - t0) * j / (tours - 1) * (1 + 0.05 * math.sin(j * 1.9 + graine))
        t = min(t1, t)
        P = [qpt(*r_, t) for r_ in rayons]
        for i in range(n):
            p, q = P[i], P[(i + 1) % n]
            ang = abs(math.atan2(q[1] - hy, q[0] - hx) - math.atan2(p[1] - hy, p[0] - hx))
            if ang > math.pi:
                ang = 2 * math.pi - ang
            if ang > 2.0:            # un trop grand écart (le coin de la paroi) : pas de feston
                continue
            m = ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)
            c = (m[0] + (hx - m[0]) * 0.12, m[1] + (hy - m[1]) * 0.12 + 0.6)
            d_s.append(quad(p, c, q))
    d_c = ' '.join(quad(p, c, q) for p, c, q in cadre)
    # le dégradé des fils : clairs en haut à droite, plus voilés en bas à gauche
    xs = [p[0] for p in anc] + [hx]
    ys = [p[1] for p in anc] + [hy]
    g = doc.lin(max(xs), min(ys), min(xs), max(ys), [(0, '#fff6e8'), (0.45, FIL), (1, '#a8a4cc')])
    out = [stroke(d_c, g, 1.1, op * 1.1), stroke(d_r, g, 0.85, op), stroke(' '.join(d_s), g, 0.7, op * 0.9)]
    # le moyeu : un petit nœud de soie
    out.append('<ellipse cx="%s" cy="%s" rx="2.2" ry="2" fill="%s" opacity="%g"/>' % (fm(hx), fm(hy), FIL, op * 0.9))
    if cocon:
        dx, dy, ang, rx, ry = cocon
        out.append(cocon_forme(doc, hx + dx, hy + dy, ang + 3 * math.sin(a + graine), rx, ry))
    return ''.join(out)


def cocon_forme(doc, x, y, ang, rx, ry):
    """Un cocon de soie : un fuseau aux bouts pointus, deux tours de fil plus sombres, éclairé en haut à droite."""
    A = math.radians(ang)

    def P(u, v):
        return (x + u * math.cos(A) - v * math.sin(A), y + u * math.sin(A) + v * math.cos(A))
    pts = [P(0, -ry), P(rx * 0.72, -ry * 0.55), P(rx, -ry * 0.05), P(rx * 0.78, ry * 0.5), P(0, ry),
           P(-rx * 0.78, ry * 0.5), P(-rx, -ry * 0.05), P(-rx * 0.72, -ry * 0.55)]
    s = sm(pts, sharp=(0, 4), t=0.8)
    out = [vol(doc, s, SOIE, r=1.0, c=1.6, ink=INK, iw=0.7)]
    inner = []
    for v0, k in ((-0.42, 0.8), (-0.04, 1), (0.36, 0.9)):
        c = [P(-rx * 1.1, ry * v0 - 1), P(0, ry * v0 + 1.6), P(rx * 1.1, ry * v0 - 1.4)]
        inner.append(path(ribbon(resample(catmull(c), 10), [0.3, 0.7, 1.0, 1.1, 1.1, 1.1, 1.0, 0.9, 0.7, 0.5, 0.2]),
                          SOIE['sh'], 0.45 * k))
    out.append('<g clip-path="%s">%s</g>' % (doc.clip(s.d()), ''.join(inner)))
    return ''.join(out)


# La grande toile, entre la paroi de gauche et le pilier ; un fil d'ancre descend de sa pointe basse jusqu'au replat.
GT_HUB = (194, 446)
GT_BAS = (192, 590)


def gt_ancres():
    return [(176, voute_y(176) + 1), (214, voute_y(214) + 1), (pilier_g(342) + 1.5, 342), (pilier_g(448) + 1.5, 448),
            (pilier_g(548) + 1.5, 548), GT_BAS, (paroi_g(556) - 1.5, 556), (paroi_g(470) - 1.5, 470),
            (paroi_g(380) - 1.5, 380)]


def gt_cadre():
    a = gt_ancres()
    p3, w1 = a[4], a[6]
    return [(GT_BAS, ((GT_BAS[0] + p3[0]) / 2, (GT_BAS[1] + p3[1]) / 2 + 4), p3),
            (GT_BAS, ((GT_BAS[0] + w1[0]) / 2, (GT_BAS[1] + w1[1]) / 2 + 4), w1)]


def grande_toile(doc, ph):
    return toile(doc, GT_HUB, gt_ancres(), gt_cadre(), ph, amp=(1.8, 1.2), tours=10, graine=0.0, op=0.55,
                 cocon=(20, 50, -14, 6.4, 10.5))


element('toile', -19, 'boucle', box=(134, 290, 112, 308), n=8, ms=600)(grande_toile)


@element('fil-ancre', -19.6, 'fixe')
def fil_ancre(doc):
    """Le long fil d'ancre de la grande toile, jusqu'au bord du replat de gauche (fixe : il ne bouge pas)."""
    b = (166, sol_g(166) + 0.5)
    c = ((GT_BAS[0] + b[0]) / 2 + 2, (GT_BAS[1] + b[1]) / 2)
    return stroke(quad(GT_BAS, c, b), doc.lin(0, GT_BAS[1], 0, b[1], [(0, FIL), (1, '#a8a4cc')]), 0.9, 0.5)


# La petite toile du coin haut-droit de la bouche, à contre-jour devant la lueur du soleil.
PT_HUB = (434, 300)


def pt_ancres():
    A = (392, voute_y(392) + 1)
    B = (paroi_d(372) + 1.5, 372)
    m1 = (A[0] + (B[0] - A[0]) / 3, A[1] + (B[1] - A[1]) / 3 + 4)
    m2 = (A[0] + (B[0] - A[0]) * 2 / 3, A[1] + (B[1] - A[1]) * 2 / 3 + 4)
    return [A, (412, voute_y(412) + 1), (432, voute_y(432) + 1), (paroi_d(292) + 1.5, 292),
            (paroi_d(330) + 1.5, 330), B, m2, m1]


def pt_cadre():
    a = pt_ancres()
    A, B = a[0], a[5]
    return [(A, ((A[0] + B[0]) / 2 - 1, (A[1] + B[1]) / 2 + 6), B)]


def petite_toile(doc, ph):
    return toile(doc, PT_HUB, pt_ancres(), pt_cadre(), ph, amp=(1.0, 0.8), tours=7, t0=0.14, t1=0.84, graine=2.1,
                 op=0.6)


element('toile-coin', -19, 'boucle', box=(386, 258, 74, 120), n=8, ms=600)(petite_toile)


# Les deux cocons pendus à la voûte (à droite des pilules du haut), qui se balancent doucement.
COCONS = [(352, 62, 7.4, 12.5, 0.0), (384, 40, 6.2, 10, 2.2)]          # x, longueur du fil, rx, ry, déphasage


def cocon_pendu(k):
    x, L, rx, ry, dph = COCONS[k]
    y0 = voute_y(x) + 1

    def fn(doc, ph):
        ang = 3.2 * math.sin(2 * math.pi * ph + dph)
        A = math.radians(ang)
        bx, by = x - L * math.sin(A), y0 + L * math.cos(A)
        out = [stroke('M%s %s L%s %s' % (fm(x), fm(y0), fm(bx), fm(by)), FIL, 0.8, 0.6)]
        cx, cy = x - (L + ry) * math.sin(A), y0 + (L + ry) * math.cos(A)
        out.append(cocon_forme(doc, cx, cy, ang, rx, ry))
        return ''.join(out)
    return fn


for _k, _c in enumerate(COCONS):
    element('cocon%d' % (_k + 1), -18.8, 'boucle', box=(_c[0] - 16, voute_y(_c[0]) - 2, 32, _c[1] + 2 * _c[3] + 8),
            n=12, ms=400)(cocon_pendu(_k))


# La petite araignée : elle descend de la voûte au bout de son fil devant la grande toile, s'arrête, remonte.
ARAI_X = 208


def araignee_forme(doc, x, y, ph):
    """Une petite araignée vue de face, pendue tête en bas : abdomen rond (marque rouge), céphalothorax, huit pattes
    repliées qui bougent un peu."""
    out = []
    jamb = 0.6 * math.sin(2 * math.pi * ph * 3)
    col = CHITINE['base']
    for sg in (-1, 1):
        for k, (ax, ay, bx, by, cx, cy) in enumerate(((1.6, 1.0, 4.6, -1.6, 6.2, 1.4), (1.8, 2.0, 5.4, 1.2, 6.6, 4.6),
                                                       (1.8, 3.0, 5.0, 4.4, 5.6, 7.6), (1.4, 3.8, 3.8, 6.6, 3.6, 9.4))):
            j = jamb * (1 if k % 2 else -1)
            pts = [(x + sg * ax, y + ay), (x + sg * bx, y + by + j), (x + sg * cx, y + cy + j * 0.6)]
            out.append(stroke('M%s %s L%s %s L%s %s' % (fm(pts[0][0]), fm(pts[0][1]), fm(pts[1][0]), fm(pts[1][1]),
                                                       fm(pts[2][0]), fm(pts[2][1])), col, 0.75))
    ab = ellipse(x, y - 2.6, 3.4, 3.8)
    out.append(vol(doc, ab, CHITINE, r=0.8, c=1.0, ink=INK, iw=0.5))
    out.append(path(sm([(x, y - 4.6), (x + 1.1, y - 3.0), (x, y - 1.4), (x - 1.1, y - 3.0)], sharp=(0, 1, 2, 3)), ROUGE))
    out.append(vol(doc, ellipse(x, y + 2.4, 2.3, 2.2), CHITINE, r=0.7, c=0.8, ink=INK, iw=0.5))
    return ''.join(out)


ARAI_N = 24


def araignee(doc, ph):
    # descente (10 images, en douceur), arrêt (2), remontée (10), arrêt (2) : sans couture
    i = round(ph * ARAI_N) % ARAI_N
    if i < 10:
        u = 0.5 - 0.5 * math.cos(math.pi * i / 10)
    elif i < 12:
        u = 1.0
    elif i < 22:
        u = 0.5 + 0.5 * math.cos(math.pi * (i - 12) / 10)
    else:
        u = 0.0
    y0 = voute_y(ARAI_X) + 1
    y = 322 + 54 * u
    out = [stroke('M%s %s L%s %s' % (ARAI_X, fm(y0), ARAI_X, fm(y - 5)), FIL, 0.7, 0.65)]
    out.append(araignee_forme(doc, ARAI_X, y, ph * 2))
    return ''.join(out)


element('araignee', -18.5, 'boucle', box=(ARAI_X - 10, 296, 20, 94), n=ARAI_N, ms=400)(araignee)


# ---------------------------------------------------------------------------------------------------- les replats
REPLAT_D = [(380, 800), (383, 770), (379, 736), (386, 700), (390, 668), (398, 654), (420, 649), (446, 647),
            (474, 650), (500, 646), (530, 649), (560, 645), (604, 648), (604, 800)]
REPLAT_G = [(-14, 800), (-14, 718), (24, 713), (60, 716), (98, 711), (134, 713), (160, 715), (174, 728), (178, 756),
            (186, 790), (190, 800)]


def sol_d(x):
    return interp(REPLAT_D[5:-1], x)


def sol_g(x):
    return interp(REPLAT_G[1:8], x)


def cristaux(doc, x, y, k=1.0, flip=False, formes=None):
    """Une grappe de cristaux grenat qui sort de la roche en (x, y), lumière en haut à droite."""
    out = []
    sg = -1 if flip else 1
    for dx, h_, w_, ang in ((-7, 13, 3.8, -24), (-1, 24, 5.0, -4), (6, 17, 4.4, 16), (11, 9, 3.2, 34)):
        a = math.radians(ang * sg)
        bx, by = x + dx * k * sg, y

        def P(u, v):
            return (bx + (u * math.cos(a) - v * math.sin(a)) * k, by + (u * math.sin(a) + v * math.cos(a)) * k)
        pts = [P(-w_, 2), P(-w_, -h_ * 0.66), P(0, -h_), P(w_, -h_ * 0.66), P(w_, 2)]
        s = rpoly(pts, 0.6)
        if formes is not None:
            formes.append(s)
        out.append(vol(doc, s, GRENAT, r=1.1, c=1.6, ink=INK, iw=0.8))
        out.append(path(rpoly([P(0, -h_), P(w_, -h_ * 0.66), P(w_, 2), P(0, 2)], 0.4), GRENAT['light'], 0.5))
    out.append(vol(doc, sm([(x - 13 * k, y + 2), (x - 7 * k, y - 3 * k), (x + 7 * k, y - 3.5 * k), (x + 15 * k, y + 2)],
                           sharp=(0, 3), t=0.8), ROC, r=0.8, c=1.0, ink=INK, iw=0.8))
    return ''.join(out)


CRISTAUX = [(402, sol_d(402) + 1, 0.85, False), (150, sol_g(150) + 1, 0.8, True), (296, 793, 0.75, False)]


@element('replats', -17.5, 'fixe')
def replats(doc):
    out = []
    for pts, droite in ((REPLAT_D, True), (REPLAT_G, False)):
        s = sm(pts, sharp=(0, len(pts) - 1) if droite else (0, 1, len(pts) - 1), t=0.75)
        xs = [p[0] for p in pts]
        g = doc.lin(max(xs), 650, min(xs) + 20, 800, [(0, ROC['light']), (0.45, ROC['base']), (1, ROC['sh'])])
        out.append(vol(doc, s, ROC, grad=g, r=2.2, c=3.6, ink=INK, iw=1.0))
        inner = []
        top = pts[5:-1] if droite else pts[1:8]
        # le dessus du replat, éclairé (une bande claire qui suit le bord)
        tl = resample(catmull(top), 30)
        inner.append(path(ribbon([(x, y + 5) for x, y in tl], [0.5] + [5.0] * 29 + [0.5]), ROC['light'], 0.6))
        if droite:
            inner.append(path(sm([(392, 672), (420, 680), (430, 720), (418, 780), (380, 790)], t=0.8), ROC['sh'], 0.45))
            inner.append(path(sm([(520, 690), (604, 680), (604, 790), (540, 790)], t=0.8), ROC['light'], 0.3))
            for pts_ in ([(452, 690), (458, 730), (450, 770)], [(500, 700), (494, 740)]):
                c = resample(catmull(pts_), 10)
                inner.append(path(ribbon(c, [0.3, 1.2, 1.8, 2.2, 2.2, 2, 1.8, 1.4, 1, 0.6, 0.2]), ROC['sh'], 0.6))
        else:
            inner.append(path(sm([(120, 730), (170, 724), (182, 790), (130, 792)], t=0.8), ROC['light'], 0.35))
            c = resample(catmull([(60, 734), (54, 764), (64, 792)]), 10)
            inner.append(path(ribbon(c, [0.3, 1.2, 1.8, 2.2, 2.2, 2, 1.8, 1.4, 1, 0.6, 0.2]), ROC['sh'], 0.6))
        out.append('<g clip-path="%s">%s</g>' % (doc.clip(s.d()), ''.join(inner)))
    for x, y, k, fl in CRISTAUX:
        out.append(cristaux(doc, x, y, k, fl))
    # des pierres tombées au pied des replats
    for x, y, w_, h_ in ((396, 800, 14, 6), (190, 799, 12, 5)):
        s = sm([(x - w_ / 2, y), (x - w_ * 0.3, y - h_), (x + w_ * 0.2, y - h_ * 1.05), (x + w_ / 2, y)],
               sharp=(0, 3), t=0.8)
        out.append(vol(doc, s, ROC, r=1.0, c=1.4, ink=INK, iw=0.8))
    return ''.join(out)


def lueur_cristaux(k_):
    x, y, k, fl = CRISTAUX[k_]

    def fn(doc, ph):
        b = 0.5 - 0.5 * math.cos(2 * math.pi * ph)
        formes = []
        cristaux(Doc(), x, y, k, fl, formes)
        out = ['<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/>' % (
            fm(x), fm(y - 16 * k), fm(18 * k), fm(15 * k), doc.rad(x, y - 16 * k, 18 * k, [
                (0, '#ff6a7e', 0.10 + 0.16 * b), (1, '#ff6a7e', 0)], ry=15 * k))]
        out.extend(path(s, GRENAT['rim'], 0.06 + 0.26 * b) for s in formes)
        return ''.join(out)
    return fn


for _k, (_x, _y, _kk, _f) in enumerate(CRISTAUX):
    element('cristaux%d' % (_k + 1), -16.8, 'boucle', box=(_x - 22 * _kk, _y - 34 * _kk, 44 * _kk, 36 * _kk),
            n=8, ms=600)(lueur_cristaux(_k))


# ---------------------------------------------------------------------------------------------------- le clan
STELE = (444, sol_d(444))


def stele(doc):
    x, y = STELE
    s = sm([(x - 12, y + 2), (x - 13, y - 30), (x - 9, y - 44), (x, y - 50), (x + 8, y - 45), (x + 12, y - 32),
            (x + 12, y + 2)], sharp=(0, 6), t=0.8)
    out = [vol(doc, s, CHITINE, r=1.6, c=2.4, ink=INK, iw=1.0)]
    # un reflet net vertical sur le bord droit (chitine luisante)
    out.append(path(ribbon(resample([(x + 7, y - 40), (x + 9, y - 26), (x + 9, y - 10)], 8),
                           [0.2, 0.9, 1.4, 1.6, 1.6, 1.4, 1.1, 0.7, 0.2]), '#a6a2d0', 0.55))
    out.append(vol(doc, rpoly([(x - 15, y + 4), (x - 14, y - 2), (x + 14, y - 3), (x + 16, y + 4)], 1.5), ROC,
                   r=0.9, c=1.2, ink=INK, iw=0.9))
    return ''.join(out)


def signe_forme(cx, cy, k):
    """Le signe d'Arachné : un losange (le corps) entre deux crochets courbes qui se rejoignent dessous en pointe
    (les chélicères, sans se toucher : pas d'anneau), deux petits points au-dessus (les yeux). Aucune lettre."""
    def P(u, v):
        return (cx + u * k, cy + v * k)
    corps = sm([P(0, -3.0), P(1.8, 0.4), P(0, 3.8), P(-1.8, 0.4)], sharp=(0, 1, 2, 3), t=0.5)
    out = corps
    for sg in (-1, 1):
        c = resample(catmull([P(sg * 1.9, -5.6), P(sg * 4.3, -2.4), P(sg * 4.1, 2.2), P(sg * 0.5, 7.0)]), 12)
        ws = [0.2, 0.55, 0.8, 0.95, 1.0, 1.0, 0.95, 0.85, 0.7, 0.55, 0.4, 0.25, 0.1]
        out = out + ribbon(c, [w * k for w in ws])
    for sg in (-1, 1):
        out = out + ellipse(cx + sg * 0.95 * k, cy - 4.6 * k, 0.6 * k, 0.6 * k)
    return out


def signe(doc, ph):
    x, y = STELE
    k = 0.5 - 0.5 * math.cos(2 * math.pi * ph)
    out = [stele(doc)]
    out.append('<ellipse cx="%s" cy="%s" rx="11" ry="13" fill="%s"/>' % (x, fm(y - 24), doc.rad(
        x, y - 24, 11, [(0, '#ff5a6e', 0.22 + 0.25 * k), (1, '#ff5a6e', 0)], ry=13)))
    out.append(path(signe_forme(x, y - 24, 1.45), mix(GRENAT['base'], '#ff8a96', 0.25 + 0.6 * k)))
    return ''.join(out)


element('signe', -17, 'boucle', box=(STELE[0] - 18, STELE[1] - 53, 36, 60), n=12, ms=400)(signe)

MATS = [(116, sol_g(116)), (414, sol_d(414)), (480, sol_d(480))]
MAT_H = 52
MAT_M = dict(CHITINE, rim='#7a76a4')


def mat(doc, x, y):
    out = [vol(doc, rpoly([(x - 1.4, y + 1), (x - 1.4, y - MAT_H), (x + 1.4, y - MAT_H), (x + 1.4, y + 1)], 0.6),
               MAT_M, r=0.7, c=0.8, ink=INK, iw=0.7)]
    out.append(vol(doc, rpoly([(x - 13, y - MAT_H + 2), (x + 13, y - MAT_H + 2), (x + 13, y - MAT_H + 5),
                               (x - 13, y - MAT_H + 5)], 1.2), MAT_M, r=0.7, c=0.8, ink=INK, iw=0.7))
    # au bout du mât, une perle de grenat
    out.append(vol(doc, sm([(x, y - MAT_H - 5), (x + 2.4, y - MAT_H - 1.4), (x, y - MAT_H + 1.6), (x - 2.4, y - MAT_H - 1.4)],
                           sharp=(0, 1, 2, 3), t=0.5), GRENAT, r=0.6, c=0.8, ink=INK, iw=0.7))
    out.append(vol(doc, rpoly([(x - 6, y + 3), (x - 5, y - 2), (x + 5, y - 2.5), (x + 7, y + 3)], 1.2), ROC,
                   r=0.8, c=1.0, ink=INK, iw=0.8))
    return ''.join(out)


def banniere(k):
    x, y = MATS[k]
    top = y - MAT_H + 5

    def fn(doc, ph):
        # la toile de soie pend sous la traverse ; elle ondule doucement (plus en bas qu'en haut), l'air vient de la
        # bouche (de la droite)
        L, w_ = 34, 22
        a = 2 * math.pi * ph

        def P(u, v):
            sway = v ** 1.5 * (2.2 * math.sin(a + v * 2.2 + k) - 1.0)
            return (x + u * w_ / 2 * (1 - 0.08 * v) + sway, top + v * L + 0.8 * math.sin(a + u * 1.5 + k) * v)
        pts = [P(-1, 0), P(1, 0)]
        for v in (0.33, 0.66, 0.92):
            pts.append(P(1, v))
        pts += [P(1, 1.04), P(0.5, 0.9), P(0, 1.08), P(-0.5, 0.9), P(-1, 1.04)]
        for v in (0.92, 0.66, 0.33):
            pts.append(P(-1, v))
        s = sm(pts, sharp=(0, 1, 5, 7, 9), t=0.6)
        out = [mat(doc, x, y), vol(doc, s, TISSU, r=1.3, c=2.0, ink=INK, iw=0.9)]
        sx, sy = P(0, 0.42)
        out.append(path(signe_forme(sx, sy + 1, 1.25), ROUGE))
        return ''.join(out)
    return fn


for _k in range(3):
    _x, _y = MATS[_k]
    element('banniere%d' % (_k + 1), -16, 'boucle', box=(_x - 20, _y - MAT_H - 7, 40, MAT_H + 12), n=12,
            ms=200)(banniere(_k))


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
    out.append(path('M-10 %dH600V%dH-10Z' % (P0, P1), doc.lin(0, 0, 590, 0, [(0, '#221a2e', 0.06),
                                                                              (1, '#fff0e0', 0.04)])))
    # les grandes dalles taillées : des joints à peine marqués, décalés d'un rang à l'autre
    rows = [P0, 826, 856, 892, 936, 988, P1]
    joints = []
    for i in range(len(rows) - 1):
        ya, yb = rows[i], rows[i + 1]
        if i > 0:
            joints.append('M-10 %s H600' % fm(ya))
        step = 170
        off = (i % 2) * step / 2 + (i * 41) % 46
        g = -900 + off
        while g < 900:
            xa, xb = sol_x(g, ya), sol_x(g, yb)
            if -10 < min(xa, xb) and max(xa, xb) < 600:
                joints.append('M%s %s L%s %s' % (fm(xa), fm(ya + 1), fm(xb), fm(yb - 1)))
            g += step + 24 * math.sin(i * 2.7 + g)
    jd = ' '.join(joints)
    out.append('<path d="%s" fill="none" stroke="#fff4ea" stroke-width="1.2" opacity="0.05" '
               'transform="translate(0.8 0.8)"/>' % jd)
    out.append('<path d="%s" fill="none" stroke="#241a30" stroke-width="1" opacity="0.11"/>' % jd)
    # la poussière claire de la carrière : quelques dalles un peu plus claires, d'autres un peu plus sombres
    for (g0, i, col, op) in ((-240, 1, '#fff0e4', 0.04), (40, 3, '#241a30', 0.04), (280, 2, '#fff0e4', 0.035),
                             (-110, 4, '#241a30', 0.035), (160, 5, '#fff0e4', 0.035), (-360, 3, '#fff0e4', 0.03)):
        ya, yb = rows[i] + 1, rows[i + 1] - 1
        pts = [(sol_x(g0, ya), ya), (sol_x(g0 + 160, ya), ya), (sol_x(g0 + 160, yb), yb), (sol_x(g0, yb), yb)]
        out.append(path(rpoly(pts, 2), col, op))
    # le bord arrière : un fil d'ombre, puis l'arête éclairée ; la lumière de la bouche sur le fond du dallage
    out.append(path('M-10 %dH600V%dH-10Z' % (P0 - 2, P0), '#2a2030', 0.7))
    out.append(path('M-10 %dH600V%dH-10Z' % (P0, P0 + 1.6), '#9e8e8a', 0.7))
    out.append(path('M-10 %dH600V%dH-10Z' % (P0, P0 + 30), doc.lin(0, P0, 0, P0 + 30, [(0, '#e0b8a0', 0.08),
                                                                                       (1, '#e0b8a0', 0)])))
    # l'arête avant éclairée, puis le flanc taillé (dans l'ombre du gouffre)
    out.append(path('M-10 %dH600V%dH-10Z' % (P1, 1064), doc.lin(0, P1, 0, 1064, [
        (0, '#4a3e48'), (0.5, '#3e3440'), (1, '#2e2636')])))
    out.append(path('M-10 %dH600V%dH-10Z' % (P1 - 1, P1 + 1.6), '#a8968e', 0.85))
    for g in range(-600, 700, 170):
        x = sol_x(g, P1)
        out.append(path(rpoly([(x - 0.6, P1 + 2), (x + 0.6, P1 + 2), (x + 0.6, 1060), (x - 0.6, 1060)], 0.3),
                        '#1e1828', 0.35))
    return ''.join(out)


@element('dessous', -15.4, 'fixe')
def dessous(doc):
    """Sous le flanc de l'arène : le gouffre. En combat, c'est sous les cartes des héros (y > 985) : simple et
    sombre, sans détail (l'accueil, qui le montre, garde un bas calme)."""
    out = [path('M-10 1062H600V1104H-10Z', doc.lin(0, 1062, 0, 1100, [(0, '#2e2438'), (0.35, '#1e182a'),
                                                                     (1, '#151020')]))]
    pts = [(-10, 1058), (600, 1058), (600, 1064)]
    x, i = 600, 0
    while x > -10:
        x -= 24 + 9 * math.sin(i * 1.7)
        pts.append((x, 1064 + 2.6 * math.sin(i * 2.3) + 1.4 * math.cos(i * 1.1)))
        i += 1
    pts.append((-10, 1064))
    out.append(path(sm(pts, sharp=(0, 1), t=0.7), doc.lin(0, 1058, 0, 1068, [(0, '#3a3040'), (1, '#2c2434')])))
    return ''.join(out)


# ---------------------------------------------------------------------------------------------------- les particules
def poussiere_image(doc, i, n):
    """Une poussière dorée dans la lumière : elle apparaît, brille, s'efface (images sur sa vie)."""
    op = (0.35, 0.85, 1.0, 0.75, 0.3)[i]
    return ('<circle cx="5" cy="5" r="4.5" fill="%s"/><circle cx="5" cy="5" r="1" fill="%s" opacity="%g"/>' % (
        doc.rad(5, 5, 4.5, [(0, '#ffe2b0', 0.35 * op), (1, '#ffe2b0', 0)]), '#fff0d0', op))


element('poussiere', -14, 'particules', taille=(10, 10), images=5, dessin=poussiere_image, zone=(170, 470, 440, 720),
        nombre=9, vie=(6000, 9000), vx=(-2.5, 2.0), vy=(-3.5, -1.0), ondule=(3, 3200))


def eclat_image(doc, i, n):
    t = i / (n - 1)
    op = (0.7, 1.0, 0.75, 0.4)[i]
    return ('<circle cx="5" cy="5" r="4.5" fill="%s"/>%s' % (
        doc.rad(5, 5, 4.5, [(0, '#ff6a7e', 0.45 * op), (1, '#ff6a7e', 0)]),
        path(sm([(5, 3.2), (6.2, 5), (5, 6.8), (3.8, 5)], sharp=(0, 1, 2, 3), t=0.5), mix('#ffd0d6', '#ff7a8a', t), op)))


element('eclats-d', -14, 'particules', taille=(10, 10), images=4, dessin=eclat_image, zone=(392, 626, 412, 640),
        nombre=2, vie=(2200, 3000), vx=(-2, 2), vy=(-11, -7), ondule=(1.5, 1600))
element('eclats-g', -14, 'particules', taille=(10, 10), images=4, dessin=eclat_image, zone=(142, 688, 160, 700),
        nombre=2, vie=(2200, 3000), vx=(-2, 2), vy=(-11, -7), ondule=(1.5, 1600))


# ---------------------------------------------------------------------------------------------------- premier plan
@element('rocher-gauche', 1300, 'morceau', box=(0, 1026, 84, 74))
def rocher_g(doc):
    s = sm([(-12, 1104), (-12, 1046), (8, 1038), (30, 1040), (50, 1052), (66, 1070), (78, 1092), (80, 1104)],
           sharp=(0, 7), t=0.8)
    out = [vol(doc, s, ROC, r=2.0, c=3.0, ink=INK, iw=1.1)]
    out.append(path(sm([(30, 1044), (50, 1054), (64, 1072), (52, 1080), (36, 1062)], t=0.9), ROC['light'], 0.55))
    out.append(cristaux(doc, 24, 1041, 0.62))
    return ''.join(out)


@element('rocher-droite', 1300, 'morceau', box=(516, 1024, 74, 76))
def rocher_d(doc):
    s = sm([(524, 1104), (530, 1080), (544, 1058), (562, 1042), (584, 1036), (604, 1040), (604, 1104)],
           sharp=(0, 6), t=0.8)
    out = [vol(doc, s, ROC, r=2.0, c=3.0, ink=INK, iw=1.1)]
    out.append(path(sm([(566, 1046), (590, 1040), (600, 1056), (584, 1064)], t=0.9), ROC['light'], 0.5))
    # un vieux cocon collé à la roche
    out.append(cocon_forme(doc, 548, 1056, -58, 5.4, 10))
    return ''.join(out)


# ---------------------------------------------------------------------------------------------------- les chauves-souris
# La touche vivante (comme les dragons de Kael) : trois chauves-souris lointaines traversent la bouche de la grotte,
# devant le ciel du soir et la carrière ; plus loin = plus petite, plus pâle (dans la brume) et plus lente. Chacune
# est une particule seule qui vit une période entière : elle naît cachée (derrière une paroi ou le pilier, remis
# devant elle par les « morceaux » devant-*) et finit cachée ; ses ailes battent vite (8 images en boucle), son
# corps monte et descend un peu à chaque battement. Elles ne passent jamais sur l'arène (y < 520).
CHAUVES = [
    # id, y de départ, y d'arrivée, demi-envergure, x de départ, x d'arrivée, couleur, opacité
    ('chauve1', 452, 430, 14.5, 98, 500, CHAUVE, 0.88),          # la plus proche : de la paroi de gauche à la droite
    ('chauve2', 486, 494, 9.0, 500, 254, '#5a4868', 0.72),       # sort de la paroi de droite, rentre derrière le pilier
    ('chauve3', 512, 502, 6.5, 254, 98, '#6e5a78', 0.6),         # la plus loin : du pilier à la paroi de gauche
]
CHAUVE_N, CHAUVE_MS = 8, 90                                       # un battement d'ailes = 0,72 s


def chauve_image(id_):
    _, ya, yb, L, xa, xb, col, op = next(c for c in CHAUVES if c[0] == id_)
    w, h = 2 * L + 6, 1.5 * L + 6
    sg = 1 if xb > xa else -1

    def fn(doc, i, n):
        ph = i / n
        a = math.cos(2 * math.pi * ph)            # 1 : ailes en haut, −1 : en bas
        bob = 0.07 * L * a                        # le corps descend quand les ailes montent
        cx, cy = w / 2, h / 2 - 0.12 * L + bob
        s_ = L / 14

        def aile(m):
            def P(u, v):
                return (cx + m * u, cy + v)
            yw = -0.30 * L * a - 0.05 * L
            yt = -0.50 * L * a + 0.04 * L
            pts = [P(1.4 * s_, -1.2 * s_), P(0.42 * L, yw), P(L, yt), P(0.82 * L, (yt + yw) / 2 + 0.2 * L),
                   P(0.64 * L, yw + 0.17 * L), P(0.46 * L, yw + 0.3 * L), P(0.28 * L, yw * 0.5 + 0.24 * L),
                   P(1.6 * s_, 2.8 * s_)]
            return sm(pts, sharp=(2, 4, 6, 7), t=0.7)
        corps = ellipse(cx, cy + 1.2 * s_, 2.3 * s_, 3.8 * s_) + ellipse(cx, cy - 2.6 * s_, 1.9 * s_, 1.7 * s_)
        oreilles = sm([(cx - 1.7 * s_, cy - 3.3 * s_), (cx - 1.2 * s_, cy - 5.9 * s_), (cx - 0.3 * s_, cy - 3.9 * s_)],
                      sharp=(0, 1, 2), t=0.4) + sm([(cx + 1.7 * s_, cy - 3.3 * s_), (cx + 1.2 * s_, cy - 5.9 * s_),
                                                     (cx + 0.3 * s_, cy - 3.9 * s_)], sharp=(0, 1, 2), t=0.4)
        body = ''.join(path(s, col) for s in (aile(-1), aile(1), corps, oreilles))
        # penchée un peu vers où elle va
        return '<g opacity="%g" transform="rotate(%s %s %s)">%s</g>' % (op, fm(6 * sg), fm(w / 2), fm(h / 2), body)
    return fn, (round(w), round(h))


for _c in CHAUVES:
    _fn, _t = chauve_image(_c[0])
    _vx = (_c[5] - _c[4]) * 1000 / PERIODE
    _vy = (_c[2] - _c[1]) * 1000 / PERIODE
    element(_c[0], -28, 'particules', taille=_t, images=CHAUVE_N, ms=CHAUVE_MS, dessin=_fn,
            zone=(_c[4], _c[1], _c[4], _c[1]), nombre=1, vie=(PERIODE, PERIODE), vx=(_vx, _vx), vy=(_vy, _vy),
            ondule=(0, PERIODE))


def devant(box):
    """Un morceau du paysage remis devant les chauves-souris : tout ce qui est fixe et plus près qu'elles (pilier,
    parois…), sans le ciel ni la carrière, coupé à la boîte."""
    def fn(doc):
        x, y, w, h = box
        body = ''.join(e['fn'](doc) for e in sorted(ELEMS, key=lambda e: e['prof'])
                       if e['genre'] == 'fixe' and e['prof'] >= -21)
        return '<g clip-path="%s">%s</g>' % (doc.clip('M%s %sH%sV%sH%sZ' % (x, y, x + w, y + h, x)), body)
    return fn


for _id, _b in (('devant-paroi-g', (68, 374, 84, 160)), ('devant-pilier', (222, 374, 68, 160)),
                ('devant-paroi-d', (444, 374, 86, 150))):
    element(_id, -26, 'morceau', box=_b)(devant(_b))


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
        r = rng('arachne-' + e['id'])
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
# Côté héros : Rocvar (dragon-terre) au fond, un chevalier (knights-1) au milieu, Arachné (myths-10, la générale)
# devant ; en face, les trois araignées du clan (rapide, cuirassée, tisseuse), retournées vers la gauche.
PERSOS = [('dragon-terre', 'heros', 0), ('knights-1', 'heros', 2), ('myths-10', 'heros', 4),
          ('mon-arachne-rapide', 'ennemis', 0), ('mon-arachne-costaud', 'ennemis', 2), ('mon-arachne-tisseuse', 'ennemis', 4)]


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
                     graine='arachne-' + e['id'])
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
    Image.open(fixe).convert('RGB').save(os.path.join(JEU, 'arachne.webp'), quality=95, method=6)
    # le fond entier pour le propriétaire (les chauves-souris en vol)
    rendre([(scene(5200), os.path.join(SORTIE, 'fond.png'))], W * UP, H * UP)
    planche, meta = calques()
    planche.save(os.path.join(JEU, 'arachne-anim.webp'), quality=90, alpha_quality=100, method=6)
    planche.save(os.path.join(TMP, 'planche.png'))
    doc = {
        'clan': 'arachne', 'style': 'vecto', 'w': W, 'h': H, 'up': UP, 'unite': round(UNIT, 5),
        'image': 'art/vecto/fonds/arachne.webp', 'planche': 'art/vecto/fonds/arachne-anim.webp',
        'note': ('Coordonnées x, y, w, h, zone en pixels du fond (590 × 1100) ; cases et tuiles en pixels de la '
                 'planche (×up). L\'image fixe ne contient que ce qui ne bouge pas : chaque calque animé se pose '
                 'dessus, entier (transparent autour). Images lisses : agrandir en LINÉAIRE. Boucle : images changées '
                 'toutes les ms (ms 0 = un morceau remis devant). Défilé : la tuile coule à vx, vy px du fond par '
                 'seconde. Particules : la règle de fond-px.ts (hasard rng("arachne-" + id)), centre en (x, y), images '
                 'sur la vie ou en boucle toutes les ms. Branché dans le jeu derrière ?vecto=1 (src/game/fond-vecto.ts).'),
        'reperes': {'hz': HZ, 'p0': P0, 'p1': P1, 'rangs_combat': [round(r, 1) for r in RANGS_COMBAT],
                    'rangs_accueil': list(RANGS), 'cartes': round(CARTES, 1), 'vue_x': [round(v, 1) for v in VUE_X]},
        'periode_ms': PERIODE, 'planche_taille': list(planche.size), 'calques': meta}
    json.dump(doc, open(os.path.join(HERE, 'fond-arachne.json'), 'w'), indent=1, ensure_ascii=False)
    ecrire_ts(doc)
    print('  jeu : public/art/vecto/fonds/arachne.webp %d Ko, arachne-anim.webp %d Ko (%d × %d), %d calques' % (
        os.path.getsize(os.path.join(JEU, 'arachne.webp')) // 1024,
        os.path.getsize(os.path.join(JEU, 'arachne-anim.webp')) // 1024, planche.size[0], planche.size[1], len(meta)))
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


_JEU_IMG = {}


def composer_jeu(doc, t, particules=False):
    """Contrôle : l'image à l'instant t refaite comme le jeu la ferait (fixe + calques de la planche, et les
    particules si demandé : la règle de bg/fond-px.ts), à ×UP."""
    if not _JEU_IMG:
        _JEU_IMG['fixe'] = Image.open(os.path.join(JEU, CLAN + '.webp')).convert('RGBA')
        _JEU_IMG['planche'] = Image.open(os.path.join(JEU, CLAN + '-anim.webp')).convert('RGBA')
    base = _JEU_IMG['fixe'].copy()
    pl = _JEU_IMG['planche']
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
        elif c['genre'] == 'particules' and particules:
            e = next(e for e in ELEMS if e['id'] == c['id'])
            for x, y, i in particules_a(e, t):
                sx, sy, w_, h_ = c['cases'][i]
                px, py = round((x - w_ / UP / 2) * UP), round((y - h_ / UP / 2) * UP)
                im = pl.crop((sx, sy, sx + w_, sy + h_))
                ox, oy = max(0, -px), max(0, -py)
                if ox or oy:
                    im = im.crop((ox, oy, w_, h_))
                if px + ox < base.width and py + oy < base.height:
                    base.alpha_composite(im, (px + ox, py + oy))
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
    # (le fond pixel est supprimé depuis la v0.65.0 : la comparaison ne se fait que s'il est encore là)
    pxf = os.path.join(ROOT, 'public', 'art', 'px', 'fonds', 'arachne.webp')
    if os.path.exists(pxf):
        pix = Image.open(pxf).convert('RGBA')
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
    # chaque image est composée comme le jeu la fait (l'image fixe ×UP, puis les calques de la planche, particules
    # comprises) : c'est ce que montre le combat, et bien plus rapide que de redessiner le SVG 480 fois
    doc = json.load(open(os.path.join(HERE, 'fond-%s.json' % CLAN)))
    gif = []
    persos = poser(Image.new('RGBA', (720, hh), (0, 0, 0, 0)), s, x0, top)       # les personnages : une fois
    for i in range(n):
        t = i * 1000 / fps
        full = composer_jeu(doc, t, particules=True)
        im = full.crop((round(x0 * UP), round(top * UP), round(VUE_X[1] * UP), H * UP)).resize((720, hh), Image.LANCZOS)
        im.alpha_composite(persos)
        im = geste(im, s, phone).convert('RGB')
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
