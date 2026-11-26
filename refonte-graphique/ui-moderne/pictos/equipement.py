# L'équipement : arme, armure, casque, bottes — le picto de la place (sans rareté) et ses 6 raretés (-0 à -5 :
# commun, peu commun, rare, épique, légendaire, mythique ; ITEM_COLORS de src/game/art.ts), et les 5 panoplies.
# La rareté se lit d'un coup d'œil : matière (fer terne → acier → acier bleuté → violet → or → rouge et or), ornements
# (rien → liseré → gemme → garde travaillée → ailes → flammes), lueur et étincelles pour les plus rares.
import math

from composants import coin, shield_shape, sparkles, sword
from lib import (C, Icon, RARITY, arc_pts, band, blob, circle, col, dark, ellipse, lite, mix, openpath, picto, poly,
                 rect, ring, rpoly, star)
from combat import flame_shape
from monnaies import heart

# matière principale, ornement, gemme — par rareté (None = la place sans rareté)
TIERS = {
    None: dict(metal='steel', trim='gold', gem='azure', accent='azure'),
    0: dict(metal='#9a9db4', trim='#8b8fa8', gem=None, accent='#8d6a4a'),
    1: dict(metal='steel', trim='#a7b0c6', gem='green', accent=RARITY[1]),
    2: dict(metal='#bcd2f2', trim='gold', gem='azure', accent=RARITY[2]),
    3: dict(metal='#c9b8f4', trim='gold', gem='purple', accent=RARITY[3]),
    4: dict(metal='#ffd65a', trim='#fff0a0', gem='azure', accent=RARITY[4]),
    5: dict(metal='#ff6170', trim='gold', gem='#ffe27a', accent=RARITY[5]),
}


def deco(ic, r):
    """Lueur derrière (légendaire, mythique) et étincelles (épique et plus)."""
    if r is None:
        return
    if r >= 4:
        ic.glow(50, 50, 50, RARITY[r], 0.55)
    if r >= 3:
        ic.sparkle(84, 16, 7 if r == 3 else 9)
    if r >= 5:
        ic.sparkle(16, 84, 6)


def mini_wing(o, x, y, s, side=1, c='white'):
    pts = [(x, y), (x + side * s * 0.9, y - s * 0.7), (x + side * s * 1.0, y - s * 0.2), (x + side * s * 0.75, y + s * 0.05), (x + side * s * 0.85, y + s * 0.35), (x + side * s * 0.4, y + s * 0.5)]
    sh = blob(pts, sharp=(0, 1, 3), t=0.9)
    o.part(sh if side > 0 else sh.rev(), c, gloss=False)


# ---------- Arme ----------

def weapon(r):
    ic = Icon()
    t = TIERS[r]
    deco(ic, r)
    if r is None or r <= 2:
        sword(ic, 26, 76, 84, 18, blade={None: 'steel', 0: 'iron', 1: 'steel', 2: '#bcd8ff'}[r], hilt=t['trim'] if r != 0 else 'wood',
              grip='green' if r == 1 else 'leather', gem_c=t['gem'], wide=1.3, guard=1.05)
    else:
        # garde travaillée (cornes recourbées), lame teintée qui brille
        sword(ic, 26, 76, 84, 18, blade=t['metal'], hilt=t['trim'], grip='night', gem_c=t['gem'], wide=1.45, guard=1.35)
    return ic


# ---------- Armure ----------

def armor(r):
    ic = Icon()
    t = TIERS[r]
    deco(ic, r)
    o = ic.obj()
    m = t['metal'] if r != 0 else '#a0714a'          # le commun : du cuir
    body = blob([(26, 26), (40, 22), (50, 30), (60, 22), (74, 26), (76, 50), (72, 78), (60, 90), (40, 90), (28, 78), (24, 50)], sharp=(2,), t=0.9)
    # épaulières
    for side in (-1, 1):
        x = 50 + side * 30
        o.part(ellipse(x - side * 2, 34, 13, 10, side * 20), t['trim'] if r and r >= 2 else m, gloss=False)
    if r is not None and r >= 4:
        for side in (-1, 1):
            mini_wing(o, 50 + side * 38, 26, 14, side, 'white' if r == 4 else '#ffd65a')
    o.part(body, m, gloss=False)
    bi = len(o.parts) - 1
    # le col, la ceinture, l'arête du plastron
    o.part(rpoly([(40, 22), (50, 32), (60, 22), (56, 18), (44, 18)], 2), dark(col(m), 0.25), gloss=False)
    o.detail(openpath([(50, 34), (50, 66)]), stroke=(dark(col(m), 0.3), 2.2), clip=bi, opacity=0.6)
    belt = t['accent'] if r is not None else 'leather'
    o.part(rect(28, 66, 44, 10, 3), belt if r != 0 else '#6e4a30', gloss=False)
    o.part(rect(45, 64, 10, 14, 3), t['trim'] if r != 0 else '#c9b28a')
    if t['gem']:
        o.part(rpoly([(50, 40), (58, 50), (50, 60), (42, 50)], 2.5), t['gem'], gloss=False)
    if r == 5:
        for side in (-1, 1):
            o.part(rpoly([(50 + side * 22, 26), (50 + side * 34, 6), (50 + side * 36, 26)], 1.5), 'gold', gloss=False)
    return ic


