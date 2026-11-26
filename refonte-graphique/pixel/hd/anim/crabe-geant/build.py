# Crabe géant (mon-kesha-costaud, clan de Kesha, eau, costaud) : le tank des abysses — pose (grosse respiration
# lente), attaque de base « Pince-massue » (il se cabre, la grosse pince armée en arrière, charge en deux pas de
# côté et abat la pince fermée sur l'ennemi), attaque spéciale « Lame de fond » (il se dresse sur la pointe des
# pattes, les deux pinces levées comme un vrai crabe qui menace, l'eau s'enroule autour de la grosse pince, puis il
# l'abat dans le sol : une vague jaillit du sol et roule vers la droite sur toute la première ligne ennemie).
#
# Lancer : python3 refonte-graphique/pixel/hd/anim/crabe-geant/build.py
# Écrit dans refonte-graphique/pixel/sortie/ : anim-crabe-geant-pose.gif, anim-crabe-geant-attaque.gif,
# anim-crabe-geant-speciale.gif, anim-crabe-geant-jeu.gif (les trois enchaînées sur le fond de prairie, ×2) et
# anim-crabe-geant-planche.png (toutes les images, ×3, numérotées avec leur durée).
#   python3 build.py essai <dossier>              → images de contrôle (planche ×2, chaque image seule)
#
# Même méthode que l'essai validé d'Eldra (../eldra/build.py) et que son chef de clan Kesha (../kesha/build.py :
# outils d'eau, palette des sept bleus, montage, fichiers de sortie, recopiés ici ; leurs dossiers ne sont pas
# touchés). La rotation au pixel près vient de Rook (../rook/build.py, trois cisaillements : aucun pixel créé ni
# perdu) :
#   - le dessin validé (../../monstres/crabe-geant.txt) n'est PAS modifié : on le découpe en morceaux (la grosse
#     pince avec son avant-bras et son anneau de bronze, ses deux doigts, la petite pince lointaine, les yeux sur
#     leurs pédoncules, les algues, le bas des six pattes, le reste du corps) et chaque image pose ces morceaux ;
#   - un vrai mouvement de crabe, pas un humain : le corps est porté par six pattes qui restent plantées ; quand il
#     se baisse ou se dresse, seul le bas des pattes se raccourcit ou s'allonge (rangées retirées ou doublées) ;
#     quand il avance, il fait de petits pas de côté, une patte sur deux (trois pattes en l'air, trois au sol qui
#     s'inclinent : cisaillement par rangées) ; les yeux rentrent dans leurs logettes avant le coup (comme un vrai
#     crabe) et suivent le corps avec une image de retard ; les algues pendent et suivent ; il bave des bulles ;
#   - les pinces TOURNENT autour de leur articulation par trois cisaillements d'un pixel entier (chaque pixel du
#     dessin est déplacé tel quel) ; comme la lumière doit rester en haut à droite, chaque pince tournée est
#     RÉÉCLAIRÉE : sur chaque pixel, le ton monte ou descend d'un cran ou deux sur la gamme de sa matière (carapace,
#     bout bleu, ivoire, bronze) selon que le bord est maintenant tourné vers la lumière ou vers l'ombre ; les doigts
#     de la grosse pince s'ouvrent et se ferment (chacun tourne autour de sa base) ;
#   - derrière l'articulation de la grosse pince, une logette sombre (membranes gris-bleu) bouche ce que l'avant-bras
#     découvre en tournant ;
#   - les effets (eau, écume, gouttes, bulles, poussière du sol) ont leur petite palette, sans contour noir, en
#     formes courbes (nappes, bouffées, volutes, gouttes) : aucun rayon droit ;
#   - c'est un tank : longues préparations tenues, coups très courts, impacts tenus (le sol tremble : petites
#     bouffées de poussière sous les pattes), retours lents.
#
# MOMENT DE LANCEMENT de la spéciale (pour le jeu) : IMAGE 11 (à partir de 0) = la vague déferle sur la première
# ligne ennemie (arrêt sur image 200 ms) ; le coup de la pince dans le sol est l'image 5.
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
HD = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.abspath(os.path.join(HD, '..', 'sortie'))
sys.path.insert(0, HD)
import hd  # noqa: E402  (lecture seule : le format des héros HD)

NAME = 'crabe-geant'
SRC = hd.load(os.path.join(HD, 'monstres', NAME + '.txt'))
PAL = {k: (hd.hexrgb(v) if isinstance(v, str) else tuple(v)) for k, v in SRC['palette'].items()}
INK = hd.INK
BG = (232, 236, 242)

# ---------------------------------------------------------------- palette des effets (eau, comme Kesha / Ilian)
# Lettres libres (le crabe utilise a-h, j-n, t-v, x-z, B-G, I, J, L-O). Les sept bleus de l'eau sont ceux de Kesha
# et des autres héros d'eau (seule la lettre de l'eau profonde change : Q au lieu de B) ; la poussière du sol
# reprend les ocres des colosses (Astérion) : le sol tremble sous le tank.
FXPAL = {
    'W': (255, 255, 255),   # écume blanche, coeur de l'éclaboussure
    'X': (214, 246, 255),   # écume pâle
    'Y': (138, 226, 248),   # eau, lumière (cyan)
    'Z': (62, 176, 232),    # eau
    'A': (34, 118, 206),    # eau, ombre
    'Q': (26, 70, 156),     # eau profonde
    'R': (20, 38, 104),     # creux de l'eau (indigo)
    'K': (242, 224, 182),   # poussière, lumière
    'P': (200, 160, 112),   # poussière (ocre)
    'S': (142, 102, 74),    # poussière, ombre
}
ALLPAL = dict(PAL)
ALLPAL.update(FXPAL)

# ---------------------------------------------------------------- la scène
# Toile des animations : le point « sol » du crabe est posé en SOL. De la place au-dessus (la pince levée en
# arrière) et beaucoup à droite (la charge, puis la vague qui roule jusqu'au bout de la ligne ennemie).
W, H = 372, 196
SOL = (92, 184)
OX, OY = SOL[0] - SRC['sol'][0], SOL[1] - SRC['sol'][1]   # grille du dessin -> toile
GROUND = SOL[1]
ENEMY_X = SOL[0] + 168                                     # l'ennemi de devant (milieu du corps, toile)
LIGHT = np.array([0.6, -0.8])                              # la lumière vient d'en haut à droite (écran)
LN = LIGHT / np.linalg.norm(LIGHT)


def grid(rows):
    return np.array([list(r) for r in rows])


CORPS = grid(SRC['calques'][0][2])
GH, GW = CORPS.shape
YY, XX = np.mgrid[0:GH, 0:GW]


def isin(g, letters):
    return np.isin(g, list(letters))


# ---------------------------------------------------------------- découpe du dessin en morceaux
rest = CORPS.copy()


def take(mask):
    part = np.where(mask, rest, '.')
    rest[mask] = '.'
    return part


filled = rest != '.'
P = {}
# la grosse pince levée (pince, avant-bras, anneau de bronze) : à droite de la face ; la limite suit le pli sombre
# entre l'avant-bras et la carapace (rangée par rangée)
CLAW_X0 = {70: 95, 71: 93, 72: 93, 73: 92, 74: 93, 75: 92, 76: 91, 77: 90}
cm = np.zeros((GH, GW), bool)
for y in range(0, 84):
    x0 = 97 if y < 51 else 95 if y < 70 else CLAW_X0.get(y, 89)
    cm[y, x0:] = True
P['pince'] = take(filled & cm)
# la petite pince lointaine (basse, devant) et son bras
P['petite'] = take(filled & (((YY >= 86) & (YY <= 99) & (XX >= 97)) | ((YY >= 84) & (YY <= 85) & (XX >= 104))))
# les yeux sur leurs pédoncules
P['yeux'] = take(filled & (YY >= 38) & (YY <= 50) & (XX >= 81) & (XX <= 96))
# les algues qui pendent du bord de la carapace (on bouche leur place avec la carapace voisine, à droite)
ALG = filled & isin(rest, 'klmn')
P['algues'] = take(ALG)
for y in range(GH):
    xs = np.nonzero(ALG[y])[0]
    for x in xs[::-1]:
        if x <= 12:
            continue                                     # le brin du bord gauche dépasse de la silhouette
        nx = x + 1
        while nx < GW and rest[y, nx] == '.':
            nx += 1
        if nx < GW:
            rest[y, x] = rest[y, nx]
# le bas des six pattes (sous la rangée LEG0) : chacune à part (pas de côté, appui, raccourcies quand il se baisse)
LEG0, LEG1 = 96, SRC['sol'][1]
legs_zone = filled & (YY >= LEG0) & (XX <= 100)
LEG_X = [(3, 10), (16, 25), (39, 49), (58, 68), (69, 80), (87, 97)]
P['pattes'] = [take(legs_zone & (XX >= a) & (XX <= b)) for a, b in LEG_X]
P['corps'] = rest.copy()
# groupes de pas (une patte sur deux) : A = 1re, 3e, 5e ; B = 2e, 4e, 6e
GROUP = ['A', 'B', 'A', 'B', 'A', 'B']

