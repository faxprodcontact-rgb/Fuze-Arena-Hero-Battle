# Le combat : les 4 éléments, les 6 rôles, les attributs (fiche d'un héros) et les statuts (au-dessus des
# combattants, vus à 27 px : très lisibles, une forme franche + une flèche de bonus / malus).
import math

from composants import arrow_badge, arrow_shape, plus_shape, shield_shape, sparkles, sword
from lib import (C, ELEMENT, Icon, arc_pts, band, blob, circle, col, dark, ellipse, lite, openpath, picto, poly, rect,
                 ring, rpoly, sparkle_shape, star)
from menus import gear_shape
from modes import bow
from monnaies import drop, heart

# ---------- Les éléments ----------


def flame_shape(cx, cy, s):
    pts = [(cx, cy - s), (cx + s * 0.22, cy - s * 0.45), (cx + s * 0.5, cy - s * 0.62), (cx + s * 0.62, cy - s * 0.05),
           (cx + s * 0.55, cy + s * 0.45), (cx, cy + s * 0.75), (cx - s * 0.55, cy + s * 0.45), (cx - s * 0.62, cy),
           (cx - s * 0.42, cy - s * 0.4), (cx - s * 0.3, cy - s * 0.12)]
    return blob(pts, sharp=(0, 2, 8), t=1)


def flame(ic, cx, cy, s, outer='fire'):
    o = ic.obj()
    o.part(flame_shape(cx, cy, s), [(0, '#ffd23a'), (0.55, col(outer)), (1, dark(col(outer), 0.3))], gloss=False, grad='v')
    o.detail(flame_shape(cx, cy + s * 0.28, s * 0.55), fill='#ffe46a', clip=0)
    o.detail(flame_shape(cx, cy + s * 0.42, s * 0.3), fill='#fffbe0', clip=0)
    return o


@picto('fire')
def _():
    ic = Icon()
    flame(ic, 50, 54, 44)
    return ic


@picto('water')
def _():
    ic = Icon()
    o = ic.obj()
    o.part(drop(50, 52, 34, 44), ELEMENT['water'], gloss=False)
    o.detail(openpath([(30, 66), (40, 60), (50, 66), (60, 60), (70, 66)], smooth=True), stroke=('#c8ecff', 3.4), clip=0, opacity=0.85)
    o.detail(ellipse(62, 48, 6, 11, -20), fill='#ffffff', clip=0, opacity=0.8, blur=1)
    return ic


def gust(cx, cy, length, r, w):
    """Une bourrasque : un trait qui finit en boucle."""
    pts = [(cx - length, cy)] + [(cx + r * math.cos(math.radians(a)), cy - r + r * math.sin(math.radians(a))) for a in range(90, -200, -30)]
    return band(pts, w)


@picto('wind')
def _():
    """Le vent : trois bourrasques enroulées."""
    ic = Icon()
    o = ic.obj()
    for cx, cy, L, r in [(58, 34, 44, 12), (70, 58, 54, 11), (46, 80, 32, 8)]:
        o.part(gust(cx, cy, L, r, 9), ELEMENT['wind'], gloss=False)
    return ic


@picto('earth')
def _():
    """La terre : un rocher à deux sommets, une herbe au pied."""
    ic = Icon()
    o = ic.obj()
    o.part(rpoly([(6, 88), (30, 34), (44, 50), (62, 14), (94, 88)], [4, 3, 3, 3, 4]), ELEMENT['earth'], gloss=False)
    o.detail(poly([(62, 14), (94, 88), (66, 88), (58, 50)]), fill=lite(ELEMENT['earth'], 0.35), clip=0, opacity=0.6)
    o.detail(rpoly([(62, 14), (70, 30), (64, 34), (58, 28), (54, 32)], 1.5), fill='#ffffff', clip=0, opacity=0.85)
    g = ic.obj(shadow=False)
    g.part(blob([(8, 88), (24, 74), (36, 80), (50, 72), (62, 80), (76, 74), (92, 88)], t=1), 'green', gloss=False)
    return ic


