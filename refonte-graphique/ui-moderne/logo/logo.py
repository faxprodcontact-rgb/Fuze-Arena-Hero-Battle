#!/usr/bin/env python3
"""Le LOGO du jeu en style moderne (29/11/2026, demande du propriétaire : « refais le logo du chargement en style
moderne »). Il remplace celui du 25/11 (refonte-graphique/pixel/ui/logo_hd.py : épées d'acier, ruban rouge, ombre floue).

Même disposition, aux couleurs de l'interface moderne (habillage pierre grise et or, boutons « Pierre de l'arène ») :
- « FUZE / ARENA » en grosses lettres d'or (les vrais contours de la police des titres, Lilita One : le logo ne dépend
  d'aucune police chargée), un or plus net (clair en haut, chaud en bas, un reflet doux en haut à droite), UN seul
  contour sombre (raisin, comme l'interface), et dessous une épaisseur de pierre grise (au lieu de la tranche brune) ;
- « HERO BATTLE » en lettres blanches sur une plaque de pierre grise cintrée, cerclée d'un filet d'or (comme les
  fenêtres et les boutons du jeu) ;
- les 4 cristaux d'élément (feu, eau, vent, terre), posés aux bouts de la plaque, à la place des épées ;
- une ombre portée SANS flou (iPhone : jamais de feGaussianBlur sur une grande forme), décalée vers le bas à gauche :
  la seule lumière du jeu vient d'en haut à droite.

  python3 refonte-graphique/ui-moderne/logo/logo.py → public/art/ui/logo.svg (posé dans index.html par
  python3 refonte-graphique/ui-moderne/chargement/chargement.py) + logo-apercu.png ici
"""
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'refonte-graphique', 'pixel', 'ui'))
from logo_hd import mot  # noqa: E402  (les lettres de Lilita One en tracés)

VW, VH = 640, 474
INK = '#1f1238'


def plaque_y(x):
    """La plaque est cintrée : ses bouts remontent un peu (un sourire), les lettres s'inclinent avec elle."""
    t = (x - 320) / 200
    return 16 * t * t, math.degrees(math.atan(2 * 16 * t / 200))


def bord(y0, x0=110, x1=530, n=42):
    return [(x0 + (x1 - x0) * i / n, y0 + plaque_y(x0 + (x1 - x0) * i / n)[0]) for i in range(n + 1)]


def poly(pts):
    return 'M' + ' L'.join('%.1f,%.1f' % p for p in pts)


def gemme(cx, cy, r, c, ang=0):
    """Un cristal à facettes (losange allongé) d'un élément : c = (reflet, lumière, base, ombre)."""
    hi, li, ba, sh = c
    w, h = r * 0.78, r * 1.25
    pts = [(0, -h), (w, -h * 0.18), (w * 0.62, h), (-w * 0.62, h), (-w, -h * 0.18)]
    rot = lambda p: (cx + p[0] * math.cos(math.radians(ang)) - p[1] * math.sin(math.radians(ang)),
                     cy + p[0] * math.sin(math.radians(ang)) + p[1] * math.cos(math.radians(ang)))
    P = [rot(p) for p in pts]
    mid = rot((w * 0.12, h * 0.05))
    out = (P[0], P[1], P[2], P[3], P[4])
    d = 'M' + ' L'.join('%.1f,%.1f' % p for p in out) + ' Z'
    lit = 'M%.1f,%.1f L%.1f,%.1f L%.1f,%.1f Z' % (*P[0], *P[1], *mid)
    dark = 'M%.1f,%.1f L%.1f,%.1f L%.1f,%.1f L%.1f,%.1f Z' % (*P[4], *P[3], *rot((-w * 0.05, h)), *mid)
    gl = rot((w * 0.16, -h * 0.42))
    return f'''
  <path d="{d}" fill="{INK}" stroke="{INK}" stroke-width="12" stroke-linejoin="round"/>
  <path d="{d}" fill="{ba}"/>
  <path d="{lit}" fill="{li}"/>
  <path d="{dark}" fill="{sh}" opacity=".85"/>
  <path d="M%.1f,%.1f L%.1f,%.1f L%.1f,%.1f Z" fill="{hi}" opacity=".9"/>
  <ellipse cx="{gl[0]:.1f}" cy="{gl[1]:.1f}" rx="{r * 0.13:.1f}" ry="{r * 0.1:.1f}" fill="#fff"/>''' % (*P[0], *rot((w * 0.5, -h * 0.55)), *rot((w * 0.18, -h * 0.25)))


