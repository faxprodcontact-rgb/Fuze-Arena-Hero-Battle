# La boîte de pièces communes des héros « gros pixels encrés » (lire GUIDE.md). Chaque pièce respecte le guide :
# un membre de peau = une seule forme (pas de trait aux articulations), un trait noir autour de chaque pièce
# d'équipement, bottes à peine plus larges que le mollet, épaulière posée sur le haut du bras, poing par-dessus le manche.
# Repère : sol y = 71, milieu x = 40, tourné vers la droite (bras droit du personnage = à gauche de l'image, devant).
# b = la respiration (le haut du corps monte de b pixels) : les pièces du haut du corps reçoivent b.
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from pix import Ramp, BREATH, BLINK, S, Canvas

ORIGIN = (24, 45)
SWAY = [0, 1, 1, 0, 0, -1, -1, 0]
INK = '#1e1424'

GOLD = Ramp('#7a4a0c', '#c0841e', '#eab036', '#ffd870', '#fff4c0')
STEEL = Ramp('#2c3040', '#4a5068', '#727a98', '#a4acc8', '#e0e6f4')
WOOD = Ramp('#2e1a0c', '#4e2e16', '#74462a', '#96603c', '#b47c52')
LEATHER = Ramp('#2a160c', '#442818', '#62402a', '#80583a', '#9a704c')
FIRE = Ramp('#7a1404', '#cc360a', '#f47216', '#ffb83a', '#fff0a0')
CORE = Ramp('#ff9a2a', '#ffc040', '#ffe27a', '#fff6c8', '#ffffff')
BLUEFIRE = Ramp('#0a2a6a', '#1a58c0', '#3a9cf0', '#8ad8ff', '#e8fbff')

# ---------- les poses : des squelettes (les points du guide, § 3) ----------
LEGS = {
    'large': ((34, 56), (27, 62), (25, 68), (47, 56), (53, 62), (55, 68)),    # garde large (le gabarit)
    'droit': ((35, 56), (33, 63), (32, 68), (46, 56), (48, 63), (49, 68)),    # debout, pieds plus proches
    'fente': ((34, 56), (24, 63), (15, 68), (46, 56), (57, 60), (60, 67)),    # élan : jambe droite loin derrière
    'moyen': ((35, 56), (30, 62), (29, 68), (46, 56), (51, 62), (52, 68)),    # garde moyenne (le cas le plus courant)
}
# Les jambes très écartées ('large') ou l'élan ('fente') : seulement pour quelques-uns (demande du propriétaire).


def up(p, b):
    return (p[0], p[1] - b)


def hand_legend(skin):
    return {'K': INK, 'a': skin.shade, 'b': skin.base, 'c': skin.light, 'd': skin.hi}


FIST = [".KKKKKK.", "KbcccddK", "KbcccdcK", "KKKKKKcK", "KbcccdcK", "KabbbbbK", ".KKKKKK."]
PUNCH = [".KKKKK.", "KbccddK", "KbccdcK", "KKKKKcK", "KbcccdK", "KabbbcK", ".KKKKK."]
PALM = ["..KKK..", ".KcddK.", "KbccdcK", "KbcccdK", "KbcccdK", ".KbbcK.", "..KKK.."]


def fist(c, p, skin, b=0):
    """Un poing qui serre un manche (centré sur p) : à poser APRÈS l'arme."""
    c.sprite(p[0] - 4, p[1] - 3 - b, FIST, hand_legend(skin))


def punch(c, p, skin, b=0):
    c.sprite(p[0] - 1, p[1] - 3 - b, PUNCH, hand_legend(skin))


def palm(c, p, skin, b=0):
    """Une main ouverte, paume levée (pour tenir une flamme, une boule)."""
    c.sprite(p[0] - 3, p[1] - 3 - b, PALM, hand_legend(skin))


# ---------- le corps ----------
def arm(c, b, shoulder, elbow, wrist, ramp, r=(5.6, 5.0, 4.6)):
    """Un bras : UNE seule forme de l'épaule au poignet (manche ou peau)."""
    c.part(c.limb([(*up(shoulder, b), r[0]), (*up(elbow, b), r[1]), (*up(wrist, b), r[2])]), ramp, 'ink')


