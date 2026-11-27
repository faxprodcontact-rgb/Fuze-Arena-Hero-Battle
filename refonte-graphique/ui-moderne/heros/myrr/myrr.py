# Myrr (mages-11, vent, soigneuse) redessinée en VECTORIEL lisse, dans le style moderne de l'interface (même outil,
# même trait, même échelle que Kael : ../kael/kael.py, ../atelier.py).
#
#   python3 refonte-graphique/ui-moderne/heros/myrr/myrr.py      # → myrr.svg + images 512 et 160 px de haut
#
# Même personnage que le pixel art (refonte-graphique/pixel/hd/myrr.txt) : l'ange héraut, sévère et lumineuse, qui
# sonne la trompette d'or. Femme ange élancée mais solide ; robe ivoire à col montant ourlé d'or, empiècement d'or en V
# décalé (trois quarts) à broche turquoise, ceinture d'or à boucle turquoise, surjupe au bas découpé en pétales arrondis
# bordés d'or, sous-jupe à l'ourlet d'or, bottes de cuir brun ; épaulière d'or en lames sur l'épaule proche, brassard
# d'or à pierre turquoise au poignet proche, manche bouffante lointaine. Cheveux blond clair tirés en arrière : tresse
# en couronne sur le crâne, gros chignon rond derrière où la tresse s'enroule, oreille dégagée avec une goutte de
# turquoise montée sur or ; auréole d'or au-dessus de la tête (de l'air entre les deux). Visage de jeune femme sévère :
# sourcils en V, paupières lourdes, yeux turquoise, nez discret, bouche serrée, menton fin.
# Deux grandes ailes d'oiseau blanches repliées « en manteau », pointes vers le bas : la proche, levée (son poignet plus
# haut que la tête), ses rémiges tombent jusqu'aux mollets ; la lointaine dépasse derrière l'épaule, dans l'ombre.
# Bras lointain : coude près du flanc, le poing serre le tube de la trompette devant la hanche (doigts devant, pouce
# par-dessus), la trompette monte en biais, le pavillon à côté du visage. Bras proche le long du corps, main ouverte
# paume en avant, pouce écarté (geste de soigneuse).
# Coordonnées = pixels du dessin pixel art (le sol est y = 116, les pieds en (66, 116)), pour se poser au même endroit
# dans le jeu. Une seule lumière, en haut à droite ; un seul contour (atelier.py).
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
from atelier import Mat, sm, limb, ribbon, xf, ellipse, rpoly, mchain, mT, mR, mS, mapp  # noqa: E402
from lib import Shape  # noqa: E402
from visage import placer  # noqa: E402
from outils import (rot, unit, add, sub, lerp, norm, ang_of, ik, arm_shape, crpath, taper, curve_band, under,  # noqa: E402
                    almond_pt, inter, FigN, poly, from_poly)

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))

# ---------- matières (tons du pixel art, passés à la gamme de l'interface : lumières chaudes, ombres violettes) ----------
SKIN = Mat('#fff2e4', '#ffe0c8', '#f3bf9e', '#cc8578', '#8e4a5a')
HAIR = Mat('#fffbe0', '#f8df92', '#e2b75a', '#b07a3a', '#6a3a2e', glint='#fffdf0')
IVORY = Mat('#ffffff', '#fffcf4', '#f2eae6', '#c6b4d4', '#8a72a6')
GOLD = Mat('#fff6c0', '#ffd04a', '#e8a032', '#a65a24', '#5c2418', glint='#fffbe8')
LEATHER = Mat('#e8a466', '#d08c52', '#9e5a34', '#6c3428', '#3a1a26')
TURQ = Mat('#c8fff0', '#6ae6c6', '#2fb4a0', '#137a74', '#0b4650', glint='#eefffa')
PLUME = Mat('#ffffff', '#f6f8ff', '#e6ecfc', '#aab3de', '#5e6498', glint='#ffffff')      # l'aile proche
PLUME2 = Mat('#f2f5ff', '#dfe6fa', '#c7d0ee', '#8e98cc', '#4e5488', glint='#ffffff')     # ses rémiges (plus bleues)
PLUMEF = Mat('#e8eeff', '#ccd5f2', '#b5c0e6', '#8590c6', '#4a5084', glint='#f6f8ff')     # l'aile lointaine (ombre)
LIPS = ('#6c1e36', '#a83a4e', '#d86e78')
BROW = '#8a5a30'
LASH = '#3a1830'

GRD = 116          # le sol
FEET = (66, 116)   # le point « pieds » du pixel art (sol: 66 116)
# la boîte de l'image (x0, y0, largeur, hauteur) en pixels du dessin
FRAME = (-1, 0, 128, 119)
H0 = (72.5, 47.5)  # le pivot de la tête (agrandie ×1,1 : proportions stylisées, comme Kael)
# la boîte de la face (ovale du visage, sans cheveux ni oreilles), repère de la tête avant l'agrandissement : les traits
# sont placés par ../visage.py (placer) ; elle est centrée sur l'axe du cou (x ≈ 72), lui-même au milieu du buste
FACE_BOX = (63.0, 24.5, 82.0, 47.0)
MOUTH = (75.07, 42.5)   # le milieu de la bouche (= placer(FACE_BOX)['bouche']) : l'embouchure s'y pose (anim.py)

# ---------- le squelette (animation) ----------
# Une pose = ces réglages ; REST est la pose du dessin. Tout est en pixels du dessin et en degrés (y vers le bas).
#   breath : souffle 0..1 (buste et épaules montent, la tête suit) ; lean : elle se penche en avant (+) depuis les
#   hanches ; crouch : elle se tasse (0..2) ; lift : elle s'élève (pixels, la spéciale) ; head / tilt : la tête ;
#   halo : l'auréole flotte (décalage vertical) ; glow : l'auréole s'embrase (0..1) ; wing / wingF : l'état des ailes
#   (voir WING_STATES : 'fold', 'demi', 'grande', 'battue', ou un mélange) ; wl / wlF : elles se lèvent (degrés,
#   autour de leur racine) ; wph : la houle des plumes ; tm : l'embouchure de la trompette ; tang : son angle ;
#   gs : où le poing la tient (distance depuis l'embouchure) ; nh : la main proche s'ouvre (0..1) ; hem : le bas de la
#   robe ondule ; ear : la goutte d'oreille se balance ; blink : yeux fermés ; cheek : elle gonfle les joues (souffle).
TM0 = (85.8, 83.6)         # l'embouchure, au repos (près de la hanche)
TANG0 = -61.5              # la trompette monte en biais vers le haut à droite
TLEN = 49.5                # de l'embouchure au bord du pavillon
GS0 = 24.0                 # le poing, sur le tube, à cette distance de l'embouchure
SF0 = (86.0, 55.0)         # l'épaule lointaine
LUF, LFF = 14.6, 9.8       # bras lointain : bras, avant-bras (jusqu'au poignet)
S0 = (53.6, 57.6)          # l'épaule proche (sous l'épaulière)
LU, LF = 11.8, 10.6        # bras proche
HAND0 = (46.6, 79.0)       # le poignet proche

REST = dict(breath=0.0, lean=0.0, crouch=0.0, lift=0.0, head=(0.0, 0.0), tilt=0.0, halo=0.0, glow=0.0,
            wing=None, wingF=None, wl=0.0, wlF=None, wph=0.0, tm=TM0, tang=TANG0, gs=GS0, nh=0.0, hem=0.0, ear=0.0,
            blink=0.0, cheek=0.0, gold=0.0, aur=0.0)   # aur : le signe du repos (anim.signe) : l'auréole s'illumine


# ======================================================================== les ailes
# Une aile = son bord d'attaque, une ligne souple R (racine, derrière l'épaule) → E (coude) → W (poignet) → T (bout de
# la main), d'où pendent les plumes : 1 tertiaire, 4 secondaires (bras), 4 grandes rémiges primaires (main) ; chacune
# part de sa racine sur le bord, dans sa direction (angle, longueur). Par-dessus : trois rangées de couvertures en
# écailles arrondies (la plus haute, lisse et éclairée, fait le bord d'attaque). Les états (repliée, ouverte…) sont des
# réglages de ce même squelette : l'animation passe de l'un à l'autre en douceur.
# Les positions sont celles de l'aile PROCHE ; l'aile lointaine est son miroir, resserré (vue de trois quarts).
FS = [0.22, 0.36, 0.45, 0.53, 0.61, 0.70, 0.79, 0.89, 0.985]     # racines des plumes (abscisse le long du bord)
FW = [10.6, 11.0, 11.2, 11.0, 10.8, 10.4, 10.0, 9.4, 8.6]        # leurs largeurs
# l'aile repliée du dessin (pixel art) : le bord, et le bout de chaque plume (de la plus proche du corps à la plus
# lointaine) ; on en tire, pour chaque plume, un petit écart d'angle et de longueur gardé dans tous les états
FOLD = dict(R=(58.0, 43.0), E=(49.6, 21.0), W=(28.4, 9.4), T=(15.8, 33.0), ai=96.0, ao=97.0, li=60.0, lo=66.0,
            c1=0.30, c2=0.50, c3=0.70, b1=2.6, b2=5.4)
FOLD_TIPS = [(48.0, 81.0), (43.6, 85.6), (39.0, 88.2), (34.0, 90.8), (29.0, 93.2), (24.0, 95.6), (19.2, 98.6),
             (14.0, 100.4), (8.8, 96.6)]
WING_STATES = dict(
    fold=FOLD,
    # à moitié ouverte : la main remonte, les plumes s'écartent en éventail
    demi=dict(R=(58.0, 43.0), E=(46.0, 26.0), W=(29.0, 8.0), T=(10.0, -4.0), ai=100.0, ao=150.0, li=50.0, lo=40.0,
              c1=0.30, c2=0.50, c3=0.70, b1=2.4, b2=3.0),
    # grande ouverte, levée en V au-dessus d'elle
    grande=dict(R=(58.0, 43.0), E=(45.0, 28.0), W=(30.0, 4.0), T=(6.0, -24.0), ai=104.0, ao=176.0, li=42.0, lo=34.0,
                c1=0.30, c2=0.50, c3=0.70, b1=2.0, b2=2.0),
    # battue (coup d'aile vers le bas) : presque à l'horizontale
    battue=dict(R=(58.0, 43.0), E=(44.0, 36.0), W=(24.0, 34.0), T=(-2.0, 40.0), ai=98.0, ao=132.0, li=36.0, lo=30.0,
                c1=0.30, c2=0.50, c3=0.70, b1=2.0, b2=2.0),
)