# les doigts de la grosse pince : chacun tourne autour de sa base
FING_L = (YY <= 30) & (XX <= 107)
FING_R = (YY <= 28) & (XX >= 116)
PIV_FL = (100.5, 30.5)
PIV_FR = (120.5, 29.5)
PIV_CLAW = (92.5, 81.5)                  # l'articulation de la grosse pince (contre la carapace)
PIV_SMALL = (97.5, 91.5)                 # l'articulation de la petite pince
TIP_CLAW = (114.0, 22.0)                 # le milieu du bout de la pince (là où elle frappe)
FIST = (111.0, 40.0)                     # le gras de la pince (le « poing »)
MOUTH = (92.0, 70.0)                     # la bouche (les bulles)
BLINK = dict(SRC['cligne'])


# ---------------------------------------------------------------- outils de pose (au pixel, jamais lissé)
def empty(shape=None):
    return np.full(shape or (H, W), '.', dtype='<U1')


def shear_rows(part, f, fill='.'):
    out = np.full_like(part, fill)
    h, w = part.shape
    for y in range(h):
        d = int(f(y))
        if d == 0:
            out[y] = part[y]
        elif d > 0:
            if d < w:
                out[y, d:] = part[y, :-d]
        else:
            if -d < w:
                out[y, :d] = part[y, -d:]
    return out


def shear_cols(part, f, fill='.'):
    out = np.full_like(part, fill)
    h, w = part.shape
    for x in range(w):
        d = int(f(x))
        if d == 0:
            out[:, x] = part[:, x]
        elif d > 0:
            if d < h:
                out[d:, x] = part[:-d, x]
        else:
            if -d < h:
                out[:d, x] = part[-d:, x]
    return out


# ---- rotation au pixel près (trois cisaillements, Paeth) + quart de tour exact, puis réclairage
RP = 96                                   # demi-côté de la grille carrée centrée sur le pivot


def light_field(m):
    """pour une forme pleine (masque) : > 0 sur les bords tournés vers la lumière (en haut à droite), < 0 sur les
    bords dans l'ombre, ~0 au milieu (deux échelles : bord net + volume doux)"""
    out = np.zeros(m.shape)
    for (sig, a, wgt) in ((1.6, 2.0, 0.55), (5.0, 6.0, 0.45)):
        im = Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(sig))
        Bm = np.asarray(im, float) / 255
        dx, dy = int(round(LN[0] * a)), int(round(LN[1] * a))
        ahead = np.roll(np.roll(Bm, -dy, 0), -dx, 1)
        behind = np.roll(np.roll(Bm, dy, 0), dx, 1)
        out += wgt * (behind - ahead)
    return out


# les gammes de tons de chaque matière (du plus sombre au plus clair) : le réclairage monte ou descend d'un cran
RAMPS = ['abcdefgh', 'BCDEF', 'GIJ', 'tjLu']
STEP = {}
for ramp in RAMPS:
    for i, ch in enumerate(ramp):
        STEP.setdefault(ch, (ramp, i))
RELIGHT = 3.2                             # force du réclairage (crans de ton par unité de lumière)


def _square(part, pivot):
    S = 2 * RP + 1
    big = np.full((S, S), '.', dtype='<U1')
    idx = np.full((S, S), -1, dtype=np.int64)
    px, py = int(math.floor(pivot[0])), int(math.floor(pivot[1]))
    ys, xs = np.nonzero(part != '.')
    by, bx = ys - py + RP, xs - px + RP
    big[by, bx] = part[ys, xs]
    idx[by, bx] = ys * GW + xs
    return big, idx, (px, py)


def _paeth(g, deg, fill):
    k = int(round(deg / 90.0))
    rem = deg - 90 * k
    if k:
        g = np.rot90(g, k)                # quart de tour exact (sens inverse des aiguilles d'une montre à l'écran)
    if abs(rem) < 0.01:
        return g
    a = math.radians(rem)
    t, s = -math.tan(a / 2), math.sin(a)
    c = RP + 0.5

    def sx(gg, kk):
        return shear_rows(gg, lambda y: math.floor(kk * (y + 0.5 - c) + 0.5), fill)

    def sy(gg, kk):
        return shear_cols(gg, lambda x: math.floor(kk * (x + 0.5 - c) + 0.5), fill)
    g = sx(g, -t)
    g = sy(g, -s)
    g = sx(g, -t)
    return g


def rotate(part, pivot, deg, relight=True):
    """tourne un morceau (grille du dessin) autour de pivot, deg > 0 : sens inverse des aiguilles d'une montre (à
    l'écran). Renvoie (grille carrée, (px, py)) : la case (RP, RP) de la grille carrée est le pivot (px, py)."""
    big, idx, pp = _square(part, pivot)
    if not deg:
        return big, pp
    ridx = _paeth(idx, deg, -1)
    out = np.full(ridx.shape, '.', dtype='<U1')
    ok = ridx >= 0
    flat = part.ravel()
    out[ok] = flat[ridx[ok]]
    if relight:
        F0 = light_field(big != '.')
        f0 = F0.ravel()
        # le champ de lumière d'origine, transporté avec chaque pixel
        bigidx = np.full(big.shape, -1, dtype=np.int64)
        m0 = idx >= 0
        bigidx[m0] = np.arange(big.size).reshape(big.shape)[m0]
        lookup = {int(v): int(b) for v, b in zip(idx[m0], bigidx[m0])}
        F1 = light_field(ok)
        ys, xs = np.nonzero(ok)
        for y, x in zip(ys, xs):
            ch = out[y, x]
            if ch not in STEP:
                continue
            ramp, i = STEP[ch]
            d = (F1[y, x] - f0[lookup[int(ridx[y, x])]]) * RELIGHT
            j = int(np.clip(i + int(math.floor(d + 0.5)), 0, len(ramp) - 1))
            if ramp == 'abcdefgh' and i >= 1:
                j = max(1, j)             # la carapace ne descend pas jusqu'au bleu des abysses
            out[y, x] = ramp[j]
    return out, pp


def rot_point(p, pivot, deg):
    """où arrive le point p (grille) quand on tourne autour de pivot de deg (même sens que rotate)"""
    a = math.radians(deg)
    vx, vy = p[0] - pivot[0], p[1] - pivot[1]
    return (pivot[0] + vx * math.cos(a) + vy * math.sin(a), pivot[1] - vx * math.sin(a) + vy * math.cos(a))


class Pose:
    """où est le crabe dans cette image : glissade, décalage du corps, appui des pattes"""
    pass


def to_canvas(p, dx, dy):
    return np.array([p[0] + OX + dx, p[1] + OY + dy], float)


def blit(canvas, part, dx=0, dy=0, swap=None, only_empty=False):
    """pose un morceau (coordonnées de la grille) sur la toile, décalé de (dx, dy) pixels"""
    ys, xs = np.nonzero(part != '.')
    cy, cx = ys + dy + OY, xs + dx + OX
    ok = (cy >= 0) & (cy < H) & (cx >= 0) & (cx < W)
    ys, xs, cy, cx = ys[ok], xs[ok], cy[ok], cx[ok]
    if only_empty:
        e = canvas[cy, cx] == '.'
        ys, xs, cy, cx = ys[e], xs[e], cy[e], cx[e]
    vals = part[ys, xs]
    if swap:
        vals = np.array([swap.get(v, v) for v in vals])
    canvas[cy, cx] = vals


def blit_sq(canvas, sq, pp, dx=0, dy=0, swap=None):
    """pose une grille carrée (rotate) : sa case (RP, RP) tombe sur le pivot pp de la grille, décalé de (dx, dy)"""
    ys, xs = np.nonzero(sq != '.')
    cy, cx = ys - RP + pp[1] + dy + OY, xs - RP + pp[0] + dx + OX
    ok = (cy >= 0) & (cy < H) & (cx >= 0) & (cx < W)
    vals = sq[ys[ok], xs[ok]]
    if swap:
        vals = np.array([swap.get(v, v) for v in vals])
    canvas[cy[ok], cx[ok]] = vals


def big_claw(open_=0.0):
    """la grosse pince, doigts ouverts (open_ > 0) ou fermés (open_ < 0 : -1 = fermée, les pointes se croisent)"""
    p = P['pince']
    if not open_:
        return p
    out = np.where(FING_L | FING_R, '.', p)
    # doigt de gauche : tourne vers la gauche pour s'ouvrir ; doigt de droite : vers la droite
    if open_ > 0:
        dl, dr = 9 * open_, -9 * open_
    else:
        dl, dr = 15 * open_, -14 * open_
    for mask, piv, deg in ((FING_L, PIV_FL, dl), (FING_R, PIV_FR, dr)):
        sq, pp = rotate(np.where(mask, p, '.'), piv, deg, relight=False)
        ys, xs = np.nonzero(sq != '.')
        gy, gx = ys - RP + pp[1], xs - RP + pp[0]
        ok = (gy >= 0) & (gy < GH) & (gx >= 0) & (gx < GW)
        gy, gx, ys, xs = gy[ok], gx[ok], ys[ok], xs[ok]
        out[gy, gx] = sq[ys, xs]
    # la base des doigts : ce que la rotation découvre est rebouché avec le ton de la paume juste dessous
    for (mask, x0, x1, y0, y1) in ((FING_L, 97, 107, 24, 31), (FING_R, 115, 126, 22, 29)):
        for y in range(y1, y0 - 1, -1):
            for x in range(x0, x1 + 1):
                if out[y, x] == '.' and p[y, x] != '.' and out[y + 1, x] != '.' and y >= y1 - 2:
                    out[y, x] = out[y + 1, x]
    return out