FEU = ('#fff0d0', '#ffa050', '#ff5a24', '#c42e18')
EAU = ('#eafaff', '#8fdcff', '#3fa6f0', '#2a68c4')
VENT = ('#f0ffe8', '#a6f08a', '#5ccc5a', '#2e9a4a')
TERRE = ('#fff6dc', '#f2cf86', '#d89a46', '#a86a2c')


def svg():
    fuze = mot('FUZE', 178, 320, 160, espace=4)
    arena = mot('ARENA', 186, 320, 300, espace=2)
    hero = mot('HERO BATTLE', 56, 320, 372, espace=5, courbe=plaque_y)
    lettres = f'{fuze} {arena}'
    haut, bas = bord(318, 100, 540), bord(390, 100, 540)
    plaque = poly(haut) + ' L' + ' L'.join('%.1f,%.1f' % p for p in reversed(bas)) + ' Z'
    filet_h = poly(bord(326, 112, 528))
    filet_b = poly(bord(382, 112, 528))
    yl, yr = plaque_y(100)[0], plaque_y(540)[0]
    # les bouts arrondis de la plaque (deux demi-disques), où sont posés les cristaux
    bout_g = f'M100,{318 + yl:.1f} A36,36 0 0 0 100,{390 + yl:.1f} Z'
    bout_d = f'M540,{318 + yr:.1f} A36,36 0 0 1 540,{390 + yr:.1f} Z'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="4 0 {VW - 8} {VH}" role="img" aria-label="Fuze Arena – Hero Battle">
  <defs>
    <linearGradient id="lg-or" gradientUnits="userSpaceOnUse" x1="0" y1="40" x2="0" y2="300">
      <stop offset="0" stop-color="#fff6c8"/><stop offset=".16" stop-color="#ffe070"/><stop offset=".36" stop-color="#ffc22e"/>
      <stop offset=".48" stop-color="#f7a21e"/><stop offset=".5" stop-color="#ffd85c"/><stop offset=".7" stop-color="#ffbb2c"/>
      <stop offset="1" stop-color="#e8831a"/>
    </linearGradient>
    <linearGradient id="lg-pierre" gradientUnits="userSpaceOnUse" x1="0" y1="60" x2="0" y2="330">
      <stop offset="0" stop-color="#6a6788"/><stop offset="1" stop-color="#2e2c47"/>
    </linearGradient>
    <linearGradient id="lg-plaque" gradientUnits="userSpaceOnUse" x1="0" y1="318" x2="0" y2="392">
      <stop offset="0" stop-color="#7a7798"/><stop offset=".45" stop-color="#55526f"/><stop offset="1" stop-color="#34314c"/>
    </linearGradient>
    <linearGradient id="lg-reflet" gradientUnits="userSpaceOnUse" x1="0" y1="40" x2="0" y2="170">
      <stop offset="0" stop-color="#fff" stop-opacity=".6"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>
    </linearGradient>
    <radialGradient id="lg-lueur" cx="420" cy="90" r="300" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#fff6d0" stop-opacity=".3"/><stop offset="1" stop-color="#fff6d0" stop-opacity="0"/>
    </radialGradient>
    <path id="lg-l" d="{lettres}"/>
    <clipPath id="lg-c0"><use href="#lg-l"/></clipPath>
    <clipPath id="lg-c1"><use href="#lg-l" transform="translate(-3,4)"/></clipPath>
  </defs>
  <!-- l'ombre portée, sans flou : deux marches de plus en plus claires, vers le bas à gauche -->
  <g opacity=".22"><use href="#lg-l" transform="translate(-10,22)" fill="#0a0620" stroke="#0a0620" stroke-width="30" stroke-linejoin="round"/>
    <path d="{plaque}" transform="translate(-10,16)" fill="#0a0620" stroke="#0a0620" stroke-width="22" stroke-linejoin="round"/></g>
  <g opacity=".28"><use href="#lg-l" transform="translate(-5,14)" fill="#0a0620" stroke="#0a0620" stroke-width="26" stroke-linejoin="round"/></g>
  <!-- l'épaisseur de pierre sous les lettres, puis le contour unique -->
  <use href="#lg-l" transform="translate(0,14)" fill="{INK}" stroke="{INK}" stroke-width="24" stroke-linejoin="round"/>
  <use href="#lg-l" fill="{INK}" stroke="{INK}" stroke-width="24" stroke-linejoin="round"/>
  <use href="#lg-l" transform="translate(0,13)" fill="url(#lg-pierre)"/>
  <use href="#lg-l" transform="translate(0,7)" fill="url(#lg-pierre)"/>
  <!-- l'or : le bord éclairé (haut droit) en clair, le corps en dégradé, un reflet doux -->
  <g clip-path="url(#lg-c0)">
    <rect width="{VW}" height="{VH}" fill="#fffbe6"/>
    <g clip-path="url(#lg-c1)">
      <rect width="{VW}" height="{VH}" fill="#d0701e"/>
      <use href="#lg-l" transform="translate(3,-4)" fill="url(#lg-or)"/>
    </g>
    <ellipse cx="360" cy="76" rx="250" ry="62" fill="url(#lg-reflet)" opacity=".55"/>
    <rect width="{VW}" height="{VH}" fill="url(#lg-lueur)"/>
  </g>
  <!-- la plaque de pierre, cerclée d'un filet d'or -->
  <path d="{bout_g}" fill="url(#lg-plaque)" stroke="{INK}" stroke-width="9" stroke-linejoin="round"/>
  <path d="{bout_d}" fill="url(#lg-plaque)" stroke="{INK}" stroke-width="9" stroke-linejoin="round"/>
  <path d="{plaque}" fill="url(#lg-plaque)" stroke="{INK}" stroke-width="9" stroke-linejoin="round"/>
  <path d="{filet_h}" fill="none" stroke="#ffd36a" stroke-width="3.5" stroke-linecap="round" opacity=".95"/>
  <path d="{filet_b}" fill="none" stroke="#c9932e" stroke-width="3" stroke-linecap="round" opacity=".8"/>
  <path d="{hero}" fill="{INK}" stroke="{INK}" stroke-width="9" stroke-linejoin="round" transform="translate(0,3)"/>
  <path d="{hero}" fill="#ffffff" stroke="{INK}" stroke-width="5" stroke-linejoin="round" paint-order="stroke"/>
  <!-- les 4 cristaux d'élément, deux à chaque bout de la plaque -->
  {gemme(78, 338 + yl, 30, FEU, -16)}
  {gemme(66, 392 + yl, 23, EAU, -34)}
  {gemme(562, 338 + yr, 30, VENT, 16)}
  {gemme(574, 392 + yr, 23, TERRE, 34)}
</svg>'''


if __name__ == '__main__':
    s = svg()
    p = os.path.join(ROOT, 'public', 'art', 'ui', 'logo.svg')
    open(p, 'w', encoding='utf-8').write(s)
    print('public/art/ui/logo.svg', len(s), 'caractères')
    rendu = os.path.join(ROOT, 'refonte-graphique', 'ui-moderne', 'heros', 'rendu.cjs')
    subprocess.run(['node', rendu, p, os.path.join(HERE, 'logo-apercu.png'), '474', '#2a2350'], check=True)
