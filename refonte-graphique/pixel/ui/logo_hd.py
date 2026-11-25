#!/usr/bin/env python3
"""Le LOGO du jeu en HD (vectoriel, net à toutes les tailles) — demande du propriétaire du 25/11 : « le logo pas en pixel,
en HD, beau ». Même disposition que l'ancien logo peint : « FUZE / ARENA » en grosses lettres d'or, le ruban rouge
« HERO BATTLE » bordé d'or, deux épées croisées derrière.

Les lettres sont les vrais contours de la police des titres du jeu (Lilita One, lilita-one.woff2) convertis en tracés :
le logo ne dépend d'aucune police chargée. Or : dégradé métallique (haut clair, « ligne d'horizon » au milieu, bas orangé),
liseré clair sur les bords tournés vers la lumière (en haut à droite), bord plus sombre en bas à gauche, reflet doux,
tranche brun rouge en dessous, un seul contour sombre épais, ombre portée douce.

  python3 refonte-graphique/pixel/ui/logo_hd.py → public/art/ui/logo.svg (lu par chargement.py, posé dans index.html)
Aperçu PNG haute définition : refonte-graphique/pixel/sortie/ui/logo-hd.png (fait par la capture Playwright).
"""
import os
import sys
import math
import re
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import uilib as U  # noqa: E402

VW, VH = 640, 474           # tout compris : pommeaux des épées, queues du ruban, contour épais, ombre floue
FONT = TTFont(U.POLICE)
GS = FONT.getGlyphSet()
CMAP = FONT.getBestCmap()
HMTX = FONT['hmtx']


def mot(texte, taille, cx, base, espace=0.0, courbe=None):
    """Le tracé SVG d'un mot centré sur cx, ligne de base `base` ; taille = hauteur de l'em en unités du logo.
    courbe(x) = (décalage vertical, angle en degrés) pour suivre un ruban."""
    k = taille / 1000
    largeurs = [HMTX[CMAP[ord(c)]][0] * k for c in texte]
    total = sum(largeurs) + espace * (len(texte) - 1)
    x = cx - total / 2
    d = []
    for c, w in zip(texte, largeurs):
        g = CMAP[ord(c)]
        dy, ang = courbe(x + w / 2) if courbe else (0, 0)
        a = math.radians(ang)
        mx, my = x + w / 2, base + dy
        # x' = mx + cos·(gx−w/2) − sin·(−gy) … (la police a y vers le haut)
        ca, sa = math.cos(a), math.sin(a)
        t = (k * ca, k * sa, k * sa, -k * ca, mx - ca * w / 2, my - sa * w / 2)
        pen = SVGPathPen(GS)
        GS[g].draw(TransformPen(pen, t))
        d.append(re.sub(r'-?\d+\.\d+', lambda m: f'{float(m.group()):.1f}'.rstrip('0').rstrip('.'), pen.getCommands()))
        x += w + espace
    return ' '.join(d)


def epee(id_, sens):
    """Une épée en X : la garde en bas, la pointe en haut vers l'extérieur. Dessinée verticale puis tournée."""
    ang = 50 * sens
    cx, cy = 320, 262
    # (repère de l'épée : 0 = la garde, la lame monte vers y négatif ; la pointe à 530 de la garde)
    lame = 'M-14,-12 L-14,-490 L0,-530 L14,-490 L14,-12 Z'
    lame_ombre = 'M0,-12 L0,-530 L14,-490 L14,-12 Z'
    arete = 'M-2,-20 L-2,-490 L0,-502 L2,-490 L2,-20 Z'
    return f'''
  <g transform="translate({cx},{cy}) rotate({ang}) translate(0,200)">
    <path d="{lame}" fill="url(#lg-acier)" stroke="#241434" stroke-width="7" stroke-linejoin="round"/>
    <path d="{lame_ombre}" fill="#5f6a9e" opacity=".55"/>
    <path d="{arete}" fill="#f6f9ff" opacity=".9"/>
    <rect x="-10" y="4" width="20" height="62" rx="7" fill="url(#lg-cuir)" stroke="#241434" stroke-width="6"/>
    <rect x="-52" y="-16" width="104" height="22" rx="11" fill="url(#lg-or-piece)" stroke="#241434" stroke-width="6"/>
    <circle cx="0" cy="-5" r="9" fill="#d9303a" stroke="#5e1418" stroke-width="3"/>
    <circle cx="3" cy="-8" r="3" fill="#ffc0b0"/>
    <circle cx="0" cy="78" r="15" fill="url(#lg-or-piece)" stroke="#241434" stroke-width="6"/>
    <circle cx="4" cy="73" r="4.5" fill="#fff6c8"/>
  </g>'''