# ---------- Casque ----------

def helmet(r):
    ic = Icon()
    t = TIERS[r]
    deco(ic, r)
    o = ic.obj()
    m = t['metal']
    if r is not None and r >= 1 and r != 5:
        # le panache (vert, crête bleue, crête violette, plumet blanc doré)
        pc = {1: 'green', 2: 'azure', 3: 'purple', 4: 'white'}.get(r, 'red')
        if r is None:
            pc = 'red'
        o.part(blob([(50, 4), (66, 8), (70, 24), (50, 30), (34, 24), (38, 10)], t=1), pc, gloss=False)
    if r is None:
        o.part(blob([(50, 4), (60, 10), (63, 24), (50, 30), (37, 24), (40, 10)], t=1), 'red', gloss=False)
    if r is not None and r >= 4:
        for side in (-1, 1):
            mini_wing(o, 50 + side * 28, 40, 20, side, 'white' if r == 4 else '#ffd65a')
    if r == 5:
        for side in (-1, 1):
            o.part(blob([(50 + side * 24, 34), (50 + side * 40, 20), (50 + side * 42, 2), (50 + side * 34, 16), (50 + side * 18, 24)], sharp=(2,), t=1), 'bone', gloss=False)
    if r == 0:
        # un simple casque de fer : calotte, bandeau rivé, nasal, deux joues
        for side in (-1, 1):
            o.part(rpoly([(50 + side * 34, 52), (50 + side * 20, 52), (50 + side * 22, 84), (50 + side * 32, 80)], 3), dark(col(m), 0.08), gloss=False)
        o.part(blob([(16, 60), (18, 38), (32, 20), (50, 14), (68, 20), (82, 38), (84, 60)], sharp=(0, 6), t=1), m, gloss=False)
        o.part(rect(12, 52, 76, 12, 5), dark(col(m), 0.15), gloss=False)
        o.part(rpoly([(45, 56), (55, 56), (53, 80), (47, 80)], 3), dark(col(m), 0.05), gloss=False)
        for x in (22, 34, 66, 78):
            o.detail(circle(x, 58, 2.2), fill=dark(col(m), 0.5))
        return ic
    o.part(blob([(18, 54), (20, 30), (34, 16), (50, 12), (66, 16), (80, 30), (82, 54), (78, 82), (60, 92), (40, 92), (22, 82)], t=1), m, gloss=False)
    hi = len(o.parts) - 1
    o.part(rect(24, 42, 52, 12, 6), 'night', gloss=False, bevel=0.4)
    o.detail(openpath([(50, 14), (50, 40)]), stroke=(dark(col(m), 0.3), 2.4), clip=hi, opacity=0.6)
    for x, y in [(60, 66), (68, 66), (60, 75), (68, 75), (32, 66), (40, 66), (32, 75), (40, 75)]:
        o.detail(circle(x, y, 2.1), fill=dark(col(m), 0.6))
    if r is not None and r >= 2:
        o.detail(openpath([(26, 34), (40, 22), (50, 20), (60, 22), (74, 34)], smooth=True), stroke=(col(t['trim']), 3.2), clip=hi)
    if t['gem'] and r is not None and r >= 3:
        o.part(rpoly([(50, 22), (56, 30), (50, 38), (44, 30)], 2), t['gem'], gloss=False)
    return ic


# ---------- Bottes ----------

