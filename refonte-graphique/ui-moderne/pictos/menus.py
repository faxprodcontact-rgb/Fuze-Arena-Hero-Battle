# Les pictos des menus : barre des onglets, médaillons de l'accueil, boutons, objets du quotidien (coffres, cadenas,
# horloge…), étoiles des héros.
import math

from composants import arrow_shape, basalt, chest, stone_chest, coin, crescent, gem, plus_shape, shield_shape, sparkles, sword
from lib import (C, Icon, arc_pts, band, blob, circle, col, dark, ellipse, lite, mix, openpath, picto, poly, rect, ring,
                 rpoly, sparkle_shape, star)
from monnaies import heart


@picto('heroes')
def _():
    """Les héros : un heaume de chevalier doré à crête rouge, fente des yeux, trous d'aération."""
    ic = Icon()
    o = ic.obj()
    o.part(blob([(50, 4), (60, 10), (63, 24), (50, 30), (37, 24), (40, 10)], t=1), 'red', gloss=False)
    o.part(blob([(18, 54), (20, 30), (34, 16), (50, 12), (66, 16), (80, 30), (82, 54), (78, 82), (60, 92), (40, 92), (22, 82)], t=1), 'gold', gloss=False)
    o.part(rect(24, 42, 52, 12, 6), 'night', gloss=False, bevel=0.4)
    o.detail(openpath([(50, 14), (50, 40)]), stroke=(dark(col('gold'), 0.3), 2.4), clip=1, opacity=0.6)
    o.detail(openpath([(50, 56), (50, 88)]), stroke=(dark(col('gold'), 0.3), 2.4), clip=1, opacity=0.6)
    for x, y in [(60, 64), (68, 64), (60, 73), (68, 73), (32, 64), (40, 64), (32, 73), (40, 73)]:
        o.detail(circle(x, y, 2.2), fill=dark(col('gold'), 0.6))
    o.detail(ellipse(66, 28, 6, 10, 25), fill='#ffffff', clip=1, opacity=0.6, blur=1)
    return ic


@picto('summon')
def _():
    """Invoquer : un tourbillon magique violet dans un anneau d'or."""
    ic = Icon()
    ic.glow(50, 50, 48, '#b06bff', 0.55)
    o = ic.obj()
    o.part(circle(50, 50, 40), 'gold', gloss=False)
    o.part(circle(50, 50, 32), [(0, '#e7b6ff'), (0.45, '#8b4dff'), (1, '#2c0d6e')], gloss=False, grad='v')
    # les bras du tourbillon
    for k in range(3):
        pts = [(50 + r * math.cos(math.radians(a + k * 120)), 50 + r * math.sin(math.radians(a + k * 120))) for r, a in [(4, 0), (12, 50), (20, 100), (28, 150)]]
        o.detail(openpath(pts, smooth=True), stroke=('#f2d6ff', 4.2), clip=1, opacity=0.75)
    o.detail(circle(50, 50, 7), fill='#ffffff', clip=1, opacity=0.9, blur=2)
    sparkles(ic, [(84, 16, 9), (14, 82, 6)])
    return ic


@picto('adventure')
def _():
    """L'aventure : une carte dépliée en trois volets, un chemin et une épingle rouge."""
    ic = Icon()
    o = ic.obj()
    xs = [12, 37, 63, 88]
    for i in range(3):
        top = 20 if i % 2 == 0 else 14
        bot = 86 if i % 2 == 0 else 80
        o.part(poly([(xs[i], top), (xs[i + 1], 14 if i % 2 == 0 else 20), (xs[i + 1], 80 if i % 2 == 0 else 86), (xs[i], bot)]),
               ['#fff1cf', '#f1d79d', '#e9c784'][i], gloss=False, cast=False)
    o.detail(blob([(18, 40), (30, 30), (44, 36), (40, 52), (24, 56)], t=1), fill='#7fd36a', opacity=0.9)
    o.detail(blob([(60, 56), (76, 50), (84, 62), (72, 74), (58, 70)], t=1), fill='#7fd36a', opacity=0.9)
    o.detail(openpath([(20, 70), (32, 64), (44, 70), (56, 60), (66, 44)], smooth=True), stroke=('#c0503a', 3), opacity=0.8)
    p = ic.obj()
    p.part(blob([(70, 46), (60, 30), (62, 18), (70, 13), (78, 18), (80, 30)], sharp=(0,), t=1), 'red', gloss=False)
    p.detail(circle(70, 25, 4.5), fill='#ffffff', opacity=0.9)
    return ic


