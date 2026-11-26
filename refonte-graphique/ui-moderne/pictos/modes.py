# Les modes de jeu (onglet Aventure, médaillons) et les six missions.
import math

from composants import gem, shield_shape, sparkles, sword
from lib import (C, Icon, arc_pts, band, blob, circle, col, dark, ellipse, lite, openpath, picto, poly, rect, ring, rpoly,
                 star)


@picto('arena')
def _():
    """L'arène : deux épées croisées."""
    ic = Icon()
    sword(ic, 24, 80, 84, 16, gem_c='azure')
    sword(ic, 76, 80, 16, 16, gem_c='red')
    return ic


@picto('tower')
def _():
    """La tour : un donjon de pierre, toit pointu rouge et fanion."""
    ic = Icon()
    o = ic.obj()
    o.part(rpoly([(26, 40), (74, 40), (70, 92), (30, 92)], [1, 1, 3, 3]), 'stone', gloss=False)
    o.part(rect(22, 34, 56, 12, 3), lite(col('stone'), 0.1), gloss=False)
    o.part(rpoly([(50, 4), (80, 36), (20, 36)], [2, 3, 3]), 'red', gloss=False)
    o.detail(rpoly([(42, 66), (58, 66), (58, 92), (42, 92)], [8, 8, 0, 0]), fill='#3a2a5e')
    o.detail(rect(46, 50, 8, 10, 4), fill='#ffe27a')
    for y in (58, 76):
        o.detail(openpath([(32, y), (40, y)]), stroke=(dark(col('stone'), 0.35), 2), clip=0, opacity=0.7)
        o.detail(openpath([(62, y + 6), (68, y + 6)]), stroke=(dark(col('stone'), 0.35), 2), clip=0, opacity=0.7)
    f = ic.obj(shadow=False)
    f.part(rect(49, -2, 3, 12, 1.5), 'wood', cast=False)
    f.part(rpoly([(52, 0), (66, 4), (52, 8)], 1), 'gold', gloss=False)
    return ic


@picto('dungeons')
def _():
    """Les donjons : l'entrée d'une grotte dans la roche, deux yeux dans le noir."""
    ic = Icon()
    o = ic.obj()
    o.part(blob([(6, 90), (12, 50), (30, 22), (50, 12), (72, 20), (90, 50), (94, 90)], sharp=(0, 6), t=1), 'stone', gloss=False)
    o.part(blob([(26, 90), (28, 60), (38, 42), (50, 36), (62, 42), (72, 60), (74, 90)], sharp=(0, 6), t=1), ('flat', '#1a1036'), gloss=False, bevel=0.5)
    o.detail(ellipse(42, 64, 4, 3), fill='#ffcf3a')
    o.detail(ellipse(58, 64, 4, 3), fill='#ffcf3a')
    o.detail(ellipse(50, 64, 16, 7), fill='#ffcf3a', opacity=0.25, blur=2)
    for pts in [[(18, 46), (28, 40)], [(72, 30), (82, 40)]]:
        o.detail(openpath(pts), stroke=(dark(col('stone'), 0.35), 2.4), clip=0, opacity=0.6)
    return ic


@picto('dailyBoss')
def _():
    """Le boss du jour : un crâne à cornes."""
    ic = Icon()
    o = ic.obj()
    o.part(blob([(26, 40), (10, 30), (6, 10), (18, 20), (34, 28)], sharp=(2,), t=1), 'bone', gloss=False)
    o.part(blob([(74, 40), (90, 30), (94, 10), (82, 20), (66, 28)], sharp=(2,), t=1), 'bone', gloss=False)
    o.part(blob([(18, 48), (24, 26), (50, 16), (76, 26), (82, 48), (72, 66), (70, 84), (30, 84), (28, 66)], t=1), 'white', gloss=False)
    o.detail(ellipse(37, 52, 9, 10), fill='#2a1748')
    o.detail(ellipse(63, 52, 9, 10), fill='#2a1748')
    o.detail(circle(37, 53, 3), fill='#ff4a5e')
    o.detail(circle(63, 53, 3), fill='#ff4a5e')
    o.detail(rpoly([(50, 62), (55, 70), (45, 70)], 1), fill='#2a1748')
    for x in (40, 50, 60):
        o.detail(openpath([(x, 76), (x, 84)]), stroke=(dark(col('white'), 0.4), 2.4), clip=2)
    return ic


def arcade(o, x0, y0, w, h, n, c, top=False):
    """Une façade d'arcades (colisée) : bande de pierre percée de n arches."""
    o.part(rect(x0, y0, w, h, 2), c, gloss=False, cast=top)
    i = len(o.parts) - 1
    aw = w / n
    for k in range(n):
        ax = x0 + aw * k + aw * 0.22
        o.detail(rpoly([(ax, y0 + h * 0.86), (ax, y0 + h * 0.38), (ax + aw * 0.28, y0 + h * 0.2), (ax + aw * 0.56, y0 + h * 0.38), (ax + aw * 0.56, y0 + h * 0.86)], [0, 2, 3, 2, 0]),
                 fill=dark(c, 0.62), clip=i)


