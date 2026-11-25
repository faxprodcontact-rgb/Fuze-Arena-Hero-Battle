# Onglets de la barre du bas, médaillons de l'accueil, barre du haut, coffres, sablier, récompenses :
#   python3 refonte-graphique/pixel/ui/pictos/menus.py [noms…]
from pictolib import *


def spirale(cx, cy, r0, r1, tours=1.6, w=2, a0=0.0):
    pts = []
    for i in range(60):
        t = i / 59
        a = a0 + t * tours * 2 * np.pi
        r = r0 + (r1 - r0) * t
        pts.append((cx + r * np.cos(a), cy + r * np.sin(a)))
    return ligne(pts, w)


# ---------- la barre du bas ----------

@picto('campaign')
def campaign(p):
    """Campagne : un drapeau rouge planté (la conquête), qui flotte vers la droite."""
    p.part(ellipse(9, 28, 6, 1.8), 'vert', lo=1, hi=3)
    p.part(rect(7, 4, 8, 28), 'bois', R=1, lo=1, hi=3)
    p.part(cercle(7.5, 3.5, 1.8), 'or', R=1.5, lo=2, hi=4)
    flag = poly([(9, 5), (15, 4), (21, 6), (28, 4), (26, 10), (28, 17), (21, 19), (15, 17), (9, 18)])
    p.part(flag, 'rouge', R=3, lo=1, hi=4)
    p.creuse(ellipse(15, 11, 1, 5) & flag, 1)            # le pli du tissu
    p.relief(etoile(20, 11.5, 4.2, 1.6, 4) & flag, 2)


@picto('heroes')
def heroes(p):
    """Héros : un casque de héros à crête rouge, de face."""
    p.part(ellipse(15.5, 9, 4, 7) & (Y <= 11) | ellipse(15.5, 5.5, 9, 3.5) & (Y <= 6), 'rouge', R=2.5, lo=1, hi=4)
    casque = ellipse(15.5, 17, 10.5, 11) & (Y <= 28) & (Y >= 7)
    p.part(casque, 'or', R=3.5, lo=1, hi=4)
    fente = rect(8, 15, 23, 17) | rect(14, 15, 17, 28)
    p.plat(fente & casque, 'nuit', 0)
    p.eclaire(ligne([(15.5, 7), (15.5, 13)]) & casque, 1)   # l'arête du casque
    p.etincelle(24, 9)


@picto('summon')
def summon(p):
    """Invoquer : un portail rond, cerclé d'or, où tourne la magie."""
    p.part(cercle(15.5, 16, 13), 'or', R=2.5, lo=1, hi=4)
    fond = cercle(15.5, 16, 10)
    p.part(fond, 'violet', mode='boule', R=11, centre=(18, 13), lo=0, hi=3, ombre=False)
    p.eclaire(spirale(15.5, 16, 1, 9, 1.4, 2, 0.5) & fond, 1)
    p.plat(cercle(15.5, 16, 2.2), 'mauve', 4)
    p.eclat(15, 15); p.eclat(16, 16)
    p.etincelle(26, 5, True)


@picto('adventure')
def adventure(p):
    """Aventure : une carte pliée en trois, un chemin pointillé jusqu'à un repère rouge."""
    g = 'parchemin'
    p.part(poly([(3, 7), (12, 4), (12, 25), (3, 28)]), g, mode='plat', lo=2, hi=2)
    p.part(poly([(12, 4), (20, 7), (20, 28), (12, 25)]), g, mode='plat', lo=3, hi=3, ombre=False)
    p.part(poly([(20, 7), (28, 4), (28, 25), (20, 28)]), g, mode='plat', lo=2, hi=2, ombre=False)
    p.plat(ellipse(7, 12, 3, 3) & poly([(3, 7), (12, 4), (12, 25), (3, 28)]), 'vert', 3)
    p.plat(ellipse(24, 20, 3, 2.5), 'ciel', 3)
    p.plat(ellipse(16, 13, 2.5, 2), 'vert', 3)
    for x, y in ((6, 23), (8, 21), (10, 19), (13, 19), (15, 21), (18, 21), (20, 18)):
        p.eclat(x, y, '#b4542e')
    m = cercle(23.5, 11, 3.5) | poly([(20.5, 12), (26.5, 12), (23.5, 17)])
    p.part(m, 'rouge', R=2, lo=1, hi=4)
    p.plat(cercle(23.5, 11, 1), 'rouge', 0)


