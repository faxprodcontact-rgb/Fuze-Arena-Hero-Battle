# La chouette du tutoriel, en 4 poses : explique (une aile levée), contente (yeux plissés, ailes ouvertes),
# montre (une aile tendue vers la droite ; le jeu la retourne quand elle est à droite), surprise (yeux ronds, bec ouvert).
import math

from lib import (Icon, blob, circle, col, dark, ellipse, lite, openpath, picto, poly, rect, rpoly)

PLUME = '#b07a48'
VENTRE = '#ffe9c4'
BEC = '#ffae2e'


def chouette(pose):
    ic = Icon()
    o = ic.obj()
    # les pattes
    for x in (40, 60):
        o.part(rpoly([(x - 7, 88), (x + 7, 88), (x + 5, 94), (x - 5, 94)], 2.5), BEC, gloss=False)
    # les ailes (derrière le corps quand elles sont baissées)
    wl = {'explain': 'down', 'happy': 'up', 'point': 'down', 'surprised': 'up'}[pose]
    wr = {'explain': 'up', 'happy': 'up', 'point': 'out', 'surprised': 'up'}[pose]

    def aile(side, how):
        x = 50 + side * 28
        if how == 'down':
            sh = blob([(x, 48), (x + side * 12, 60), (x + side * 10, 80), (x - side * 2, 86), (x - side * 6, 70)], t=1)
        elif how == 'up':
            sh = blob([(x - side * 2, 62), (x + side * 10, 50), (x + side * 18, 32), (x + side * 16, 24), (x + side * 6, 34), (x - side * 6, 50)], t=1)
        else:  # tendue vers la droite, le bout en pointe
            sh = blob([(x - 6, 54), (x + 6, 46), (x + 20, 44), (x + 22, 50), (x + 18, 56), (x + 4, 64)], sharp=(3,), t=1)
        return sh

    o.part(aile(-1, wl), dark(PLUME, 0.1), gloss=False)
    o.part(aile(1, wr), dark(PLUME, 0.1), gloss=False)
    # le corps, les aigrettes
    o.part(blob([(26, 22), (36, 30), (50, 28), (64, 30), (74, 22), (76, 40), (80, 60), (72, 82), (50, 90), (28, 82), (20, 60), (24, 40)], sharp=(0, 4), t=1), PLUME, gloss=False)
    bi = len(o.parts) - 1
    o.part(blob([(34, 60), (50, 54), (66, 60), (64, 78), (50, 86), (36, 78)], t=1), VENTRE, gloss=False, bevel=0.5)
    vi = len(o.parts) - 1
    for x, y in [(44, 66), (56, 66), (50, 74), (42, 78), (58, 78)]:
        o.detail(openpath([(x - 3.5, y), (x, y + 3), (x + 3.5, y)], smooth=True), stroke=(dark(VENTRE, 0.3), 1.8), clip=vi, opacity=0.8)
    # le masque du visage (deux disques clairs)
    for x in (39, 61):
        o.part(circle(x, 44, 13), lite(PLUME, 0.55), gloss=False, bevel=0.4)
    # les yeux
    for x in (39, 61):
        if pose == 'happy':
            o.detail(openpath([(x - 7, 46), (x, 40), (x + 7, 46)], smooth=True), stroke=('#2a1748', 3.4))
        else:
            r = 10 if pose == 'surprised' else 9
            o.part(circle(x, 44, r), '#ffffff', gloss=False, bevel=0.4)
            pr = 4.4 if pose == 'surprised' else 5.6
            dx = 2 if pose == 'point' else 0
            o.detail(circle(x + dx, 45, pr), fill='#2a1748')
            o.detail(circle(x + dx + 1.8, 43, 1.8), fill='#ffffff')
    if pose == 'happy':
        for x in (30, 70):
            o.detail(ellipse(x, 54, 5, 3), fill='#ff8aa0', opacity=0.7, blur=1)
    # le bec
    if pose in ('surprised', 'explain'):
        o.part(rpoly([(45, 52), (55, 52), (50, 58)], 2), BEC, gloss=False)
        o.part(ellipse(50, 62, 4, 3 if pose == 'explain' else 4.5), '#c0392b', gloss=False, bevel=0.2, cast=False)
    else:
        o.part(rpoly([(45, 52), (55, 52), (50, 62)], 2), BEC, gloss=False)
    # la tête : un reflet doux
    o.detail(ellipse(64, 28, 6, 3, -20), fill='#ffffff', opacity=0.45, blur=1, clip=bi)
    return ic


for _p in ('explain', 'happy', 'point', 'surprised'):
    picto('owl-' + _p)(lambda _p=_p: chouette(_p))