@picto('guild')
def _():
    """La guilde : une bannière bleue suspendue à une hampe d'or, une couronne brodée."""
    ic = Icon()
    o = ic.obj()
    o.part(rpoly([(22, 16), (78, 16), (78, 88), (50, 74), (22, 88)], [2, 2, 2, 3, 2]), 'azure', gloss=False)
    o.detail(rpoly([(28, 20), (72, 20), (72, 80), (50, 68), (28, 80)], 1), stroke=(lite(col('azure'), 0.45), 2), opacity=0.7)
    o.part(rect(12, 10, 76, 9, 4.5), 'gold')
    for x in (12, 88):
        o.part(circle(x, 14.5, 6), 'gold')
    cr = ic.obj(shadow=False)
    cr.part(rpoly([(34, 56), (34, 34), (42, 44), (50, 30), (58, 44), (66, 34), (66, 56)], [2, 1.5, 1.5, 1.5, 1.5, 1.5, 2]), 'gold', gloss=False)
    return ic


@picto('shop')
def _():
    """La boutique : un sac de marchand corail, anse d'or, une gemme en fermoir."""
    ic = Icon()
    o = ic.obj()
    o.part(ring(50, 30, 17, 10.5), 'gold', gloss=False)
    o.part(rpoly([(16, 34), (84, 34), (90, 88), (10, 88)], [5, 5, 7, 7]), 'coral', gloss=False)
    o.part(rect(16, 34, 68, 12, 5), dark(col('coral'), 0.1), gloss=False)
    gem(ic, 50, 64, 30, 24, 'azure')
    return ic


@picto('bag')
def _():
    """Le sac : un sac à dos d'aventurier en cuir, rabat et boucle d'or."""
    ic = Icon()
    o = ic.obj()
    o.part(ring(50, 20, 11, 6), 'leather', gloss=False)
    o.part(blob([(16, 50), (20, 26), (50, 18), (80, 26), (84, 50), (84, 88), (16, 88)], sharp=(5, 6), t=0.9), 'leather', gloss=False)
    o.part(rpoly([(26, 62), (74, 62), (74, 86), (26, 86)], 5), dark(col('leather'), 0.12), gloss=False)
    o.part(blob([(18, 46), (22, 28), (50, 21), (78, 28), (82, 46), (66, 56), (34, 56)], t=1), lite(col('leather'), 0.12), gloss=False)
    o.part(rect(44, 44, 12, 20, 3), 'gold')
    o.detail(rect(47.5, 49, 5, 8, 2), fill=dark(col('gold'), 0.45))
    return ic


@picto('quests')
def _():
    """Les quêtes : une feuille sur une planchette, et une coche verte."""
    ic = Icon()
    o = ic.obj()
    o.part(rect(16, 14, 60, 76, 7), 'wood', gloss=False)
    o.part(rect(22, 22, 48, 62, 3), 'paper', gloss=False)
    o.part(rect(34, 8, 24, 12, 4), 'iron')
    for y in (36, 48, 60):
        o.detail(openpath([(30, y), (60, y)]), stroke=(dark(col('paper'), 0.4), 3), clip=1, opacity=0.55)
    k = ic.obj()
    k.part(check_shape(66, 70, 26), 'green', grad='v', gloss=False)
    return ic


def check_shape(cx, cy, s):
    """Une coche épaisse."""
    pts = [(cx - s, cy - s * 0.05), (cx - s * 0.6, cy - s * 0.45), (cx - s * 0.25, cy - s * 0.1), (cx + s * 0.55, cy - s * 0.9),
           (cx + s * 0.95, cy - s * 0.5), (cx - s * 0.25, cy + s * 0.7)]
    return rpoly(pts, [s * 0.16, s * 0.16, s * 0.05, s * 0.16, s * 0.16, s * 0.12])


@picto('mail')
def _():
    """Le courrier : une enveloppe blanche au sceau rouge."""
    ic = Icon()
    o = ic.obj()
    o.part(rect(10, 24, 80, 56, 6), 'white', gloss=False)
    o.part(rpoly([(10, 26), (90, 26), (50, 58)], [5, 5, 6]), lite(col('white'), 0.3), gloss=False)
    o.detail(openpath([(14, 76), (40, 54)]), stroke=(dark(col('white'), 0.3), 2), clip=0, opacity=0.6)
    o.detail(openpath([(86, 76), (60, 54)]), stroke=(dark(col('white'), 0.3), 2), clip=0, opacity=0.6)
    s = ic.obj()
    s.part(blob([(50 + 11 * math.cos(math.radians(a)) * (1.08 if i % 2 else 1), 56 + 11 * math.sin(math.radians(a)) * (1.08 if i % 2 else 1)) for i, a in enumerate(range(0, 360, 30))]), 'red')
    s.detail(heart(50, 56, 7), fill=lite(col('red'), 0.45))
    return ic