# ---------- Les rôles ----------


@picto('warrior')
def _():
    """Guerrier : une hache de bataille."""
    ic = Icon()
    o = ic.obj()
    o.part(rect(46, 8, 8, 86, 4).rot(30, 50, 50), 'wood', gloss=False)
    head = blob([(52, 18), (78, 6), (90, 26), (86, 50), (64, 46), (54, 36)], sharp=(0, 5), t=1)
    o.part(head.rot(30, 50, 50), ('metal', 'steel'), gloss=False)
    o.part(rect(46, 16, 12, 24, 3).rot(30, 50, 50), 'gold')
    return ic


@picto('assassin')
def _():
    """Assassin : deux dagues courbes croisées."""
    ic = Icon()
    for flip in (1, -1):
        o = ic.obj()
        # une dague courbe : le dos bombé, le tranchant creusé, la pointe relevée
        blade = blob([(0, -6), (34, -11), (62, -4), (36, 2), (0, 6)], sharp=(0, 2, 4), t=1)
        ang = -45 if flip > 0 else -135
        cx, cy = (26, 74) if flip > 0 else (74, 74)
        T = lambda s: s.rot(ang, 0, 0).move(cx, cy)
        o.part(T(rect(-18, -4.5, 16, 9, 3.5)), 'night')
        o.part(T(circle(-20, 0, 5)), 'violet')
        o.part(T(blade), ('metal', 'steel'), gloss=False)
        o.part(T(rpoly([(-3, -14), (4, -12), (4, 12), (-3, 14)], 2.5)), 'violet')
    return ic


@picto('marksman')
def _():
    ic = Icon()
    bow(ic, 42, 50, 40, rot=-45)
    return ic


@picto('healer')
def _():
    ic = Icon()
    o = ic.obj()
    o.part(plus_shape(50, 50, 40), 'green', gloss=False)
    o.detail(ellipse(62, 22, 4, 7, 20), fill='#ffffff', opacity=0.7, blur=1, clip=0)
    return ic


@picto('protector')
def _():
    """Protecteur : un grand écu bleu cerclé d'or, une étoile."""
    ic = Icon()
    o = ic.obj()
    o.part(shield_shape(50, 50, 78, 86), 'gold', gloss=False)
    o.part(shield_shape(50, 49, 62, 70), 'azure', gloss=False, cast=False)
    o.detail(star(50, 46, 15, rr=1.2), fill='#ffe27a')
    return ic


@picto('support')
def _():
    """Soutien : un bâton de bois, une orbe bleue lumineuse au sommet."""
    ic = Icon()
    ic.glow(64, 30, 32, '#8fe6ff', 0.75)
    o = ic.obj()
    o.part(rect(44, 30, 11, 68, 5).rot(32, 50, 62), 'wood')
    o.part(blob([(52, 44), (48, 26), (58, 12), (72, 10), (82, 22), (80, 40)], t=1), 'gold', gloss=False)
    o.part(circle(65, 29, 16), ('radial', 'sky'), gloss=False)
    ic.sparkle(86, 12, 7)
    return ic


# ---------- Les attributs ----------


@picto('atk')
def _():
    ic = Icon()
    sword(ic, 26, 76, 82, 18, wide=1.4, guard=1.1)
    return ic


def round_shield(ic, cx=50, cy=50, r=40, c='azure'):
    o = ic.obj()
    o.part(circle(cx, cy, r), ('metal', 'steel'), gloss=False)
    o.part(circle(cx, cy, r * 0.78), c, gloss=False, cast=False)
    o.part(circle(cx, cy, r * 0.28), 'gold')
    for a in range(0, 360, 60):
        t = math.radians(a + 30)
        o.detail(circle(cx + r * 0.89 * math.cos(t), cy + r * 0.89 * math.sin(t), r * 0.05), fill=dark(col('steel'), 0.4))
    return o