@picto('guild')
def guild(p):
    """Guilde : une bannière bleue suspendue, un signe d'or."""
    p.part(ligne([(4, 4), (27, 4)], 2), 'bois', R=1, lo=1, hi=3)
    p.part(cercle(3.5, 4.5, 1.8) | cercle(27.5, 4.5, 1.8), 'or', R=1.5, lo=2, hi=4)
    ban = poly([(7, 6), (24, 6), (24, 27), (15.5, 22), (7, 27)])
    p.part(ban, 'bleu', R=3, lo=1, hi=4)
    signe = poly([(11, 10), (13, 13), (15.5, 9), (18, 13), (20, 10), (20, 17), (11, 17)])
    p.part(signe, 'or', R=1.5, lo=2, hi=4)


# ---------- les médaillons ----------

@picto('mail')
def mail(p):
    env = rrect(3, 8, 28, 25, 2)
    p.part(env, 'blanc', mode='plat', lo=2, hi=3)
    rabat = poly([(3, 8), (28, 8), (15.5, 19)])
    p.part(rabat, 'blanc', mode='plat', lo=3, hi=4)
    p.creuse(ligne([(3, 25), (12, 17)]) | ligne([(28, 25), (19, 17)]), 1)
    p.part(cercle(15.5, 18.5, 3.8), 'rouge', R=2.5, lo=1, hi=4)
    p.relief(cercle(15.5, 18.5, 1.2), 1)


@picto('quests')
def quests(p):
    """Quêtes du jour : une feuille de parchemin et une grande coche verte."""
    f = rrect(5, 3, 24, 28, 2)
    p.part(f, 'parchemin', mode='plat', lo=2, hi=3)
    for y in (8, 12, 16):
        p.creuse(rect(9, y, 20, y), 1)
    coche = ligne([(12, 20), (17, 25), (28, 12)], 4)
    p.part(coche, 'vert', R=1.8, lo=1, hi=4)


@picto('missions')
def missions(p):
    """Missions : une boussole."""
    p.part(cercle(15.5, 16, 13), 'or', R=2.5, lo=1, hi=4)
    cad = cercle(15.5, 16, 10)
    p.part(cad, 'creme', mode='plat', lo=3, hi=4, ombre=False)
    p.creuse(cad & ~decale(cad, -1, 1), 1)
    p.part(poly([(21.5, 9.5), (17, 17.5), (14, 14.5)]), 'rouge', mode='plat', lo=3, hi=3)
    p.part(poly([(9.5, 22.5), (14, 14.5), (17, 17.5)]), 'bleu', mode='plat', lo=2, hi=2)
    p.plat(cercle(15.5, 16, 1), 'or', 4)
    p.part(rect(14, 1, 17, 3), 'or', lo=2, hi=4)


@picto('shop')
def shop(p):
    """Boutique : un sac d'achat rouge, une pièce d'or dessus."""
    p.part(anneau(15.5, 11, 6.5, 4.5) & (Y <= 11), 'or', R=1.5, lo=1, hi=4)
    sac = poly([(5, 11), (26, 11), (28, 28), (3, 28)])
    p.part(sac, 'rouge', R=3, lo=1, hi=4)
    p.part(rect(5, 11, 26, 13), 'rouge', mode='plat', lo=3, hi=3, ombre=False)
    p.part(cercle(15.5, 20.5, 4.5), 'or', R=2, lo=1, hi=4)
    p.relief(poly([(15.5, 18), (17.5, 20.5), (15.5, 23), (13.5, 20.5)]), 1)