@picto('friends')
def _():
    """Les amis : deux personnes côte à côte (bustes)."""
    ic = Icon()
    for cx, c, s, dy in [(34, 'azure', 0.9, -4), (62, 'orange', 1.0, 4)]:
        o = ic.obj()
        o.part(blob([(cx - 26 * s, 90), (cx - 24 * s, 70 + dy), (cx - 12 * s, 58 + dy), (cx + 12 * s, 58 + dy), (cx + 24 * s, 70 + dy), (cx + 26 * s, 90)], sharp=(0, 5), t=1), c, gloss=False)
        o.part(circle(cx, 40 + dy, 16 * s), 'skin')
        o.part(blob([(cx - 16 * s, 40 + dy), (cx - 14 * s, 28 + dy), (cx, 22 + dy), (cx + 14 * s, 28 + dy), (cx + 16 * s, 38 + dy), (cx + 6 * s, 32 + dy), (cx - 6 * s, 34 + dy)], t=1),
               '#5a3a8a' if c == 'azure' else '#7a3b20', gloss=False)
    return ic


@picto('chat')
def _():
    """Le tchat : une bulle bleue, trois points."""
    ic = Icon()
    o = ic.obj()
    o.part(blob([(14, 46), (20, 24), (50, 16), (80, 24), (86, 46), (80, 66), (54, 74), (36, 74), (20, 90), (24, 70), (16, 60)], sharp=(7, 8, 9), t=1), 'azure', gloss=False)
    for x in (34, 50, 66):
        o.detail(circle(x, 46, 6), fill='#ffffff')
    o.detail(ellipse(66, 27, 10, 4, -12), fill='#ffffff', opacity=0.55, blur=1, clip=0)
    return ic


def gear_shape(cx, cy, R, r, n=8, hole=0):
    pts = []
    for i in range(n):
        a = 360 / n * i
        for da, rad in [(-11, R), (11, R), (360 / n / 2 - 9, r), (360 / n / 2 + 9, r)]:
            t = math.radians(a + da)
            pts.append((cx + rad * math.cos(t), cy + rad * math.sin(t)))
    g = rpoly(pts, 2)
    return g.hole(circle(cx, cy, hole)) if hole else g


@picto('settings')
def _():
    """Les réglages : un engrenage d'acier."""
    ic = Icon()
    o = ic.obj()
    o.part(gear_shape(50, 50, 42, 32, 8, 12), ('metal', 'steel'), gloss=False)
    o.detail(ring(50, 50, 22, 18), fill=dark(col('steel'), 0.35), clip=0, opacity=0.45)
    return ic


@picto('ranking')
def _():
    """Le classement : un podium à trois marches, une étoile d'or sur la plus haute."""
    ic = Icon()
    o = ic.obj()
    o.part(rect(8, 58, 30, 32, 4), 'azure', gloss=False)
    o.part(rect(62, 66, 30, 24, 4), 'coral', gloss=False)
    o.part(rect(34, 46, 32, 44, 4), 'gold', gloss=False)
    s = ic.obj()
    s.part(star(50, 26, 19), 'gold', gloss=False)
    s.detail(ellipse(55, 20, 4, 2.6, -30), fill='#ffffff', opacity=0.8, blur=1)
    ic.sparkle(80, 18, 7)
    return ic


@picto('calendar')
def _():
    """Le calendrier : une page à anneaux, entête rouge, une coche verte."""
    ic = Icon()
    o = ic.obj()
    o.part(rect(12, 18, 76, 72, 8), 'white', gloss=False)
    o.part(rpoly([(12, 18), (88, 18), (88, 38), (12, 38)], [8, 8, 0, 0]), 'red', gloss=False)
    for x in (32, 68):
        o.part(rect(x - 4, 8, 8, 18, 4), 'steel')
    k = ic.obj(shadow=False)
    k.part(check_shape(52, 66, 22), 'green', grad='v', gloss=False)
    return ic


@picto('campaign')
def _():
    """La campagne : un drapeau rouge flottant, frappé d'une étoile, sur une hampe."""
    ic = Icon()
    o = ic.obj()
    o.part(rect(18, 10, 8, 82, 4), 'wood')
    o.part(blob([(24, 14), (50, 10), (70, 18), (90, 14), (84, 34), (90, 54), (70, 58), (48, 50), (24, 56)], sharp=(0, 8), t=1), 'red', gloss=False)
    o.detail(star(55, 33, 11, rr=1), fill='#ffe27a')
    o.part(circle(22, 10, 6), 'gold', cast=False)
    return ic