def small_claw(pinch=0):
    """la petite pince : pinch = 1 elle s'entrouvre (le doigt du haut se soulève d'un pixel), -1 elle se ferme"""
    p = P['petite']
    if not pinch:
        return p
    m = (YY <= 89) & (XX >= 118)
    top = np.where(m, p, '.')
    out = np.where(m, '.', p)
    top = shear_cols(top, lambda x: -pinch * (1 if x >= 121 else 0))
    put = top != '.'
    out[put] = top[put]
    return out


def eyes_part(dy=0):
    """les yeux : dy > 0 ils rentrent (ils passent derrière la carapace), dy < 0 les pédoncules s'allongent"""
    e = P['yeux']
    if dy >= 0:
        return e, dy
    up = np.full_like(e, '.')
    up[:dy] = e[-dy:]                     # tout remonte de |dy| …
    for k in range(-dy):                  # … et la dernière rangée des pédoncules est doublée
        row = 50 + dy + 1 + k
        up[row] = np.where(e[50] != '.', e[50], up[row])
    return up, 0


def algae(sway=0):
    """les algues pendent du bord : leur bas part vers l'arrière (sway < 0) ou l'avant, le haut reste accroché"""
    a = P['algues']
    if not sway:
        return a
    return shear_rows(a, lambda y: int(round(sway * max(0, y - 56) / 14.0)) if y >= 56 else 0)


def lower_leg(i, top_dx, top_dy, foot_dx, lift):
    """le bas d'une patte : son haut suit le corps (top_dx, top_dy), sa pointe est en foot_dx, levée de lift.
    Les rangées du milieu sont doublées ou retirées (jamais d'image lissée) ; la patte s'incline par rangées."""
    part = P['pattes'][i]
    rows = list(range(LEG0, LEG1 + 1))
    n_src = len(rows)
    y_top = LEG0 + top_dy
    y_bot = LEG1 - lift
    n = y_bot - y_top + 1
    keep_top, keep_bot = 2, 6
    mid = rows[keep_top:n_src - keep_bot]
    n_mid = n - keep_top - keep_bot
    if n_mid < 1:
        n_mid = 1
    src = rows[:keep_top] + [mid[min(len(mid) - 1, int(k * len(mid) / n_mid))] for k in range(n_mid)] + \
        rows[n_src - keep_bot:]
    out = []
    for k, s in enumerate(src):
        t = k / max(1, len(src) - 1)
        dx = top_dx + (foot_dx - top_dx) * t
        out.append((y_top + k, s, int(math.floor(dx + 0.5))))
    return part, out


def draw_leg(canvas, part, rows):
    for (y, s, dx) in rows:
        row = part[s]
        xs = np.nonzero(row != '.')[0]
        cy = y + OY
        if not 0 <= cy < H:
            continue
        cx = xs + dx + OX
        ok = (cx >= 0) & (cx < W)
        canvas[cy, cx[ok]] = row[xs[ok]]


# ---------------------------------------------------------------- rendu
def to_rgba(canvas, pal=ALLPAL):
    img = np.zeros((canvas.shape[0], canvas.shape[1], 4), np.uint8)
    for ch, rgb in pal.items():
        m = canvas == ch
        if m.any():
            img[m, :3] = rgb
            img[m, 3] = 255
    return img


