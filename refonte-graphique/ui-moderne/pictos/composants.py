# Les pièces réutilisées par plusieurs pictos : pièce de monnaie, gemme, coffre, épée, écu, flèche de bonus…
# Chaque fonction AJOUTE un objet (ou des morceaux) à un Icon, aux coordonnées données (case de 100).
import math

from lib import (C, Shape, band, blob, circle, col, dark, ellipse, lite, mix, openpath, poly, ring, rect, rpoly,
                 sparkle_shape, star)


def coin(ic, cx=50, cy=50, r=40, color='gold', sign='diamond', edge=True):
    """Une pièce épaisse : tranche, face bombée, filet intérieur, un signe inventé en relief."""
    c = col(color)
    o = ic.obj()
    if edge:
        o.part(ellipse(cx - r * 0.06, cy + r * 0.09, r, r), dark(c, 0.35), gloss=False, bevel=0.6)
    o.part(circle(cx, cy, r * 0.95), c, gloss=False)
    o.part(circle(cx, cy, r * 0.72), [(0, dark(c, 0.12)), (1, lite(c, 0.32))], gloss=False, bevel=0.6, cast=False)
    o.detail(ring(cx, cy, r * 0.75, r * 0.70), fill=dark(c, 0.3), opacity=0.55)
    s = coin_sign(sign, cx, cy, r * 0.42)
    if s is not None:
        o.detail(s.move(-r * 0.035, r * 0.06), fill=dark(c, 0.55), opacity=0.8, blur=1)
        o.detail(s, fill=lite(c, 0.72))
        o.detail(s.move(r * 0.02, -r * 0.02).scale(0.6, 0.6, cx + r * 0.08, cy - r * 0.1), fill='#ffffff', opacity=0.5, blur=1)
    # le reflet en croissant sur le bord haut-droit
    o.detail(crescent(cx, cy, r * 0.9, 0.12, -45), fill='#ffffff', opacity=0.55, blur=1)
    return o


def crescent(cx, cy, r, th=0.15, ang=-45, span=110):
    """Un croissant de lumière collé au bord intérieur d'un disque, centré sur l'angle `ang`."""
    a0, a1 = ang - span / 2, ang + span / 2
    pts = []
    for i in range(13):
        a = math.radians(a0 + (a1 - a0) * i / 12)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    for i in range(12, -1, -1):
        a = math.radians(a0 + (a1 - a0) * i / 12)
        k = 1 - th * math.sin(math.pi * i / 12)
        pts.append((cx + r * k * math.cos(a), cy + r * k * math.sin(a)))
    return blob(pts, sharp=(0, 13), t=0.6)


def coin_sign(sign, cx, cy, s):
    if sign == 'diamond':
        return rpoly([(cx, cy - s), (cx + s * 0.7, cy), (cx, cy + s), (cx - s * 0.7, cy)], s * 0.12)
    if sign == 'star':
        return star(cx, cy, s * 1.05, rr=s * 0.08)
    if sign == 'shield':
        return shield_shape(cx, cy + s * 0.05, s * 1.6, s * 1.9)
    if sign == 'sword':
        # une épée debout : lame pointue, garde, poignée, pommeau
        return (rpoly([(cx - s * 0.2, cy + s * 0.35), (cx - s * 0.2, cy - s * 0.7), (cx, cy - s * 1.05), (cx + s * 0.2, cy - s * 0.7), (cx + s * 0.2, cy + s * 0.35)], s * 0.05)
                + rect(cx - s * 0.62, cy + s * 0.32, s * 1.24, s * 0.26, s * 0.12) + rect(cx - s * 0.13, cy + s * 0.5, s * 0.26, s * 0.42, s * 0.06)
                + circle(cx, cy + s * 0.98, s * 0.17))
    return None


def gem_shape(cx, cy, w, h):
    """Le contour d'une gemme taillée (table en haut, pointe en bas)."""
    return rpoly([(cx - w * 0.28, cy - h * 0.5), (cx + w * 0.28, cy - h * 0.5), (cx + w * 0.5, cy - h * 0.16),
                  (cx, cy + h * 0.5), (cx - w * 0.5, cy - h * 0.16)], [2, 2, 2.5, 3, 2.5])