@picto('colisee')
def _():
    """Le Colisée : l'amphithéâtre, trois rangs d'arcades, deux fanions."""
    ic = Icon()
    o = ic.obj()
    arcade(o, 8, 60, 84, 30, 5, '#e9c995')
    arcade(o, 14, 38, 72, 24, 4, '#f4d9a8', top=True)
    arcade(o, 20, 22, 60, 18, 4, '#fbe6bd', top=True)
    for x, c in [(24, 'red'), (76, 'azure')]:
        f = ic.obj(shadow=False)
        f.part(rect(x - 1.5, 4, 3, 20, 1.5), 'wood', cast=False)
        f.part(rpoly([(x + 1.5, 5), (x + 16, 10), (x + 1.5, 15)], 1), c, gloss=False)
    return ic


@picto('defense')
def _():
    """Le Colisée (tuile du mode, clé « defense ») : l'amphithéâtre, et deux petites épées croisées devant, en bas."""
    ic = Icon()
    o = ic.obj()
    arcade(o, 6, 50, 88, 32, 5, '#e9c995')
    arcade(o, 13, 28, 74, 24, 4, '#f4d9a8', top=True)
    arcade(o, 20, 12, 60, 18, 4, '#fbe6bd', top=True)
    sword(ic, 40, 92, 82, 56, gem_c='azure', wide=0.62, guard=0.62)
    sword(ic, 82, 92, 40, 56, gem_c='red', wide=0.62, guard=0.62)
    return ic


@picto('summonAltar')
def _():
    """L'autel d'invocation : un socle de pierre, un cristal violet qui flotte."""
    ic = Icon()
    ic.glow(50, 34, 32, '#c48cff', 0.7)
    o = ic.obj()
    o.part(rpoly([(30, 62), (70, 62), (66, 80), (34, 80)], 2), 'stone', gloss=False)
    o.part(rect(18, 78, 64, 14, 5), 'stone', gloss=False)
    o.part(rect(22, 56, 56, 10, 4), lite(col('stone'), 0.15), gloss=False)
    o.detail(rpoly([(44, 68), (56, 68), (50, 76)], 1), fill='#b67bff')
    c = ic.obj()
    c.part(rpoly([(50, 6), (64, 28), (50, 48), (36, 28)], 3), 'violet', gloss=False)
    c.detail(poly([(50, 6), (64, 28), (50, 48), (50, 28)]), fill='#e3c6ff', clip=0, opacity=0.55)
    sparkles(ic, [(80, 20, 7), (20, 30, 5)])
    return ic


@picto('summonPortal')
def _():
    """Le portail d'invocation : une arche ronde de pierre et un tourbillon violet."""
    ic = Icon()
    o = ic.obj()
    o.part(rect(12, 80, 76, 12, 5), 'stone', gloss=False)
    o.part(ring(50, 50, 38, 27), 'stone', gloss=False)
    o.part(circle(50, 50, 27), [(0, '#f0c8ff'), (0.5, '#8b4dff'), (1, '#2c0d6e')], gloss=False, grad='v', cast=False)
    for k in range(3):
        pts = [(50 + r * math.cos(math.radians(a + k * 120)), 50 + r * math.sin(math.radians(a + k * 120))) for r, a in [(3, 0), (10, 50), (17, 100), (24, 150)]]
        o.detail(openpath(pts, smooth=True), stroke=('#f2d6ff', 3.4), clip=2, opacity=0.75)
    o.detail(circle(50, 50, 6), fill='#ffffff', clip=2, opacity=0.9, blur=2)
    for a in (-90, -30, 30, 210, 150):
        t = math.radians(a)
        o.detail(circle(50 + 32.5 * math.cos(t), 50 + 32.5 * math.sin(t), 2.6), fill='#c99bff')
    return ic


# ---------- Missions ----------

@picto('mission-escort')
def _():
    """Escorte : une charrette bâchée sur deux roues."""
    ic = Icon()
    o = ic.obj()
    o.part(rect(8, 50, 84, 22, 4), 'wood', gloss=False)
    o.part(blob([(12, 52), (14, 30), (30, 18), (50, 15), (70, 18), (86, 30), (88, 52)], sharp=(0, 6), t=1), 'cream', gloss=False)
    for x in (30, 50, 70):
        o.detail(openpath([(x, 18), (x, 52)]), stroke=(dark(col('cream'), 0.3), 2), clip=1, opacity=0.6)
    for x in (28, 72):
        o.part(circle(x, 78, 13), 'brown', gloss=False)
        o.part(circle(x, 78, 4.5), 'gold', cast=False)
        i = len(o.parts) - 2
        for a in range(0, 180, 45):
            t = math.radians(a)
            o.detail(openpath([(x - 9 * math.cos(t), 78 - 9 * math.sin(t)), (x + 9 * math.cos(t), 78 + 9 * math.sin(t))]), stroke=(lite(col('brown'), 0.3), 2), clip=i, opacity=0.7)
    return ic