def ruban_y(x):
    """Le ruban est cintré : ses bouts remontent (sourire), et chaque lettre s'incline avec lui."""
    t = (x - 320) / 190
    return 22 * t * t, math.degrees(math.atan(2 * 22 * t / 190))


def svg():
    fuze = mot('FUZE', 178, 320, 160, espace=4)
    arena = mot('ARENA', 186, 320, 300, espace=2)
    hero = mot('HERO BATTLE', 50, 320, 361, espace=3, courbe=ruban_y)
    lettres = f'{fuze} {arena}'
    # le ruban : bande cintrée de x 120 à 520 (bouts relevés), queues repliées derrière
    def bord(y0):
        pts = []
        for i in range(0, 41):
            x = 120 + i * 10
            pts.append((x, y0 + ruban_y(x)[0]))
        return pts
    haut, bas = bord(318), bord(372)
    bande = 'M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in haut) + ' L' + ' L'.join(
        f'{x:.1f},{y:.1f}' for x, y in reversed(bas)) + ' Z'
    ligne_h = 'M' + ' L'.join(f'{x:.1f},{y + 6:.1f}' for x, y in haut)
    ligne_b = 'M' + ' L'.join(f'{x:.1f},{y - 6:.1f}' for x, y in bas)
    yl, yr = ruban_y(120)[0], ruban_y(520)[0]
    queue_g = f'M132,{336 + yl:.0f} L64,{346 + yl:.0f} L86,{374 + yl:.0f} L58,{404 + yl:.0f} L140,{398 + yl:.0f} Z'
    queue_d = f'M508,{336 + yr:.0f} L576,{346 + yr:.0f} L554,{374 + yr:.0f} L582,{404 + yr:.0f} L500,{398 + yr:.0f} Z'
    pli_g = f'M120,{372 + yl:.0f} L140,{398 + yl:.0f} L140,{372 + yl:.0f} Z'
    pli_d = f'M520,{372 + yr:.0f} L500,{398 + yr:.0f} L500,{372 + yr:.0f} Z'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="4 0 {VW - 8} {VH}" role="img" aria-label="Fuze Arena – Hero Battle">
  <defs>
    <linearGradient id="lg-or" gradientUnits="userSpaceOnUse" x1="0" y1="40" x2="0" y2="300">
      <stop offset="0" stop-color="#fffbe0"/><stop offset=".14" stop-color="#ffe886"/><stop offset=".3" stop-color="#ffc93a"/>
      <stop offset=".41" stop-color="#f39a1c"/><stop offset=".47" stop-color="#ffe27a"/><stop offset=".6" stop-color="#ffd24a"/>
      <stop offset=".72" stop-color="#ffb02c"/><stop offset=".88" stop-color="#ffd860"/><stop offset="1" stop-color="#e2801c"/>
    </linearGradient>
    <linearGradient id="lg-tranche" gradientUnits="userSpaceOnUse" x1="0" y1="60" x2="0" y2="320">
      <stop offset="0" stop-color="#9a3a1a"/><stop offset="1" stop-color="#5a1820"/>
    </linearGradient>
    <linearGradient id="lg-acier" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#aab6dc"/><stop offset=".45" stop-color="#eef3ff"/><stop offset=".55" stop-color="#c3cdea"/><stop offset="1" stop-color="#7d88b8"/>
    </linearGradient>
    <linearGradient id="lg-or-piece" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#fff0a0"/><stop offset=".45" stop-color="#ffc23a"/><stop offset="1" stop-color="#b8601a"/>
    </linearGradient>
    <linearGradient id="lg-cuir" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#5e1e2a"/><stop offset=".6" stop-color="#9a3a34"/><stop offset="1" stop-color="#6a2230"/>
    </linearGradient>
    <linearGradient id="lg-rouge" gradientUnits="userSpaceOnUse" x1="0" y1="318" x2="0" y2="400">
      <stop offset="0" stop-color="#ff7a62"/><stop offset=".22" stop-color="#e4423e"/><stop offset=".7" stop-color="#b42632"/><stop offset="1" stop-color="#7e1426"/>
    </linearGradient>
    <linearGradient id="lg-reflet" gradientUnits="userSpaceOnUse" x1="0" y1="40" x2="0" y2="170">
      <stop offset="0" stop-color="#fff" stop-opacity=".55"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>
    </linearGradient>
    <path id="lg-l" d="{lettres}"/>
    <clipPath id="lg-c0"><use href="#lg-l"/></clipPath>
    <clipPath id="lg-c1"><use href="#lg-l" transform="translate(-3,4)"/></clipPath>
    <clipPath id="lg-c2"><use href="#lg-l" transform="translate(3,-4)"/></clipPath>
    <filter id="lg-flou" x="-10%" y="-10%" width="120%" height="130%"><feGaussianBlur stdDeviation="7"/></filter>
  </defs>
  <g filter="url(#lg-flou)" opacity=".55" transform="translate(0,12)">
    <use href="#lg-l" fill="#0c0614" stroke="#0c0614" stroke-width="26" stroke-linejoin="round"/>
    <path d="{bande}" fill="#0c0614" stroke="#0c0614" stroke-width="12"/>
  </g>
  {epee('g', -1)}
  {epee('d', +1)}
  <use href="#lg-l" transform="translate(0,12)" fill="#2a1030" stroke="#2a1030" stroke-width="24" stroke-linejoin="round"/>
  <use href="#lg-l" fill="#2a1030" stroke="#2a1030" stroke-width="24" stroke-linejoin="round"/>
  <use href="#lg-l" transform="translate(0,11)" fill="url(#lg-tranche)"/>
  <use href="#lg-l" transform="translate(0,6)" fill="url(#lg-tranche)"/>
  <g clip-path="url(#lg-c0)">
    <rect width="{VW}" height="{VH}" fill="#fffbe6"/>
    <g clip-path="url(#lg-c1)">
      <rect width="{VW}" height="{VH}" fill="#c4581a"/>
      <use href="#lg-l" transform="translate(3,-4)" fill="url(#lg-or)"/>
    </g>
    <ellipse cx="350" cy="78" rx="250" ry="66" fill="url(#lg-reflet)" opacity=".7"/>
  </g>
  <path d="{queue_g}" fill="#8a1a2a" stroke="#2a1030" stroke-width="7" stroke-linejoin="round"/>
  <path d="{queue_d}" fill="#8a1a2a" stroke="#2a1030" stroke-width="7" stroke-linejoin="round"/>
  <path d="{pli_g}" fill="#4e0c1a"/><path d="{pli_d}" fill="#4e0c1a"/>
  <path d="{bande}" fill="url(#lg-rouge)" stroke="#2a1030" stroke-width="7" stroke-linejoin="round"/>
  <path d="{ligne_h}" fill="none" stroke="#ffd24a" stroke-width="4" stroke-linecap="round"/>
  <path d="{ligne_b}" fill="none" stroke="#c98a24" stroke-width="4" stroke-linecap="round"/>
  <path d="{hero}" fill="#2a1030" stroke="#2a1030" stroke-width="9" stroke-linejoin="round" transform="translate(0,3)"/>
  <path d="{hero}" fill="#fff3d6" stroke="#5e1418" stroke-width="5" stroke-linejoin="round" paint-order="stroke"/>
  <path d="M503,12 l6,16 l16,6 l-16,6 l-6,16 l-6,-16 l-16,-6 l16,-6 Z" fill="#fffbe6"/>
</svg>'''


if __name__ == '__main__':
    s = svg()
    p = os.path.join(U.PUBLIC, 'art', 'ui', 'logo.svg')
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'w', encoding='utf-8').write(s)
    print('public/art/ui/logo.svg', len(s), 'caractères')