@picto('def')
def _():
    ic = Icon()
    round_shield(ic)
    return ic


def wing_shape(cx, cy, s):
    """Une aile (plumes en éventail), tournée vers la gauche."""
    pts = [(cx + s * 0.5, cy - s * 0.1), (cx + s * 0.2, cy - s * 0.62), (cx - s * 0.3, cy - s * 0.75), (cx - s * 0.8, cy - s * 0.62),
           (cx - s * 0.5, cy - s * 0.38), (cx - s * 0.86, cy - s * 0.26), (cx - s * 0.52, cy - s * 0.04), (cx - s * 0.8, cy + s * 0.12),
           (cx - s * 0.42, cy + s * 0.28), (cx - s * 0.56, cy + s * 0.46), (cx + s * 0.1, cy + s * 0.42), (cx + s * 0.5, cy + s * 0.2)]
    return blob(pts, sharp=(3, 5, 7, 9), t=0.9)


@picto('speed')
def _():
    """Vitesse : une aile blanche, deux traits de vitesse."""
    ic = Icon()
    o = ic.obj()
    o.part(wing_shape(56, 54, 46), 'white', gloss=False)
    o.detail(openpath([(56, 36), (30, 44)], smooth=False), stroke=(dark(col('white'), 0.25), 2), clip=0, opacity=0.7)
    o.detail(openpath([(56, 52), (28, 58)], smooth=False), stroke=(dark(col('white'), 0.25), 2), clip=0, opacity=0.7)
    s = ic.obj(shadow=False)
    for y, L in [(74, 26), (86, 16)]:
        s.part(rect(70 - L / 2, y - 3, L, 6, 3), 'sky', gloss=False)
    return ic


def target(ic, cx=50, cy=50, r=40):
    o = ic.obj()
    o.part(circle(cx, cy, r), 'red', gloss=False)
    o.part(circle(cx, cy, r * 0.72), 'white', gloss=False, cast=False)
    o.part(circle(cx, cy, r * 0.46), 'red', gloss=False, cast=False)
    o.part(circle(cx, cy, r * 0.2), 'white', gloss=False, cast=False)
    return o


@picto('crit')
def _():
    """Coup critique : une cible et une flèche plantée au centre."""
    ic = Icon()
    target(ic, 46, 54, 38)
    a = ic.obj()
    a.part(rect(44, 46, 46, 5, 2.5).rot(-40, 46, 54), 'wood', gloss=False)
    a.part(rpoly([(72, 32), (90, 24), (86, 40)], 1.5).rot(0), 'red', gloss=False)
    return ic


def burst_shape(cx, cy, R, r, n=8, rot=-90):
    pts = []
    for i in range(2 * n):
        a = math.radians(rot + i * 180 / n)
        rad = R * (1 if i % 4 == 0 else 0.82) if i % 2 == 0 else r
        pts.append((cx + rad * math.cos(a), cy + rad * math.sin(a)))
    return rpoly(pts, 1.5)


@picto('critDmg')
def _():
    """Dégâts critiques : une explosion orange au cœur blanc."""
    ic = Icon()
    o = ic.obj()
    o.part(burst_shape(50, 50, 46, 24, 8), 'orange', gloss=False)
    o.part(burst_shape(50, 50, 28, 14, 8, -67.5), '#ffd23a', gloss=False, cast=False)
    o.detail(circle(50, 50, 8), fill='#ffffff', opacity=0.9, blur=1)
    return ic


def feather_shape(cx, cy, s, rot=-40):
    pts = [(cx, cy + s), (cx - s * 0.32, cy + s * 0.2), (cx - s * 0.26, cy - s * 0.5), (cx, cy - s), (cx + s * 0.3, cy - s * 0.45), (cx + s * 0.3, cy + s * 0.25)]
    return blob(pts, sharp=(0, 3), t=1).rot(rot, cx, cy)