def wing_curve(st, n=60):
    """Le bord d'attaque : R → E → W → T, arrondi au coude et au poignet (b1, b2 : bombé vers le dehors)."""
    R, E, W, T = st['R'], st['E'], st['W'], st['T']
    fd = unit(st['ai'])

    def bulge(a, b, t, k):
        m = lerp(a, b, t)
        d = norm(sub(b, a))
        n_ = (-d[1], d[0])
        if n_[0] * fd[0] + n_[1] * fd[1] > 0:
            n_ = (-n_[0], -n_[1])
        return add(m, n_, k)
    return crpath([R, E, bulge(E, W, 0.5, st.get('b1', 2.0)), W, bulge(W, T, 0.35, st.get('b2', 2.0)), T], n)


def _at(curve, s):
    """Le point et la tangente du bord à l'abscisse s (0..1)."""
    n = len(curve) - 1
    k = min(n - 1, max(0, int(s * n)))
    f_ = s * n - k
    p = lerp(curve[k], curve[k + 1], f_)
    t = norm(sub(curve[k + 1], curve[k]))
    return p, t


def _lin_af(st, i):
    t = i / (len(FS) - 1)
    return st['ai'] + (st['ao'] - st['ai']) * t, st['li'] + (st['lo'] - st['li']) * t


def _jitter():
    cur = wing_curve(FOLD)
    out = []
    for i, s in enumerate(FS):
        p0, tg = _at(cur, s)
        p = p0
        for _ in range(4):
            d = sub(FOLD_TIPS[i], p)
            dd = norm(d)
            p = add(p0, outward(tg, dd), -0.5 * FW[i] * abs(tg[0] * dd[0] + tg[1] * dd[1]))
        d = sub(FOLD_TIPS[i], p)
        a0, l0 = _lin_af(FOLD, i)
        out.append((ang_of(d) - a0, math.hypot(*d) / l0))
    return out




def mix_state(a, b, t):
    """Un état entre deux états d'aile (t = 0 → a, 1 → b)."""
    A = WING_STATES[a] if isinstance(a, str) else a
    B = WING_STATES[b] if isinstance(b, str) else b
    out = {}
    for k in A:
        if isinstance(A[k], tuple):
            out[k] = lerp(A[k], B[k], t)
        else:
            out[k] = A[k] + (B[k] - A[k]) * t
    return out


def feathers(st, ph=0.0, flut=0.0):
    """Les plumes d'un état : (racine, points du rachis, largeur, angle) de la plus proche du corps à la plus lointaine."""
    cur = wing_curve(st)
    out = []
    n = len(FS)
    for i, s in enumerate(FS):
        p, tg = _at(cur, s)
        a0, l0 = _lin_af(st, i)
        ja, jl = JIT[i]
        a = a0 + ja + flut * 2.2 * math.sin(ph - 0.7 * i)
        dd = unit(a)
        p = add(p, outward(tg, dd), -0.5 * FW[i] * abs(tg[0] * dd[0] + tg[1] * dd[1]))
        L = l0 * jl
        d = unit(a)
        side = (-d[1], d[0])
        bend = 1.4 + 0.5 * math.sin(ph * 0.5 - 0.5 * i) * flut
        c = [add(add(p, d, L * u), side, bend * math.sin(math.pi * u) * (1 if i < n - 1 else 0.6)) for u in (0, 0.25, 0.5, 0.75, 1.0)]
        out.append((p, crpath(c, 14), FW[i], a))
    return cur, out


def feather_shape(c, w):
    """Une plume : étroite à la racine, pleine au milieu, bout arrondi (un peu en ogive)."""
    n = len(c) - 1
    ws = [w * (0.62 + 0.38 * math.sin(math.pi * min(1.0, i / n * 1.25) * 0.5 + 0.0) if i < n * 0.8 else 1.0) for i in range(n + 1)]
    # le bout : il s'arrondit sur le dernier cinquième
    for i in range(n + 1):
        t = i / n
        if t > 0.82:
            ws[i] = w * math.sqrt(max(0.0, 1 - ((t - 0.82) / 0.2) ** 2)) * 0.98 + 0.05
    from atelier import sides
    left, right = sides(c, ws)
    return sm(left + [c[-1]] + right[::-1], t=0.85)


def outward(tg, d):
    """La normale au bord d'attaque, du côté opposé aux plumes (vers le dehors de l'aile)."""
    n = (-tg[1], tg[0])
    if n[0] * d[0] + n[1] * d[1] > 0:
        n = (-n[0], -n[1])
    return n


def covert_row(cur, st, feat, frac, lobes, back=1.0, seed=0.0, s0=0.0, s1=1.0, tipfall=0.4):
    """Une rangée de couvertures : le haut suit le bord d'attaque (un peu derrière), le bas fait des écailles arrondies
    (des bouts de plumes) ; profondeur = frac × longueur locale des plumes, qui baisse vers le bout de la main."""
    n = len(cur) - 1
    # la direction et la longueur locales des plumes, interpolées le long du bord
    def local(s):
        # entre les racines voisines
        if s <= FS[0]:
            i0, i1, f_ = 0, 0, 0.0
        elif s >= FS[-1]:
            i0, i1, f_ = len(FS) - 1, len(FS) - 1, 0.0
        else:
            i1 = next(k for k in range(len(FS)) if FS[k] >= s)
            i0 = i1 - 1
            f_ = (s - FS[i0]) / (FS[i1] - FS[i0])
        a = feat[i0][3] + (feat[i1][3] - feat[i0][3]) * f_
        L0 = math.dist(feat[i0][1][0], feat[i0][1][-1])
        L1 = math.dist(feat[i1][1][0], feat[i1][1][-1])
        return unit(a), L0 + (L1 - L0) * f_
    top = []
    m = 24
    for k in range(m + 1):
        s = s0 + (s1 - s0) * k / m
        p, tg = _at(cur, s)
        d, _ = local(s)
        top.append(add(p, outward(tg, d), back))
    bot = []
    sharp = []
    edges = [s0 + (s1 - s0) * (j + 0.12 * math.sin(3.1 * j + seed)) / lobes for j in range(lobes + 1)]
    edges[0], edges[-1] = s0, s1
    for j in range(lobes):
        a_, b_ = edges[j], edges[j + 1]
        for k in range(7):
            if k == 0 and j > 0:
                sharp.append(len(bot))
            u = k / 6
            s = a_ + (b_ - a_) * u
            p, _ = _at(cur, s)
            d, L = local(s)
            fall = 1 - tipfall * max(0.0, (s - 0.63) / 0.37)
            dep = frac * L * fall * (0.86 + 0.14 * math.sin(math.pi * u))
            bot.append(add(p, d, dep))
    pts = top + bot[::-1]
    nt = len(top)
    sh = [nt + (len(bot) - 1 - i) for i in sharp]
    return sm(pts, sharp=sh, t=0.9), top


JIT = _jitter()