@picto('missions')
def _():
    """Les missions : une boussole dorée, aiguille rouge."""
    ic = Icon()
    o = ic.obj()
    o.part(rect(44, 4, 12, 12, 4), 'gold')
    o.part(circle(50, 54, 40), 'gold', gloss=False)
    o.part(circle(50, 54, 31), [(0, '#ffffff'), (1, '#e6e2f6')], gloss=False)
    for a in range(0, 360, 90):
        t = math.radians(a)
        o.detail(circle(50 + 25 * math.cos(t), 54 + 25 * math.sin(t), 2.4), fill=dark(col('white'), 0.45), clip=1)
    n = ic.obj(shadow=False)
    n.part(rpoly([(50, 54), (64, 36), (56, 60)], 1.5).rot(0), 'red', gloss=False)
    n.part(rpoly([(50, 54), (36, 72), (44, 48)], 1.5), 'steel', gloss=False, cast=False)
    n.part(circle(50, 54, 4.5), 'gold')
    return ic


def ticket_shape(x, y, w, h, notch=7):
    """Un billet : rectangle arrondi aux encoches rondes au milieu des petits côtés."""
    return rect(x, y, w, h, 7)


@picto('pass')
def _():
    """Le passe : un billet violet à étoile d'or."""
    ic = Icon()
    o = ic.obj()
    o.part(rect(8, 24, 84, 52, 9).rot(-10), 'violet', gloss=False)
    o.detail(openpath([(64, 28), (68, 72)]).rot(-10), stroke=(lite(col('violet'), 0.5), 2.5), clip=0, opacity=0.7)
    s = ic.obj(shadow=False)
    s.part(star(40, 52, 17).rot(-10, 40, 52), 'gold', gloss=False)
    for k in (-1, 1):
        o.detail(circle(66 + k * 1, 50 + k * 30, 0.1), fill='#ffffff')
    return ic


def gift(ic, cx=50, cy=56, w=76, h=58, box='red', rib='gold'):
    o = ic.obj()
    o.part(blob([(cx, cy - h * 0.42), (cx - w * 0.36, cy - h * 0.72), (cx - w * 0.3, cy - h * 0.42)], sharp=(0,), t=1), rib, gloss=False)
    o.part(blob([(cx, cy - h * 0.42), (cx + w * 0.36, cy - h * 0.72), (cx + w * 0.3, cy - h * 0.42)], sharp=(0,), t=1), rib, gloss=False)
    o.part(rect(cx - w * 0.44, cy - h * 0.1, w * 0.88, h * 0.6, 5), dark(col(box), 0.08), gloss=False)
    o.part(rect(cx - w / 2, cy - h * 0.42, w, h * 0.34, 6), box, gloss=False)
    o.part(rect(cx - 6, cy - h * 0.42, 12, h * 0.92, 2), rib, gloss=False, cast=False)
    return o


@picto('gift')
def _():
    ic = Icon()
    gift(ic, 50, 58, 76, 64, 'red', 'gold')
    ic.sparkle(84, 18, 8)
    return ic


@picto('ad')
def _():
    """La publicité : un écran vert arrondi et le triangle de lecture."""
    ic = Icon()
    o = ic.obj()
    o.part(rect(8, 18, 84, 64, 14), 'green', gloss=False)
    o.detail(rpoly([(40, 34), (66, 50), (40, 66)], 4), fill='#ffffff')
    o.detail(ellipse(72, 26, 12, 4, -10), fill='#ffffff', opacity=0.5, blur=1, clip=0)
    return ic


def crown_shape(cx, cy, w, h):
    x0, x1, y1 = cx - w / 2, cx + w / 2, cy + h / 2
    pts = [(x0 + w * 0.06, y1), (x0, cy - h * 0.38), (x0 + w * 0.28, cy - h * 0.05), (cx, cy - h * 0.55), (x1 - w * 0.28, cy - h * 0.05),
           (x1, cy - h * 0.38), (x1 - w * 0.06, y1)]
    return rpoly(pts, [3, 2.5, 2, 2.5, 2, 2.5, 3])


@picto('crown')
def _():
    ic = Icon()
    o = ic.obj()
    o.part(crown_shape(50, 52, 80, 56), 'gold', gloss=False)
    o.part(rect(13, 68, 74, 14, 5), 'goldD', gloss=False)
    for x, c in [(30, 'azure'), (50, 'red'), (70, 'green')]:
        o.part(circle(x, 75, 4.6), c, cast=False)
    for x, y in [(10, 32), (50, 22), (90, 32)]:
        o.part(circle(x, y, 5.5), 'gold')
    ic.sparkle(80, 14, 7)
    return ic


@picto('badge')
def _():
    """Une médaille : ruban bleu et rouge, disque d'or à étoile."""
    ic = Icon()
    r = ic.obj()
    r.part(rpoly([(28, 6), (46, 6), (58, 46), (44, 52)], 2), 'azure', gloss=False)
    r.part(rpoly([(54, 6), (72, 6), (56, 52), (42, 46)], 2), 'red', gloss=False)
    coin(ic, 50, 64, 28, 'gold', 'star', edge=False)
    return ic