@picto('pass')
def pass_(p):
    """Passe : un billet violet à étoile d'or."""
    m = rrect(2, 8, 29, 24, 2) & ~cercle(2, 16, 3) & ~cercle(29, 16, 3)
    p.part(m, 'violet', R=3, lo=1, hi=4)
    for y in range(10, 23, 3):
        p.creuse(rect(9, y, 9, y + 1), 1)
    p.part(etoile(18.5, 16.5, 6.5, 2.8), 'or', R=2, lo=2, hi=4)
    p.etincelle(26, 5)


@picto('calendar')
def calendar(p):
    p.part(rrect(4, 6, 27, 28, 3), 'creme', mode='plat', lo=2, hi=3)
    p.part(rrect(4, 6, 27, 12, 3) & (Y <= 11), 'rouge', R=2, lo=1, hi=4, ombre=False)
    for x in (9, 21):
        p.part(rect(x, 3, x + 1, 9), 'argent', R=1, lo=1, hi=4)
    for x in (8, 12, 16, 20, 24):
        for y in (15, 19, 23):
            p.creuse(rect(x - 1, y, x, y), 1)
    p.part(ligne([(11, 20), (15, 24), (24, 14)], 3), 'vert', R=1.5, lo=1, hi=4)


@picto('friends')
def friends(p):
    """Amis : deux bustes côte à côte."""
    def buste(cx, cy, habit, cheveux, r=4.5):
        p.part(ellipse(cx, cy + 13, r + 4.5, 7) & (Y <= 29), habit, R=3, lo=1, hi=4)
        p.part(cercle(cx, cy, r), 'creme', R=3, lo=1, hi=4)
        p.part(cercle(cx, cy, r + 0.6) & (Y <= cy - 1) | cercle(cx + r * 0.6, cy - 1, 2) & cercle(cx, cy, r + 0.6), cheveux, R=2, lo=1, hi=4, ombre=True)
    buste(21, 10, 'bleu', 'bois', 4)
    buste(11, 12, 'orange', 'or', 5)


@picto('ranking')
def ranking(p):
    """Classement : un podium à trois marches, une étoile sur la plus haute."""
    p.part(rect(3, 18, 11, 28), 'argent', R=2, lo=1, hi=4)
    p.part(rect(20, 21, 28, 28), 'bronze', R=2, lo=1, hi=4)
    p.part(rect(11, 13, 20, 28), 'or', R=2, lo=1, hi=4)
    p.part(etoile(15.5, 7.5, 6, 2.6), 'or', R=2, lo=2, hi=4)
    p.etincelle(26, 10)


@picto('settings')
def settings(p):
    """Réglages : une roue dentée."""
    m = cercle(15.5, 15.5, 10)
    for i in range(8):
        a = i * np.pi / 4 + np.pi / 8
        c, s = np.cos(a), np.sin(a)
        pts = [(15.5 + c * r - s * w, 15.5 + s * r + c * w) for r, w in ((8, -2.6), (13.2, -2), (13.2, 2), (8, 2.6))]
        m |= poly(pts)
    p.part(m, 'argent', R=3, lo=1, hi=4)
    trou = cercle(15.5, 15.5, 3.6)
    p.creuse(cercle(15.5, 15.5, 5.6) & ~trou, 1)
    p.efface(trou)


@picto('chat')
def chat(p):
    m = rrect(3, 5, 28, 22, 6) | poly([(8, 20), (15, 21), (6, 28)])
    p.part(m, 'bleu', R=3.5, lo=1, hi=4)
    for x in (10, 16, 22):
        p.part(cercle(x, 13.5, 1.8), 'blanc', R=1.5, lo=3, hi=4, ombre=True)