@picto('dodge')
def _():
    """Esquive : une plume bleue légère, traits de vitesse."""
    ic = Icon()
    o = ic.obj()
    o.part(feather_shape(54, 48, 44), 'sky', gloss=False)
    o.detail(openpath([(54, 92), (54, 4)]).rot(-40, 54, 48), stroke=('#eafaff', 2.6), clip=0, opacity=0.9)
    s = ic.obj(shadow=False)
    for y, L in [(78, 22), (88, 14)]:
        s.part(rect(14, y - 3, L, 6, 3), 'sky', gloss=False)
    return ic


@picto('tenacity')
def _():
    """Ténacité : une ancre."""
    ic = Icon()
    o = ic.obj()
    o.part(ring(50, 16, 9, 4.5), 'violet', gloss=False)
    o.part(rect(45, 22, 10, 62, 5), 'violet', gloss=False)
    o.part(rect(30, 32, 40, 9, 4.5), 'violet', gloss=False)
    arc = arc_pts(50, 58, 32, 20, 160, 14)
    o.part(band(arc, 9), 'violet', gloss=False)
    for x, d in [(82, 1), (18, -1)]:
        o.part(rpoly([(x - d * 2, 60), (x + d * 8, 64), (x + d * 4, 74), (x - d * 6, 74)], 1.5), 'violet', gloss=False)
    return ic


# ---------- Les statuts (combat) ----------


def stat_sword(ic):
    sword(ic, 22, 80, 70, 24, wide=1.1, guard=1.1)


def stat_shield(ic):
    o = ic.obj()
    o.part(shield_shape(42, 48, 66, 74), 'azure', gloss=False)
    o.detail(rpoly([(42, 30), (52, 46), (42, 64), (32, 46)], 2), fill='#ffe27a')


@picto('st-atkUp')
def _():
    ic = Icon()
    stat_sword(ic)
    arrow_badge(ic, 74, 66, 22, True)
    return ic


@picto('st-atkDown')
def _():
    ic = Icon()
    stat_sword(ic)
    arrow_badge(ic, 74, 66, 22, False)
    return ic


@picto('st-defUp')
def _():
    ic = Icon()
    stat_shield(ic)
    arrow_badge(ic, 74, 66, 22, True)
    return ic


@picto('st-defDown')
def _():
    ic = Icon()
    stat_shield(ic)
    arrow_badge(ic, 74, 66, 22, False)
    return ic


@picto('st-critUp')
def _():
    ic = Icon()
    target(ic, 40, 44, 34)
    arrow_badge(ic, 74, 66, 22, True)
    return ic


@picto('st-speedUp')
def _():
    ic = Icon()
    o = ic.obj()
    o.part(wing_shape(46, 44, 42), 'white', gloss=False)
    arrow_badge(ic, 74, 66, 22, True)
    return ic


@picto('st-bleed')
def _():
    """Saignement : trois gouttes rouges."""
    ic = Icon()
    for x, y, r, h in [(36, 42, 22, 30), (70, 34, 13, 18), (68, 74, 12, 16)]:
        o = ic.obj()
        o.part(drop(x, y, r, h), 'red', gloss=False)
        o.detail(ellipse(x + r * 0.35, y + h * 0.1, r * 0.18, r * 0.32, -20), fill='#ffffff', opacity=0.75, blur=1, clip=0)
    return ic


@picto('st-burn')
def _():
    ic = Icon()
    flame(ic, 50, 54, 44, outer='#ff4a26')
    return ic


@picto('st-poison')
def _():
    """Poison : une goutte verte qui bouillonne."""
    ic = Icon()
    o = ic.obj()
    o.part(drop(46, 56, 32, 42), '#6fdc2e', gloss=False)
    o.detail(circle(38, 66, 6), fill='#2e8a1a', clip=0, opacity=0.6)
    o.detail(circle(54, 74, 4), fill='#2e8a1a', clip=0, opacity=0.6)
    o.detail(ellipse(56, 52, 5, 9, -20), fill='#ffffff', opacity=0.7, blur=1, clip=0)
    for x, y, r in [(80, 26, 7), (88, 44, 4.5), (72, 12, 4)]:
        b = ic.obj()
        b.part(circle(x, y, r), '#8ff04a', gloss=False)
    return ic