@picto('avatarFrame')
def _():
    """Un cadre de portrait : un anneau d'or serti de trois gemmes."""
    ic = Icon()
    o = ic.obj()
    o.part(ring(50, 52, 40, 29), 'gold', gloss=False)
    o.detail(ring(50, 52, 35.5, 33.5), fill=dark(col('gold'), 0.3), clip=0, opacity=0.5)
    for a, c in [(-90, 'red'), (150, 'azure'), (30, 'green')]:
        t = math.radians(a)
        o.part(circle(50 + 35 * math.cos(t), 52 + 35 * math.sin(t), 7), c)
    return ic


@picto('trophy')
def _():
    """Le trophée : une coupe d'or à deux anses sur un socle."""
    ic = Icon()
    o = ic.obj()
    o.part(ring(22, 34, 14, 8).scale(1, 1.1, 22, 34), 'gold', gloss=False)
    o.part(ring(78, 34, 14, 8).scale(1, 1.1, 78, 34), 'gold', gloss=False)
    o.part(rect(28, 82, 44, 12, 4), 'wood')
    o.part(rpoly([(42, 66), (58, 66), (62, 84), (38, 84)], 2), 'goldD')
    o.part(blob([(24, 14), (76, 14), (74, 40), (64, 60), (50, 68), (36, 60), (26, 40)], sharp=(0, 1), t=1), 'gold', gloss=False)
    o.detail(star(50, 38, 11, rr=1), fill=lite(col('gold'), 0.7))
    o.detail(ellipse(66, 28, 5, 10, 15), fill='#ffffff', opacity=0.7, blur=1, clip=4)
    ic.sparkle(86, 12, 8)
    return ic


@picto('defeat')
def _():
    """La défaite : un écu d'acier brisé en deux, les morceaux écartés, la cassure sombre."""
    ic = Icon()
    left = [(14, 16), (48, 10), (42, 32), (54, 48), (44, 64), (50, 90), (30, 78), (16, 56)]
    right = [(52, 10), (86, 16), (84, 56), (70, 78), (54, 90), (48, 64), (58, 48), (46, 32)]
    for pts, rot, dx, sh in [(left, -9, -3, (0, 1, 2, 3, 4, 5)), (right, 9, 3, (0, 1, 4, 5, 6, 7))]:
        o = ic.obj()
        o.part(blob(pts, sharp=sh, t=0.9).rot(rot, 50, 92).move(dx, 0), 'iron', gloss=False)
        o.detail(blob(pts, sharp=sh, t=0.9).rot(rot, 50, 92).move(dx, 0).scale(0.7, 0.7, 50 + dx * 8, 44), stroke=(lite(col('iron'), 0.35), 2.2), clip=0, opacity=0.5)
    return ic


@picto('clock')
def _():
    ic = Icon()
    o = ic.obj()
    for x in (24, 76):
        o.part(circle(x, 20, 10), 'gold')
    o.part(circle(50, 54, 40), 'gold', gloss=False)
    o.part(circle(50, 54, 31), [(0, '#ffffff'), (1, '#e4e0f4')], gloss=False)
    for a in range(0, 360, 30):
        t = math.radians(a)
        r0 = 25 if a % 90 else 22
        o.detail(openpath([(50 + r0 * math.cos(t), 54 + r0 * math.sin(t)), (50 + 28 * math.cos(t), 54 + 28 * math.sin(t))]), stroke=('#6d6794', 2.4 if a % 90 == 0 else 1.6), clip=3)
    o.detail(openpath([(50, 54), (50, 34)]), stroke=(C['night'], 4.4))
    o.detail(openpath([(50, 54), (64, 62)]), stroke=(C['red'], 3.6))
    o.detail(circle(50, 54, 4), fill=C['night'])
    return ic


@picto('hourglass')
def _():
    """Le sablier de l'arène : socle et chapeau de basalte cerclés d'or, montants d'or, verre ambré, sable d'or qui luit."""
    ic = Icon()
    ic.glow(50, 68, 30, '#ffc94d', 0.6)
    o = ic.obj()
    glass = blob([(31, 19), (69, 19), (67, 36), (54, 50), (67, 64), (69, 81), (31, 81), (33, 64), (46, 50), (33, 36)], sharp=(0, 1, 6, 7), t=0.9)
    o.part(glass, [(0, '#fff8e6'), (0.55, '#e9dcc2'), (1, '#b9a98c')], gloss=False, bevel=0.7)
    # le sable : en haut (il baisse), le filet qui tombe, le tas d'en bas qui luit
    o.detail(blob([(37, 31), (63, 31), (56, 42), (50, 47), (44, 42)], t=1), fill='#ffcf3a', clip=0)
    o.detail(openpath([(50, 46), (50, 66)]), stroke=('#ffcf3a', 2.4), clip=0)
    o.detail(blob([(33, 81), (67, 81), (64, 70), (50, 59), (36, 70)], t=1), fill='#f6a417', clip=0)
    o.detail(blob([(40, 80), (62, 80), (59, 72), (50, 64), (43, 72)], t=1), fill='#ffe58a', clip=0, opacity=0.85, blur=2)
    o.detail(ellipse(61, 29, 2.3, 7, 22), fill='#ffffff', opacity=0.85, clip=0)
    o.detail(ellipse(60, 72, 1.8, 5, -22), fill='#ffffff', opacity=0.5, clip=0)
    for x in (23, 77):
        o.part(rect(x - 3.5, 15, 7, 70, 3.5), ('metal', 'gold'), gloss=False, bevel=0.6, cast=False)
    for y, rim in ((5, 17), (82, 78)):
        o.part(rect(13, y, 74, 13, 6.5), basalt(), gloss=False)
        o.part(rect(18, rim, 64, 5.5, 2.7), ('metal', 'gold'), gloss=False, bevel=0.5)
    # deux petites gemmes d'ambre au milieu du socle et du chapeau
    for y in (11.5, 88.5):
        o.part(circle(50, y, 3.4), ('radial', '#f29a12'), gloss=False, bevel=0.3, cast=False)
    return ic