def gem(ic, cx=50, cy=52, w=78, h=66, color='pink', obj=None):
    """Une gemme taillée à facettes (table, couronne, pavillon), très brillante."""
    c = col(color)
    o = obj or ic.obj()
    o.part(gem_shape(cx, cy, w, h), c, gloss=False, bevel=0.7)
    i = len(o.parts) - 1
    top, mid = cy - h * 0.5, cy - h * 0.16
    # les facettes : des triangles plus clairs / plus sombres (lumière en haut à droite)
    fac = [
        ([(cx - w * 0.28, top), (cx - w * 0.12, mid), (cx - w * 0.5, mid)], lite(c, 0.18)),
        ([(cx - w * 0.28, top), (cx + w * 0.28, top), (cx + w * 0.12, mid), (cx - w * 0.12, mid)], lite(c, 0.55)),
        ([(cx + w * 0.28, top), (cx + w * 0.5, mid), (cx + w * 0.12, mid)], lite(c, 0.72)),
        ([(cx - w * 0.5, mid), (cx - w * 0.12, mid), (cx, cy + h * 0.5)], dark(c, 0.28)),
        ([(cx - w * 0.12, mid), (cx + w * 0.12, mid), (cx, cy + h * 0.5)], lite(c, 0.08)),
        ([(cx + w * 0.12, mid), (cx + w * 0.5, mid), (cx, cy + h * 0.5)], lite(c, 0.35)),
    ]
    for pts, fc in fac:
        o.detail(poly(pts), fill=fc, clip=i, opacity=0.9)
    o.detail(openpath([(cx - w * 0.5, mid), (cx + w * 0.5, mid)]), stroke=(lite(c, 0.8), 1.2), clip=i, opacity=0.7)
    o.detail(ellipse(cx + w * 0.17, top + h * 0.12, w * 0.1, h * 0.05, rot=-20), fill='#ffffff', opacity=0.9, blur=1)
    return o


def shield_shape(cx, cy, w, h):
    """Un écu : haut droit aux coins arrondis, flancs bombés, pointe en bas."""
    x0, x1, y0 = cx - w / 2, cx + w / 2, cy - h / 2
    pts = [(x0, y0), (cx, y0 - h * 0.04), (x1, y0), (x1, cy + h * 0.02), (cx + w * 0.3, cy + h * 0.33), (cx, cy + h / 2),
           (cx - w * 0.3, cy + h * 0.33), (x0, cy + h * 0.02)]
    return blob(pts, sharp=(0, 2, 5), t=0.85)


def arrow_shape(cx, cy, s, up=True):
    """Une grosse flèche (vers le haut ou le bas), bout arrondi."""
    pts = [(cx, cy - s), (cx + s * 0.9, cy - s * 0.05), (cx + s * 0.38, cy - s * 0.05), (cx + s * 0.38, cy + s),
           (cx - s * 0.38, cy + s), (cx - s * 0.38, cy - s * 0.05), (cx - s * 0.9, cy - s * 0.05)]
    sh = rpoly(pts, [s * 0.18, s * 0.14, s * 0.08, s * 0.14, s * 0.14, s * 0.08, s * 0.14])
    return sh if up else sh.scale(1, -1, cx, cy)


def arrow_badge(ic, cx, cy, s, up=True, color=None):
    """La flèche de bonus (verte, vers le haut) ou de malus (rouge, vers le bas), posée sur un coin du picto."""
    o = ic.obj()
    o.part(arrow_shape(cx, cy, s, up), col(color or ('green' if up else 'red')), grad='v')
    return o


def plus_shape(cx, cy, s, t=0.36):
    a = s * t
    return rpoly([(cx - a, cy - s), (cx + a, cy - s), (cx + a, cy - a), (cx + s, cy - a), (cx + s, cy + a), (cx + a, cy + a),
                  (cx + a, cy + s), (cx - a, cy + s), (cx - a, cy + a), (cx - s, cy + a), (cx - s, cy - a), (cx - a, cy - a)],
                 [s * 0.22, s * 0.22, s * 0.06, s * 0.22, s * 0.22, s * 0.06, s * 0.22, s * 0.22, s * 0.06, s * 0.22, s * 0.22, s * 0.06])