def bow(ic, cx, cy, s, rot=0, arrow=True):
    o = ic.obj()
    limb = [(cx - 4, cy - s), (cx + s * 0.35, cy - s * 0.6), (cx + s * 0.45, cy), (cx + s * 0.35, cy + s * 0.6), (cx - 4, cy + s)]
    o.part(band(limb, 8).rot(rot, cx, cy), 'wood', gloss=False)
    o.detail(openpath([(cx - 4, cy - s), (cx - 4, cy + s)]).rot(rot, cx, cy), stroke=('#f4efff', 1.8))
    if arrow:
        a = ic.obj()
        a.part(rect(cx - s * 0.7, cy - 2, s * 1.55, 4, 2).rot(rot, cx, cy), 'wood', gloss=False)
        a.part(rpoly([(cx + s * 0.8, cy - 7), (cx + s * 1.08, cy), (cx + s * 0.8, cy + 7)], 1.5).rot(rot, cx, cy), ('metal', 'steel'), gloss=False)
        a.part(rpoly([(cx - s * 0.72, cy - 2), (cx - s * 0.56, cy - 10), (cx - s * 0.44, cy - 2)], 1).rot(rot, cx, cy), 'red', gloss=False)
        a.part(rpoly([(cx - s * 0.72, cy + 2), (cx - s * 0.56, cy + 10), (cx - s * 0.44, cy + 2)], 1).rot(rot, cx, cy), 'red', gloss=False)
    return o


@picto('mission-hunt')
def _():
    ic = Icon()
    bow(ic, 42, 50, 40, rot=-45)
    return ic


@picto('mission-patrol')
def _():
    """Patrouille : une lanterne allumée."""
    ic = Icon()
    ic.glow(50, 56, 34, '#ffd36b', 0.8)
    o = ic.obj()
    o.part(ring(50, 14, 9, 5), 'iron', gloss=False)
    o.part(rpoly([(28, 30), (72, 30), (66, 20), (34, 20)], 3), 'dark', gloss=False)
    o.part(rect(30, 28, 40, 52, 6), [(0, '#fff7c2'), (0.5, '#ffc93a'), (1, '#ff8a1a')], gloss=False)
    o.detail(blob([(50, 40), (57, 56), (50, 68), (43, 56)], sharp=(0,), t=1), fill='#ffffff', opacity=0.9, clip=2)
    for x in (30, 50, 70):
        o.part(rect(x - 3, 28, 6, 52, 2), 'dark', gloss=False, cast=False)
    o.part(rect(24, 78, 52, 12, 4), 'dark', gloss=False)
    return ic


@picto('mission-relic')
def _():
    """Relique : une amulette d'or sertie d'une gemme bleue, sur sa chaîne."""
    ic = Icon()
    o = ic.obj()
    o.detail(openpath(arc_pts(50, 30, 28, 200, 340, 10), smooth=True), stroke=(C['gold'], 3.6))
    o.part(circle(50, 60, 30), 'gold', gloss=False)
    gem(ic, 50, 62, 34, 30, 'azure')
    ic.sparkle(82, 26, 8)
    return ic


@picto('mission-ruins')
def _():
    """Ruines : des colonnes brisées sur un dallage, une herbe qui pousse."""
    ic = Icon()
    o = ic.obj()
    o.part(rect(8, 80, 84, 12, 4), 'stone', gloss=False)
    for x, top in [(24, 18), (50, 40), (76, 28)]:
        o.part(rpoly([(x - 9, 82), (x - 9, top + 4), (x - 3, top), (x + 2, top + 6), (x + 9, top + 2), (x + 9, 82)], [0, 1, 1, 1, 1, 0]), 'cream', gloss=False)
        i = len(o.parts) - 1
        for dx in (-3, 3):
            o.detail(openpath([(x + dx, top + 10), (x + dx, 78)]), stroke=(dark(col('cream'), 0.3), 1.6), clip=i, opacity=0.7)
    o.part(rect(36, 64, 28, 18, 3).rot(-12, 50, 72), lite(col('stone'), 0.2), gloss=False)
    g = ic.obj(shadow=False)
    g.part(blob([(84, 80), (86, 64), (90, 72)], sharp=(0, 1), t=1), 'green', gloss=False)
    g.part(blob([(14, 80), (12, 66), (18, 72)], sharp=(0, 1), t=1), 'green', gloss=False)
    return ic


@picto('mission-siege')
def _():
    """Siège : une catapulte de bois, une pierre dans la cuillère."""
    ic = Icon()
    o = ic.obj()
    o.part(rect(10, 70, 80, 9, 4), 'wood', gloss=False)
    o.part(rpoly([(30, 72), (44, 40), (52, 40), (46, 72)], 2), 'wood', gloss=False)
    o.part(rect(20, 36, 70, 8, 4).rot(-32, 48, 44), lite(col('wood'), 0.1), gloss=False)
    o.part(ellipse(78, 20, 12, 7, -32), dark(col('wood'), 0.2), gloss=False)
    o.part(circle(80, 15, 9), 'stone')
    for x in (22, 78):
        o.part(circle(x, 82, 9), 'brown')
        o.part(circle(x, 82, 3), 'iron', cast=False)
    return ic