def lock_shape():
    return rect(18, 42, 64, 50, 10)


@picto('lock')
def _():
    """Le cadenas : anse d'acier, corps d'or, trou de serrure."""
    ic = Icon()
    o = ic.obj()
    o.part(blob([(26, 50), (26, 30), (36, 12), (50, 8), (64, 12), (74, 30), (74, 50), (64, 50), (64, 32), (58, 20), (50, 18), (42, 20), (36, 32), (36, 50)],
                sharp=(0, 6, 7, 13), t=1), ('metal', 'steel'), gloss=False)
    o.part(lock_shape(), 'gold', gloss=False)
    o.detail(circle(50, 62, 6.5) + rpoly([(46, 64), (54, 64), (56, 80), (44, 80)], 2), fill=dark(col('gold'), 0.62))
    o.detail(ellipse(70, 50, 6, 3, -20), fill='#ffffff', opacity=0.7, blur=1, clip=1)
    return ic


@picto('copy')
def _():
    """Copier : deux cartes l'une sur l'autre."""
    ic = Icon()
    a = ic.obj()
    a.part(rect(12, 10, 52, 62, 9), 'sky', gloss=False)
    b = ic.obj()
    b.part(rect(36, 30, 52, 62, 9), 'white', gloss=False)
    for y in (48, 60, 72):
        b.detail(openpath([(46, y), (76 if y < 72 else 64, y)]), stroke=('#b7b0d8', 3.4))
    return ic


@picto('dice')
def _():
    """Le dé : un cube blanc vu en biais, points rouges."""
    ic = Icon()
    o = ic.obj()
    top = rpoly([(50, 10), (88, 28), (50, 46), (12, 28)], 6)
    left = rpoly([(12, 28), (50, 46), (50, 92), (12, 72)], 6)
    right = rpoly([(50, 46), (88, 28), (88, 72), (50, 92)], 6)
    o.part(left, dark(col('white'), 0.14), gloss=False, bevel=0.5)
    o.part(right, lite(col('white'), 0.2), gloss=False, bevel=0.5, cast=False)
    o.part(top, '#ffffff', gloss=False, bevel=0.5, cast=False)
    o.detail(ellipse(50, 28, 6, 3.4), fill='red')
    for x, y in [(22, 44), (31, 60), (40, 76)]:
        o.detail(ellipse(x, y, 3.3, 4.4, 25), fill=dark(col('red'), 0.1))
    for x, y in [(62, 50), (76, 70), (76, 44), (62, 76)]:
        o.detail(ellipse(x, y, 3.3, 4.4, -25), fill='red')
    return ic


@picto('hand')
def _():
    """La main du tutoriel (le « curseur ») : l'index levé sur le bord gauche, le pouce sorti, trois doigts repliés."""
    ic = Icon()
    o = ic.obj()
    sk = col('skin')
    o.part(rect(32, 82, 44, 14, 4), 'azure', gloss=False)
    o.part(blob([(28, 52), (14, 46), (10, 54), (18, 66), (30, 76)], t=1), dark(sk, 0.06), gloss=False)
    o.part(rect(28, 46, 50, 40, 12), sk, gloss=False, cast=False)
    for x in (51, 62, 73):
        o.part(ellipse(x, 52, 6.4, 8), sk, gloss=False)
    o.part(rect(29, 8, 15, 52, 7.5), sk, gloss=False)
    o.detail(ellipse(39, 15, 2.4, 4.5), fill='#ffffff', opacity=0.6)
    return ic


@picto('chestClosed')
def _():
    ic = Icon()
    stone_chest(ic, 'closed')
    return ic