def sword(ic, x0, y0, x1, y1, blade='steel', hilt='gold', grip='leather', L=None, wide=1.0, guard=1.0, gem_c='red', obj=None):
    """Une épée de la garde (x0, y0) à la pointe (x1, y1)."""
    ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
    L = math.dist((x0, y0), (x1, y1))
    o = obj or ic.obj()
    bw = 6.2 * wide
    # tout est dessiné à l'horizontale (garde en 0, pointe vers la droite) puis tourné
    blade_s = rpoly([(0, -bw), (L - bw * 2.1, -bw), (L, 0), (L - bw * 2.1, bw), (0, bw)], [0, 1.2, 1.0, 1.2, 0])
    grip_s = rect(-17, -3.4, 15, 6.8, 2.2)
    pommel = circle(-19.5, 0, 5)
    gu = 15 * guard
    guard_s = rpoly([(-3, -gu), (3, -gu + 1.5), (3, gu - 1.5), (-3, gu)], 2.6)
    T = lambda s: s.rot(ang, 0, 0).move(x0, y0)
    o.part(T(grip_s), grip, gloss=False)
    o.part(T(pommel), hilt)
    o.part(T(blade_s), ('metal', blade) if blade in ('steel', 'iron') else blade, gloss=False)
    bi = len(o.parts) - 1
    o.part(T(guard_s), hilt)
    # l'arête du tranchant (une ligne claire) et le fil sombre en dessous
    o.detail(T(openpath([(4, -bw * 0.15), (L - bw * 2.3, -bw * 0.15)])), stroke=('#ffffff', 1.6), clip=bi, opacity=0.8)
    o.detail(T(openpath([(4, bw * 0.45), (L - bw * 2.5, bw * 0.45)])), stroke=(dark(col(blade), 0.4), 1.4), clip=bi, opacity=0.6)
    if gem_c:
        o.part(T(circle(0, 0, 3.6)), gem_c, cast=False)
    return o


def chest(ic, cx=50, cy=56, w=80, h=56, state='closed', wood='wood', metal='gold', obj=None):
    """Un coffre au trésor : caisse, couvercle bombé, cerclages et serrure. state : closed / open / ready."""
    o = obj or ic.obj()
    x0, y0 = cx - w / 2, cy - h * 0.12
    body = rect(x0, y0, w, h * 0.62, 4)
    lid_h = h * 0.42
    if state == 'open':
        # le couvercle ouvert, renversé en arrière ; l'or déborde
        lid = rpoly([(x0 + 2, y0 - lid_h * 0.95), (x0 + w - 2, y0 - lid_h * 0.95), (x0 + w + 1, y0 - 2), (x0 - 1, y0 - 2)], [6, 6, 2, 2])
        o.part(lid, dark(col(wood), 0.15), gloss=False)
        o.part(rect(x0 + 4, y0 - lid_h * 0.65, w - 8, lid_h * 0.6, 3), dark(col(wood), 0.55), gloss=False, bevel=0.3, cast=False)
        o.part(blob([(x0 + 6, y0 + 4), (x0 + w * 0.2, y0 - 9), (x0 + w * 0.45, y0 - 13), (x0 + w * 0.7, y0 - 10), (x0 + w - 6, y0 + 2)]), 'gold')
        o.part(body, wood, gloss=False)
    else:
        lift = 6 if state == 'ready' else 0
        lid = Shape([((x0, y0 - lift), [])])
        lid = blob([(x0, y0 - lift), (x0 + 1, y0 - lid_h * 0.7 - lift), (x0 + w * 0.2, y0 - lid_h - lift), (cx, y0 - lid_h * 1.06 - lift),
                    (x0 + w * 0.8, y0 - lid_h - lift), (x0 + w - 1, y0 - lid_h * 0.7 - lift), (x0 + w, y0 - lift)], sharp=(0, 6), t=0.9)
        if state == 'ready':
            ic.glow(cx, y0 - 2, w * 0.55, '#ffe680', 0.9)
        o.part(body, wood, gloss=False)
        if state == 'ready':
            o.part(rect(x0 + 3, y0 - lift - 1, w - 6, lift + 3, 2), ('flat', '#fff4b8'), gloss=False, bevel=0, cast=False)
        o.part(lid, lite(col(wood), 0.1), gloss=False)
    bi = 0
    m = col(metal)
    # les cerclages de métal (verticaux), la bordure du bas, la serrure
    for fx in (0.17, 0.83):
        x = x0 + w * fx
        o.part(rect(x - 4.5, y0 - (lid_h * 0.95 if state != 'open' else 0) - (6 if state == 'ready' else 0), 9, h * 0.62 + (lid_h * 0.95 if state != 'open' else 0) + (6 if state == 'ready' else 0), 2.5), m, gloss=False, bevel=0.8)
    o.part(rect(x0, y0 + h * 0.62 - 7, w, 7, 3), m, gloss=False)
    lock_y = y0 - (6 if state == 'ready' else 0)
    if state != 'open':
        o.part(rpoly([(cx - 8, lock_y - 6), (cx + 8, lock_y - 6), (cx + 8, lock_y + 8), (cx, lock_y + 13), (cx - 8, lock_y + 8)], 3), m)
        o.detail(circle(cx, lock_y + 1.5, 2.4) + rect(cx - 1.1, lock_y + 2, 2.2, 5, 1), fill=dark(m, 0.6))
    else:
        o.part(rpoly([(cx - 8, y0 - 1), (cx + 8, y0 - 1), (cx + 8, y0 + 10), (cx, y0 + 15), (cx - 8, y0 + 10)], 3), m)
    # le bois : des lattes (traits sombres doux)
    for fy in (0.33,):
        o.detail(openpath([(x0 + w * 0.26, y0 + h * 0.62 * fy), (x0 + w * 0.74, y0 + h * 0.62 * fy)]), stroke=(dark(col(wood), 0.4), 1.6), clip=bi, opacity=0.6)
    return o


