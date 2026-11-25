#!/usr/bin/env python3
"""Le LOGO du jeu en pixel art HD : « FUZE ARENA » en lettres d'or épaisses, le ruban rouge « HERO BATTLE », deux épées
croisées derrière. Même disposition que l'ancien logo peint (le propriétaire le connaît), redessinée pixel par pixel.

  python3 refonte-graphique/pixel/ui/logo.py         → public/art/ui-px/logo.webp (×1, le jeu l'agrandit sans flou)
                                                      + refonte-graphique/pixel/sortie/ui/logo.png (aperçu ×4)

Choix :
- lettres : la police des titres du jeu (Lilita One) tracée sans lissage, puis peinte comme du métal doré : le haut
  clair et chaud, une « ligne d'horizon » nette au milieu (reflet du métal), le bas orangé ; un liseré très clair sur
  les bords tournés vers la lumière (en haut à droite), un bord plus sombre en bas à gauche ;
- épaisseur : la tranche des lettres descend de 4 pixels (brun rouge), puis un seul contour sombre de 2 pixels autour
  du tout (un seul contour, jamais un contour par morceau) ;
- épées : en X d'un coin à l'autre, pente 2 pour 3 (marches régulières 1-2-1-2), acier bleuté (ombre
  vers le violet), garde et pommeau d'or, poignée de cuir rouge ;
- ruban : rouge du bandeau des titres (TitleBanner), légèrement cintré, queues repliées derrière, lettres crème.
"""
import os
import sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import uilib as U  # noqa: E402

W, H = 236, 156

# ---------------------------------------------------------------------------------------------- les gammes
OR = ['#a83e1c', '#cf5f1a', '#ec8a1e', '#f9b52c', '#ffd84a', '#ffec88', '#fff8c8']    # du plus sombre au plus clair
OR_ECLAT = '#fffdf0'
TRANCHE = ['#4e1420', '#6c1e1c', '#8e301a']                                           # l'épaisseur des lettres
ACIER = ['#3e3c6a', '#5c6494', '#8a98c4', '#c4d0ec', '#f2f6ff']
OR_PIECE = ['#6e2a1c', '#b0601a', '#e89a26', '#ffd24a', '#fff2a0']                     # garde, pommeau
CUIR = ['#3a1424', '#5e1e2a', '#86302e', '#a84a38']
RUBAN = ['#4a0e1c', '#7a1a26', '#a82a30', '#d6443e', '#f06a52', '#ff9a72']
CREME = '#fff3d6'


def lettres(mot, taille, espace):
    """Un mot en lettres d'or avec sa tranche : renvoie (couleurs h×w×4, masque face, masque tranche)."""
    m = U.texte(mot, taille, espace)
    h, w = m.shape
    pad = 6
    face = np.zeros((h + pad * 2, w + pad * 2), bool)
    face[pad:pad + h, pad:pad + w] = m
    T = U.Toile(face.shape[1], face.shape[0])
    # la tranche : la face poussée vers le bas (la lumière vient d'en haut)
    tr = np.zeros_like(face)
    for k in range(1, 5):
        tr |= U.S(face, 0, -k)
    tr &= ~face
    haut_tr = tr & (U.S(face, 0, -1) | U.S(face, 0, -2))
    T.peint(tr, TRANCHE[0])
    T.peint(haut_tr, TRANCHE[1])
    T.peint(tr & U.bord(tr, 1, 0) & ~U.bord(tr, 0, 1), TRANCHE[2])            # un reflet sur le bord droit de la tranche
    # la face : bandes de métal (haut clair, horizon net au milieu, bas orangé)
    y0, y1 = pad, pad + h
    Y = T.Y
    t = (Y - y0) / max(1, (y1 - y0))
    idx = np.full(face.shape, 3)
    idx[t < 0.16] = 6
    idx[(t >= 0.16) & (t < 0.30)] = 5
    idx[(t >= 0.30) & (t < 0.50)] = 4
    idx[(t >= 0.50) & (t < 0.56)] = 2                 # la ligne d'horizon du métal
    idx[(t >= 0.56) & (t < 0.80)] = 3
    idx[t >= 0.80] = 2
    for i, c in enumerate(OR):
        T.peint(face & (idx == i), c)
    # lumière en haut à droite : liseré clair ; ombre en bas à gauche : un ton plus sombre
    T.peint(U.bord(face, 0, 1) & U.bord(face, -1, 0) & face & (t < 0.6), OR[1])
    T.peint(U.bord(face, -1, 0) & (t >= 0.5), OR[1])
    T.peint(U.bord(face, 0, 1) & (t >= 0.5), OR[0])
    T.peint(U.bord(face, 1, 0) & (t < 0.5), OR_ECLAT)
    T.peint(U.bord(face, 0, -1) & (idx >= 4), OR_ECLAT)
    return T, face, tr