@picto('chestReady')
def _():
    ic = Icon()
    stone_chest(ic, 'ready')
    sparkles(ic, [(86, 18, 8), (14, 26, 5.5)])
    return ic


@picto('chestOpen')
def _():
    ic = Icon()
    stone_chest(ic, 'open')
    sparkles(ic, [(74, 12, 7)])
    return ic


@picto('questChest')
def _():
    ic = Icon()
    chest(ic, 50, 60, 80, 56, 'closed', wood='azure', metal='gold')
    ic.sparkle(84, 18, 8)
    return ic


@picto('cardBack')
def _():
    """Le dos d'une carte de héros : violet, bordure d'or, un losange lumineux."""
    ic = Icon()
    o = ic.obj()
    o.part(rect(18, 6, 64, 88, 9), 'gold', gloss=False)
    o.part(rect(24, 12, 52, 76, 6), 'violet', gloss=False, cast=False)
    o.detail(rpoly([(50, 26), (64, 50), (50, 74), (36, 50)], 3), fill='#e4c8ff')
    o.detail(rpoly([(50, 34), (58, 50), (50, 66), (42, 50)], 2), fill='#ffffff', opacity=0.9)
    return ic


@picto('unknownHero')
def _():
    """Un adversaire inconnu : une silhouette encapuchonnée, deux yeux qui luisent."""
    ic = Icon()
    o = ic.obj()
    o.part(blob([(14, 92), (22, 56), (30, 26), (50, 8), (70, 26), (78, 56), (86, 92)], sharp=(0, 6), t=1), 'violet', gloss=False)
    o.part(blob([(32, 64), (34, 40), (50, 28), (66, 40), (68, 64), (50, 72)], t=1), ('flat', '#1a0f38'), gloss=False, bevel=0.3)
    o.detail(ellipse(43, 50, 3.6, 2.6), fill='#7ff3ff')
    o.detail(ellipse(57, 50, 3.6, 2.6), fill='#7ff3ff')
    o.detail(ellipse(43, 50, 7, 5), fill='#7ff3ff', opacity=0.4, blur=2)
    o.detail(ellipse(57, 50, 7, 5), fill='#7ff3ff', opacity=0.4, blur=2)
    return ic


@picto('allElements')
def _():
    """Tous les éléments : quatre perles (feu, vent, eau, terre) en losange."""
    from lib import ELEMENT
    ic = Icon()
    for (x, y), e in zip([(50, 22), (78, 50), (50, 78), (22, 50)], ['fire', 'wind', 'water', 'earth']):
        o = ic.obj()
        o.part(circle(x, y, 17), ('radial', ELEMENT[e]), gloss=False)
        o.detail(ellipse(x + 5, y - 6, 5, 3, -35), fill='#ffffff', opacity=0.85, blur=1)
    return ic


@picto('rebirth')
def _():
    """La renaissance : une plume de phénix, de feu."""
    ic = Icon()
    o = ic.obj()
    feather = blob([(18, 88), (30, 62), (44, 36), (62, 16), (86, 8), (82, 30), (70, 52), (50, 70), (30, 80)], sharp=(0, 4), t=1)
    o.part(feather, [(0, '#fff07a'), (0.35, '#ffa12e'), (0.7, '#ff4a3a'), (1, '#a3165a')], gloss=False)
    o.detail(openpath([(18, 88), (40, 64), (60, 38), (82, 12)], smooth=True), stroke=('#fff3c0', 2.6), clip=0, opacity=0.9)
    for t in (0.35, 0.55, 0.72):
        x, y = 18 + 64 * t, 88 - 76 * t
        o.detail(openpath([(x, y), (x + 9, y + 6)]), stroke=(dark('#ff6a2e', 0.3), 1.8), clip=0, opacity=0.6)
    sparkles(ic, [(30, 24, 8), (84, 50, 6)])
    return ic