def arm_front(c, b, shoulder, elbow, wrist, ramp, r=(5.6, 5.0, 4.6), root=None):
    """Le bras de devant, À APPELER APRÈS LE TORSE (le même bras a déjà été posé AVANT le torse avec arm()) : on repose
    par-dessus le torse tout le bras SAUF sa racine autour de l'épaule, qui reste sous le vêtement (le haut du bras ne
    passe jamais devant le tee-shirt). Les traits noirs restent ceux du bras entier : pas de coupure visible."""
    in_front(c, lambda tc: arm(tc, b, shoulder, elbow, wrist, ramp, r), up(shoulder, b), root or r[0] + 2.6)


def in_front(c, draw_fn, root, rr):
    """Repose par-dessus ce qui est déjà dessiné une pièce dessinée par draw_fn (sur une toile à part), SAUF dans le
    cercle (root, rr) : là, ce qui est dessus (le vêtement, le torse) reste devant."""
    tmp = Canvas(c.w, c.h, c.ox, c.oy)
    draw_fn(tmp)
    keep = (tmp.col[:, :, 3] > 0) & ~c.ellipse(root[0], root[1], rr, rr)
    c.n += 1
    c.col[keep] = tmp.col[keep]
    c.pid[keep] = c.n


def bracer(c, b, elbow, wrist, ramp=GOLD, u=0.5, half=5.2):
    p0, p1 = up(elbow, b), up(wrist, b)
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    n = math.hypot(dx, dy) or 1
    dx, dy = dx / n, dy / n
    nx, ny = -dy, dx
    cx, cy = p0[0] + (p1[0] - p0[0]) * u, p0[1] + (p1[1] - p0[1]) * u
    c.part(c.poly([(cx - dx * 2.6 - nx * half, cy - dy * 2.6 - ny * half), (cx + dx * 2.6 - nx * half, cy + dy * 2.6 - ny * half),
                   (cx + dx * 2.6 + nx * half, cy + dy * 2.6 + ny * half), (cx - dx * 2.6 + nx * half, cy - dy * 2.6 + ny * half)]), ramp, 'ink', band=1)


def legs(c, pose, ramp, r=(6.0, 5.2, 4.6)):
    """Les deux jambes (chacune d'une seule forme) : à dessiner AVANT la jupe et la ceinture."""
    hd, gd, kd, hg, gg, kg = LEGS[pose] if isinstance(pose, str) else pose
    for (h, g, k) in ((hd, gd, kd), (hg, gg, kg)):
        c.part(c.limb([(*h, r[0]), (*g, r[1]), (*k, r[2])]), ramp, 'ink')


def feet(c, pose, ramp, kind='boot'):
    """Bottes (à peine plus larges que le mollet), sandales ou pieds nus, posées sur le sol (y = 71)."""
    hd, gd, kd, hg, gg, kg = LEGS[pose] if isinstance(pose, str) else pose
    for k in (kd, kg):
        x = k[0]
        if kind == 'boot':
            c.part(c.poly([(x - 5, 65), (x + 5, 65), (x + 7, 69), (x + 7, 72), (x - 6, 72)]), ramp, 'ink')
        else:  # pied nu ou sandale : un pied court
            c.part(c.poly([(x - 4, 67), (x + 4, 67), (x + 7, 70), (x + 7, 72), (x - 5, 72)]), ramp, 'ink')


def greaves(c, pose, ramp):
    """Jambières (armure) sur le bas des mollets."""
    hd, gd, kd, hg, gg, kg = LEGS[pose] if isinstance(pose, str) else pose
    for (g, k) in ((gd, kd), (gg, kg)):
        c.part(c.poly([(g[0] - 4, g[1] + 1), (g[0] + 4, g[1] + 1), (k[0] + 4, k[1] - 1), (k[0] - 4, k[1] - 1)]), ramp, 'ink', band=1)