def epee(T, hx, hy, sens, long, graine=0):
    """Une épée dont le bout de la poignée est en (hx, hy), la lame montant vers le haut et vers `sens` (+1 droite,
    −1 gauche), pente 2 pour 1. Peinte dans la toile T (sans contour : il est fait pour tout le logo)."""
    X, Y = T.X, T.Y
    # repère de la lame : u le long (0 = bout de la poignée), v en travers (positif = côté haut)
    dx, dy = 3 * sens, -2
    n = np.hypot(dx, dy)
    ux, uy = dx / n, dy / n
    vx, vy = -uy * sens, ux * sens            # la normale côté haut
    rx, ry = X - hx, Y - hy
    u = rx * ux + ry * uy
    v = rx * vx + ry * vy
    poignee = 13
    garde = poignee + 3
    lame0 = garde + 2
    pointe = long - 14
    # lame : largeur 3,5 px de chaque côté, la pointe s'affine
    demi = np.where(u < pointe, 4.2, 4.2 * np.clip((long - u) / 14, 0, 1))
    lame = (u >= lame0) & (u <= long) & (np.abs(v) <= demi)
    m_cote_haut = lame & (v > 0.6)
    m_cote_bas = lame & (v < -0.6)
    arete = lame & ~m_cote_haut & ~m_cote_bas
    # côté tourné vers la lumière (en haut à droite) : le haut pour l'épée qui monte à gauche, l'arête pour l'autre
    if sens < 0:
        T.peint(m_cote_haut, ACIER[3]); T.peint(m_cote_bas, ACIER[1]); T.peint(arete, ACIER[4])
        T.peint(m_cote_bas & (np.abs(v) > demi - 1.1), ACIER[0])
    else:
        T.peint(m_cote_haut, ACIER[2]); T.peint(m_cote_bas, ACIER[1]); T.peint(arete, ACIER[3])
        T.peint(m_cote_bas & (np.abs(v) > demi - 1.1), ACIER[0])
        T.peint(m_cote_haut & (np.abs(v) > demi - 1.1), ACIER[3])
    # garde : une barre en travers, bouts arrondis
    g = (u >= garde - 2.5) & (u <= garde + 1.5) & (np.abs(v) <= 10)
    T.peint(g, OR_PIECE[2])
    T.peint(g & (u > garde), OR_PIECE[1])
    T.peint(g & (u < garde - 1.2) & (v > -8), OR_PIECE[3])
    T.peint(g & (np.abs(v) > 8.6), OR_PIECE[1])
    # gemme rouge au milieu de la garde
    gem = (np.hypot(u - (garde - 0.5), v) <= 1.8)
    T.peint(gem, RUBAN[3]); T.peint(gem & (v > 0.4), RUBAN[5])
    # poignée de cuir
    p = (u >= 4) & (u <= garde - 2.5) & (np.abs(v) <= 2.0)
    T.peint(p, CUIR[2])
    T.peint(p & (v < -0.6), CUIR[1])
    T.peint(p & (v > 1.0), CUIR[3])
    # pommeau d'or
    pom = np.hypot(u - 2.2, v) <= 3.4
    T.peint(pom, OR_PIECE[2])
    T.peint(pom & (v - u * 0.2 > 0.8), OR_PIECE[3])
    T.peint(pom & (v < -1.6), OR_PIECE[1])