@picto('gift')
def gift(p):
    p.part(rect(5, 15, 26, 28), 'rouge', R=2.5, lo=1, hi=3)
    p.part(rect(3, 11, 28, 15), 'rouge', R=2, lo=2, hi=4)
    p.part(rect(14, 11, 17, 28), 'or', mode='plat', lo=3, hi=4)
    p.creuse(rect(14, 16, 17, 16), 1)
    for cx in (11, 20):
        boucle = ellipse(cx, 7.5, 4.6, 3.3)
        p.part(boucle, 'or', R=2, lo=2, hi=4)
        p.creuse(ellipse(cx, 7.5, 2, 1.2), 2)
    p.part(rect(14, 7, 17, 11), 'or', R=1.5, lo=2, hi=4)
    p.etincelle(27, 5)


@picto('bag')
def bag(p):
    """Sac (inventaire) : un sac à dos de cuir, rabat et boucle d'or."""
    p.part(anneau(15.5, 8, 4.5, 2.5) & (Y <= 8), 'cuir', R=1.5, lo=1, hi=3)
    p.part(rrect(5, 17, 9, 26, 1), 'cuir', R=2, lo=1, hi=3)
    p.part(rrect(7, 8, 25, 28, 5), 'bois', R=4, lo=1, hi=4)
    p.part(rrect(7, 7, 25, 18, 5) & (Y <= 17), 'cuir', R=3, lo=1, hi=4)
    p.part(rrect(14, 15, 17, 19, 1), 'or', R=1.5, lo=2, hi=4)
    p.plat(rect(15, 16, 16, 17), 'bois', 1)
    p.creuse(rect(10, 23, 22, 23), 1)


@picto('forge')
def forge(p):
    """Forge : une enclume et un marteau."""
    enclume = poly([(2, 13), (8, 12), (27, 12), (27, 16), (22, 18), (20, 21), (24, 27), (8, 27), (12, 21), (10, 18), (6, 16)])
    p.part(enclume, 'fer', R=3, lo=1, hi=4)
    p.eclaire(rect(8, 12, 27, 12), 1)
    p.part(ligne([(13, 15), (24, 4)], 2), 'bois', R=1, lo=2, hi=4)
    tete = poly([(18, 3), (22, 0), (28, 6), (25, 9)])
    p.part(tete & rect(0, 2, 31, 31) | poly([(19, 4), (23, 2), (27, 6), (25, 9), (21, 7)]), 'argent', R=1.5, lo=1, hi=4)
    p.etincelle(9, 7); p.eclat(12, 9, '#ffbe36'); p.eclat(6, 10, '#ff761c')


@picto('fusion')
def fusion(p):
    """Fusion : deux forces qui s'enroulent en une seule boule."""
    b = cercle(15.5, 16, 12)
    p.part(b, 'violet', mode='boule', R=12.5, centre=(18, 13), lo=1, hi=4)
    autre = b & (X - 15.5 > 5 * np.sin((Y - 16) / 12 * np.pi))
    p.part(autre, 'or', mode='boule', R=12.5, centre=(18, 13), lo=1, hi=4, ombre=False)
    p.plat(cercle(10.5, 11, 2), 'or', 3)
    p.plat(cercle(20.5, 21, 2), 'violet', 2)
    p.etincelle(26, 5, True)


# ---------- coffres, sablier ----------