def torso(c, b, ramp, w=1.0, top=27, waist=52):
    """Le torse : trapèzes qui montent vers le cou, épaules larges (w = 1 costaud, 0,8 fin)."""
    L, R = 40 - 16 * w, 40 + 16 * w
    c.part(c.poly([(L, 31 - b), (40 - 9 * w, top - b), (40 + 8 * w, top - 1 - b), (R, 30 - b), (R, 38 - b), (40 + 12 * w, 46), (40 + 10 * w, waist),
                   (40 - 9 * w, waist), (40 - 12 * w, 46), (L, 38 - b)]), ramp, 'ink')


def abs_lines(c, b, ramp, w=1.0):
    """Pectoraux et abdominaux (torse nu)."""
    c.line(40 - 13 * w, 41 - b, 39, 42 - b, ramp.deep), c.line(41, 42 - b, 40 + 13 * w, 40 - b, ramp.deep)
    c.line(40, 34 - b, 40, 51, ramp.deep)
    for y in (46, 49):
        c.line(40 - 7 * w, y, 39, y, ramp.shade), c.line(41, y, 40 + 7 * w, y, ramp.shade)


def plates(c, b, ramp, w=1.0):
    """Lignes d'une cuirasse : le milieu, deux plaques du ventre, un reflet en haut à droite."""
    c.line(40, 30 - b, 40, 50, ramp.deep)
    for y in (42, 46):
        c.line(40 - 12 * w, y, 40 + 12 * w, y - 1, ramp.deep)
    c.line(42, 30 - b, 40 + 13 * w, 30 - b, ramp.hi)


def neck(c, b, skin, head_y, head_rows, x0=36, x1=45):
    """Le cou, À POSER AVANT LE TORSE : le col du torse en couvre le bas, le menton en couvre le haut ; il ne se voit que
    sur 2 ou 3 pixels (jamais un long cou, jamais devant le torse)."""
    top = head_y + len(head_rows) - 5
    c.part(c.rect(x0, top - b, x1, 31 - b), skin, 'ink')


def belt(c, ramp, buckle=GOLD, y=49, w=1.0):
    c.part(c.rect(40 - 12 * w, y, 40 + 12 * w, y + 5), ramp, 'ink', band=1)
    c.part(c.rect(37, y - 1, 44, y + 6), buckle, 'ink', band=1)


def skirt(c, ramp, kind='cloth', w=1.0):
    """Le bas de la tunique : 'cloth' (pan fendu), 'plates' (pans d'armure), 'long' (robe jusqu'au sol)."""
    if kind == 'plates':
        for (x0, x1, y1) in [(30, 37, 61), (37, 44, 62), (44, 51, 60)]:
            c.part(c.poly([(x0, 52), (x1, 52), (x1 + 1, y1), (x0 - 1, y1)]), ramp, 'ink', band=1)
    elif kind == 'long':
        c.part(c.poly([(40 - 12 * w, 50), (40 + 12 * w, 50), (40 + 17 * w, 71), (40 - 19 * w, 71)]), ramp, 'ink')
        c.line(36, 54, 33, 70, ramp.shade), c.line(45, 54, 48, 70, ramp.shade)
    else:
        c.part(c.poly([(28, 52), (53, 52), (57, 61), (49, 62), (41, 58), (33, 62), (24, 61)]), ramp, 'ink')


def pauldron(c, b, center, ramp, rx=7.2, ry=5.2):
    c.part(c.ellipse(center[0], center[1] - b, rx, ry), ramp, 'ink')
    c.line(center[0] - rx * 0.6, center[1] - ry * 0.6 - b, center[0] + rx * 0.5, center[1] - ry * 0.7 - b, ramp.hi)


def cape(c, b, ramp, sw, long=True):
    c.part(c.poly([(30, 30 - b), (22, 34 - b), (14, 46), (9, (60 if long else 50) + sw), (6, (70 if long else 56) + sw),
                   (18, 70 if long else 56), (26, 60 if long else 50), (30, 44)]), ramp, 'ink')