def scroll(ic, cx=50, cy=50, w=70, h=56, paper='paper', seal='violet', rot=-12):
    """Un parchemin roulé aux deux bouts, avec un sceau."""
    o = ic.obj()
    sheet = rect(cx - w * 0.38, cy - h * 0.42, w * 0.76, h * 0.84, 3)
    o.part(sheet.rot(rot, cx, cy), paper, gloss=False)
    for sy in (-1, 1):
        r = ellipse(cx, cy + sy * h * 0.44, w * 0.5, 6.5).rot(rot, cx, cy)
        o.part(r, lite(col(paper), 0.05) if sy < 0 else dark(col(paper), 0.08), gloss=False)
        o.part(circle(cx - w * 0.5, cy + sy * h * 0.44, 6).rot(rot, cx, cy), dark(col(paper), 0.22), gloss=False, cast=False)
    for k in (-0.18, 0, 0.18):
        o.detail(openpath([(cx - w * 0.24, cy + h * k), (cx + w * 0.24, cy + h * k)]).rot(rot, cx, cy), stroke=(dark(col(paper), 0.35), 2), clip=0, opacity=0.5)
    if seal:
        s = ic.obj()
        sx, sy2 = cx + w * 0.26, cy + h * 0.26
        s.part(blob([(sx + 9 * math.cos(math.radians(a)) * (1 + 0.08 * (i % 2)), sy2 + 9 * math.sin(math.radians(a)) * (1 + 0.08 * (i % 2))) for i, a in enumerate(range(0, 360, 36))]), seal)
        s.detail(star(sx, sy2, 4.5, rr=0.6), fill=lite(col(seal), 0.5))
    return o


def sparkles(ic, pts):
    for x, y, r in pts:
        ic.sparkle(x, y, r)


# ---------- La pierre des boutons (« Pierre de l'arène », src/game/ui/buttons.ts) ----------
# basalte : arête claire, haut, bas, épaisseur ; l'or brûle dedans (braise, gemme d'ambre)
BASALT = ['#8a86a8', '#4d4a6a', '#2e2c47', '#1f1d33']
EMBER = '#ffb53a'


def basalt(k=0.0):
    """Le dégradé d'une pierre de basalte, clair en haut à droite (k > 0 : plus claire)."""
    return [(0, mix('#7d7a9c', '#fff6cf', 0.08 + k)), (0.45, lite(BASALT[1], k)), (1, BASALT[2])]


def rune(cx, cy, r):
    """Le signe gravé de l'arène (inventé) : un losange et ses quatre éclats."""
    sh = rpoly([(cx, cy - r), (cx + r * 0.62, cy), (cx, cy + r), (cx - r * 0.62, cy)], r * 0.12)
    for dx, dy in ((-1, 0), (1, 0)):
        sh = sh + circle(cx + dx * r * 1.2, cy + dy * r, r * 0.2)
    return sh