def coffre(p, bois='bois', fer='or', ouvert=False, petit=False):
    x0, x1 = (6, 25) if petit else (3, 28)
    y1 = 28
    corps = rect(x0, 16, x1, y1)
    p.part(corps, bois, R=2.5, lo=1, hi=3)
    if ouvert:
        p.part(poly([(x0 + 1, 15), (x1 - 1, 15), (x1 - 3, 4), (x0 + 3, 4)]), bois, R=2, lo=0, hi=2)
        p.part(rect(x0 + 3, 4, x1 - 3, 6), fer, R=1.5, lo=1, hi=3, ombre=False)
        p.part(ellipse(15.5, 15.5, (x1 - x0) / 2 - 1, 4) & (Y <= 17), 'or', R=2.5, lo=2, hi=4)
        for x, y in ((11, 13), (19, 12), (15, 14)):
            p.part(ellipse(x, y, 2.5, 1.5), 'orpale', mode='plat', lo=3, hi=4, ombre=False)
        p.part(cercle(22, 13.5, 2.2), 'rose', R=2, lo=2, hi=4)
        p.etincelle(15, 6, True); p.etincelle(25, 9)
    else:
        cou = ellipse(15.5, 15, (x1 - x0) / 2 + 0.4, 9 if not petit else 7) & (Y <= 15) & (Y >= 6 if not petit else 8)
        p.part(cou, bois, R=3, lo=1, hi=4)
    for bx in ((x0 + 3, x1 - 4) if not petit else (x0 + 2, x1 - 3)):
        p.part(rect(bx, 6 if not ouvert else 16, bx + 1, y1) & p.on, fer, mode='plat', lo=2, hi=3, ombre=True)
    p.part(rect(x0, 16, x1, 17), fer, R=1, lo=2, hi=4)
    plaque = rrect(13, 15, 18, 21, 1)
    p.part(plaque, fer, R=1.5, lo=2, hi=4)
    p.plat(rect(15, 17, 16, 19), 'nuit', 0)


@picto('chestClosed')
def chest_closed(p):
    coffre(p)
    p.etincelle(26, 5)


@picto('chestOpen')
def chest_open(p):
    coffre(p, ouvert=True)


@picto('questChest')
def quest_chest(p):
    coffre(p, bois='bleu', fer='or')
    p.part(etoile(15.5, 10, 3.5, 1.5, 4), 'or', R=1.5, lo=3, hi=4)
    p.etincelle(26, 5)


@picto('hourglass')
def hourglass(p):
    verre = poly([(8, 6), (23, 6), (17, 15.5), (23, 25), (8, 25), (14, 15.5)]) | ellipse(15.5, 9, 7.5, 4) | ellipse(15.5, 22, 7.5, 4)
    verre &= rect(7, 5, 24, 26)
    p.part(verre, 'ciel', R=3, lo=2, hi=4)
    p.part(poly([(10, 10), (21, 10), (16.5, 14.5), (14.5, 14.5)]), 'orange', R=2, lo=2, hi=4, ombre=False)
    p.part(rect(15, 15, 16, 21), 'orange', mode='plat', lo=3, hi=3, ombre=False)
    p.part(ellipse(15.5, 24, 6, 3.5) & (Y <= 25), 'orange', R=2, lo=2, hi=4, ombre=False)
    p.eclat(20, 8); p.eclat(20, 9)
    for y in (2, 26):
        p.part(rrect(4, y, 27, y + 3, 1), 'bois', R=1.5, lo=1, hi=4)
    for x in (5, 25):
        p.part(rect(x, 5, x + 1, 26), 'or', R=1, lo=1, hi=4)


# ---------- récompenses et signes ----------

@picto('crown')
def crown(p):
    m = poly([(4, 21), (4, 8), (10, 14), (15.5, 5), (21, 14), (27, 8), (27, 21)])
    p.part(m, 'or', R=3, lo=1, hi=4)
    p.part(rect(4, 20, 27, 26), 'or', R=2, lo=1, hi=4)
    for x, y in ((4, 7), (15.5, 4), (27, 7)):
        p.part(cercle(x, y, 1.8), 'orpale', R=1.5, lo=2, hi=4)
    p.part(cercle(15.5, 23, 2.4), 'rouge', R=2, lo=1, hi=4)
    p.part(cercle(9, 23, 1.6) | cercle(22, 23, 1.6), 'bleu', R=1.5, lo=2, hi=4)
    p.etincelle(25, 14)


@picto('trophy')
def trophy(p):
    p.part(anneau(7, 11, 4.5, 2.4) | anneau(24, 11, 4.5, 2.4), 'or', R=1.5, lo=1, hi=4)
    coupe = poly([(6, 4), (25, 4), (24, 11), (19, 17), (12, 17), (7, 11)])
    p.part(coupe, 'or', R=4, lo=1, hi=4)
    p.part(rect(14, 17, 17, 22), 'or', R=1.5, lo=1, hi=3)
    p.part(rrect(9, 22, 22, 28, 1), 'bois', R=2, lo=1, hi=4)
    p.part(rect(12, 24, 19, 26), 'or', mode='plat', lo=3, hi=3, ombre=False)
    p.relief(etoile(15.5, 10, 4, 1.7) & coupe, 1)
    p.etincelle(26, 3)


