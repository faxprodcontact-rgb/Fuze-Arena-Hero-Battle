# Les 12 blasons de guilde (emblem-0 … emblem-11) : un écu, un champ de couleur, un signe inventé d'or ou de blanc.
#   python3 refonte-graphique/pixel/ui/pictos/guilde.py [noms…]
from pictolib import *

ECUS = {
    'pointe': poly([(5, 3), (26, 3), (26, 15), (21, 23), (15.5, 28), (10, 23), (5, 15)]),
    'rond': cercle(15.5, 15.5, 12.5),
    'bannière': poly([(6, 3), (25, 3), (25, 28), (15.5, 23), (6, 28)]),
    'ogive': poly([(5, 3), (26, 3), (26, 17), (15.5, 28), (5, 17)]) & ~(rect(0, 0, 31, 3)) | rrect(5, 3, 26, 10, 4),
}


def signe(nom):
    c = (15.5, 14.5)
    if nom == 'etoile':
        return etoile(15.5, 15, 7, 3)
    if nom == 'lune':
        return cercle(15.5, 14.5, 6.5) & ~cercle(18.5, 12.5, 5.5)
    if nom == 'flamme':
        return poly([(15.5, 6), (20, 13), (20, 18), (15.5, 22), (11, 18), (11, 13), (13, 15)]) & ~poly([(15.5, 13), (17.5, 17), (15.5, 20), (13.5, 17)])
    if nom == 'vague':
        return ligne([(9, 16), (11, 13), (14, 13), (15.5, 16), (17, 19), (20, 19), (22, 16)], 3) | cercle(22, 13.5, 1.6)
    if nom == 'feuille':
        return poly([(10, 21), (11, 13), (16, 8), (22, 7), (21, 13), (16, 19)]) & ~ligne([(11, 20), (19, 10)], 1)
    if nom == 'couronne':
        return poly([(9, 19), (9, 10), (12.5, 14), (15.5, 8), (18.5, 14), (22, 10), (22, 19)])
    if nom == 'tour':
        return rect(11, 10, 20, 21) & ~rect(13, 10, 13, 11) & ~rect(15, 10, 16, 11) & ~rect(18, 10, 18, 11) & ~rrect(14, 16, 17, 22, 1)
    if nom == 'epee':
        return poly([(14.5, 18), (14.5, 8), (15.5, 6), (16.5, 8), (16.5, 18)]) | rect(11, 17, 20, 18) | rect(15, 19, 16, 21) | rect(14, 22, 17, 23)
    if nom == 'eclair':
        return poly([(17, 6), (10, 16), (15, 16), (13, 23), (21, 12), (16, 12), (19, 6)])
    if nom == 'coeur':
        return coeur(15.5, 14, 6)
    if nom == 'ailes':
        return poly([(15.5, 18), (9, 9), (13, 10), (15.5, 13), (18, 10), (22, 9)]) | poly([(15.5, 18), (8, 13), (12, 13)]) | poly([(15.5, 18), (23, 13), (19, 13)])
    if nom == 'losange':
        return poly([(15.5, 7), (21, 14.5), (15.5, 22), (10, 14.5)]) & ~poly([(15.5, 11), (18, 14.5), (15.5, 18), (13, 14.5)])
    if nom == 'soleil':
        return cercle(15.5, 14.5, 4.5) | anneau(15.5, 14.5, 7.5, 6.3) & ~((np.abs(X - 15.5) < 1.2) | (np.abs(Y - 14.5) < 1.2))
    raise KeyError(nom)


# (forme de l'écu, champ, bordure, signe, couleur du signe)
BLASONS = [
    ('pointe', 'rouge', 'or', 'couronne', 'or'),
    ('rond', 'bleu', 'argent', 'vague', 'blanc'),
    ('bannière', 'vert', 'or', 'feuille', 'or'),
    ('ogive', 'violet', 'or', 'lune', 'creme'),
    ('pointe', 'orange', 'bronze', 'flamme', 'or'),
    ('rond', 'cyan', 'or', 'etoile', 'blanc'),
    ('bannière', 'nuit', 'or', 'eclair', 'or'),
    ('ogive', 'rose', 'argent', 'ailes', 'blanc'),
    ('pointe', 'pierre', 'or', 'tour', 'creme'),
    ('rond', 'rouge', 'argent', 'coeur', 'blanc'),
    ('bannière', 'ciel', 'or', 'soleil', 'or'),
    ('ogive', 'vert', 'argent', 'losange', 'blanc'),
]


def blason(p, forme, champ, bord, sg, coul):
    ecu = ECUS[forme]
    p.part(ecu, bord, R=2.5, lo=1, hi=4)
    dedans = ronge(ecu, 2)
    p.part(dedans, champ, R=4, lo=1, hi=3, ombre=False)
    p.creuse(dedans & ~decale(dedans, -1, 1), 1)
    m = signe(sg) & ronge(dedans, 1)
    p.part(m, coul, R=2, lo=2, hi=4)


for i, b in enumerate(BLASONS):
    picto(f'emblem-{i}')(lambda p, b=b: blason(p, *b))

if __name__ == '__main__':
    import pictolib
    for k in [k for k in REGISTRE if k.startswith('emblem-')]:
        REGISTRE[k].__module__ = '__main__'
    lance()
