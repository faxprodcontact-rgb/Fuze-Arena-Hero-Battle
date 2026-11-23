# Cyclope (myths-3, terre, guerrier épique) : le minotaure. Tête de taureau brune, grandes cornes blanches, anneau d'or
# au nez ; torse nu massif, sangles de cuir, pagne, sabots. Pose : jambes écartées, il tient à deux mains sa grande
# hache à double tranchant, basse, en travers du corps, prête à frapper.
from kit import *

ORIGIN = (24, 45)
FUR = Ramp('#2e160a', '#4e2814', '#74401e', '#965a2e', '#b47644')
HORN = Ramp('#8a826e', '#bab29a', '#e8e2cc', '#ffffff', '#ffffff')
HOOF = Ramp('#0e0a0a', '#1e1614', '#2e2420', '#443630', '#5a4a42')
HEAD = check_head([r.ljust(21, '.') for r in [
    "....KK.........KK",
    "...KfFK.......KfFK",
    "...KffKKKKKKKKKffK",
    "....KKFfFfFfFfFKK",
    "..KKffffffffffffKK",
    ".KffffffffffffffffK",
    ".KfFfffffffffffffffK",
    ".KffffffKffffKffffK",
    ".KffffffbyKffbyKfffK",
    ".KffffffffffffffffK",
    ".KfffffffffMMMMMMMMK",
    ".KffffffffMMMMMMMMMMK",
    ".KffffffffMMKMMMKMMMK",
    ".KffffffffMMMMMMMMMMK",
    "..KffffffffMMgggMMMK",
    "...KffffffffKgKgKKK",
    "....KfffffffKgggK",
    ".....KKKKKKKKKKK",
]])
HEAD_C = {'K': INK, 'n': '#e8e2cc', 'f': '#74401e', 'F': '#965a2e', 'b': '#ffffff', 'y': '#c01a10', 'M': '#b47644',
          'g': '#eab036'}
HEAD_BLINK = {'b': 'f', 'y': 'f'}


def draw(c, t):
    b = BREATH[t]
    D = ((24, 32), (21, 40), (30, 42))      # bras droit (devant) : le manche, en haut
    G = ((56, 31), (59, 40), (48, 47))      # bras gauche (derrière) : le manche, en bas
    arm(c, b, *G, FUR, r=(6.4, 5.8, 5.2))
    arm(c, b, *D, FUR, r=(6.4, 5.8, 5.2))
    legs(c, 'large', FUR, r=(7, 6.2, 5.6))
    for (x, y) in ((25, 68), (55, 68)):
        c.part(c.poly([(x - 5, y), (x + 5, y), (x + 6, 72), (x - 5, 72)]), HOOF, 'ink', band=1)
    c.part(c.poly([(27, 50), (54, 50), (57, 61), (24, 61)]), LEATHER, 'ink')
    neck(c, b, FUR, 6, HEAD)
    torso(c, b, FUR, w=1.2)
    abs_lines(c, b, FUR, w=1.2)
    c.line(26, 32 - b, 52, 48, LEATHER.base), c.line(27, 32 - b, 53, 48, LEATHER.shade)
    c.part(c.rect(26, 47, 55, 51), LEATHER, 'ink', band=1)
    c.sprite(30, 6 - b, HEAD, HEAD_C, HEAD_BLINK if t == BLINK else None)
    # les grandes cornes blanches, qui partent des côtés du crâne et montent
    c.part(c.limb([(33, 12 - b, 2.8), (24, 9 - b, 2.4), (19, 3 - b, 1.9), (20, -3 - b, 1.2)]), HORN, 'ink')
    c.part(c.limb([(46, 11 - b, 2.8), (55, 8 - b, 2.4), (60, 2 - b, 1.9), (59, -4 - b, 1.2)]), HORN, 'ink')
    arm_front(c, b, *D, FUR, r=(6.4, 5.8, 5.2))
    # la hache : le manche en travers, les deux fers en bas, à droite
    c.part(c.limb([(16, 37 - b, 1.6), (66, 56 - b, 1.6)]), WOOD, 'ink')
    for sgn in (-1, 1):
        c.part(c.poly([(64, 55 - b), (64 + sgn * 5, 46 - b + sgn * 2), (64 + sgn * 9, 56 - b + sgn * 6), (64 + sgn * 3, 60 - b)]), STEEL, 'ink', band=1)
    fist(c, (48, 47), FUR, b)
    fist(c, (31, 41), FUR, b)