# ---------- les armes et objets ----------
def shaft(c, x, y0, y1, ramp=WOOD, w=3):
    """Un manche droit, vertical (lance, bâton, hampe)."""
    c.part(c.rect(x - w // 2, y0, x - w // 2 + w, y1), ramp, 'ink', band=1)


def spear(c, x, y0, y1, head=STEEL, ramp=WOOD):
    shaft(c, x, y0 + 8, y1, ramp)
    c.part(c.poly([(x, y0 - 2), (x + 3, y0 + 5), (x + 1, y0 + 10), (x - 1, y0 + 10), (x - 3, y0 + 5)]), head, 'ink', band=1)


def blade(c, p, d, length, width=5, ramp=STEEL, guard=GOLD, grip=LEATHER):
    """Une épée : la poignée en p (là où est le poing), la lame vers d (vecteur unitaire)."""
    dx, dy = d
    nx, ny = -dy, dx
    hw = width / 2
    a = (p[0] + dx * 3, p[1] + dy * 3)
    tip = (p[0] + dx * (3 + length), p[1] + dy * (3 + length))
    c.part(c.poly([(a[0] - nx * hw, a[1] - ny * hw), (tip[0] - nx * hw * 0.7 - dx * 3, tip[1] - ny * hw * 0.7 - dy * 3), tip,
                   (tip[0] + nx * hw * 0.7 - dx * 3, tip[1] + ny * hw * 0.7 - dy * 3), (a[0] + nx * hw, a[1] + ny * hw)]), ramp, 'ink', band=1)
    c.line(a[0] + dx * 2, a[1] + dy * 2, tip[0] - dx * 5, tip[1] - dy * 5, ramp.light)
    c.part(c.poly([(a[0] - nx * 5, a[1] - ny * 5), (a[0] + nx * 5, a[1] + ny * 5), (a[0] + nx * 5 - dx * 2.6, a[1] + ny * 5 - dy * 2.6),
                   (a[0] - nx * 5 - dx * 2.6, a[1] - ny * 5 - dy * 2.6)]), guard, 'ink', band=1)
    c.part(c.ellipse(p[0] - dx * 4, p[1] - dy * 4, 2.2, 2.2), guard, 'ink')


def round_shield(c, b, center, r, ramp, rim=GOLD):
    x, y = center[0], center[1] - b
    c.part(c.ellipse(x, y, r, r), rim, 'ink')
    c.part(c.ellipse(x, y, r - 2.6, r - 2.6), ramp, 'ink')


def rect_shield(c, b, x0, y0, x1, y1, ramp, rim=GOLD):
    c.part(c.rect(x0, y0 - b, x1, y1 - b), rim, 'ink', band=1)
    c.part(c.rect(x0 + 2, y0 + 2 - b, x1 - 2, y1 - 2 - b), ramp, 'ink')


def erode(m, n=1):
    for _ in range(n):
        m = m & S(m, 1, 0) & S(m, -1, 0) & S(m, 0, 1) & S(m, 0, -1)
    return m


def flame(c, t, x, y, r, ramp=FIRE, core=CORE, h=1.6):
    """Une flamme (dans une main, sur une torche) : une seule masse, le cœur clair ; elle danse avec t."""
    f = [0, 1, 0, -1, 0, 1, 0, -1][t]
    m = c.ellipse(x, y, r, r)
    for (dx, hh) in ((-r * 0.5, h * 0.8), (0, h), (r * 0.5, h * 0.7)):
        m = m | c.limb([(x + dx, y - r * 0.3, r * 0.55), (x + dx * 1.2 + f, y - r * hh - 1, 0.8)])
    c.part(m, ramp, 'ink')
    c.fill(erode(m, 2), ramp.light)
    c.fill(erode(m, 3), core.base)


def bow(c, b, grip, ramp=WOOD, string_to=None, h=17):
    """Un arc tenu par la main gauche (grip), la corde tirée vers string_to."""
    x, y = grip[0], grip[1] - b
    c.part(c.limb([(x - 2, y - h, 1.6), (x + 3, y - h * 0.5, 2), (x + 4, y, 2.2), (x + 3, y + h * 0.5, 2), (x - 2, y + h, 1.6)]), ramp, 'ink')
    if string_to:
        sx, sy = string_to[0], string_to[1] - b
        c.line(x - 2, y - h, sx, sy, '#e8e0d0'), c.line(sx, sy, x - 2, y + h, '#e8e0d0')


def check_head(rows):
    """Toutes les lignes d'une tête ont la même largeur (sinon le dessin se décale)."""
    w = {len(r) for r in rows}
    assert len(w) == 1, [(i, len(r)) for i, r in enumerate(rows)]
    return rows


# Le visage commun (lignes 6 à 19 d'une tête de 21 de large) : à mettre sous les lignes du haut (cheveux, coiffe).
# h = les cheveux sur le côté, S/s/H = la peau, b = sourcils, w/p = l'œil (blanc, iris), m = la bouche.
FACE = [
    ".KhhKhhSShhSSShhhhK..",
    ".KhhKSSSSSSSSSSSSHK..",
    ".KhhKSbbSSSSSSSbbSK..",
    ".KhhKSSbbbSSSbbbSSHK.",
    ".KhhKSSwpKSSSKpwSSHK.",
    ".KhhKSSsssSsSsssSSSSK",
    ".KhhKSSSSSSssSSSSSSK.",
    "..KhKSSSSSSSSSSSSSK..",
    "..KhKSSSSmmmmmSSSK...",
    "..KhKsSSSSSSSSSSSK...",
    "...KKssSSSSSSSSSK....",
    "....KKsSSSSSSSHK.....",
    ".....KKKssssKKK......",
    "........KKKK.........",
]
FACE_BLINK = {'w': 'b', 'p': 'b'}


def face_legend(skin, hair, eye='#2a1a10', mouth='#4a1010', brow='#2a160c'):
    return {'K': INK, 'h': hair, 'S': skin.light, 's': skin.base, 'H': skin.hi, 'b': brow, 'w': '#ffffff', 'p': eye, 'm': mouth}


def feather_wing(c, b, root, sgn, ramp, cover=None, fl=0, size=1.0, tip=None):
    """Une aile de plumes levée (ange, aigle, corbeau…) : une seule forme pleine, du bord d'attaque jusqu'au bout des
    grandes plumes au bord festonné, cerclée de noir ; une rangée de plumes de couverture le long du bord ; le bout des
    plumes plus clair (ou de la couleur tip)."""
    rx, ry = root
    s = size
    edge = [(rx, ry), (rx + sgn * 8 * s, ry - 10 * s), (rx + sgn * 15 * s, ry - 19 * s), (rx + sgn * 24 * s, ry - 24 * s), (rx + sgn * 32 * s, ry - 26 * s)]
    lengths = [10 * s, 13 * s, 16 * s, 18 * s, 17 * s]
    d = [(sgn * 0.25, 1), (sgn * 0.3, 1), (sgn * 0.4, 1), (sgn * 0.5, 1), (sgn * 0.6, 1)]
    tips = [(x + dx * L + sgn * fl * 0.4 * k / 4, y + dy * L + fl * k / 4) for k, ((x, y), (dx, dy), L) in enumerate(zip(edge, d, lengths))]
    feathers = []
    for k in range(len(tips)):
        feathers.append(tips[k])
        if k < len(tips) - 1:
            feathers.append(((tips[k][0] + tips[k + 1][0]) / 2, (tips[k][1] + tips[k + 1][1]) / 2 + 2))
    m = c.poly([(x, y - b) for (x, y) in edge] + [(x, y - b) for (x, y) in reversed(tips)])
    for (x, y) in feathers:
        m = m | c.ellipse(x, y - b, 3.2 * s, 3.6 * s)
    c.part(m, ramp, 'ink')
    for (x, y) in feathers:
        c.fill(c.ellipse(x, y - 1 - b, 1.4, 1.6) & m, tip or ramp.hi)
    for k in range(len(feathers) - 1):
        (x0, y0), (x1, y1) = feathers[k], feathers[k + 1]
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2 - 1
        ex, ey = edge[min(len(edge) - 1, (k + 1) // 2)]
        c.line(mx, my - b, mx + (ex - mx) * 0.3, my + (ey - my) * 0.3 - b, ramp.deep)
    cov = c.limb([(x + dx * 3, y + dy * 3 - b, (5.4 - 2.4 * k / 4) * s) for k, ((x, y), (dx, dy)) in enumerate(zip(edge, d))])
    c.part(cov, cover or ramp, 'ink')