def compose(hero, fx_back=None, fx_front=None, flash=None):
    out = np.zeros((H, W, 4), np.uint8)
    layers = []
    if fx_back is not None:
        layers.append(to_rgba(fx_back))
    h = hd.outline(to_rgba(hero))
    if flash:
        m = (h[:, :, 3] > 0) & ~np.all(h[:, :, :3] == INK, axis=2)
        h[m, :3] = (h[m, :3].astype(int) + (255 - h[m, :3].astype(int)) * flash // 100).astype(np.uint8)
    layers.append(h)
    if fx_front is not None:
        layers.append(to_rgba(fx_front))
    for L in layers:
        m = L[:, :, 3] > 0
        out[m] = L[m]
    return out


class Ctx:
    pass


def socket(cv, c):
    """la logette sombre derrière l'articulation de la grosse pince (membranes) : bouche ce que l'avant-bras découvre"""
    cx, cy = c
    for y in range(int(cy - 7), int(cy + 7)):
        for x in range(int(cx - 6), int(cx + 6)):
            dx, dy = (x + 0.5 - cx) / 5.5, (y + 0.5 - cy) / 6.5
            if dx * dx + dy * dy <= 1 and 0 <= x < W and 0 <= y < H and cv[y, x] == '.':
                cv[y, x] = 'B' if (dx > 0.1 and dy < 0.2) else 'a'


def rig_frame(f):
    """f : réglages de l'image. Renvoie (crabe, effets derrière, effets devant, ctx)
    x : glissade du corps ; bx, by : décalage du corps en plus (by > 0 il se baisse) ;
    fa, fb : (x, levée) des pointes des pattes A et B (par défaut : sous le corps, au sol) ;
    cb : angle de la grosse pince (> 0 en arrière, < 0 abattue vers l'avant), cbo : (dx, dy) de la pince en plus ;
    op : doigts ouverts (> 0) ou fermés (< 0) ; cs : angle de la petite pince, pin : la petite pince pince ;
    ey : yeux (dy, > 0 rentrés), exy : décalage des yeux en x ; al : algues ; k : clignement ; flash : éclair"""
    x = f.get('x', 0)
    bx, by = x + f.get('bx', 0), f.get('by', 0)
    cv, back, front = empty(), empty(), empty()
    ctx = Ctx()
    ctx.f = f
    ctx.body = (bx, by)
    swap = BLINK if f.get('k') else None
    feet = {'A': f.get('fa', (x, 0)), 'B': f.get('fb', (x, 0))}

    # 1) les pattes (bas) : derrière tout le reste
    for i in range(6):
        fx_, lift = feet[GROUP[i]]
        part, rows = lower_leg(i, bx, by, fx_, lift)
        draw_leg(cv, part, rows)
    # 2) les yeux (derrière la carapace : ils peuvent y rentrer)
    ey = f.get('ey', 0)
    ep, edy = eyes_part(ey)
    eyx, eyy = f.get('eo', (0, 0))
    blit(cv, ep, bx + eyx, by + edy + eyy, swap)
    # 3) le corps, puis les algues
    blit(cv, P['corps'], bx, by)
    blit(cv, algae(f.get('al', 0)), bx, by)
    # 4) la petite pince (lointaine), puis la logette et la grosse pince (devant)
    cso = f.get('cso', (0, 0))
    cs = f.get('cs', 0)
    sp = small_claw(f.get('pin', 0))
    sq, pp = rotate(sp, PIV_SMALL, cs)
    blit_sq(cv, sq, pp, bx + cso[0], by + cso[1])
    cbo = f.get('cbo', (0, 0))
    cb = f.get('cb', 0)
    socket(cv, to_canvas((90.5, 82.0), bx, by))
    sq, pp = rotate(big_claw(f.get('op', 0)), PIV_CLAW, cb)
    blit_sq(cv, sq, pp, bx + cbo[0], by + cbo[1])
    ctx.tip = to_canvas(rot_point(TIP_CLAW, PIV_CLAW, cb), bx + cbo[0], by + cbo[1])
    ctx.fist = to_canvas(rot_point(FIST, PIV_CLAW, cb), bx + cbo[0], by + cbo[1])
    ctx.mouth = to_canvas(MOUTH, bx, by)
    ctx.feet = [to_canvas((sum(LEG_X[i]) / 2.0, LEG1), feet[GROUP[i]][0], -feet[GROUP[i]][1]) for i in range(6)]
    for fx in f.get('fx', []):
        fx(cv, back, front, ctx)
    return cv, back, front, ctx


# ---------------------------------------------------------------- les effets d'eau (outils de Kesha, Zaroth, Ilian)
def put(cv, x, y, ch, keep=None):
    x, y = int(math.floor(x)), int(math.floor(y))
    if 0 <= x < W and 0 <= y < H and y <= GROUND and (keep is None or cv[y, x] in keep):
        cv[y, x] = ch


def sprite(cv, rows, x, y):
    for j, r in enumerate(rows):
        for i, ch in enumerate(r):
            if ch != '.':
                put(cv, x + i, y + j, ch)


DROP_S = {1: ['Y'], 2: ['YX', 'AZ'], 3: ['.YX', 'ZYX', 'AZ.'], 4: ['.YX.', 'ZYYX', 'AZYZ', '.AZ.']}


def drop(cv, x, y, size=2, v=(0.0, 0.0)):
    """une goutte de taille 1 à 4 en (x, y) ; v = sa vitesse (la traîne part à l'opposé, 1 ou 2 pixels)"""
    rows = DROP_S[size]
    x0, y0 = int(round(x - len(rows[0]) / 2)), int(round(y - len(rows) / 2))
    sp = math.hypot(*v)
    if sp > 0.5 and size >= 2:
        ux, uy = -v[0] / sp, -v[1] / sp
        for k in range(1, 2 + (size >= 3)):
            cx, cy = x + ux * (len(rows) / 2 + k - 0.5), y + uy * (len(rows) / 2 + k - 0.5)
            put(cv, math.floor(cx), math.floor(cy), 'Z' if k == 1 else 'A')
    sprite(cv, rows, x0, y0)


# les bulles : un anneau d'eau pâle, creux, avec un reflet blanc en haut à droite
BUBBLE_S = {1: ['X'], 2: ['YX', 'ZY'], 3: ['.YW', 'Y.X', '.Z.'], 4: ['.YY.', 'Y..W', 'Z..Y', '.ZZ.'],
            5: ['.YYY.', 'Y...W', 'Z...Y', 'Z...Y', '.ZZZ.']}


def bubble(cv, x, y, size=3):
    rows = BUBBLE_S[size]
    sprite(cv, rows, int(round(x - len(rows[0]) / 2)), int(round(y - len(rows) / 2)))


def bezier(p0, p1, p2, p3, n):
    out = []
    for i in range(n + 1):
        t = i / n
        a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return out


def stroke(cv, pts, widths, tones):
    """peint un ruban le long de points, avec une épaisseur par point (coeur clair -> bord sombre)"""
    best = {}
    for (px, py), wv in zip(pts, widths):
        R = wv / 2
        if R < 0.35:
            continue
        for y in range(int(py - R - 1), int(py + R + 2)):
            for x in range(int(px - R - 1), int(px + R + 2)):
                d = math.hypot(x + 0.5 - px, y + 0.5 - py)
                if d <= R:
                    k = d / R if R >= 1.2 else 0.85
                    if k < best.get((x, y), 9):
                        best[(x, y)] = k
    m = len(tones)
    for (x, y), k in best.items():
        put(cv, x, y, tones[min(m - 1, int(k * m))])


def pop(cv, c, r, facing=0.0, tones='WXYZ'):
    """un éclat d'impact en forme de nuage (un coeur et des pétales arrondis, plus gros vers l'avant)"""
    cx, cy = c
    lobes = [(0, 0, r)]
    for da in (-70, -25, 20, 65, 150, 210):
        a = math.radians(facing + da)
        big = 0.62 if abs(da) < 80 else 0.45
        lobes.append((r * 0.95 * math.cos(a), -r * 0.95 * math.sin(a), r * big))
    m = len(tones)
    best = {}
    for (dx, dy, rr) in lobes:
        for y in range(int(cy + dy - rr - 1), int(cy + dy + rr + 2)):
            for x in range(int(cx + dx - rr - 1), int(cx + dx + rr + 2)):
                if math.hypot(x + 0.5 - cx - dx, y + 0.5 - cy - dy) <= rr:
                    D = math.hypot(x + 0.5 - cx, y + 0.5 - cy) / (r * 1.5)
                    if D < best.get((x, y), 9):
                        best[(x, y)] = D
    for (x, y), D in best.items():
        put(cv, x, y, tones[min(m - 1, int(D * m))])


def stroke_mask(pts, widths):
    """la forme d'un ruban épais (points + épaisseurs) : masque, et pour chaque pixel sa place le long du ruban (0..1)"""
    Pp = np.array(pts, float)
    Rr = np.array(widths, float) / 2
    N = len(Pp)
    A, B = Pp[:-1], Pp[1:]
    rA, rB = Rr[:-1], Rr[1:]
    sA = np.arange(N - 1) / (N - 1)
    pad = Rr.max() + 2
    x0, x1 = int(Pp[:, 0].min() - pad), int(Pp[:, 0].max() + pad)
    y0, y1 = int(Pp[:, 1].min() - pad), int(Pp[:, 1].max() + pad)
    ys, xs = np.mgrid[y0:y1 + 1, x0:x1 + 1]
    q = np.stack([xs.ravel() + 0.5, ys.ravel() + 0.5], 1)
    v = B - A
    L2 = np.maximum((v * v).sum(1), 1e-9)
    best_q = np.full(len(q), 9.0)
    best_s = np.zeros(len(q))
    for j in range(N - 1):
        t = np.clip(((q - A[j]) @ v[j]) / L2[j], 0, 1)
        c = A[j] + t[:, None] * v[j]
        w = q - c
        d = np.hypot(w[:, 0], w[:, 1])
        r = rA[j] + (rB[j] - rA[j]) * t
        ok = r >= 0.4
        qq = np.where(ok, d / np.maximum(r, 1e-6), 9.0)
        m = qq < best_q
        best_q[m] = qq[m]
        best_s[m] = (sA[j] + t / (N - 1))[m]
    inside = best_q <= 1.0
    m = np.zeros((H, W), bool)
    sm = np.zeros((H, W))
    qi = np.floor(q[inside]).astype(int)
    ok = (qi[:, 0] >= 0) & (qi[:, 0] < W) & (qi[:, 1] >= 0) & (qi[:, 1] < H)
    m[qi[ok, 1], qi[ok, 0]] = True
    sm[qi[ok, 1], qi[ok, 0]] = best_s[inside][ok]
    return m, sm


def ellipse_mask(c, rx, ry):
    yy, xx = np.mgrid[0:H, 0:W]
    return ((xx + 0.5 - c[0]) / rx) ** 2 + ((yy + 0.5 - c[1]) / ry) ** 2 <= 1.0


def shade_mask(cv, m, tones='XYZAQ', foam=None, keep=None, only=None):
    """peint une forme pleine selon la lumière : bord éclairé clair, bord dans l'ombre sombre, coeur moyen ;
    foam (masque) : là, le bord le plus éclairé devient écume blanche"""
    v = light_field(m)
    mm = m if only is None else (m & only)
    ys, xs = np.nonzero(mm)
    for y, x in zip(ys, xs):
        k = v[y, x]
        if foam is not None and foam[y, x] and k > 0.16:
            ch = 'W' if k > 0.3 else 'X'
        else:
            ch = tones[0] if k > 0.3 else tones[1] if k > 0.1 else tones[2] if k > -0.12 else \
                tones[3] if k > -0.32 else tones[4]
        put(cv, x, y, ch, keep)


def lit_stroke(cv, pts, widths, tones='XYZAQ', foam=None, keep=None):
    m, sm = stroke_mask(pts, widths)
    shade_mask(cv, m, tones, foam=None if not foam else (sm >= foam[0]) & (sm <= foam[1]), keep=keep)
    return m


def foam(cv, c, r, hollow=0.0, seed=0, tones='WWXYZ'):
    """un bouillon d'écume en chou-fleur, modelé comme un seul volume ; hollow (0..1) : il se défait"""
    rng = np.random.RandomState(seed)
    cx, cy = c
    lobes = [(0, 0, r)]
    for i in range(5):
        a = math.radians(170 - i * 40 + rng.uniform(-12, 12))
        d = r * rng.uniform(0.6, 0.85)
        lobes.append((d * math.cos(a), -d * math.sin(a) * 0.75, r * rng.uniform(0.45, 0.65)))
    if hollow:
        lobes = [(dx * (1 + hollow), dy * (1 + hollow) - hollow * r * 0.5, rr * (1 - 0.5 * hollow))
                 for (dx, dy, rr) in lobes[1:]] + [(0, -hollow * r * 0.4, r * (1 - 0.65 * hollow))]
    m = np.zeros((H, W), bool)
    for (dx, dy, rr) in lobes:
        m |= ellipse_mask((cx + dx, min(cy + dy, GROUND - rr * 0.5)), rr, rr)
    shade_mask(cv, m, tones)


def sheet(cv, P0, ang, length, bend, w, tail=0.0, blob=True, tones='XYZAQ'):
    """une nappe d'eau épaisse qui jaillit (pleine et modelée par la lumière), qui finit en grosse goutte"""
    a0, a1 = math.radians(ang), math.radians(ang + bend)
    d0 = np.array([math.cos(a0), -math.sin(a0)])
    d1 = np.array([math.cos(a1), -math.sin(a1)])
    P0 = np.array(P0, float)
    P3 = P0 + length * (0.55 * d0 + 0.45 * d1)
    pts = bezier(P0, P0 + length * 0.45 * d0, P3 - length * 0.3 * d1, P3, 40)
    widths = []
    for i in range(len(pts)):
        t = i / (len(pts) - 1)
        widths.append(0 if t < tail else w * (1.0 - 0.55 * t) + 0.8)
    lit_stroke(cv, pts, widths, tones, foam=(0.55, 1.0))
    if blob:
        e = pts[-1]
        drop(cv, e[0] + d1[0] * 3, e[1] + d1[1] * 3, 4 if w >= 5 else 3, v=tuple(d1))


def spray(cv, origin, t, seeds, g=0.9, sizes=(3, 2, 2, 1), front=None):
    """une volée de gouttes lancées d'un point, qui retombent en cloche (celles qui touchent le sol disparaissent)"""
    ox, oy = origin
    for j, (vx, vy) in enumerate(seeds):
        x = ox + vx * t
        y = oy + vy * t + 0.5 * g * t * t
        if y >= GROUND - 1:
            continue
        sz = sizes[j % len(sizes)]
        if t > 2.5 and sz > 1:
            sz -= 1
        drop(front if (front is not None and j % 3 == 0) else cv, x, y, sz, v=(vx, vy + g * t))


def hump(x, c, w, h):
    """une bosse douce (cloche) centrée en c, demi-largeur w, hauteur h"""
    d = (x - c) / w
    return h * max(0.0, 1 - d * d) ** 1.5


def water_band(cv, x0, x1, hfun, foam_rows=2, tones='XYZAQ'):
    """une masse d'eau posée sur le sol, de x0 à x1, dont le dessus suit hfun(x) : modelée par la lumière, le bord
    du haut en écume"""
    m = np.zeros((H, W), bool)
    topm = np.zeros((H, W), bool)
    for x in range(int(x0), int(x1) + 1):
        if not 0 <= x < W:
            continue
        h = hfun(x)
        if h < 0.6:
            continue
        y0 = int(round(GROUND + 1 - h))
        m[max(0, y0):GROUND + 1, x] = True
        topm[max(0, y0):max(0, y0) + foam_rows, x] = True
    shade_mask(cv, m, tones, foam=topm)
    return m


# ---- la poussière du sol (le tank fait trembler la terre) : bouffées rondes, éclairées en haut à droite
def puff(cv, c, r, tones='KPS', hollow=0.0):
    cx, cy = c
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            w = np.array([x + 0.5 - cx, y + 0.5 - cy])
            d = math.hypot(*w)
            if d <= r and d >= hollow * r:
                k = (w @ LN) / max(r, 1e-6)
                put(cv, x, y, tones[min(len(tones) - 1, int((1 - k) / 2 * len(tones)))])


def dust(cv, c, r, hollow=0.0, seed=0):
    """un petit nuage de poussière posé au sol (une bouffée et deux ou trois petites), qui se défait (hollow)"""
    rng = np.random.RandomState(seed)
    cx, cy = c
    lobes = [(0, 0, r)]
    for i in range(3):
        a = math.radians(160 - i * 60 + rng.uniform(-15, 15))
        d = r * rng.uniform(0.6, 0.85)
        lobes.append((d * math.cos(a), -d * math.sin(a) * 0.6, r * rng.uniform(0.5, 0.7)))
    for (dx, dy, rr) in lobes:
        rr2 = rr * (1 - 0.35 * hollow)
        yy = min(cy + dy - hollow * r * 0.6, GROUND - rr2 * 0.55)
        puff(cv, (cx + dx * (1 + hollow * 0.6), yy), rr2, 'KPS' if hollow < 0.5 else 'KKP', hollow=0.0)


# ---------------------------------------------------------------- 1) la pose (grosse respiration lente)
# 10 images, en boucle (1,6 s). Le corps se soulève de deux pixels sur ses pattes plantées (seul le bas des pattes
# s'allonge) puis redescend lourdement ; les pinces suivent avec une image de retard, la grosse pince s'entrouvre
# à l'inspiration et se referme ; la petite pince pince deux fois ; les yeux suivent avec du retard et regardent
# l'ennemi, un clignement ; les algues pendent et suivent ; une bulle naît à la bouche, monte et éclate.
def fx_bubbles(stage):
    """les bulles qui sortent de la bouche (petites, rondes) : stage 0 … 5"""
    def f(cv, back, front, ctx):
        mx, my = ctx.mouth
        seq = {
            0: [],
            1: [(1, 1, 2)],
            2: [(2, 0, 3)],
            3: [(4, -4, 3), (1, 2, 2)],
            4: [(6, -9, 4), (3, -2, 2)],
            5: [(8, -15, 4), (5, -7, 2)],
            6: [(10, -21, 3), (7, -12, 1)],
            7: [(9, -16, 1)],
        }[stage]
        for (dx, dy, s) in seq:
            bubble(front, mx + dx, my + dy, s)
    return f


POSE = [
    dict(by=0, ey=0, al=0, ms=170),
    dict(by=-1, cbo=(0, 1), ey=0, al=0, pin=1, fx=[fx_bubbles(1)], ms=150),
    dict(by=-1, ey=-1, al=-1, op=0.3, pin=1, fx=[fx_bubbles(2)], ms=150),
    dict(by=-2, cbo=(0, 1), ey=-1, al=-1, op=0.5, fx=[fx_bubbles(3)], ms=180),
    dict(by=-2, ey=-1, eo=(1, 0), al=-1, op=0.6, fx=[fx_bubbles(4)], ms=170),
    dict(by=-1, ey=-1, eo=(1, 0), al=0, op=0.3, pin=1, fx=[fx_bubbles(5)], ms=150),
    dict(by=-1, ey=0, eo=(1, 0), al=1, pin=1, fx=[fx_bubbles(6)], ms=140),
    dict(by=0, ey=0, al=1, k=1, fx=[fx_bubbles(7)], ms=110),
    dict(by=0, ey=0, al=1, ms=150),
    dict(by=0, ey=0, al=0, ms=160),
]


# ---------------------------------------------------------------- 2) l'attaque de base : « Pince-massue »
# Il se cabre : le corps recule et se tasse, les yeux rentrent dans leurs logettes, la grosse pince part en arrière
# grande ouverte (anticipation tenue). Il charge en deux petits pas de côté (une patte sur deux) en abattant la
# pince : elle se referme en tournant vers l'avant (une traînée d'eau suit son bout) et ÉCRASE l'ennemi à hauteur du
# ventre (arrêt sur l'image : éclat d'écume, nappes d'eau, débris d'eau ; le sol tremble : poussière sous ses
# pattes). Il reste appuyé un instant, puis relève la pince et revient à sa place à petits pas lourds.
def fx_trail(a0, a1, w=6.0):
    """la traînée d'eau derrière le bout de la pince qui s'abat : un ruban courbe le long de l'arc parcouru (du
    pivot), épais contre la pince, effilé derrière"""
    def f(cv, back, front, ctx):
        bx, by = ctx.body
        piv = to_canvas(PIV_CLAW, bx, by)
        r = math.hypot(TIP_CLAW[0] - PIV_CLAW[0], TIP_CLAW[1] - PIV_CLAW[1]) - 4
        base = math.degrees(math.atan2(-(TIP_CLAW[1] - PIV_CLAW[1]), TIP_CLAW[0] - PIV_CLAW[0]))
        pts, ws = [], []
        n = 40
        for i in range(n + 1):
            t = i / n
            a = math.radians(base + a0 + (a1 - a0) * t)
            rr = r - 5 - 3 * math.sin(math.pi * t)
            pts.append((piv[0] + rr * math.cos(a), piv[1] - rr * math.sin(a)))
            ws.append(0.8 + w * t ** 1.1)
        lit_stroke(back, pts, ws, 'XYZAQ', foam=(0.6, 1.0))
    return f


HIT = [None]


def fx_smash(k):
    """l'écrasement sur l'ennemi : k = 0 l'impact (éclat d'écume, nappes qui s'ouvrent vers l'avant), 1 elles
    s'ouvrent et retombent, 2 il ne reste que de l'écume qui se défait et des gouttes"""
    def f(cv, back, front, ctx):
        if k == 0:
            HIT[0] = ctx.tip.copy() + np.array([3.0, 0.0])
        X, Y = HIT[0]
        seeds = [(3.0, -4.0), (4.5, -1.5), (2.0, -5.5), (5.0, 0.5), (0.5, -5.0), (3.5, 1.5), (-1.0, -6.0),
                 (6.0, -2.5)]
        if k == 0:
            sheet(back, (X - 2, Y - 3), 76, 24, -60, 5.8, blob=True)
            sheet(back, (X + 1, Y + 3), -18, 20, -46, 5.0, blob=True)
            sheet(back, (X - 4, Y - 4), 120, 14, 44, 3.6, blob=True)
            spray(back, (X + 2, Y), 1.0, seeds)
            pop(front, (X + 3, Y), 7.0, facing=10, tones='WWXY')
        elif k == 1:
            sheet(back, (X - 2, Y - 3), 76, 28, -88, 6.0, tail=0.3, blob=True)
            sheet(back, (X + 1, Y + 3), -18, 22, -64, 5.2, tail=0.25, blob=True)
            foam(front, (X + 5, Y - 1), 6.0, hollow=0.25, seed=3)
            spray(back, (X + 2, Y), 2.2, seeds)
        else:
            foam(back, (X + 5, Y - 2), 4.0, hollow=0.7, seed=4)
            spray(front, (X + 2, Y), 3.4, seeds)
    return f


def fx_quake(k, xs=None, r=4.0):
    """le sol tremble : de petites bouffées de poussière sous les pattes (k = 0 elles naissent, 1 elles s'ouvrent,
    2 elles se défont) ; xs : où (toile), sinon sous chaque patte"""
    def f(cv, back, front, ctx):
        pts = xs if xs is not None else [p[0] for p in ctx.feet]
        for j, X in enumerate(pts):
            rr = r * (0.8 + 0.25 * (j % 2))
            dust(back if j % 2 else front, (X + (j % 2) - 2 + k * 1.5 * (1 if j % 2 else -1), GROUND - 1),
                 rr * (1 + 0.25 * k), hollow=[0.0, 0.35, 0.75][k], seed=j + 5 * k)
    return f


ATTAQUE = [
    # 0 : en garde
    dict(ms=100),
    # 1 : il se cabre : le corps recule et se tasse, la pince part en arrière et s'ouvre, les yeux rentrent
    dict(bx=-2, by=1, cb=8, op=0.6, cs=4, ey=2, al=1, ms=120),
    # 2 : anticipation tenue : pince tout en arrière, grande ouverte, corps tassé, pinces armées
    dict(bx=-4, by=2, cb=16, op=1.0, cs=8, ey=3, al=2, pin=1, ms=300),
    # 3 : premier pas de côté (pattes A en l'air), la pince commence à s'abattre
    dict(x=12, bx=0, by=0, fa=(14, 3), fb=(2, 0), cb=-20, op=0.2, cs=0, ey=2, al=1,
         fx=[fx_trail(16, -16, 11.0)], ms=60),
    # 4 : IMPACT (arrêt sur l'image) : la pince fermée écrase l'ennemi ; le sol tremble
    dict(x=26, by=2, fa=(26, 0), fb=(26, 0), cb=-68, cbo=(1, 1), op=-1, cs=-6, pin=-1, ey=1, al=-1,
         fx=[fx_trail(-30, -64, 12.0), fx_smash(0), fx_quake(0)], ms=200),
    # 5 : il reste appuyé, les nappes retombent
    dict(x=26, by=2, cb=-66, op=-1, cs=-4, pin=-1, ey=0, al=-2, fx=[fx_smash(1), fx_quake(1)], ms=110),
    # 6 : il relève la pince et recule d'un pas (pattes B en l'air)
    dict(x=16, by=1, fa=(26, 0), fb=(15, 3), cb=-30, op=-0.4, cs=0, al=1, fx=[fx_smash(2), fx_quake(2)], ms=100),
    # 7 : second pas en arrière (pattes A en l'air)
    dict(x=5, by=1, fa=(4, 3), fb=(15, 0), cb=-6, op=0, al=1, ms=100),
    # 8 : il se pose lourdement
    dict(by=2, cb=2, al=0, ey=0, ms=120),
    # 9 : en garde
    dict(by=0, cb=0, ms=150),
]


# ---------------------------------------------------------------- 3) l'attaque spéciale : « Lame de fond »
# Il se dresse sur la pointe des pattes, les deux pinces levées (la menace d'un vrai crabe), il bave des bulles ;
# l'eau monte du sol et s'enroule autour de la grosse pince (tenu : le danger monte). Il l'abat de tout son poids
# dans le sol devant lui (arrêt sur l'image, éclair, le sol tremble) : une VAGUE jaillit du sol au point d'impact,
# grossit en roulant vers la droite, sa crête d'écume s'enroule, et elle DÉFERLE sur toute la première ligne
# ennemie (arrêt sur l'image) ; puis elle retombe en écume et en flaques. Il relève la pince et revient en garde.
def fx_coil(k):
    """l'eau monte du sol et s'enroule autour de la grosse pince levée : k = 0 le sol bouillonne devant lui (une
    flaque, des bulles, des gouttes qui montent), 1 une trombe s'élève en tournant jusqu'à la pince, 2 elle l'entoure
    (une volute derrière, une devant), des gouttes en suspens"""
    def f(cv, back, front, ctx):
        F = ctx.fist
        T = ctx.tip
        G = GROUND
        X = F[0] + 12
        water_band(front, X - 16, X + 16, lambda x: hump(x, X, 15, [4, 6, 5][k]) + 0.6, foam_rows=1)
        if k == 0:
            for j, (dx, dy, s_) in enumerate(((-6, -10, 2), (4, -16, 3), (10, -8, 2), (-2, -24, 2), (7, -30, 1))):
                if j % 2:
                    bubble(front, X + dx, G + dy, s_)
                else:
                    drop(front, X + dx, G + dy, s_, v=(0, -2))
            return
        if k == 1:
            pts = bezier((X - 4, G - 4), (X + 14, G - 24), (X - 6, F[1] + 30), (F[0] + 16, F[1] + 4), 40)
            lit_stroke(front, pts, [9.5 - 4.5 * (i / 40) for i in range(41)], foam=(0.55, 1.0))
            pts = bezier((X + 6, G - 4), (X - 10, G - 20), (X + 12, F[1] + 36), (F[0] + 6, F[1] + 18), 40)
            lit_stroke(back, pts, [5.0 - 2.6 * (i / 40) for i in range(41)])
            for j, (dx, dy) in enumerate(((22, -4), (-6, -24), (24, -30), (10, 16))):
                drop(front, F[0] + dx, F[1] + dy, 2, v=(0, -1.5))
            return
        # k = 2 : la trombe monte et fait le tour de la pince (derrière à gauche, devant à droite)
        pts = bezier((X - 2, G - 4), (X + 16, G - 26), (X + 2, F[1] + 26), (F[0] + 12, F[1] + 8), 40)
        lit_stroke(front, pts, [10.0 - 3.5 * (i / 40) for i in range(41)], foam=(0.6, 1.0))
        pts = bezier((F[0] + 12, F[1] + 8), (F[0] + 26, F[1] - 10), (F[0] + 12, T[1] - 14), (F[0] - 4, T[1] - 10), 40)
        lit_stroke(front, pts, [6.5 + 2.0 * math.sin(math.pi * i / 40) for i in range(41)], foam=(0.0, 0.6))
        pts = bezier((F[0] - 4, T[1] - 10), (F[0] - 22, T[1] - 4), (F[0] - 26, F[1] + 6), (F[0] - 12, F[1] + 18), 40)
        lit_stroke(back, pts, [7.0 - 4.0 * (i / 40) for i in range(41)], foam=(0.0, 0.3))
        for j, (dx, dy) in enumerate(((-28, -8), (30, -14), (-10, -30), (28, 10), (34, -2))):
            drop(back if j % 2 else front, F[0] + dx, F[1] + dy, 2 if j % 3 else 3, v=(0.5, -1.5))
    return f


IMPACT_X = [None]


def fx_slam(k):
    """la pince frappe le sol : k = 0 éclair d'écume au point d'impact, nappes qui jaillissent du sol ; 1 elles
    retombent"""
    def f(cv, back, front, ctx):
        if k == 0:
            IMPACT_X[0] = float(ctx.tip[0])
        X = IMPACT_X[0]
        G = GROUND
        seeds = [(-2.5, -6.0), (2.5, -7.0), (-4.0, -3.5), (4.5, -4.5), (0.5, -8.0), (6.0, -2.0)]
        if k == 0:
            sheet(back, (X - 6, G - 3), 112, 26, 38, 6.0, blob=True)
            sheet(back, (X + 6, G - 3), 66, 30, -40, 6.5, blob=True)
            water_band(front, X - 22, X + 24, lambda x: hump(x, X, 18, 7) + 1.0)
            pop(front, (X + 1, G - 6), 7.5, facing=60, tones='WWXY')
            spray(back, (X, G - 8), 1.0, seeds)
        else:
            sheet(back, (X - 8, G - 2), 116, 30, 70, 5.0, tail=0.3, blob=True)
            sheet(back, (X + 8, G - 2), 62, 32, -72, 5.4, tail=0.3, blob=True)
            water_band(front, X - 22, X + 22, lambda x: hump(x, X, 18, 4) + 0.8)
            foam(front, (X + 2, G - 4), 4.5, hollow=0.3, seed=9)
            spray(back, (X, G - 8), 2.2, seeds)
    return f


def wave(back, front, xf, h, curl_k, X0, seed=0, crash=0.0):
    """la vague qui roule sur le sol vers la droite : son front en xf, sa hauteur h (au-dessus du sol), sa crête qui
    s'enroule vers l'avant (curl_k 0..1) ; derrière elle l'eau s'abaisse jusqu'au point d'impact X0"""
    G = GROUND
    top_x = xf - 0.42 * h                                # le sommet du rouleau
    back_len = 1.2 * h + 10

    def hf(x):
        d = top_x - x                                    # > 0 derrière le sommet
        if x < X0 - 6 or x > xf:
            return 0.0
        if d < 0:                                        # la face avant, sous la lèvre : raide et creuse
            u = -d / (xf - top_x)
            return h * 0.8 * max(0.0, 1 - u * u) ** 0.8
        e = d / back_len
        return max(h * 0.86 * math.exp(-e * e * 1.4), 2.2 * max(0.0, 1 - d / (top_x - X0 + 1)) + 0.8)
    water_band(back, X0 - 6, xf + 2, hf, foam_rows=1)
    # la lèvre : un boudin d'eau épais qui monte du dos, passe le sommet et s'enroule vers l'avant et vers le sol
    if h > 8:
        c = curl_k
        pts = bezier((top_x - 0.55 * h, G - 0.62 * h), (top_x - 0.1 * h, G - 1.08 * h),
                     (top_x + 0.5 * h, G - 1.02 * h), (top_x + 0.48 * h, G - (0.78 - 0.34 * c) * h), 40)
        if c > 0.2:                                      # le bout se recourbe vers l'arrière (le tube)
            pts += bezier(pts[-1], (top_x + 0.46 * h, G - (0.3 - 0.1 * c) * h), (top_x + 0.3 * h, G - 0.3 * h),
                          (top_x + (0.36 - 0.1 * c) * h, G - (0.42 - 0.04 * c) * h), 16)[1:int(4 + 12 * c)]
        n = len(pts)
        ws = [(0.15 + 0.85 * math.sin(math.pi * min(1.0, (i / (n - 1)) * 1.6) / 2 + 0.0)) * (0.3 * h + 2) *
              (1 - 0.6 * max(0.0, i / (n - 1) - 0.5)) for i in range(n)]
        lit_stroke(front, pts, ws, 'XYZAQ', foam=(0.15, 0.6))
        foam(front, (top_x + 0.05 * h, G - 1.06 * h), 1.8 + h * 0.07, seed=seed)
        if c > 0.2:
            foam(front, (top_x + 0.5 * h, G - 3), 2.0 + h * 0.08, seed=seed + 2)   # là où la lèvre retombe
    # les gouttes arrachées à la crête, qui partent devant
    for j, (dx, dy, s_) in enumerate(((0.6, -1.18, 2), (0.75, -0.8, 1), (0.2, -1.3, 2), (0.85, -0.5, 1),
                                      (-0.3, -1.15, 1))):
        if h > 8:
            drop(front if j % 2 else back, top_x + dx * h + seed % 3, G + dy * h, s_, v=(2.5, -1.0))


def fx_wave(dxf, h, curl_k, seed=0):
    """la vague, son front à dxf pixels du point d'impact"""
    def f(cv, back, front, ctx):
        X0 = IMPACT_X[0]
        wave(back, front, X0 + dxf, h, curl_k, X0, seed=seed)
    return f


def fx_crash(k):
    """la vague déferle sur la ligne ennemie : k = 0 le grand fracas (gerbe haute, éclat d'écume, nappes), 1 la
    gerbe retombe en pluie, 2 l'écume et les flaques, 3 les dernières gouttes"""
    def f(cv, back, front, ctx):
        X, G = ENEMY_X - 6, GROUND
        X0 = IMPACT_X[0]
        seeds = [(-3.0, -7.0), (3.0, -8.0), (-5.5, -4.5), (5.5, -5.0), (-1.0, -9.5), (1.5, -9.0), (7.5, -3.0),
                 (-7.5, -2.5), (4.0, -10.0), (9.0, -6.0)]
        if k == 0:
            water_band(back, X0 - 4, X + 50, lambda x: hump(x, X, 40, 34) + hump(x, X + 40, 24, 14) +
                       2.0 * (x < X), foam_rows=2)
            sheet(back, (X - 20, G - 30), 124, 48, 50, 9.0, blob=True)
            sheet(back, (X + 16, G - 32), 70, 54, -62, 9.5, blob=True)
            sheet(back, (X + 40, G - 10), 40, 30, -70, 6.0, blob=True)
            sheet(back, (X - 2, G - 40), 94, 30, -20, 7.0, blob=True)
            foam(front, (X + 2, G - 30), 8.0, seed=20)
            foam(front, (X + 12, G - 22), 6.0, seed=28)
            foam(front, (X - 20, G - 12), 6.0, seed=21)
            foam(front, (X + 28, G - 9), 6.5, seed=22)
            spray(back, (X, G - 40), 1.0, seeds)
        elif k == 1:
            water_band(back, X0 - 2, X + 56, lambda x: hump(x, X + 4, 44, 18) + hump(x, X + 42, 24, 9) +
                       1.2 * (x < X), foam_rows=2)
            sheet(back, (X - 22, G - 14), 128, 46, 92, 6.4, tail=0.35, blob=True)
            sheet(back, (X + 18, G - 16), 62, 50, -96, 6.8, tail=0.35, blob=True)
            sheet(back, (X + 44, G - 6), 36, 30, -90, 4.6, tail=0.4, blob=True)
            foam(front, (X - 10, G - 9), 6.0, hollow=0.2, seed=23)
            foam(front, (X + 22, G - 8), 6.0, hollow=0.2, seed=24)
            spray(back, (X, G - 40), 2.4, seeds)
        elif k == 2:
            water_band(back, X - 50, X + 60, lambda x: hump(x, X - 20, 30, 4) + hump(x, X + 20, 34, 5), foam_rows=1)
            foam(front, (X - 16, G - 4), 4.5, hollow=0.5, seed=25)
            foam(front, (X + 18, G - 4), 5.0, hollow=0.5, seed=26)
            spray(back, (X, G - 40), 3.6, seeds)
        else:
            water_band(back, X - 40, X + 50, lambda x: hump(x, X - 14, 26, 2.2) + hump(x, X + 22, 26, 2.4),
                       foam_rows=1)
            foam(front, (X + 8, G - 2), 3.2, hollow=0.75, seed=27)
            spray(front, (X, G - 40), 4.6, seeds[::2])
    return f


def fx_mouth_foam(n):
    """il bave des bulles (la colère du crabe) : n bulles en grappe à la bouche"""
    def f(cv, back, front, ctx):
        mx, my = ctx.mouth
        pos = [(1, 1, 3), (3, -3, 2), (0, 4, 2), (4, 2, 3), (2, -7, 2), (5, -2, 1)]
        for (dx, dy, s) in pos[:n]:
            bubble(front, mx + dx, my + dy, s)
    return f


SPECIALE = [
    # 0 : en garde
    dict(ms=100),
    # 1 : il se dresse : le corps monte sur la pointe des pattes, les deux pinces se lèvent
    dict(bx=-1, by=-3, cb=8, op=0.5, cs=22, cso=(0, -1), ey=-1, al=1, fx=[fx_mouth_foam(2)], ms=120),
    # 2 : la menace : tout en haut, les deux pinces levées et ouvertes, l'eau monte du sol
    dict(bx=-2, by=-6, cb=16, op=1.0, cs=40, cso=(0, -2), ey=-1, al=2, pin=1, fx=[fx_mouth_foam(4), fx_coil(0)],
         ms=150),
    # 3 : tenu : l'eau s'enroule autour de la grosse pince, il bave
    dict(bx=-2, by=-6, cb=18, op=1.0, cs=42, cso=(0, -2), ey=-1, eo=(1, 0), al=1, pin=1,
         fx=[fx_mouth_foam(6), fx_coil(1)], ms=150),
    dict(bx=-3, by=-7, cb=20, op=1.0, cs=44, cso=(0, -2), ey=-1, eo=(1, 0), al=0, pin=-1,
         fx=[fx_mouth_foam(5), fx_coil(2)], ms=240),
    # 5 : il abat la pince de tout son poids
    dict(x=4, by=-1, cb=-40, op=-0.5, cs=10, ey=2, al=-1, fx=[fx_trail(22, -36, 13.0)], ms=50),
    # 6 : IMPACT dans le sol (arrêt sur l'image, éclair) : la vague naît
    dict(x=8, by=4, cb=-96, cbo=(2, 2), op=-1, cs=-14, pin=-1, ey=3, al=-2,
         fx=[fx_slam(0), fx_quake(0, r=5.0)], ms=200),
    # 7 à 10 : la vague grossit et roule vers la droite, sa crête s'enroule ; il reste appuyé
    dict(x=8, by=4, cb=-94, cbo=(2, 2), op=-1, cs=-12, ey=3, al=-1,
         fx=[fx_slam(1), fx_quake(1, r=5.0), fx_wave(34, 16, 0.0, 0)], ms=70),
    dict(x=8, by=3, cb=-94, cbo=(2, 2), op=-1, cs=-12, ey=2, al=0, fx=[fx_quake(2, r=5.0), fx_wave(70, 28, 0.3, 1)],
         ms=70),
    dict(x=8, by=3, cb=-94, cbo=(2, 2), op=-1, cs=-10, ey=2, al=1, fx=[fx_wave(106, 40, 0.6, 2)], ms=70),
    dict(x=8, by=3, cb=-92, cbo=(2, 2), op=-1, cs=-10, ey=1, al=1, fx=[fx_wave(136, 48, 0.9, 3)], ms=70),
    # 11 : la vague DÉFERLE sur la première ligne ennemie (arrêt sur l'image)
    dict(x=8, by=3, cb=-92, cbo=(2, 2), op=-1, cs=-10, ey=1, al=0, fx=[fx_crash(0)], ms=200),
    # 12, 13 : la gerbe retombe ; il relève la pince
    dict(x=8, by=2, cb=-70, cbo=(1, 1), op=-0.6, cs=-6, ey=0, al=-1, fx=[fx_crash(1)], ms=100),
    dict(x=5, by=1, fa=(4, 3), cb=-36, op=-0.2, cs=-2, ey=0, al=-1, fx=[fx_crash(2)], ms=100),
    # 14 : il recule d'un pas lourd ; l'écume se défait
    dict(x=1, by=2, fa=(0, 0), fb=(1, 2), cb=-8, op=0, cs=0, al=1, fx=[fx_crash(3)], ms=120),
    # 15, 16 : en garde
    dict(by=1, cb=2, al=1, ms=120),
    dict(ms=150),
]

# ---------------------------------------------------------------- retouches pixel par pixel (après le montage)
# RETOUCHES[nom][numéro d'image] = [(x, y, 'TEXTE')] en coordonnées de la GRILLE du dessin, décalées avec le corps
# de l'image ; '.' efface, ' ' laisse le pixel tel quel.
RETOUCHES = {'pose': {}, 'attaque': {}, 'speciale': {}}


def retouch(cv, fixes, off=(0, 0)):
    for (x, y, text) in fixes:
        for i, ch in enumerate(text):
            if ch != ' ':
                X, Y = x + i + OX + off[0], y + OY + off[1]
                if 0 <= X < W and 0 <= Y < H:
                    cv[Y, X] = ch


# ---------------------------------------------------------------- toutes les images, et les fichiers
def build_all():
    anims = {}
    for name, specs in (('pose', POSE), ('attaque', ATTAQUE), ('speciale', SPECIALE)):
        fr = []
        for i, spec in enumerate(specs):
            cv, back, front, ctx = rig_frame(dict(spec))
            retouch(cv, RETOUCHES[name].get(i, []), ctx.body)
            fr.append((compose(cv, back, front, flash=spec.get('flash')), spec['ms']))
        anims[name] = fr
    return anims


def on_bg(img, bg=BG):
    im = Image.new('RGBA', (img.shape[1], img.shape[0]), bg + (255,))
    im.alpha_composite(Image.fromarray(img, 'RGBA'))
    return im


def bbox(frames, margin=4):
    a = np.zeros((H, W), bool)
    for img, _ in frames:
        a |= img[:, :, 3] > 0
    ys, xs = np.nonzero(a)
    return (max(0, xs.min() - margin), max(0, ys.min() - margin), min(W, xs.max() + 1 + margin),
            min(H, ys.max() + 1 + margin))


GAME_BOX = (OX, OY, OX + hd.FRAME_W, OY + hd.FRAME_H)       # la case du jeu : 128 × 120, sol en (64, 116)


def save_gif(path, images, durations):
    """GIF en boucle, une palette commune, pas de tramage (les pixels restent nets)"""
    rgb = [im.convert('RGB') for im in images]
    W0, H0 = rgb[0].size
    sheet_ = Image.new('RGB', (W0, H0 * len(rgb)))
    for i, im in enumerate(rgb):
        sheet_.paste(im, (0, i * H0))
    ncol = len(sheet_.getcolors(maxcolors=1 << 20) or [])
    if ncol <= 256:
        pal = sheet_.quantize(colors=min(256, ncol), method=Image.Quantize.MAXCOVERAGE, dither=Image.Dither.NONE)
    else:
        pal = sheet_.quantize(colors=255, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    ps = [im.quantize(palette=pal, dither=Image.Dither.NONE) for im in rgb]
    ps[0].save(path, save_all=True, append_images=ps[1:], duration=durations, loop=0, disposal=1, optimize=False)


def attack_box(anims):
    """une seule case pour les deux attaques (même sol, même place) : on voit la portée des effets"""
    bb = bbox(anims['attaque'] + anims['speciale'] + anims['pose'], 6)
    return (bb[0], bb[1], max(bb[2], ENEMY_X + 40), min(H, GROUND + 6))


def planche(anims, path, box, k=3, per=None):
    per = per or {'pose': 10, 'attaque': 4, 'speciale': 4}
    blocks = []
    for name in ('pose', 'attaque', 'speciale'):
        bx = GAME_BOX if name == 'pose' else box
        cells = [on_bg(img).crop(bx) for img, _ in anims[name]]
        blocks.append((name, per[name], cells, [ms for _, ms in anims[name]]))
    Wt = max(min(p, len(cells)) * (cells[0].width * k + 6) for _, p, cells, _ in blocks) + 6
    Ht = 6 + sum(26 + ((len(cells) + p - 1) // p) * (cells[0].height * k + 22) for _, p, cells, _ in blocks)
    sh = Image.new('RGB', (Wt, Ht), (250, 250, 252))
    d = ImageDraw.Draw(sh)
    y = 6
    titles = {'pose': 'POSE (respiration, en boucle)', 'attaque': 'ATTAQUE DE BASE (pince-massue)',
              'speciale': 'ATTAQUE SPECIALE (lame de fond)'}
    for name, p, cells, mss in blocks:
        cw, ch = cells[0].width * k, cells[0].height * k
        d.text((8, y + 8), f"{titles[name]} : {len(cells)} images, {sum(mss)} ms", fill=(30, 20, 36))
        y += 26
        for i, c in enumerate(cells):
            if i and i % p == 0:
                y += ch + 22
            X = 6 + (i % p) * (cw + 6)
            sh.paste(c.resize((cw, ch), Image.NEAREST), (X, y + 16))
            d.text((X + 2, y + 2), f'{i}   ({mss[i]} ms)', fill=(30, 20, 36))
        y += ch + 22
    sh.save(path)


def write_outputs(anims):
    os.makedirs(OUT, exist_ok=True)
    bb = attack_box(anims)
    boxes = {'pose': GAME_BOX, 'attaque': bb, 'speciale': bb}
    for name in ('pose', 'attaque', 'speciale'):
        box = boxes[name]
        ims = [on_bg(img).crop(box) for img, _ in anims[name]]
        ims = [im.resize((im.width * 4, im.height * 4), Image.NEAREST) for im in ims]
        save_gif(os.path.join(OUT, f'anim-{NAME}-{name}.gif'), ims, [ms for _, ms in anims[name]])
    planche(anims, os.path.join(OUT, f'anim-{NAME}-planche.png'), bb)
    # le rythme en jeu : pose ×2, attaque, pose, spéciale, pose — sur le fond de combat (prairie), ×2
    seq = anims['pose'] * 2 + anims['attaque'] + anims['pose'] + anims['speciale'] + anims['pose']
    box = bb
    bw, bh = box[2] - box[0], box[3] - box[1]
    try:
        fond = Image.open(os.path.join(HD, '..', '..', '..', 'public', 'art', 'px', 'fond-prairie.webp')).convert('RGBA')
        fond = fond.resize((fond.width // 3, fond.height // 3), Image.NEAREST)
        fy = 374 - (GROUND - box[1])                    # les pattes sur le chemin de terre
        strip = fond.crop((0, fy, fond.width, fy + bh))
        base = Image.new('RGBA', (bw, bh))
        x, flip = 0, False
        while x < bw:                                   # la prairie est plus étroite que la scène : prolongée en miroir
            base.paste(strip.transpose(Image.FLIP_LEFT_RIGHT) if flip else strip, (x, 0))
            x += strip.width
            flip = not flip
    except Exception:
        base = Image.new('RGBA', (bw, bh), (120, 170, 110, 255))
    ims = []
    for img, _ in seq:
        im = base.copy()
        im.alpha_composite(Image.fromarray(img, 'RGBA').crop(box))
        ims.append(im.resize((im.width * 2, im.height * 2), Image.NEAREST))
    save_gif(os.path.join(OUT, f'anim-{NAME}-jeu.gif'), ims, [ms for _, ms in seq])
    return boxes


def essai(folder):
    """images de contrôle (dans un dossier de brouillon) : planche ×2 et chaque image seule"""
    os.makedirs(folder, exist_ok=True)
    anims = build_all()
    bb = attack_box(anims)
    planche(anims, os.path.join(folder, 'planche.png'), bb, k=2, per={'pose': 10, 'attaque': 5, 'speciale': 4})
    for name in ('pose', 'attaque', 'speciale'):
        box = GAME_BOX if name == 'pose' else bb
        for i, (img, ms) in enumerate(anims[name]):
            on_bg(img).crop(box).save(os.path.join(folder, f'{name}-{i:02d}.png'))
    return anims


# ---------------------------------------------------------------- export vers le jeu (../jeu_export.py, consigne export-jeu.md)
# Attaque : la pince s'abat au contact (corps à corps, les deux pas sont cuits dans les images ; `avance` reste au
# maximum pendant l'écrasement). Spéciale : la vague qui roule à travers la première ligne ennemie est posée sur
# chaque cible (à partir de la colonne 201, juste devant la pince) ; l'éclat du coup dans le sol reste avec lui.
JEU = {
    'attaque': dict(calques=True, genre='melee', coup=4, cible=(228, 150), coupe=[None] * 4 + [205, 205, 200] + [None] * 3,
                    avance=[0, 0, 0, 12, 26, 26, 16, 5, 0, 0]),
    # la vague court au ras du sol de la pince à la cible (projectile), puis jaillit sur elle
    'speciale': dict(genre='tir', tir=(7, 11), depuis=200, rase=True, coup=11, cible=(ENEMY_X, GROUND - 40),
                     coupe=[None] * 11 + [160] * 4 + [None] * 2, charge=(2, 4), calques=True),   # vague entière
}


if __name__ == '__main__':
    if len(sys.argv) > 2 and sys.argv[1] == 'essai':
        essai(sys.argv[2])
        sys.exit()
    anims = build_all()
    boxes = write_outputs(anims)
    for n in ('pose', 'attaque', 'speciale'):
        print(f"{n} : {len(anims[n])} images, {sum(ms for _, ms in anims[n])} ms")
    print('cadre des attaques :', boxes['attaque'])
    print('écrit dans', OUT)