def ruban(T, cx, y, demi_l, haut, mot):
    """Le ruban cintré (bouts relevés) avec ses queues repliées derrière et le texte crème."""
    X, Y = T.X, T.Y
    off = np.round(4 * ((X - cx) / demi_l) ** 2).astype(int)              # cintrage : les bouts montent de 4 px
    yy = Y + off                                                            # y « déplié »
    # les queues (derrière) : plus bas, échancrées en V
    for s in (-1, 1):
        x0 = cx + s * (demi_l - 6)
        x1 = cx + s * (demi_l + 22)
        lo, hi = min(x0, x1), max(x0, x1)
        q = (X >= lo) & (X <= hi) & (yy >= y + 7) & (yy <= y + haut + 7)
        bout = x1
        q &= ~((np.abs(X - bout) < 7 - np.abs(yy - (y + 7 + haut / 2)) * 0.9) & (np.sign(X - (bout - s * 7)) == s))
        T.peint(q, RUBAN[1])
        T.peint(q & (yy <= y + 8), RUBAN[2])
        T.peint(q & (yy >= y + haut + 6), RUBAN[0])
        # le pli (le revers sombre qui relie la queue au ruban)
        pli = (np.abs(X - x0) <= 3) & (yy >= y + haut - 1) & (yy <= y + haut + 7)
        T.peint(pli, RUBAN[0])
    bande = (np.abs(X - cx) <= demi_l) & (yy >= y) & (yy < y + haut)
    t = (yy - y) / haut
    T.peint(bande, RUBAN[3])
    T.peint(bande & (t < 0.12), RUBAN[5])
    T.peint(bande & (t >= 0.12) & (t < 0.3), RUBAN[4])
    T.peint(bande & (t >= 0.78), RUBAN[2])
    T.peint(bande & (t >= 0.92), RUBAN[1])
    # le texte, qui suit le cintrage
    m = U.texte(mot, 17, 0)
    h, w = m.shape
    tx0 = cx - w // 2
    ty0 = y + (haut - h) // 2
    for j in range(w):
        x = tx0 + j
        o = int(round(4 * ((x - cx) / demi_l) ** 2))
        col = m[:, j]
        for i in np.nonzero(col)[0]:
            yy0 = ty0 + i - o
            T.col[yy0 + 1, x, :3] = U.rgb(RUBAN[0])          # l'ombre portée des lettres
            T.col[yy0 + 1, x, 3] = 255
    for j in range(w):
        x = tx0 + j
        o = int(round(4 * ((x - cx) / demi_l) ** 2))
        for i in np.nonzero(m[:, j])[0]:
            T.col[ty0 + i - o, x, :3] = U.rgb(CREME)
            T.col[ty0 + i - o, x, 3] = 255


def logo():
    T = U.Toile(W, H)
    cx = W // 2
    # 1. les épées croisées (derrière)
    epee(T, 16, 150, +1, 240)
    epee(T, W - 17, 150, -1, 240)
    # 2. les mots
    fuze, _, _ = lettres('FUZE', 54, 2)
    arena, _, _ = lettres('ARENA', 56, 1)
    T.colle(fuze.image(), cx - fuze.w // 2, 4)
    T.colle(arena.image(), cx - arena.w // 2, 46)
    # 3. le ruban
    ruban(T, cx, 102, 66, 20, 'HERO BATTLE')
    # un seul contour autour du tout (2 pixels)
    T.contour(U.CONTOUR, r=2)
    return T


if __name__ == '__main__':
    T = logo()
    m = T.masque()
    ys, xs = np.nonzero(m)
    print('logo', T.w, T.h, 'boîte utile', xs.min(), ys.min(), xs.max(), ys.max())
    n = U.sauve(T.image(), os.path.join(U.OUT_DIR, 'logo.webp'))
    U.sauve(T.image(4), os.path.join(U.SORTIE, 'logo.png'))
    print('public/art/ui-px/logo.webp', n, 'octets')