def boots(r):
    ic = Icon()
    t = TIERS[r]
    deco(ic, r)
    o = ic.obj()
    leather = {None: 'leather', 0: '#9a6640', 1: 'leather', 2: '#5d6a9e', 3: '#6a45b8', 4: '#f2f0ff', 5: '#c8243e'}[r]
    if r is not None and r >= 4:
        mini_wing(o, 30, 30, 22, -1, 'white' if r == 4 else '#ffd65a')
    o.part(blob([(30, 10), (60, 10), (62, 52), (86, 62), (90, 80), (86, 90), (24, 90), (24, 60)], sharp=(0, 1, 6, 7), t=0.8), leather, gloss=False)
    bi = len(o.parts) - 1
    o.part(rect(24, 80, 68, 11, 4), dark(col(leather), 0.4), gloss=False)
    cuff = t['accent'] if r not in (None, 0) else dark(col(leather), 0.15)
    o.part(rect(26, 8, 38, 14, 5), cuff, gloss=False)
    if r is not None and r >= 2:
        # jambière et pointe de métal
        o.part(rpoly([(32, 28), (58, 28), (58, 54), (32, 58)], 3), t['trim'] if r != 4 else 'gold', gloss=False)
        o.part(rpoly([(72, 64), (86, 66), (90, 80), (74, 80)], 3), t['trim'] if r != 4 else 'gold', gloss=False)
    if t['gem'] and r is not None and r >= 3:
        o.part(rpoly([(45, 36), (51, 43), (45, 50), (39, 43)], 2), t['gem'], gloss=False)
    if r is None or r <= 1:
        for y in (34, 44):
            o.detail(openpath([(34, y), (56, y)]), stroke=(dark(col(leather), 0.35), 2.2), clip=bi, opacity=0.6)
    return ic


for _slot, _fn in [('weapon', weapon), ('armor', armor), ('helmet', helmet), ('boots', boots)]:
    picto(_slot)(lambda _fn=_fn: _fn(None))
    for _r in range(6):
        picto('%s-%d' % (_slot, _r))(lambda _fn=_fn, _r=_r: _fn(_r))


# ---------- Les panoplies (médaillons) ----------

def medallion(color, sign):
    ic = Icon()
    o = ic.obj()
    o.part(circle(50, 50, 42), 'gold', gloss=False)
    o.part(circle(50, 50, 33), ('radial', color), gloss=False, cast=False)
    s = ic.obj(shadow=False, w=2.2)
    sign(s)
    return ic


def bat_shape(cx, cy, s):
    pts = [(cx, cy - s * 0.25), (cx + s * 0.12, cy - s * 0.5), (cx + s * 0.22, cy - s * 0.22), (cx + s * 0.62, cy - s * 0.45), (cx + s, cy - s * 0.1),
           (cx + s * 0.75, cy + s * 0.05), (cx + s * 0.6, cy + s * 0.35), (cx + s * 0.38, cy + s * 0.18), (cx, cy + s * 0.5),
           (cx - s * 0.38, cy + s * 0.18), (cx - s * 0.6, cy + s * 0.35), (cx - s * 0.75, cy + s * 0.05), (cx - s, cy - s * 0.1),
           (cx - s * 0.62, cy - s * 0.45), (cx - s * 0.22, cy - s * 0.22), (cx - s * 0.12, cy - s * 0.5)]
    return rpoly(pts, 1.2)


picto('set-fury')(lambda: medallion('red', lambda s: s.part(flame_shape(50, 52, 24), [(0, '#fff3a0'), (1, '#ffb02e')], gloss=False, grad='v')))
picto('set-guard')(lambda: medallion('green', lambda s: s.part(shield_shape(50, 50, 32, 38), 'white', gloss=False)))
picto('set-rampart')(lambda: medallion('#c47a3a', lambda s: s.part(rpoly([(36, 72), (36, 34), (42, 34), (42, 40), (47, 40), (47, 34), (53, 34), (53, 40), (58, 40), (58, 34), (64, 34), (64, 72)], 1.2), 'cream', gloss=False)))
picto('set-storm')(lambda: medallion('azure', lambda s: s.part(rpoly([(56, 26), (38, 54), (49, 54), (44, 76), (64, 46), (53, 46), (58, 26)], 1.5), '#ffe45a', gloss=False)))
picto('set-vampire')(lambda: medallion('purple', lambda s: s.part(bat_shape(50, 50, 26), '#2a1748', gloss=False, bevel=0.5)))