@picto('st-regen')
def _():
    """Régénération : une feuille verte et une croix de soin."""
    ic = Icon()
    o = ic.obj()
    o.part(blob([(14, 86), (20, 48), (44, 22), (80, 12), (72, 46), (50, 72)], sharp=(0, 3), t=1), 'green', gloss=False)
    o.detail(openpath([(16, 84), (38, 58), (66, 26)], smooth=True), stroke=(lite(col('green'), 0.5), 2.6), clip=0, opacity=0.8)
    p = ic.obj()
    p.part(plus_shape(74, 70, 20), 'white', gloss=False)
    return ic


@picto('st-silence')
def _():
    """Silence : une bulle de parole barrée."""
    ic = Icon()
    o = ic.obj()
    o.part(blob([(12, 44), (18, 22), (50, 14), (82, 22), (88, 44), (80, 64), (54, 70), (36, 70), (20, 86), (24, 66), (14, 58)], sharp=(7, 8, 9), t=1), 'white', gloss=False)
    for x in (34, 50, 66):
        o.detail(circle(x, 44, 5.5), fill='#8a84b0')
    s = ic.obj()
    s.part(rect(4, 42, 92, 11, 5.5).rot(-35, 50, 47), 'red', gloss=False)
    return ic


@picto('st-slow')
def _():
    """Lenteur : un escargot."""
    ic = Icon()
    o = ic.obj()
    o.part(blob([(8, 84), (14, 74), (40, 72), (70, 72), (82, 60), (88, 48), (94, 54), (92, 70), (84, 84)], sharp=(0, 8), t=1), '#9de06a', gloss=False)
    o.part(circle(46, 50, 28), 'orange', gloss=False)
    spiral = [(46 + r * math.cos(math.radians(a)), 50 + r * math.sin(math.radians(a))) for r, a in [(2, 0), (8, 120), (14, 240), (19, 360), (23, 470)]]
    o.detail(openpath(spiral, smooth=True), stroke=(dark(col('orange'), 0.4), 3.4), clip=1, opacity=0.8)
    for x in (86, 94):
        o.detail(openpath([(x - 2, 52), (x, 38)]), stroke=(dark('#9de06a', 0.3), 2.4))
        o.detail(circle(x, 37, 3), fill=dark('#9de06a', 0.3))
    return ic


@picto('st-stun')
def _():
    """Étourdi : trois étoiles qui tournent sur une orbite."""
    ic = Icon()
    o = ic.obj(shadow=False)
    o.detail(ellipse(50, 56, 38, 14, -8), stroke=('#c9a6ff', 3), opacity=0.9)
    for x, y, r in [(18, 52, 15), (52, 38, 19), (82, 62, 14)]:
        s = ic.obj()
        s.part(star(x, y, r, rr=1.5), 'gold', gloss=False)
    return ic


@picto('st-taunt')
def _():
    """Provocation : un cor de guerre rouge qui sonne."""
    ic = Icon()
    o = ic.obj()
    o.part(blob([(14, 40), (24, 36), (60, 18), (68, 14), (74, 30), (76, 50), (72, 72), (66, 86), (58, 80), (24, 62), (14, 58)], sharp=(0, 3, 7, 10), t=0.9), 'red', gloss=False)
    o.part(ellipse(70, 50, 9, 33), dark(col('red'), 0.35), gloss=False, cast=False)
    o.part(rect(8, 38, 12, 22, 4), 'gold')
    s = ic.obj(shadow=False)
    for r, op in [(20, 1), (28, 0.8)]:
        s.detail(openpath(arc_pts(68, 50, r, -35, 35, 8), smooth=True), stroke=('#ffd23a', 4), opacity=op)
    return ic