def stone_chest(ic, state='closed', cx=50):
    """Le coffre de l'arène : caisse et couvercle de basalte taillé à facettes, ferrures d'or, un signe gravé où brûle
    la lumière d'or (comme les boutons de pierre), serrure à gemme d'ambre.
    state : closed (fermé, la braise dort), ready (le couvercle se soulève, la lumière fuit par la fente), open (ouvert,
    l'or déborde et luit)."""
    x0, x1 = cx - 38, cx + 38
    yb, ye = 56, 89                     # la caisse : du joint au sol
    lift = 7 if state == 'ready' else 0
    if state in ('ready', 'open'):
        ic.glow(cx, yb - 4, 46, '#ffd36a', 0.9)
    o = ic.obj()
    if state == 'open':
        # le couvercle renversé en arrière (on voit son dessous sombre), l'or qui déborde
        o.part(rpoly([(x0 + 5, 16), (x1 - 5, 16), (x1 + 1, yb - 5), (x0 - 1, yb - 5)], [7, 7, 2, 2]), basalt(0.06), gloss=False)
        o.part(rpoly([(x0 + 9, 22), (x1 - 9, 22), (x1 - 5, yb - 8), (x0 + 5, yb - 8)], 4), [(0, '#3a3858'), (1, '#1f1d33')], gloss=False, bevel=0.3, cast=False)
        o.part(blob([(x0 + 4, yb + 2), (x0 + 12, yb - 10), (cx - 10, yb - 17), (cx + 6, yb - 15), (x1 - 13, yb - 11), (x1 - 4, yb + 1)]),
               [(0, '#fff6c0'), (0.45, '#ffcf3a'), (1, '#e58a00')], gloss=False)
    o.part(rect(x0, yb, x1 - x0, ye - yb, 5), basalt(), gloss=False)
    bi = len(o.parts) - 1
    ly = yb - lift
    if state != 'open':
        if state == 'ready':
            # la fente qui luit, sous le couvercle soulevé
            o.part(rect(x0 + 3, ly - 2, x1 - x0 - 6, lift + 4, 2), [(0, '#fffbe0'), (1, '#ffd25a')], gloss=False, bevel=0, cast=False)
        # le couvercle taillé : un flanc, une face du dessus plus claire (la lumière vient d'en haut à droite)
        lid = rpoly([(x0, ly), (x0 + 3, ly - 17), (x0 + 15, ly - 28), (x1 - 15, ly - 28), (x1 - 3, ly - 17), (x1, ly)], [2, 5, 6, 6, 5, 2])
        o.part(lid, basalt(0.1), gloss=False)
        li = len(o.parts) - 1
        o.detail(rpoly([(x0 + 6, ly - 17), (x0 + 16, ly - 26), (x1 - 16, ly - 26), (x1 - 6, ly - 17)], 3), fill='#ffffff', clip=li, opacity=0.16)
        o.detail(openpath([(x0 + 16, ly - 26), (x1 - 16, ly - 26), (x1 - 6, ly - 17)]), stroke=('#fff6cf', 1.6), clip=li, opacity=0.45, blur=1)
        # les coins d'or du couvercle
        for pts in ([(x0 + 1, ly - 19), (x0 + 13, ly - 29), (x0 + 19, ly - 29), (x0 + 4, ly - 12)],
                    [(x1 - 1, ly - 19), (x1 - 4, ly - 12), (x1 - 19, ly - 29), (x1 - 13, ly - 29)]):
            o.part(rpoly(pts, 2.5), ('metal', 'gold'), gloss=False, bevel=0.5)
    # le panneau creusé dans la caisse, et son signe où brûle l'or
    o.detail(rect(x0 + 11, yb + 10, x1 - x0 - 22, ye - yb - 17, 4), fill='#15132a', clip=bi, opacity=0.5, blur=1)
    hot = state != 'closed'
    o.detail(rune(cx, yb + 18.5, 6.5), fill='#ffb53a', clip=bi, opacity=0.9 if hot else 0.55, blur=2)
    o.detail(rune(cx, yb + 18.5, 5), fill='#fff1b8' if hot else '#ffcf5a', clip=bi, opacity=1 if hot else 0.85)
    # les ferrures d'or : le cerclage du couvercle, les coins du bas
    if state != 'open':
        o.part(rect(x0 - 2, ly - 7, x1 - x0 + 4, 8, 4), ('metal', 'gold'), gloss=False, bevel=0.7)
    else:
        o.part(rect(x0 - 2, yb - 3, x1 - x0 + 4, 7, 3.5), ('metal', 'gold'), gloss=False, bevel=0.7)
    for pts in ([(x0 - 1, ye - 13), (x0 + 8, ye - 5), (x0 + 15, ye + 1), (x0 - 1, ye + 1)],
                [(x1 + 1, ye - 13), (x1 + 1, ye + 1), (x1 - 15, ye + 1), (x1 - 8, ye - 5)]):
        o.part(rpoly(pts, 3), ('metal', 'gold'), gloss=False, bevel=0.6)
    # la serrure : un écu d'or sur le joint, une gemme d'ambre
    sy = ly - 3 if state != 'open' else yb
    o.part(rpoly([(cx - 9, sy - 7), (cx + 9, sy - 7), (cx + 9, sy + 6), (cx, sy + 13), (cx - 9, sy + 6)], 3.5), ('metal', 'gold'), bevel=0.8)
    if state != 'open':
        o.part(circle(cx, sy + 1, 4.6), ('radial', EMBER if state == 'closed' else '#ffe27a'), gloss=False, bevel=0.4, cast=False)
        o.detail(circle(cx + 1.5, sy - 0.6, 1.4), fill='#fffbe6', opacity=0.95)
    return o