def wing(fig, pre, st, mp, mats, P, far=False):
    """Les morceaux d'une aile, dans le repère de l'aile proche ; mp : ce repère → le dessin (levée, miroir)."""
    names = []
    m_cov, m_rem = mats
    ph = P['wph']
    flut = 1.0

    def part(name, sh, mat, **k):
        names.append(pre + name)
        if 'details' in k:
            k['details'] = [(d[0].map(mp), mfill(d[1]), d[2]) for d in k['details']]
        if k.get('grad'):
            g = k['grad']
            a, b = mp((g[0], g[1])), mp((g[2], g[3]))
            k['grad'] = (a[0], a[1], b[0], b[1], g[4])
        return fig.part(pre + name, sh.map(mp), mat, **k)

    def mfill(fl):
        if isinstance(fl, tuple) and fl[0] == 'lin':
            a, b = mp((fl[1], fl[2])), mp((fl[3], fl[4]))
            return ('lin', a[0], a[1], b[0], b[1], fl[5])
        return fl

    cur, feat = feathers(st, ph, flut)
    rows = [('c3', st['c3'], 6, 0.6, 1.0), ('c2', st['c2'], 6, 2.1, 0.95), ('c1', st['c1'], 8, 4.0, 0.9)]
    row_sh = {}
    for nm, frac, lobes, seed, cst in rows:
        row_sh[nm] = covert_row(cur, st, feat, frac, lobes, seed=seed, s0=0.05,
                                tipfall={'c3': 0.55, 'c2': 0.75, 'c1': 0.9}[nm])
    # le fond de l'aile (le dessous des plumes, dans l'ombre) : rien ne se voit à travers, sauf entre les bouts
    tips_in = [lerp(f_[1][0], f_[1][-1], 0.72) for f_ in feat]
    top3 = row_sh['c3'][1]
    und = sm(top3[::2] + [top3[-1]] + tips_in[::-1], t=0.8)
    part('under', und, m_rem, grad=(st['W'][0], st['W'][1], tips_in[0][0], tips_in[0][1] + 10,
                                     [(0, m_rem.shadow), (1, m_rem.deep)]), cel=0, rim=0, cast=0)
    # les plumes : de la plus lointaine (bout de la main) à la plus proche du corps ; chacune pose son ombre douce sur
    # la précédente (jamais de trait)
    allp = [pre + 'f%d' % j for j in range(len(feat))]
    for i in range(len(feat) - 1, -1, -1):
        p, c, w, a = feat[i]
        sh = feather_shape(c, w)
        mid = c[len(c) // 2]
        tip = c[-1]
        prim = i >= 5
        mat = m_rem
        top_col = m_cov.base if not prim else m_rem.light
        grad = (c[0][0] + 3, c[0][1] - 3, tip[0] - 2, tip[1] + 2,
                [(0, top_col), (0.55, m_rem.base if prim else m_cov.shadow if False else m_rem.light), (1, m_rem.base)])
        det = [(ribbon(c[2:-3], [0.1] + [0.42] * (len(c) - 7) + [0.1]), m_cov.hi, 0.55),               # le rachis
               (taper([add(q, unit(a + 90), -w * 0.22) for q in c[4:-2]], 0.1, 0.1, wmid=w * 0.22), m_rem.shadow, 0.16)]
        part('f%d' % i, sh, mat, grad=grad, cel=1.0, rim=0.55, cast=1.2,
             cast_on=[pre + 'under'] + allp[i + 1:], details=det)
    # les couvertures : trois rangées en écailles (de la plus basse à la plus haute)
    prev = [pre + 'under'] + allp
    for nm, frac, lobes, seed, cst in rows:
        sh = row_sh[nm][0]
        top_c = m_cov.light if nm != 'c3' else m_cov.base
        W_ = st['W']
        part(nm, sh, m_cov, grad=(W_[0] + 6, W_[1] - 6, W_[0] - 8, W_[1] + 40,
                                  [(0, m_cov.hi if nm == 'c1' else top_c), (0.5, m_cov.light if nm == 'c1' else m_cov.base), (1, m_cov.base)]),
             cel=1.1, rim=0.7 if nm == 'c1' else 0.5, cast=cst, cast_on=list(prev))
        prev.append(pre + nm)
    # le bord d'attaque : un liseré de lumière lisse le long du haut de l'aile (peint dans la rangée du haut)
    return names, cur, feat


def wing_maps(P):
    """Les repères des deux ailes : la proche tourne autour de sa racine ; la lointaine est son miroir resserré."""
    R = FOLD['R']
    lift = P['wl']
    liftF = P['wl'] if P['wlF'] is None else P['wlF']
    MN = mR(-lift, R[0], R[1])
    # miroir : la racine (58, 43) vient en (81, 37), largeur × 0,64, hauteur × 0,8
    MF = mchain(mT(81.0, 37.0), mR(liftF, 0, 0), mS(-0.64, 0.8), mT(-R[0], -R[1]))
    return MN, MF


# ======================================================================== la trompette (repère : x le long du tube)

def tr_frame(tm, tang):
    u = unit(tang)
    v = (-u[1], u[0])

    def L(x, y):
        return (tm[0] + u[0] * x + v[0] * y, tm[1] + u[1] * x + v[1] * y)
    return L, u, v


def bell_r(x):
    """Le rayon du tube à l'abscisse x (pavillon qui s'évase sur les 15 derniers pixels)."""
    b0 = TLEN - 16.0
    if x <= b0:
        return 1.0
    t = (x - b0) / (TLEN - b0)
    return 1.0 + 5.6 * t ** 2.3


def trumpet(fig, P):
    L, u, v = tr_frame(P['tm'], P['tang'])
    names = []
    # le tube et le pavillon : une seule forme (profil évasé), le bord du pavillon arrondi
    xs = [0.8 + (TLEN - 0.8) * k / 40 for k in range(41)]
    top = [L(x, -bell_r(x)) for x in xs]
    bot = [L(x, bell_r(x)) for x in xs]
    rim_ry = bell_r(TLEN)
    rim_rx = 1.9
    # l'au-delà du bord : la moitié de l'ellipse du bord (côté pavillon)
    arc = [L(TLEN + rim_rx * math.sin(math.pi * k / 8), -rim_ry * math.cos(math.pi * k / 8)) for k in range(1, 8)]
    body = sm(top + arc + bot[::-1], sharp=(0, len(top) + len(arc) + len(bot) - 1), t=0.7)
    gl = P['gold']
    det = [(ribbon([L(3, -0.45), L(16, -0.5), L(TLEN - 16, -0.5), L(TLEN - 6, -2.6), L(TLEN - 1.5, -5.0)],
                   [0.1, 0.42, 0.42, 0.6, 0.1]), GOLD.hi, 0.9)]
    # la bague à mi-longueur, et la virole au pied du pavillon
    for x0, x1 in ((20.0, 21.8), (TLEN - 16.6, TLEN - 15.4)):
        det += [(sm([L(x0, -1.6), L(x1, -1.6), L(x1, 1.6), L(x0, 1.6)], sharp=(0, 1, 2, 3), t=0.3), GOLD.light, 1),
                (sm([L(x0, 0.4), L(x1, 0.4), L(x1, 1.6), L(x0, 1.6)], sharp=(0, 1, 2, 3), t=0.3), GOLD.shadow, 0.9)]
    # l'ouverture du pavillon : la lèvre éclairée, l'intérieur d'or sombre (vu un peu de face)
    cx, cy = L(TLEN, 0)
    lip = ellipse(cx, cy, rim_rx + 0.15, rim_ry + 0.1, P['tang'])
    inside = ellipse(*L(TLEN + 0.25, 0.25), rim_rx - 0.55, rim_ry - 0.75, P['tang'])
    det += [(lip, GOLD.hi, 1),
            (inside, ('rad', *L(TLEN - 0.6, 1.4), 6.0, 6.0, [(0, GOLD.deep), (0.6, GOLD.shadow), (1, GOLD.base)]), 1),
            (ribbon([L(TLEN + 0.4, -rim_ry + 1.0), L(TLEN + 1.3, -rim_ry * 0.3), L(TLEN + 1.0, rim_ry * 0.45)],
                    [0.1, 0.5, 0.1]), GOLD.base, 0.8)]
    if gl > 0:
        det.append((body, GOLD.hi, 0.4 * gl))
    fig.part('trumpet', body, GOLD, grad=(*L(TLEN, -6), *L(TLEN * 0.3, 3), [(0, GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]),
             cel=0.55, rim=0.45, cast=0.9, details=det)
    names.append('trumpet')
    # l'embouchure : une petite coupe au bout du tube
    mouth = sm([L(-1.6, -1.5), L(1.4, -1.0), L(2.4, -0.7), L(2.4, 0.7), L(1.4, 1.0), L(-1.6, 1.5), L(-2.0, 0)], t=0.8)
    fig.part('tmouth', mouth, GOLD, cel=0.4, rim=0.35, cast=0.5, details=[(ellipse(*L(-1.5, -0.3), 0.35, 1.0, P['tang']), GOLD.hi, 0.9)])
    names.append('tmouth')
    return names, L, u, v


# ======================================================================== le dessin

def build(ow=0.95, pose=None, fx=None, frame=FRAME):
    P = dict(REST, **(pose or {}))
    fig = FigN(*frame, ow=ow)
    br = P['breath']
    lf = P['lift']
    cr = P['crouch']
    BODY = mT(0, -lf)                                                             # tout le corps (elle s'élève)
    U = mchain(BODY, mT(P['lean'] * 0.35, cr * 0.6), mR(P['lean'] * 1.0, 68, 104))  # le haut du corps (hanches)
    UC = mchain(U, mT(0, -0.6 * br))                                              # ce qui monte avec le souffle
    TOR = mchain(U, mS(1, 1 + 0.012 * br, 72, 72))
    HEAD = mchain(UC, mT(*P['head']), mR(P['tilt'], H0[0], H0[1] - 4), mS(1.1, 1.1, H0[0], H0[1]))
    ROBE = mchain(BODY, mT(0, cr * 0.3), mR(P['lean'] * 0.3, 68, 112))

    # ---- les ailes : la lointaine, puis la proche (derrière tout le corps) ----
    MN, MF = wing_maps(P)
    stN = P['wing'] or FOLD
    stF = P['wingF'] or stN
    if isinstance(stN, str):
        stN = WING_STATES[stN]
    if isinstance(stF, str):
        stF = WING_STATES[stF]
    wing_names = []
    nf, curF, featF = wing(fig, 'wf', stF, lambda p: mapp(mchain(UC, MF), p), (PLUMEF, PLUMEF), P, far=True)
    wing_names += nf
    nn, curN, featN = wing(fig, 'wn', stN, lambda p: mapp(mchain(UC, MN), p), (PLUME, PLUME2), P)
    wing_names += nn

    # ---- l'auréole (au-dessus de la tête, de l'air entre les deux) ----
    halo_names = halo(fig, P)

    # ---- la trompette : sa pose (dans le repère du haut du corps) ----
    tm_ = mapp(U, P['tm'])
    tang = P['tang'] + P['lean'] * 1.0
    P2 = dict(P, tm=tm_, tang=tang)
    Lt, ut, vt = tr_frame(tm_, tang)
    G = Lt(P['gs'], 0)                                   # le point de prise sur le tube

    # ---- le bras lointain (gauche) : manche ivoire, coude près du flanc, le poignet sous le poing ----
    SF = mapp(UC, SF0)
    WF = add(add(G, ut, -4.4), vt, -1.4)                  # le poignet : sous le poing, du côté de la paume
    EF = ik(SF, WF, LUF, LFF, 1)
    farm = arm_shape(SF, EF, WF, (7.4, 6.4, 5.0))
    fa = ang_of(sub(WF, EF))
    Lf = math.dist(EF, WF)
    fdet = [(xf(rpoly([(Lf - 3.4, -5), (Lf + 0.6, -5), (Lf + 0.6, 5), (Lf - 3.4, 5)], 0.4), EF[0], EF[1], fa), GOLD.base, 1),
            (xf(rpoly([(Lf - 3.4, -5), (Lf + 0.6, -5), (Lf + 0.6, -1.4), (Lf - 3.4, -1.4)], 0.4), EF[0], EF[1], fa), GOLD.light, 0.9),
            (xf(ribbon([(Lf - 3.2, 0.2), (Lf - 1.4, 0.6), (Lf + 0.4, 0.2)], [0.1, 0.6, 0.1]), EF[0], EF[1], fa), GOLD.shadow, 0.8)]
    fig.part('farm', farm, IVORY, grad=(EF[0] + 4, EF[1] - 6, SF[0] - 2, SF[1] + 10, [(0, IVORY.base), (0.5, IVORY.shadow), (1, IVORY.deep)]),
             cel=1.0, rim=0.5, cast=1.0, cast_on=wing_names, details=fdet)
    # la manche bouffante, à l'épaule lointaine, son brassard d'or dessous
    puff = sm([add(SF, (-3.6, -2.8)), add(SF, (1.4, -3.6)), add(SF, (4.8, -1.0)), add(SF, (5.4, 3.6)), add(SF, (4.0, 7.2)),
               add(SF, (0.6, 8.4)), add(SF, (-3.0, 6.6))], t=0.95)
    fig.part('puff', puff, IVORY, grad=(SF[0] + 5, SF[1] - 3, SF[0] - 3, SF[1] + 8, [(0, IVORY.light), (0.55, IVORY.base), (1, IVORY.shadow)]),
             cel=1.1, rim=0.7, cast=1.0, cast_on=wing_names + ['farm'],
             details=[(ribbon([add(SF, (1.2, -2.4)), add(SF, (3.2, 1.0)), add(SF, (2.6, 5.4))], [0.1, 0.8, 0.1]), IVORY.shadow, 0.45),
                      (ribbon([add(SF, (-3.4, 6.4)), add(SF, (0.6, 8.0)), add(SF, (4.0, 7.0))], [0.3, 1.3, 0.3]), GOLD.base, 1),
                      (ribbon([add(SF, (-3.0, 6.0)), add(SF, (0.6, 7.5)), add(SF, (3.8, 6.6))], [0.1, 0.5, 0.1]), GOLD.hi, 0.9)])

    # ---- les bottes (sous la robe) ----
    boots(fig, P, BODY)

    # ---- la sous-jupe (l'ourlet d'or) puis la robe : buste et surjupe aux pétales bordés d'or ----
    dress_names = dress(fig, P, ROBE, TOR)

    # ---- le bras proche (droit), le long du corps ----
    S = mapp(UC, S0)
    nh = P['nh']
    W = mapp(U, add(HAND0, (1.6 * nh, -1.2 * nh)))
    E = ik(S, W, LU, LF, 1)
    ua_ = ang_of(sub(E, S))
    fa_ = ang_of(sub(W, E))
    Ln = math.dist(E, W)
    narm = arm_shape(S, E, W, (8.2, 7.2, 6.4))
    ndet = [(ribbon([lerp(S, E, 0.25), lerp(S, E, 0.7), lerp(E, W, 0.1), lerp(E, W, 0.55)], [0.1, 1.0, 0.8, 0.1]).move(1.6, 0.2), IVORY.light, 0.5),
            (ribbon([lerp(S, E, 0.4), lerp(E, W, 0.0), lerp(E, W, 0.4)], [0.1, 0.9, 0.1]).move(-1.4, 0.2), IVORY.deep, 0.25),
            # le brassard d'or, à pierre turquoise (il fait le tour du poignet)
            (xf(rpoly([(Ln * 0.42, -6), (Ln + 0.8, -6), (Ln + 0.8, 6), (Ln * 0.42, 6)], 0.4), E[0], E[1], fa_), GOLD.base, 1),
            (xf(rpoly([(Ln * 0.42, -6), (Ln + 0.8, -6), (Ln + 0.8, -1.6), (Ln * 0.42, -1.6)], 0.4), E[0], E[1], fa_), GOLD.light, 0.95),
            (xf(ribbon([(Ln * 0.44, -1.0), (Ln * 0.44, 1.6), (Ln * 0.46, 3.6)], [0.3, 0.7, 0.2]), E[0], E[1], fa_), GOLD.shadow, 0.7),
            (xf(ribbon([(Ln + 0.2, -3.6), (Ln + 0.3, 0), (Ln + 0.2, 3.6)], [0.2, 0.8, 0.2]), E[0], E[1], fa_), GOLD.shadow, 0.85),
            (xf(ellipse(Ln * 0.72, -0.2, 1.4, 1.65), E[0], E[1], fa_), TURQ.shadow, 1),
            (xf(ellipse(Ln * 0.72, -0.25, 1.05, 1.25), E[0], E[1], fa_), ('rad', *xf_pt(E, fa_, (Ln * 0.7, -0.8)), 1.6, 1.6,
                                                                             [(0, TURQ.hi), (0.45, TURQ.light), (1, TURQ.base)]), 1),
            (xf(ellipse(Ln * 0.68, -0.75, 0.32, 0.36), E[0], E[1], fa_), '#ffffff', 0.9)]
    fig.part('narm', narm, IVORY, grad=(S[0] + 5, S[1], W[0] - 4, W[1], [(0, IVORY.base), (0.5, IVORY.shadow), (1, '#a892c0')]),
             cel=1.2, rim=0.6, cast=1.2, cast_on=wing_names + dress_names, details=ndet)
    hand_names = hand(fig, W, fa_, nh, wing_names + dress_names + ['narm'])

    # ---- l'épaulière d'or en lames, sur l'épaule proche ----
    pa_names = pauldron(fig)
    fig.pose(pa_names, UC)

    # ---- le cou et le col montant ourlé d'or (corrigé le 26/11 : l'axe du cou au milieu du buste, x ≈ 71,8, entre
    # les deux épaules ; la nuque remonte sous les cheveux, aucun vide derrière la mâchoire) ----
    neck = sm([(61.2, 40.2), (70.0, 39.6), (76.8, 41.6), (77.0, 46.6), (77.2, 51.0), (66.8, 51.4), (66.2, 47.8),
               (63.4, 44.0)], t=0.9)
    fig.part('neck', neck, SKIN, grad=(78, 44, 64, 50, [(0, SKIN.base), (1, SKIN.shadow)]), cel=1.0, rim=0.4, cast=0.8,
             details=[(sm([(61.6, 40.4), (70.0, 40.2), (76.8, 42.4), (76.4, 45.6), (73.0, 47.4), (68.8, 47.0), (66.6, 49.0),
                           (63.8, 44.4)]), SKIN.shadow, 0.6)])
    CI = [(65.0, 48.2), (68.6, 49.2), (73.0, 49.7), (76.6, 49.3), (78.8, 48.2)]
    CO = [(64.6, 52.5), (68.4, 53.5), (73.0, 53.9), (76.8, 53.5), (79.2, 52.3)]
    collar = sm([(64.8, 47.8)] + CI[1:-1] + [(79.0, 47.6), (79.8, 50.2), (79.2, 52.6)] + CO[::-1][1:-1] + [(64.4, 52.9), (64.0, 50.2)], t=0.9)
    cd = [(curve_band(CI, CO, -0.5, 0.2), GOLD.base, 1), (curve_band(CI, CO, -0.5, 0.06), GOLD.light, 0.95),
          (curve_band(CI, CO, 0.2, 0.32), GOLD.shadow, 0.55),
          (curve_band(CI, CO, 0.86, 1.4), GOLD.base, 1), (curve_band(CI, CO, 0.86, 0.94), GOLD.light, 0.8),
          (sm([(63.6, 48.0), (67.6, 49.4), (68.0, 54.2), (63.6, 53.4)]), IVORY.shadow, 0.55)]
    fig.part('collar', collar, IVORY, grad=(79.5, 48, 64, 53, [(0, IVORY.light), (0.6, IVORY.base), (1, IVORY.shadow)]),
             cel=0.9, rim=0.6, cast=1.1, details=cd)
    fig.pose(['neck', 'collar'], UC)

    # ---- la tête ----
    head_names = head(fig, P)
    fig.pose(head_names, HEAD)
    fig.pose(halo_names, mchain(HEAD, mT(0, P['halo'])))

    # ---- la trompette (devant la hanche ; aux lèvres, elle passe devant le visage) ----
    tr_names, _, _, _ = trumpet(fig, P2)

    # ---- le poing lointain, serré sur le tube (doigts devant, pouce par-dessus) ----
    fist_names = fist(fig, G, ut, vt, tr_names + ['farm', 'puff'] + dress_names)

    fig.ctx = dict(P=P, U=U, UC=UC, HEAD=HEAD, BODY=BODY, G=G, Lt=Lt, ut=ut, vt=vt, tang=tang,
                   bell=Lt(TLEN + 1.0, 0), mouth=Lt(0, 0), head=mapp(HEAD, (74, 34)), chest=mapp(TOR, (72, 62)),
                   waist=mapp(U, (72, 71)), hand=W, halo=mapp(mchain(HEAD, mT(0, P['halo'])), HALO_C),
                   MN=mchain(UC, MN), MF=mchain(UC, MF), curN=curN, featN=featN)
    if fx:
        for f_ in fx:
            f_(fig, fig.ctx)
    return fig


def xf_pt(o, a, p):
    r = rot(p, a)
    return (o[0] + r[0], o[1] + r[1])


# ---------------------------------------------------------------- l'auréole
HALO_C = (67.0, 13.4)


def halo(fig, P):
    """Un anneau d'or posé à plat au-dessus de la tête (vu un peu de dessus) : une seule forme percée."""
    cx, cy = HALO_C
    rx, ry = 13.4, 3.5
    outer = ellipse(cx, cy, rx, ry)
    inner = ellipse(cx + 0.2, cy - 0.15, rx - 2.4, ry - 1.25)
    ring = outer.hole(inner)
    g = P['glow']
    det = [(ellipse(cx, cy + 0.9, rx - 0.6, ry - 0.7).hole(ellipse(cx, cy - 0.3, rx - 1.0, ry - 0.6)), GOLD.shadow, 0.55),
           (ribbon([(cx - 9.0, cy - 2.6), (cx - 1.0, cy - 3.35), (cx + 7.6, cy - 2.85), (cx + 12.0, cy - 1.0)],
                   [0.1, 0.55, 0.6, 0.1]), GOLD.hi, 0.95),
           (ribbon([(cx - 6.0, cy + 2.5), (cx + 2.0, cy + 3.0), (cx + 9.0, cy + 2.3)], [0.1, 0.45, 0.1]), GOLD.light, 0.7)]
    if g > 0:
        det.append((ring, GOLD.hi, 0.55 * g))
    if P['aur'] > 0:
        # le repos (anim.signe) : l'anneau s'illumine doucement (sans changer son dégradé)
        det.append((ring, GOLD.hi, 0.85 * P['aur']))
    fig.part('halo', ring, GOLD, grad=(cx + rx, cy - ry, cx - rx, cy + ry, [(0, GOLD.hi if g > 0.5 else GOLD.light), (0.5, GOLD.base), (1, GOLD.shadow)]),
             cel=0.6, rim=0.5, cast=0, details=det)
    return ['halo']


# ---------------------------------------------------------------- les bottes
def boots(fig, P, BODY):
    names = []
    for name, pts, buck in (
            ('nboot', [(46.4, 116.2), (46.8, 112.0), (48.8, 109.6), (55.0, 109.4), (58.4, 111.0), (62.2, 113.0), (63.2, 116.2)], (57.4, 112.6)),
            ('fboot', [(70.2, 116.2), (70.6, 111.8), (73.0, 109.6), (79.8, 109.6), (83.6, 111.4), (87.2, 113.4), (88.0, 116.2)], (82.4, 112.6))):
        sh = sm(pts, sharp=(0, 6), t=0.9)
        x0_, x1_ = pts[0][0], pts[-1][0]
        det = [(sm([(x0_ - 1, 114.6), (x1_ + 1, 114.6), (x1_ + 1, 117), (x0_ - 1, 117)], sharp=(0, 1, 2, 3), t=0.2), LEATHER.deep, 1),
               (sm([(x0_ - 1, 114.6), (x1_ + 1, 114.6), (x1_ + 1, 115.2), (x0_ - 1, 115.2)], sharp=(0, 1, 2, 3), t=0.2), LEATHER.shadow, 1),
               # le cou-de-pied éclairé, une boucle d'or sur la bride
               (ellipse(buck[0] + 2.4, 111.0, 3.2, 1.0, -12), LEATHER.hi, 0.55),
               # la bride, de l'empeigne à la semelle (elle fait le tour du pied), sa boucle d'or
               (ribbon([(buck[0] - 1.6, buck[1] - 4.0), (buck[0], buck[1]), (buck[0] + 0.9, buck[1] + 3.0)], [1.2, 1.3, 1.2]), LEATHER.deep, 0.7),
               (rpoly([(buck[0] - 1.0, buck[1] - 1.1), (buck[0] + 1.1, buck[1] - 1.0), (buck[0] + 1.1, buck[1] + 1.1), (buck[0] - 1.0, buck[1] + 1.0)], 0.45), GOLD.base, 1),
               (rpoly([(buck[0] - 0.4, buck[1] - 0.5), (buck[0] + 0.5, buck[1] - 0.45), (buck[0] + 0.5, buck[1] + 0.5), (buck[0] - 0.4, buck[1] + 0.45)], 0.2), LEATHER.deep, 0.8),
               (ellipse(buck[0] + 0.5, buck[1] - 0.8, 0.45, 0.25), GOLD.hi, 0.9)]
        fig.part(name, sh, LEATHER, grad=(x1_, 109, x0_, 116, [(0, LEATHER.light), (0.5, LEATHER.base), (1, LEATHER.shadow)]),
                 cel=1.0, rim=0.6, cast=0.8, details=det)
        names.append(name)
    fig.pose(names, BODY)
    return names


# ---------------------------------------------------------------- la robe
# les pétales du bas de la surjupe : (début, fin, profondeur du bas) ; les creux entre deux pétales
PETALS = [(47.2, 52.2, 101.0), (52.2, 62.0, 104.0), (62.0, 72.2, 105.2), (72.2, 82.0, 105.0), (82.0, 90.0, 103.0)]
CUSP_Y = {47.2: 98.6, 52.2: 98.6, 62.0: 99.4, 72.2: 99.8, 82.0: 99.2, 90.0: 99.2}


def petal_edge(hm=0.0):
    """Le bas découpé de la surjupe, de gauche à droite : des pétales arrondis comme des plumes (sommets vifs entre
    eux) ; rend les points et les indices des creux."""
    pts, cusps = [], []
    for i, (a, b, yb) in enumerate(PETALS):
        ya, yb2 = CUSP_Y[a], CUSP_Y[b]
        sway = hm * (0.6 + 0.2 * i)
        for k in range(9):
            if k == 0 and i > 0:
                continue
            u = k / 8
            x = a + (b - a) * u
            base = ya + (yb2 - ya) * u
            dep = (yb - (ya + yb2) / 2) * (math.sin(math.pi * u) ** 0.8)
            # le bout du pétale, un peu en ogive (comme une plume)
            dep *= 1 + 0.06 * math.cos(math.pi * (u - 0.5) * 2)
            if k == 0:
                cusps.append(len(pts))
            pts.append((x + sway * math.sin(math.pi * u), base + dep))
            if k == 8:
                cusps.append(len(pts) - 1)
    return pts, sorted(set(cusps))


def dress(fig, P, ROBE, TOR):
    hm = P['hem']
    names = []
    # ---- la sous-jupe (ivoire, ourlet d'or), d'un côté à l'autre ----
    skirt = sm([(57.8, 71.0), (86.4, 71.0), (88.2, 84.0), (89.8, 97.0), (90.6 + 0.5 * hm, 105.8), (91.2 + 0.7 * hm, 110.6),
                (82.0, 111.2 + 0.2 * hm), (68.0, 111.4 - 0.2 * hm), (54.0, 111.0 + 0.2 * hm), (44.4 - 0.6 * hm, 110.4),
                (44.8 - 0.5 * hm, 105.6), (47.4, 96.4), (52.2, 85.0)], sharp=(5, 9), t=0.9)
    hem_in = [(42, 108.4), (56, 109.0), (68, 109.2), (80, 109.0), (93, 108.4)]
    sd = [(sm([(43.6, 111.0), (47.0, 97.0), (51.0, 100.0), (50.6, 111.4)]), IVORY.shadow, 0.6),
          (ribbon([(57.0, 101.0), (56.6, 105.0), (56.0, 109.6)], [0.2, 1.1, 0.4]), IVORY.shadow, 0.45),
          (ribbon([(67.0, 103.0), (66.8, 106.0), (66.6, 109.6)], [0.2, 0.9, 0.3]), IVORY.shadow, 0.35),
          (ribbon([(77.4, 103.0), (77.8, 106.0), (78.2, 109.6)], [0.2, 0.8, 0.3]), IVORY.shadow, 0.3),
          (ribbon([(85.6, 101.0), (86.8, 105.0), (87.4, 109.6)], [0.2, 0.9, 0.3]), IVORY.shadow, 0.3),
          (sm(hem_in + [(93, 118), (42, 118)], sharp=(4, 5, 6), t=0.7), GOLD.base, 1),
          (ribbon([add(p, (0, 0.45)) for p in hem_in], [0.2, 0.6, 0.7, 0.6, 0.2]), GOLD.light, 0.95),
          (sm([(42, 110.6), (93, 110.4), (93, 118), (42, 118)], sharp=(0, 1, 2, 3), t=0.3), GOLD.shadow, 0.6)]
    fig.part('skirt', skirt, IVORY, grad=(92, 96, 44, 110, [(0, '#f8f2f2'), (0.55, '#e8dee6'), (1, '#cfc2da')]),
             cel=1.2, rim=0.6, cast=1.0, details=sd)
    names.append('skirt')

    # ---- la robe : le buste et la surjupe d'un seul tenant, le bas en pétales ----
    edge, cusps = petal_edge(hm)
    left_side = [(48.2 - 0.3 * hm, 97.2), (51.6, 88.0), (55.0, 79.0), (57.4, 71.6), (56.8, 66.4), (55.0, 61.4),
                 (54.8, 56.0), (57.6, 52.6), (64.8, 50.4)]
    right_side = [(78.8, 50.0), (84.0, 51.4), (86.8, 54.2), (87.2, 59.4), (86.4, 66.2), (86.6, 71.6), (88.0, 82.0),
                  (89.4, 92.0), (90.0 + 0.3 * hm, 98.4)]
    pts = left_side + right_side + edge[::-1]
    n0 = len(left_side) + len(right_side)
    sharp = [n0 - 1 + 1 + (len(edge) - 1 - c) for c in cusps]
    body = sm(pts, sharp=[0, n0 - 1] + sharp, t=0.9)
    dd = []
    # le côté proche (à gauche) dans l'ombre lilas, l'ivoire éclairé vers la droite
    dd += [(sm([(46.6, 100), (51.0, 88.0), (55.0, 78.6), (57.6, 71.4), (61.8, 72.4), (58.8, 82.0), (55.8, 92.0), (54.0, 104)]), IVORY.shadow, 0.55),
           (sm([(53.4, 104), (56.4, 92.0), (59.6, 82.0), (62.8, 72.6), (65.6, 73.0), (63.0, 84.0), (60.8, 94.0), (60.0, 104)]), IVORY.shadow, 0.28),
           (sm([(53.6, 52.0), (60.6, 50.6), (61.4, 57.0), (59.6, 66.0), (58.6, 72.0), (54.0, 70.0)]), IVORY.shadow, 0.5)]
    # deux plis doux qui tombent de la ceinture (jamais des rayures) ; le genou lointain tend l'étoffe
    dd += [(ribbon([(67.4, 74.0), (66.8, 86.0), (66.0, 101.0)], [0.2, 1.3, 0.5]), IVORY.shadow, 0.45),
           (ribbon([(68.6, 74.6), (68.2, 87.0), (67.8, 100.0)], [0.1, 0.6, 0.2]), IVORY.hi, 0.8),
           (ribbon([(77.8, 74.0), (78.4, 86.0), (79.0, 100.0)], [0.2, 1.0, 0.4]), IVORY.shadow, 0.32),
           (ellipse(83.6, 88.0, 2.4, 6.0, -8), IVORY.hi, 0.55)]
    # la poitrine : une ombre douce dessous, un éclat sur la lumière (pudique, sans détail)
    dd += [(ribbon([(62.0, 64.2), (67.0, 65.6), (72.6, 65.0)], [0.2, 1.2, 0.2]), IVORY.shadow, 0.45),
           (ribbon([(75.0, 65.0), (80.0, 65.4), (84.4, 64.0)], [0.2, 1.0, 0.2]), IVORY.shadow, 0.38),
           (ellipse(80.6, 60.4, 3.0, 2.0, -15), IVORY.hi, 0.85),
           (ellipse(68.0, 60.6, 2.6, 1.8, -10), IVORY.hi, 0.4)]
    # l'empiècement d'or en V, décalé à droite (trois quarts) : de l'épaule proche à la broche, puis vers l'épaule
    # lointaine (deux bandes d'or bordées d'éclat)
    VL = [(58.0, 52.4), (63.4, 54.0), (69.0, 56.6), (74.6, 59.0)]
    VR = [(74.6, 59.0), (79.0, 57.2), (83.0, 54.8), (86.6, 53.6)]
    for V, wv in ((VL, 1.5), (VR, 1.5)):
        dd += [(ribbon([add(p, (0, 0.15)) for p in V], [wv * 0.7, wv, wv, wv * 0.7]), GOLD.base, 1),
               (ribbon([add(p, (0.1, -0.35)) for p in V], [0.2, 0.5, 0.5, 0.3]), GOLD.hi, 0.85),
               (ribbon([add(p, (-0.1, 0.75)) for p in V], [0.2, 0.4, 0.4, 0.2]), GOLD.shadow, 0.7)]
    # l'ombre sous le V (le tissu de l'empiècement est un peu en relief)
    dd += [(ribbon([add(p, (-0.2, 1.6)) for p in VL], [0.1, 0.9, 0.9, 0.1]), IVORY.shadow, 0.35)]
    # le bas des pétales bordé d'or (une bande le long du bord découpé, peinte dans la robe)
    up = [(x, y - 1.25) for x, y in edge]
    dd += [(ribbon(edge, [2.6] * len(edge)), GOLD.base, 1),
           (ribbon([(x + 0.1, y - 0.95) for x, y in edge], [0.55] * len(edge)), GOLD.light, 0.95),
           (ribbon([(x, y + 0.55) for x, y in edge], [0.8] * len(edge)), GOLD.shadow, 0.7)]
    del up
    # chaque pétale se détache comme une plume : un pli doux qui remonte de chaque creux, le pétale un peu bombé
    for a, b, yb in PETALS[1:]:
        cy_ = CUSP_Y[a]
        dd += [(ribbon([(a + 0.3, cy_ - 0.2), (a + 0.1, cy_ - 3.0), (a - 0.3, cy_ - 6.4)], [0.9, 0.6, 0.1]), IVORY.shadow, 0.55)]
    for a, b, yb in PETALS:
        m = (a + b) / 2
        dd += [(ellipse(m + 1.4, CUSP_Y[a] - 2.4, (b - a) * 0.2, 1.2, -8), IVORY.hi, 0.5)]
    # la ceinture d'or, plus basse devant (elle fait le tour de la taille)
    belt_top = [(54, 69.0), (62, 69.6), (70, 70.2), (78, 70.0), (88, 69.2)]
    belt_bot = [(54, 72.0), (62, 72.6), (70, 73.2), (78, 73.0), (88, 72.2)]
    dd += [(sm(belt_top + belt_bot[::-1], sharp=(0, 4, 5, 9), t=0.8), GOLD.base, 1),
           (ribbon([add(p, (0, 0.55)) for p in belt_top], [0.2, 0.7, 0.8, 0.7, 0.2]), GOLD.light, 0.95),
           (ribbon([add(p, (0, -0.45)) for p in belt_bot], [0.2, 0.6, 0.7, 0.6, 0.2]), GOLD.shadow, 0.9),
           (ribbon([add(p, (0, 1.0)) for p in belt_bot], [0.1, 1.0, 1.2, 1.0, 0.1]), IVORY.shadow, 0.4)]
    fig.part('dress', body, IVORY, grad=(90, 54, 50, 100, [(0, IVORY.light), (0.55, IVORY.base), (1, '#d8cce0')]),
             cel=1.4, rim=0.7, cast=1.2, details=dd, occl=(IVORY.deep, 0.1, 3.0))
    names.append('dress')
    # ---- la broche turquoise de l'empiècement, la boucle de la ceinture ----
    bx, by = 74.6, 59.2
    brooch = sm([(bx - 1.9, by - 0.2), (bx, by - 2.0), (bx + 1.9, by - 0.2), (bx, by + 2.4)], t=0.9)
    fig.part('brooch', brooch, GOLD, cel=0.5, rim=0.4, cast=0.7, cast_on=['dress'],
             details=[(ellipse(bx, by + 0.05, 1.15, 1.45), TURQ.shadow, 1),
                      (ellipse(bx + 0.05, by - 0.05, 0.85, 1.1), ('rad', bx + 0.4, by - 0.5, 1.3, 1.3, [(0, TURQ.hi), (0.5, TURQ.light), (1, TURQ.base)]), 1),
                      (ellipse(bx + 0.35, by - 0.5, 0.28, 0.3), '#ffffff', 0.9)])
    buckle = rpoly([(72.6, 69.2), (77.8, 69.0), (78.0, 73.8), (72.6, 74.0)], 1.3)
    fig.part('buckle', buckle, GOLD, cel=0.6, rim=0.5, cast=0.8, cast_on=['dress'],
             details=[(ellipse(75.3, 71.5, 1.55, 1.5), TURQ.shadow, 1),
                      (ellipse(75.4, 71.4, 1.15, 1.1), ('rad', 75.8, 70.9, 1.3, 1.3, [(0, TURQ.hi), (0.5, TURQ.light), (1, TURQ.base)]), 1),
                      (ellipse(75.8, 70.9, 0.35, 0.3), '#ffffff', 0.9)])
    names += ['brooch', 'buckle']
    fig.pose(['skirt'], ROBE)
    fig.pose(['dress'], ROBE)
    fig.pose(['brooch', 'buckle'], ROBE)
    return names


# ---------------------------------------------------------------- l'épaulière
def pauldron(fig):
    """L'épaulière d'or en lames, sur l'épaule proche : une calotte, deux lames en croissant dessous."""
    lame2 = sm([(45.4, 62.0), (49.8, 60.2), (55.4, 60.4), (59.0, 59.4), (58.8, 62.0), (56.0, 64.6), (50.6, 65.4), (46.6, 64.6)], sharp=(0,))
    lame1 = sm([(45.8, 58.0), (50.6, 56.0), (56.6, 56.2), (60.4, 54.8), (60.8, 57.8), (58.0, 60.6), (51.6, 61.6), (46.8, 61.0)], sharp=(0,))
    dome = sm([(47.6, 55.4), (50.8, 51.2), (56.4, 49.2), (61.6, 50.2), (63.6, 53.0), (61.4, 56.4), (54.4, 57.8), (48.6, 58.0)])
    names = []
    for nm, sh, cst in (('lame2', lame2, 1.1), ('lame1', lame1, 1.1), ('dome', dome, 1.2)):
        det = []
        if nm == 'dome':
            det = [(sm([(49.6, 55.2), (52.4, 52.0), (56.6, 50.4), (61.0, 51.0), (56.6, 52.4), (52.6, 54.8)]), GOLD.light, 0.85),
                   (ribbon([(51.6, 54.4), (55.6, 51.4), (60.4, 51.0)], [0.2, 0.9, 0.2]), GOLD.glint, 0.95),
                   (ellipse(58.4, 52.0, 1.3, 0.6, -15), '#ffffff', 0.8)]
        else:
            yb = 58.6 if nm == 'lame1' else 62.6
            det = [(ribbon([(47.4, yb), (52.0, yb - 1.2), (57.6, yb - 1.0), (60.0, yb - 2.4)], [0.1, 0.8, 0.7, 0.1]), GOLD.hi, 0.8)]
        fig.part(nm, sh, GOLD, cel=1.0, rim=0.7, cast=cst, details=det)
        names.append(nm)
    return names


# ---------------------------------------------------------------- les mains
def hand(fig, W, fa, nh, bg):
    """La main proche, ouverte, paume vers l'avant : la paume, trois doigts un peu écartés vers le bas, le pouce écarté
    vers l'extérieur (à gauche de l'image)."""
    a = math.radians(fa)
    u = (math.cos(a), math.sin(a))
    o = (-u[1], u[0])
    if o[0] > 0:
        o = (-o[0], -o[1])

    def L(x, y):
        return (W[0] + u[0] * x + o[0] * y, W[1] + u[1] * x + o[1] * y)
    palm = sm([L(-0.8, -2.8), L(2.0, -3.5), L(5.8, -3.3), L(7.2, -1.1), L(7.0, 2.0), L(4.8, 3.3), L(1.2, 3.0), L(-0.6, 2.4)], t=0.9)
    fig.part('palm', palm, SKIN, cel=0.8, rim=0.45, cast=0.8, cast_on=bg,
             details=[(sm([L(1.6, -2.0), L(5.0, -2.2), L(5.4, 0.4), L(2.4, 0.6)]), SKIN.hi, 0.35),
                      (ribbon([L(1.6, 1.6), L(3.6, 0.5), L(5.8, 0.3)], [0.1, 0.5, 0.1]), SKIN.shadow, 0.45),
                      (ribbon([L(2.2, -1.6), L(4.6, -1.0), L(6.2, -1.4)], [0.1, 0.4, 0.1]), SKIN.shadow, 0.3)])
    names = ['palm']
    sp = 1 + 0.8 * nh
    for i, (y0, ang, ln, w) in enumerate(((-2.1, -6 * sp, 4.0, 2.2), (-0.1, 1 * sp, 4.8, 2.25), (1.9, 7 * sp, 4.3, 2.1))):
        base = L(6.0, y0)
        dirv = rot(u, ang if o[0] < 0 and u[1] > 0 else -ang)
        mid = add(base, dirv, ln * 0.55)
        tip = add(base, dirv, ln)
        sh = limb([base, mid, tip], [w, w * 0.96, w * 0.84])
        fig.part('fg%d' % i, sh, SKIN, cel=0.5, rim=0.35, cast=0.55, cast_on=['palm'] + ['fg%d' % j for j in range(i)] + bg)
        names.append('fg%d' % i)
    fig.part('thumb', limb([L(1.0, 2.4), L(2.8, 4.1), L(4.6, 4.8)], [2.6, 2.2, 1.8]), SKIN, cel=0.5, rim=0.35, cast=0.6,
             cast_on=['palm'] + bg)
    names.append('thumb')
    return names


def fist(fig, G, u, v, bg):
    """Le poing lointain, serré sur le tube : le dos des doigts devant le tube (quatre rouleaux de tailles inégales),
    le pouce couché par-dessus, le long du tube. Repère : u le long du tube (vers le pavillon), v en travers."""
    def L(x, y):
        return (G[0] + u[0] * x + v[0] * y, G[1] + u[1] * x + v[1] * y)
    # côté paume : v < 0 (à gauche du tube, vers le corps)
    body = sm([L(-4.0, -3.6), L(-1.0, -4.4), L(2.6, -3.8), L(4.2, -1.6), L(4.0, 1.8), L(2.2, 3.0), L(-1.6, 3.0),
               L(-4.4, 1.6), L(-5.0, -1.4)], t=0.95)
    det = [(ellipse(*L(1.4, -2.0), 1.6, 2.4, ang_of(u)), SKIN.hi, 0.3)]
    for x0, x1 in ((-3.8, -1.9), (-1.9, 0.1), (0.1, 2.0), (2.0, 3.8)):
        det += [(ribbon([L(x1, -3.6), L(x1 + 0.1, -0.6), L(x1 - 0.1, 2.4)], [0.1, 0.5, 0.1]), SKIN.shadow, 0.6),
                (ellipse(*L((x0 + x1) / 2, 1.2), 0.5, 0.75, ang_of(u)), SKIN.hi, 0.35)]
    fig.part('fist', body, SKIN, grad=(*L(3, 3), *L(-4, -4), [(0, SKIN.light), (0.5, SKIN.base), (1, SKIN.shadow)]),
             cel=0.8, rim=0.5, cast=0.8, cast_on=bg, details=det)
    thumb = limb([L(-3.4, 2.2), L(-0.4, 2.9), L(2.6, 2.2)], [2.4, 2.1, 1.7])
    fig.part('fthumb', thumb, SKIN, cel=0.45, rim=0.4, cast=0.6, cast_on=['fist'] + bg)
    return ['fist', 'fthumb']


# ---------------------------------------------------------------- la tête
def rim_band(shape, dx, dy, cut):
    """Le liseré de lumière d'une forme (elle-même moins sa copie décalée de (-dx, -dy)), sauf dans le polygone cut."""
    from shapely.geometry import Polygon
    a = Polygon(poly(shape)).buffer(0)
    b = Polygon([(x - dx, y - dy) for x, y in poly(shape)]).buffer(0)
    g = a.difference(b).difference(Polygon(cut))
    return [from_poly(list(q.exterior.coords)[:-1]) for q in getattr(g, 'geoms', [g]) if q.geom_type == 'Polygon' and q.area > 0.05]


def head(fig, P):
    """Le chignon, le visage sévère, les cheveux tirés (tresse en couronne), l'oreille et sa goutte de turquoise ;
    rend la liste des morceaux (posés avec la tête).
    Corrigé le 26/11 (avis du propriétaire : « on dirait une perruque ») : la chevelure épouse le crâne (une calotte
    fine qui suit la sphère de la tête, la tempe raccordée au contour du visage, plus de bloc qui pend derrière
    l'oreille) ; le visage est reconstruit avec ../visage.py (yeux, nez, bouche aux places de placer(FACE_BOX))."""
    names = []

    def part(name, *a, **k):
        names.append(name)
        return fig.part(name, *a, **k)

    V = placer(FACE_BOX)
    # la ligne du front (racine des cheveux), de la tempe lointaine jusqu'au-dessus de l'oreille : elle suit la sphère
    HL = [(81.7, 31.2), (80.9, 28.6), (78.8, 27.1), (75.6, 26.6), (72.0, 27.0), (68.8, 28.0), (66.4, 29.8), (65.0, 32.0),
          (64.6, 34.2)]
    (nx, ny, nw), (fx_, fy, fw) = V['oeil_proche'], V['oeil_fond']
    nw, fw = nw * 1.15, fw * 1.15                 # des yeux un peu plus grands (chibi), mêmes proportions
    nzx, nzy = V['nez']
    mx, my, mw = V['bouche']

    # ---- le gros chignon rond, derrière (la tresse s'y enroule), collé à l'arrière du crâne ----
    bcx, bcy = 56.4, 30.2
    bun = ellipse(bcx, bcy, 6.8, 7.2, -10)
    bd = []
    spi = [(bcx + 6.0 * (1 - 0.8 * t) * math.cos(math.radians(-50 + 470 * t)),
            bcy + 6.2 * (1 - 0.8 * t) * math.sin(math.radians(-50 + 470 * t))) for t in [k / 40 for k in range(41)]]
    bd += [(taper(spi, 1.25, 0.2), HAIR.shadow, 0.7),
           (taper([(x + 0.5, y - 0.8) for x, y in spi[2:-6]], 0.85, 0.15), HAIR.light, 0.7)]
    for k in range(3, 36, 3):
        p_ = spi[k]
        tg = norm(sub(spi[k + 1], spi[k - 1]))
        c = add(p_, (-tg[1], tg[0]), -1.3)
        bd += [(ellipse(c[0], c[1], 1.25 * (1 - k / 60), 0.5, ang_of(tg) + 40), HAIR.shadow, 0.35)]
    bd += [(ellipse(bcx - 0.6, bcy - 4.6, 2.0, 1.0, -25), HAIR.hi, 0.5)]
    part('bun', bun, HAIR, grad=(bcx + 6, bcy - 7, bcx - 6, bcy + 7, [(0, HAIR.light), (0.5, HAIR.base), (1, HAIR.shadow)]),
         cel=1.2, rim=0.6, cast=1.0, details=bd)

    # ---- le visage : joue proche (gauche) bien ronde, côté droit plus plat, menton sur la médiane ----
    chin = V['menton']
    face = sm([(64.2, 28.0), (67.4, 25.2), (72.4, 24.0), (77.4, 24.4), (80.6, 26.4), (81.8, 30.0), (82.0, 34.5),
               (81.6, 38.6), (80.6, 42.2), (78.8, 45.0), (76.6, 46.5), (chin[0], 47.05), (72.0, 46.5), (68.6, 44.5),
               (65.6, 41.2), (63.6, 36.8), (63.2, 32.0)], t=0.9)
    fd = []
    blink = P['blink'] > 0.5
    ch = P['cheek']
    # la racine des cheveux : sous la ligne du front, une ombre très douce (deux voiles qui s'éteignent) et un voile
    # doré à la racine : les cheveux naissent de la peau, aucun trait ni marche entre les deux
    wl = [0.2] + [1.0] * (len(HL) - 2) + [0.2]
    fd += [(ribbon([(x - 0.2, y + 0.9) for x, y in HL], [w * 1.6 for w in wl]), SKIN.shadow, 0.22),
           (ribbon([(x - 0.1, y + 0.45) for x, y in HL], [w * 0.9 for w in wl]), SKIN.shadow, 0.3),
           (ribbon([(x, y + 0.1) for x, y in HL], [w * 0.55 for w in wl]), HAIR.shadow, 0.45)]
    # les plans du visage : la joue proche et la tempe dans une ombre douce, le plan de face éclairé
    fd += [(sm([(63.8, 33.0), (65.2, 38.8), (68.2, 43.2), (72.0, 45.9), (75.0, 46.9), (71.6, 46.8), (67.4, 44.4),
                (64.4, 40.0)]), SKIN.shadow, 0.55),
           (sm([(78.4, 28.0), (81.2, 28.8), (81.8, 32.0), (80.8, 32.6), (79.2, 30.2)]), SKIN.hi, 0.45),
           (ellipse(69.0 - 0.2 * ch, 40.4, 2.5 + 0.5 * ch, 1.5 + 0.4 * ch, 8), '#ec8a7c', 0.24 + 0.12 * ch),   # la pommette
           (ellipse(80.4 + 0.2 * ch, 40.2, 0.9 + 0.3 * ch, 0.8 + 0.2 * ch), '#ec8a7c', 0.2 + 0.1 * ch)]
    # l'ombre sous le menton (portée par la mâchoire sur le cou : peinte en bas du visage)
    fd += [(sm([(70.6, 45.6), (chin[0], 46.6), (78.4, 45.4), (80.4, 43.0), (78.8, 45.9), (chin[0], 47.3), (70.8, 46.6)]), SKIN.shadow, 0.45)]
    # la paupière lourde : un pli de peau sous le sourcil (demi-teinte), qui tombe vers le nez (l'air sévère)
    n0, n1 = nx - nw / 2, nx + nw / 2
    f0, f1 = fx_ - fw / 2, fx_ + fw / 2
    fd += [(sm([(n0 - 0.2, ny - 0.8), (n0 + 1.1, ny - 1.7), (n1 - 1.0, ny - 1.6), (n1 + 0.4, ny - 0.5), (n1 - 0.1, ny - 0.15),
                (n1 - 1.1, ny - 0.95), (n0 + 1.2, ny - 1.0), (n0 + 0.2, ny - 0.15)], t=0.85), SKIN.shadow, 0.42),
           (sm([(f0 - 0.3, ny - 0.4), (f0 + 0.8, ny - 1.4), (f1 - 0.9, ny - 1.75), (f1 + 0.2, ny - 0.95), (f1 - 0.2, ny - 0.65),
                (f1 - 1.0, ny - 1.1), (f0 + 0.9, ny - 0.8), (f0 + 0.2, ny + 0.1)], t=0.85), SKIN.shadow, 0.36)]
    # les sourcils blonds foncés en V : le bout intérieur (vers le nez) plus bas et plus épais
    fd += [(sm([(n0 - 0.8, ny - 2.65), (n0 + 1.2, ny - 3.35), (n1 - 0.6, ny - 2.85), (n1 + 0.6, ny - 1.75),
                (n1 + 0.3, ny - 1.15), (n1 - 0.9, ny - 2.05), (n0 + 1.1, ny - 2.5), (n0 - 0.5, ny - 2.05)],
               sharp=(0, 3), t=0.85), BROW, 0.95),
           (sm([(f0 - 0.5, ny - 1.25), (f0 + 0.9, ny - 2.75), (f1 - 0.4, ny - 3.45), (f1 + 0.6, ny - 3.25),
                (f1 + 0.45, ny - 2.65), (f1 - 0.5, ny - 2.65), (f0 + 1.0, ny - 1.95), (f0 - 0.15, ny - 0.75)],
               sharp=(0, 3), t=0.85), BROW, 0.95)]
    # les yeux : l'amande (le haut aplati et incliné vers le nez : paupière lourde), l'iris turquoise coupé par les
    # paupières, la pupille, l'éclat ; un trait de cils épais en haut, fin en bas ; l'œil du fond de même forme, sur
    # la même ligne, à peine plus étroit. Le regard part vers la droite (l'iris un peu décalé dans les deux yeux).
    hn, hf = 1.0, 0.95
    eyes = (
        (sm([(n0, ny + 0.1), (n0 + nw * 0.24, ny - hn), (n1 - nw * 0.24, ny - hn * 0.75), (n1, ny + 0.1),
             (n1 - nw * 0.24, ny + hn * 1.05), (n0 + nw * 0.26, ny + hn * 1.05)], sharp=(0, 3), t=0.9),
         (nx + 0.3, ny + 0.1), 1.05, 1.0),
        (sm([(f0, ny + 0.1), (f0 + fw * 0.24, ny - hf * 0.75), (f1 - fw * 0.24, ny - hf), (f1, ny + 0.05),
             (f1 - fw * 0.24, ny + hf * 1.05), (f0 + fw * 0.26, ny + hf * 1.05)], sharp=(0, 3), t=0.9),
         (fx_ + 0.25, ny + 0.1), 1.0, 0.86),
    )
    meas = []
    for almond, (ix, iy), ir, sx in eyes:
        b0, b1, b2, b3 = almond.bbox()
        meas.append(((b0 + b2) / 2, (b1 + b3) / 2, b2 - b0))
        p0, p1, p2, p3 = (almond_pt(almond, i) for i in range(4))
        p4, p5 = almond_pt(almond, 4), almond_pt(almond, 5)
        if blink:
            fd += [(almond.scale(1.04, 1.1, ix, iy), SKIN.base, 1),
                   (ribbon([p0, lerp(p5, p4, 0.5), p3], [0.3, 0.85, 0.25]).move(0, -0.3), LASH, 0.95)]
            continue
        # Tour 2 de l'avis (26/11 soir) : « les yeux blancs total sans pupille » : plus d'iris ni de pupille, l'œil
        # entier est une lumière blanche divine (cœur blanc pur, bord à peine doré), avec un léger rayonnement doux
        # sur la peau autour (aplats dégradés, aucun flou) ; la forme de l'amande, les cils et le reste du visage
        # restent les mêmes.
        cx_, cy_ = (b0 + b2) / 2, (b1 + b3) / 2
        fd += [(almond.scale(1 + 0.11 * k, 1 + 0.22 * k, cx_, cy_), '#fff2d0', 0.09) for k in (4, 3, 2, 1)]
        fd += [
               (almond, ('rad', cx_ + 0.2, cy_ - 0.1, (b2 - b0) * 0.6, (b2 - b0) * 0.6,
                         [(0, '#ffffff'), (0.55, '#fffdf6'), (1, '#f4e6c4')]), 1),
               # l'ombre de la paupière du haut, très légère (l'œil garde son volume sans perdre sa lumière)
               (sm([p0, p1, p2, p3, lerp(p3, (ix, iy), 0.2), lerp(p2, (ix, iy + 0.6), 0.25), lerp(p1, (ix, iy + 0.6), 0.25)], t=0.8), '#e8cfa0', 0.35)]
        # les cils : épais sur le haut, plus marqués au coin extérieur (à gauche pour l'œil proche, à droite pour l'autre)
        fd += [(ribbon([add(p0, (-0.45, -0.15)), p1, p2, add(p3, (0.2, 0.05))], [0.35, 0.72, 0.55, 0.15] if p0[0] < 75 else [0.15, 0.5, 0.62, 0.38]), LASH, 0.95),
               (ribbon([p0, p5, p4, p3], [0.1, 0.3, 0.26, 0.1]), '#7a3a4a', 0.6)]
    if blink:
        meas = [((e[0].bbox()[0] + e[0].bbox()[2]) / 2, (e[0].bbox()[1] + e[0].bbox()[3]) / 2, e[0].bbox()[2] - e[0].bbox()[0]) for e in eyes]
    # le nez discret, SUR la médiane entre les deux yeux : l'arête éclairée, le flanc proche dans une ombre douce, un
    # petit bout arrondi, l'ombre et les narines dessous (rien ne dépasse du contour)
    fd += [(sm([(nzx - 1.0, ny + 0.9), (nzx - 0.45, nzy - 1.2), (nzx - 0.1, nzy - 0.1), (nzx - 1.0, nzy + 0.35),
                (nzx - 1.5, nzy - 0.3)], t=0.9), SKIN.shadow, 0.32),
           (ribbon([(nzx - 0.2, ny + 0.3), (nzx + 0.05, nzy - 1.6), (nzx + 0.3, nzy - 0.5)], [0.1, 0.4, 0.35]), SKIN.hi, 0.7),
           (ellipse(nzx + 0.25, nzy - 0.35, 0.5, 0.35), SKIN.hi, 0.55),
           (ellipse(nzx, nzy + 0.35, 1.05, 0.32), SKIN.shadow, 0.5),
           (ellipse(nzx - 0.55, nzy + 0.2, 0.32, 0.18, 15), SKIN.deep, 0.5),
           (ellipse(nzx + 0.6, nzy + 0.2, 0.26, 0.15, -15), SKIN.deep, 0.4)]
    # la bouche serrée, centrée sous le nez : lèvre du haut rouge sombre, lèvre du bas rose, coins un peu tombants
    a0, a1 = mx - mw / 2, mx + mw / 2
    if ch > 0.3:
        # elle souffle dans l'embouchure : lèvres pincées en avant
        fd += [(ellipse(mx, my + 0.05, 1.35, 0.95), LIPS[1], 1), (ellipse(mx + 0.15, my, 0.7, 0.42), LIPS[0], 1)]
    else:
        fd += [(sm([(a0, my + 0.05), (mx - 0.9, my - 0.5), (mx, my - 0.35), (mx + 0.9, my - 0.5), (a1, my + 0.05),
                    (mx + 0.9, my + 0.25), (mx - 0.9, my + 0.25)], sharp=(0, 4), t=0.85), LIPS[1], 1),
               (ribbon([(a0 - 0.1, my + 0.12), (mx - 0.7, my + 0.2), (mx + 0.7, my + 0.2), (a1 + 0.1, my + 0.12)],
                       [0.1, 0.4, 0.4, 0.1]), LIPS[0], 0.95),
               (sm([(mx - 1.15, my + 0.42), (mx, my + 0.5), (mx + 1.15, my + 0.42), (mx + 0.8, my + 1.25), (mx, my + 1.5),
                    (mx - 0.8, my + 1.25)], t=0.9), LIPS[2], 0.95),
               (ellipse(mx + 0.2, my + 0.9, 0.6, 0.22, -4), '#f4a0a0', 0.8),
               (ribbon([(a0 - 0.35, my - 0.05), (a0 + 0.05, my + 0.6)], [0.1, 0.3]), SKIN.deep, 0.35),
               (ribbon([(a1 + 0.35, my - 0.05), (a1 - 0.05, my + 0.6)], [0.1, 0.25]), SKIN.deep, 0.3),
               (ribbon([(mx - 1.1, my + 2.6), (mx, my + 2.85), (mx + 1.1, my + 2.6)], [0.1, 0.4, 0.1]), SKIN.shadow, 0.3)]
    part('face', face, SKIN, grad=(83, 27, 64, 45, [(0, SKIN.light), (0.55, SKIN.base), (1, SKIN.shadow)]),
         cel=1.1, rim=0.5, cast=1.0, details=fd)
    fig.face = {'oeil_proche': meas[0], 'oeil_fond': meas[1], 'nez': (nzx, nzy), 'bouche': (mx, my, mw)}

    # ---- les cheveux tirés en arrière : UNE calotte fine qui épouse le crâne (dessus, tempe, derrière l'oreille,
    # nuque). Devant : la ligne du front suit la sphère de la tête, la tempe se raccorde au contour du visage (aucun
    # vide entre les cheveux et la peau) ; derrière l'oreille, les cheveux remontent vers le chignon ----
    hair = sm(HL + [(63.9, 38.0), (63.6, 41.0), (62.4, 43.0), (60.6, 43.2), (59.0, 41.0),
               (58.0, 36.6), (58.1, 31.4), (59.6, 26.4), (62.8, 22.4), (67.4, 20.0), (72.8, 19.4), (77.6, 20.6),
               (80.7, 23.0), (82.1, 26.0), (82.2, 28.8)], sharp=(0, 12), t=0.9)
    hd = []
    # la nuque et l'arrière du crâne dans l'ombre (la lumière vient d'en haut à droite)
    hd += [(sm([(57.6, 30.0), (59.6, 33.6), (62.2, 37.6), (64.2, 41.4), (62.6, 44.0), (59.6, 43.6), (57.4, 38.0)]), HAIR.deep, 0.32),
           (sm([(57.4, 27.0), (59.0, 25.6), (60.2, 30.2), (61.6, 36.4), (59.2, 38.6), (57.4, 34.0)]), HAIR.shadow, 0.35)]
    # le reflet qui suit la courbe du crâne, entre le front et la tresse
    hd += [(ribbon([(80.6, 26.6), (77.0, 24.6), (72.0, 24.2), (67.0, 25.2), (63.4, 27.6)], [0.2, 1.1, 1.3, 1.0, 0.2]), HAIR.light, 0.6),
           (ribbon([(79.8, 26.2), (76.4, 24.4), (72.6, 24.0)], [0.1, 0.45, 0.1]), HAIR.hi, 0.7)]
    # les mèches peignées en arrière : elles naissent de la ligne du front et filent vers le chignon (creux doux,
    # jamais de rayures : quelques courbes qui s'effilent)
    for pts, w, op in (([(78.6, 27.4), (73.6, 25.8), (67.6, 26.4), (62.6, 29.0), (59.4, 31.4)], 0.55, 0.45),
                       ([(73.4, 27.4), (69.0, 27.8), (64.6, 30.0), (61.0, 33.0)], 0.55, 0.45),
                       ([(67.6, 29.0), (65.0, 31.0), (62.6, 34.6), (61.2, 37.2)], 0.5, 0.4)):
        hd += [(ribbon(pts, [0.1] + [w] * (len(pts) - 2) + [0.1]), HAIR.shadow, op),
               (ribbon([(x + 0.3, y - 0.6) for x, y in pts], [0.1] + [w * 0.6] * (len(pts) - 2) + [0.1]), HAIR.hi, op * 0.9)]
    # la tresse en couronne posée sur le crâne (suit sa courbe), de la tempe lointaine jusqu'au chignon
    BR = crpath([(81.0, 24.4), (78.0, 21.8), (73.0, 20.8), (67.6, 21.4), (62.8, 23.8), (59.6, 27.6), (57.8, 31.6)], 20)
    hd += [(taper(BR, 4.2, 4.0), HAIR.shadow, 0.45)]
    for k in range(1, len(BR) - 1):
        p = BR[k]
        tdir = norm(sub(BR[k + 1], BR[k - 1]))
        nrm = (-tdir[1], tdir[0])
        side = 1 if k % 2 else -1
        c = add(p, nrm, 0.85 * side)
        a = ang_of(tdir) + 38 * side
        hd += [(ellipse(c[0] - 0.22, c[1] + 0.26, 1.7, 1.0, a), HAIR.deep, 0.32),
               (ellipse(c[0], c[1], 1.6, 0.92, a), HAIR.base, 1),
               (ellipse(c[0] + 0.22, c[1] - 0.22, 1.08, 0.52, a), HAIR.light, 0.95),
               (ellipse(c[0] + 0.4, c[1] - 0.35, 0.48, 0.22, a), HAIR.hi, 0.8)]
    # le liseré de lumière seulement sur le dessus et l'arrière du crâne (pas sur la ligne du front)
    hd += [(b, HAIR.hi, 0.85) for b in rim_band(hair, 0.45, -0.6, [(55, 28.4), (70, 28.4), (70, 50), (55, 50)])]
    part('hair', hair, HAIR, grad=(82, 19, 58, 42, [(0, HAIR.light), (0.4, HAIR.base), (1, HAIR.shadow)]),
         cel=0, rim=0, cast=0.6, cast_on=['bun'], details=hd)

    # ---- l'oreille dégagée (devant les cheveux de la nuque, sa racine fondue dans la peau), à hauteur des yeux ----
    ox, oy = V['oreille']
    ear = sm([(ox + 1.6, oy - 2.5), (ox, oy - 3.1), (ox - 1.3, oy - 1.9), (ox - 1.6, oy + 0.7), (ox - 0.8, oy + 3.0),
              (ox + 0.6, oy + 4.0), (ox + 1.8, oy + 2.9)], t=0.95)
    part('ear', ear, SKIN, grad=(ox + 1.8, oy - 2.5, ox - 1.6, oy + 3.5, [(0, SKIN.base), (1, SKIN.shadow)]), cel=0.6, rim=0.4,
         cast=0.7, cast_on=['hair'],
         details=[(sm([(ox + 1.4, oy - 1.7), (ox + 0.1, oy - 1.3), (ox - 0.2, oy + 0.9), (ox + 0.6, oy + 2.7), (ox + 1.3, oy + 1.4)], t=0.9), SKIN.shadow, 0.7),
                  (ribbon([(ox + 0.8, oy - 2.3), (ox - 0.2, oy - 0.7), (ox - 0.2, oy + 1.9)], [0.1, 0.4, 0.1]), SKIN.hi, 0.5)])
    # ---- la goutte de turquoise montée sur or, sous le lobe ----
    e = P['ear']
    ex, ey = ox + 0.3, oy + 3.8
    dx = 0.5 * e
    drop = sm([(ex - 0.55, ey - 0.4), (ex + 0.55, ey - 0.4), (ex + 0.6 + dx * 0.5, ey + 0.6), (ex + 1.15 + dx, ey + 2.1),
               (ex + dx, ey + 3.5), (ex - 1.15 + dx, ey + 2.1), (ex - 0.6 + dx * 0.5, ey + 0.6)], sharp=(0, 1), t=0.9)
    part('earring', drop, GOLD, cel=0.4, rim=0.35, cast=0.6, cast_on=['face', 'hair', 'ear'],
         details=[(ellipse(ex + dx, ey + 2.25, 0.8, 1.0), TURQ.shadow, 1),
                  (ellipse(ex + dx + 0.05, ey + 2.15, 0.6, 0.78), ('rad', ex + dx + 0.25, ey + 1.8, 0.9, 0.9, [(0, TURQ.hi), (0.5, TURQ.light), (1, TURQ.base)]), 1),
                  (ellipse(ex + dx + 0.25, ey + 1.75, 0.2, 0.22), '#ffffff', 0.9)])
    return names


def main():
    """myrr.svg (grand) et myrr-petit.svg (contour plus épais, pour les cases), puis les images du jeu :
    public/art/vecto/mages-11.webp (512 px de haut) et mages-11-160.webp (160 px de haut)."""
    from PIL import Image
    rendu = os.path.join(HERE, '..', 'rendu.cjs')
    pub = os.path.join(ROOT, 'public', 'art', 'vecto')
    os.makedirs(pub, exist_ok=True)
    for name, ow, h, out in (('myrr', 0.95, 512, 'mages-11'), ('myrr-petit', 1.35, 160, 'mages-11-160')):
        svg = build(ow=ow).svg()
        path = os.path.join(HERE, name + '.svg')
        open(path, 'w').write(svg)
        png = os.path.join(HERE, name + '.png')
        subprocess.run(['node', rendu, path, png, str(h)], check=True)
        Image.open(png).save(os.path.join(pub, out + '.webp'), 'WEBP', quality=90, method=6)
        print('écrit %s.svg (%d ko) → art/vecto/%s.webp' % (name, len(svg) // 1024, out))
    x0, y0, w, h = FRAME
    print('mesures pour src/game/vecto.ts : [largeur, hauteur, x et y des pieds] =', [w, h, FEET[0] - x0, FEET[1] - y0])


if __name__ == '__main__':
    main()