@picto('foundry')
def _():
    """La fonderie (27/11, à la place du « recyclage ») : un creuset de fonte penché verse un filet de métal en fusion
    dans un moule à lingot ; quelques étincelles. Fondre un objet rend de la poussière."""
    ic = Icon()
    ic.glow(62, 74, 30, '#ffb02e', 0.45)
    MOLTEN = [(0, '#fff6b0'), (0.35, '#ffc23a'), (0.75, '#ff7a1e'), (1, '#d8401e')]
    # le moule (fonte sombre) et le métal qui l'emplit
    m = ic.obj()
    m.part(rpoly([(34, 70), (94, 70), (88, 92), (40, 92)], 4), ('metal', 'iron'), gloss=False)
    m.part(rpoly([(40, 69), (88, 69), (85, 81), (43, 81)], 2), [(0, '#fff6b0'), (0.45, '#ffc23a'), (1, '#ff7a1e')], gloss=False)
    m.detail(ellipse(70, 72.5, 10, 1.6), fill='#fffbe0', opacity=0.8)
    # le filet qui coule de la lèvre du creuset jusqu'au moule
    f = ic.obj()
    f.part(band([(48, 38), (55, 45), (60, 56), (61, 66), (61, 74)], 7.5), [(0, '#fff3a0'), (0.5, '#ffc23a'), (1, '#ff8a1e')], gloss=False)
    # le creuset penché (bord épais, métal fondu à la lèvre)
    c = ic.obj()
    pot = rpoly([(10, 16), (46, 16), (42, 50), (16, 50)], 7).rot(-38, 30, 34)
    c.part(pot, ('metal', 'iron'), gloss=False)
    c.part(rpoly([(7, 12), (49, 12), (49, 20), (7, 20)], 4).rot(-38, 30, 34), dark(col('iron'), 0.25), gloss=False)
    c.part(ellipse(28, 16.5, 16, 5).rot(-38, 30, 34), [(0, '#fff6b0'), (0.5, '#ffc23a'), (1, '#ff7a1e')], gloss=False)
    ic.sparkle(80, 56, 7, color='#ffd36b')
    ic.sparkle(26, 72, 5, color='#ffb02e')
    return ic


@picto('forge')
def _():
    """La forge : une enclume et un marteau."""
    ic = Icon()
    a = ic.obj()
    a.part(rpoly([(30, 70), (70, 70), (76, 90), (24, 90)], 3), 'dark', gloss=False)
    a.part(rpoly([(38, 56), (62, 56), (60, 72), (40, 72)], 2), dark(col('iron'), 0.2), gloss=False)
    a.part(blob([(8, 44), (28, 44), (88, 44), (88, 58), (66, 60), (34, 60), (22, 54)], sharp=(1, 2, 3, 4, 5), t=1), ('metal', 'iron'), gloss=False)
    h = ic.obj()
    h.part(rect(58, 4, 8, 44, 3).rot(38, 62, 26), 'wood')
    h.part(rect(44, 6, 34, 16, 4).rot(38, 62, 26), ('metal', 'steel'), gloss=False)
    ic.sparkle(30, 30, 8, color='#ffd36b')
    ic.sparkle(18, 20, 5, color='#ffd36b')
    return ic


@picto('fusion')
def _():
    """La fusion : deux moitiés de sphère (violet et or) qui se rejoignent dans une lumière."""
    ic = Icon()
    ic.glow(50, 50, 44, '#ffe7a0', 0.6)
    for side, c in [(-1, 'violet'), (1, 'gold')]:
        o = ic.obj()
        pts = arc_pts(50 + side * 4, 50, 36, 90 if side < 0 else -90, 270 if side < 0 else 90, 16)
        o.part(rpoly(pts, 0.8), ('radial', c), gloss=False)
    ic.sparkle(50, 50, 14)
    sparkles(ic, [(84, 16, 7)])
    return ic


@picto('armory')
def _():
    """L'armurerie : un râtelier de bois avec une épée et un écu."""
    ic = Icon()
    o = ic.obj()
    o.part(rect(10, 10, 80, 82, 7), 'wood', gloss=False)
    o.part(rect(17, 17, 66, 68, 4), dark(col('wood'), 0.45), gloss=False, bevel=0.4)
    sword(ic, 34, 76, 34, 20, wide=0.85, guard=0.8)
    s = ic.obj()
    s.part(shield_shape(64, 54, 30, 38), 'red', gloss=False)
    s.detail(rpoly([(64, 42), (71, 53), (64, 66), (57, 53)], 1.5), fill='#ffe27a')
    return ic


@picto('star')
def _():
    ic = Icon()
    o = ic.obj()
    o.part(star(50, 54, 44, rr=4), 'gold', gloss=False)
    o.detail(star(50, 54, 44, rr=4).scale(0.55, 0.55, 50, 54), fill=lite(col('gold'), 0.35), opacity=0.6, blur=2)
    o.detail(ellipse(62, 36, 6, 3.5, -30), fill='#ffffff', opacity=0.85, blur=1)
    return ic


@picto('starEmpty')
def _():
    ic = Icon()
    o = ic.obj()
    o.part(star(50, 54, 44, rr=4), '#5d5590', gloss=False, bevel=0.6)
    o.detail(star(50, 54, 30, rr=3), fill='#3e3670', opacity=0.8, blur=1)
    return ic


@picto('revive')
def _():
    """Un héros se relève : une croix verte lumineuse."""
    ic = Icon()
    ic.glow(50, 50, 48, '#9dffb0', 0.6)
    o = ic.obj()
    o.part(plus_shape(50, 52, 38), 'green', gloss=False)
    o.detail(ellipse(62, 24, 4, 7, 20), fill='#ffffff', opacity=0.7, blur=1, clip=0)
    sparkles(ic, [(84, 18, 8), (16, 80, 6)])
    return ic