@picto('badge')
def badge(p):
    p.part(poly([(8, 2), (14, 2), (18, 13), (12, 13)]), 'rouge', R=2, lo=1, hi=4)
    p.part(poly([(17, 2), (23, 2), (19, 13), (13, 13)]), 'bleu', R=2, lo=1, hi=4)
    p.part(cercle(15.5, 20, 9), 'or', R=2.5, lo=1, hi=4)
    p.relief(etoile(15.5, 20.5, 5.5, 2.4), 2)


@picto('avatarFrame')
def avatar_frame(p):
    p.part(anneau(15.5, 16.5, 13, 9.5), 'or', R=2, lo=1, hi=4)
    p.part(cercle(15.5, 4, 3), 'rouge', R=2, lo=1, hi=4)
    p.part(cercle(4, 22, 2) | cercle(27, 22, 2), 'bleu', R=1.5, lo=1, hi=4)


@picto('cardBack')
def card_back(p):
    p.part(rrect(5, 2, 26, 29, 2), 'or', R=2, lo=1, hi=4)
    p.part(rrect(7, 4, 24, 27, 1), 'nuit', mode='plat', lo=2, hi=3, ombre=False)
    p.part(poly([(15.5, 8), (21, 15.5), (15.5, 23), (10, 15.5)]), 'violet', R=2, lo=1, hi=4)
    p.part(etoile(15.5, 15.5, 4, 1.5, 4), 'or', R=1.5, lo=3, hi=4)


@picto('defeat')
def defeat(p):
    """Défaite : un bouclier fendu en deux."""
    ecu = poly([(4, 4), (27, 4), (27, 14), (22, 23), (15.5, 29), (9, 23), (4, 14)])
    fente = ligne([(17, 3), (14, 10), (18, 15), (13, 21), (16, 30)], 2)
    gauche = ecu & ~fente & ((X - 15.5) < -(np.interp(Y, [3, 10, 15, 21, 30], [17, 14, 18, 13, 16]) - 15.5) * -1)
    droite = ecu & ~fente & ~gauche
    p.part(decale(gauche, -1, 1), 'argent', R=3, lo=1, hi=3)
    p.part(droite, 'argent', R=3, lo=1, hi=3, ombre=False)
    p.creuse(decale(ronge(gauche, 3), -1, 1) | ronge(droite, 3), 1)


@picto('rebirth')
def rebirth(p):
    """Renaissance : une plume de phénix en flamme."""
    plume = poly([(6, 28), (9, 20), (13, 12), (19, 5), (27, 3), (25, 11), (20, 18), (13, 24)])
    p.part(plume, 'lave', R=3, lo=1, hi=4)
    p.part(ligne([(6, 28), (24, 6)], 1), 'or', mode='plat', lo=4, hi=4, ombre=False)
    p.etincelle(25, 14)


@picto('recycle')
def recycle(p):
    """Recycler : deux flèches qui tournent en rond."""
    r = anneau(15.5, 16, 12, 7.5)
    haut = r & (Y - 16 < -(X - 15.5) * 0.3) & ~(X < 9)
    bas = r & (Y - 16 > -(X - 15.5) * 0.3) & ~(X > 22)
    p.part(haut, 'vert', R=2, lo=1, hi=4)
    p.part(poly([(3, 13), (13, 13), (8, 20)]), 'vert', R=2, lo=1, hi=4, ombre=False)
    p.part(bas, 'cyan', R=2, lo=1, hi=4)
    p.part(poly([(28, 19), (18, 19), (23, 12)]), 'cyan', R=2, lo=1, hi=4)


if __name__ == '__main__':
    lance()
