# Les modes de l'Aventure, les missions, les ligues de l'arène, les bâtiments :
#   python3 refonte-graphique/pixel/ui/pictos/modes.py [noms…]
from pictolib import *
from menus import spirale


def epee(p, a, b, lame='argent', garde='or', w=3):
    """Une épée de (a) la poignée à (b) la pointe."""
    (ax, ay), (bx, by) = a, b
    dx, dy = bx - ax, by - ay
    L = np.hypot(dx, dy); ux, uy = dx / L, dy / L
    gx, gy = ax + ux * 6, ay + uy * 6                      # la garde, à 6 pixels de la poignée
    nx, ny = -uy, ux
    tip = (bx, by)
    p.part(poly([(gx + nx * 1.4, gy + ny * 1.4), (bx - ux * 3 + nx * 1.4, by - uy * 3 + ny * 1.4), tip,
                 (bx - ux * 3 - nx * 1.4, by - uy * 3 - ny * 1.4), (gx - nx * 1.4, gy - ny * 1.4)]), lame, R=1.5, lo=1, hi=4)
    p.part(ligne([(gx + nx * 4, gy + ny * 4), (gx - nx * 4, gy - ny * 4)], 2), garde, R=1, lo=1, hi=4)
    p.part(ligne([(ax + ux * 1.5, ay + uy * 1.5), (gx - ux, gy - uy)], 2), 'cuir', R=1, lo=1, hi=3)
    p.part(cercle(ax, ay, 1.6), garde, R=1.5, lo=2, hi=4)


@picto('tower')
def tower(p):
    """Tour : une tour de pierre, toit pointu rouge et fanion."""
    p.part(ligne([(15.5, 2), (15.5, 7)], 1), 'bois', lo=2, hi=3)
    p.part(poly([(16, 2), (22, 3.5), (16, 5)]), 'bleu', R=1, lo=2, hi=4)
    corps = rect(9, 13, 22, 28) | rect(7, 26, 24, 29)
    p.part(corps, 'pierre', R=3, lo=1, hi=4)
    for y in (17, 22):
        p.creuse(rect(9, y, 22, y), 1)
    p.creuse(rect(13, 13, 13, 16) | rect(18, 18, 18, 21) | rect(12, 23, 12, 26), 1)
    p.part(poly([(7, 13), (24, 13), (15.5, 5)]), 'rouge', R=3, lo=1, hi=4)
    porte = rrect(13, 22, 18, 29, 2) & (Y <= 28)
    p.plat(porte, 'bois', 1)
    p.plat(rrect(17, 16, 19, 19, 1), 'nuit', 1)
    p.eclat(18, 17, '#ffd84a')


@picto('dungeons')
def dungeons(p):
    """Donjons : une porte de pierre en arc, le noir et deux yeux qui luisent."""
    arc = rrect(3, 4, 28, 29, 12) & (Y <= 28)
    p.part(arc, 'pierre', R=3, lo=1, hi=4)
    for y in (9, 15, 21):
        p.creuse(rect(3, y, 7, y) | rect(24, y, 28, y), 1)
    trou = rrect(9, 10, 22, 30, 7) & (Y <= 28)
    p.plat(trou, 'nuit', 0)
    p.plat(ronge(trou, 2) & (Y > 14), 'nuit', 1)
    for x in (13, 18):
        p.eclat(x, 18, '#ffd84a'); p.eclat(x + 1, 18, '#ff761c')
    p.part(ellipse(15.5, 29, 13, 1.3) & (Y <= 29), 'pierre', mode='plat', lo=1, hi=1)


@picto('dailyBoss')
def daily_boss(p):
    """Boss du jour : un crâne cornu aux yeux de braise."""
    for s in (1, -1):
        corne = poly([(15.5 + s * 6, 9), (15.5 + s * 12, 7), (15.5 + s * 13.5, 1.5), (15.5 + s * 15, 10), (15.5 + s * 9, 13)])
        p.part(corne, 'bois', R=2, lo=1, hi=4)
    crane = ellipse(15.5, 14, 10, 9.5) | rrect(9, 18, 22, 28, 3)
    p.part(crane, 'creme', R=4, lo=1, hi=4)
    for x in (11.5, 19.5):
        p.plat(ellipse(x, 15, 3, 2.6), 'nuit', 0)
        p.eclat(int(x), 15, '#ff761c'); p.eclat(int(x) + 1, 15, '#ffd84a')
    p.plat(poly([(15.5, 18), (17, 21), (14, 21)]), 'nuit', 1)
    for x in (12, 15, 18):
        p.creuse(rect(x, 24, x, 27), 2)
    p.creuse(rect(10, 24, 21, 24), 1)


@picto('arena')
def arena(p):
    """Arène : deux épées croisées."""
    epee(p, (4, 27), (26, 4))
    epee(p, (27, 27), (5, 4))
    p.etincelle(15, 8)


def colisee(p):
    """Le Colisée : un amphithéâtre de pierre claire, deux étages d'arches, des fanions."""
    p.part(ellipse(15.5, 9, 13, 4) & (Y >= 6), 'pierre', R=2, lo=1, hi=4)
    corps = ellipse(15.5, 9, 13, 4) | rect(2.5, 9, 28.5, 26) | ellipse(15.5, 26, 13, 3.5)
    p.part(corps, 'creme', R=3, lo=1, hi=4)
    p.plat(ellipse(15.5, 8.5, 11, 2.5), 'pierre', 1)
    for row, (y0, y1) in enumerate(((12, 17), (20, 26))):
        for i, x in enumerate(range(4, 28, 5)):
            a = rrect(x, y0, x + 2, y1 + (row == 1 and 0), 1)
            p.plat(a & corps, 'nuit', 2 if x > 15 else 1)
    p.creuse(rect(3, 18, 28, 18), 1)
    for x in (6, 15, 25):
        p.part(ligne([(x, 1), (x, 6)], 1), 'bois', lo=2, hi=3)
        p.part(poly([(x + 1, 1), (x + 5, 2.5), (x + 1, 4)]), 'rouge', lo=2, hi=4, ombre=False)


@picto('colisee')
def colisee_(p):
    colisee(p)


@picto('defense')
def defense(p):
    colisee(p)


# ---------- les missions ----------

@picto('mission-patrol')
def m_patrol(p):
    """Patrouille : une lanterne allumée."""
    p.part(anneau(15.5, 5, 3.5, 1.8) & (Y <= 5), 'fer', R=1.5, lo=1, hi=4)
    p.part(rrect(9, 6, 22, 9, 1), 'fer', R=1.5, lo=1, hi=4)
    verre = rect(10, 10, 21, 24)
    p.part(verre, 'or', mode='boule', R=10, centre=(17, 15), lo=2, hi=4)
    p.plat(ellipse(15.5, 18, 2.2, 3.5), 'blanc', 4)
    p.eclat(15, 16); p.eclat(16, 16)
    for x in (9, 15, 21):
        p.part(rect(x, 9, x + 1, 25), 'fer', R=1, lo=1, hi=3)
    p.part(rrect(8, 25, 23, 28, 1), 'fer', R=1.5, lo=1, hi=4)
    p.etincelle(26, 12)


@picto('mission-escort')
def m_escort(p):
    """Escorte : un chariot bâché."""
    bache = rrect(5, 5, 26, 22, 7) & (Y <= 18)
    p.part(bache, 'creme', R=4, lo=1, hi=4)
    for x in (11, 20):
        p.creuse(ellipse(x, 12, 0.6, 7) & bache, 1)
    p.part(rect(3, 17, 28, 22), 'bois', R=2, lo=1, hi=4)
    p.creuse(rect(3, 19, 28, 19), 1)
    for cx in (9, 23):
        roue = cercle(cx, 24, 4.5)
        p.part(roue, 'bois', R=2, lo=1, hi=4)
        p.plat(anneau(cx, 24, 2.6, 1.2), 'bois', 1)
        p.plat(cercle(cx, 24, 1), 'fer', 3)


@picto('mission-ruins')
def m_ruins(p):
    """Ruines : des colonnes brisées."""
    p.part(ellipse(15.5, 27, 14, 2.5), 'vert', lo=1, hi=3)
    p.part(rect(6, 6, 12, 26) & ~poly([(6, 6), (12, 9), (12, 6)]), 'creme', R=3, lo=1, hi=4)
    p.part(rect(5, 24, 13, 27), 'pierre', R=2, lo=1, hi=4)
    p.creuse(rect(8, 10, 8, 23) | rect(10, 10, 10, 23), 1)
    p.part(rect(19, 14, 25, 26) & ~poly([(19, 14), (25, 17), (25, 14)]), 'creme', R=3, lo=1, hi=4)
    p.part(rect(18, 24, 26, 27), 'pierre', R=2, lo=1, hi=4)
    p.creuse(rect(21, 18, 21, 23) | rect(23, 18, 23, 23), 1)
    p.part(rrect(13, 22, 19, 27, 1), 'pierre', R=2, lo=1, hi=4)
    p.part(ellipse(26, 8, 3, 2) | ellipse(23, 9, 2, 1.5), 'vert', R=2, lo=1, hi=4)


@picto('mission-hunt')
def m_hunt(p):
    """Chasse : un arc tendu et sa flèche."""
    arc = anneau(9, 16, 13, 11) & (X >= 9) & rect(9, 3, 23, 29)
    p.part(arc, 'bois', R=1.5, lo=1, hi=4)
    p.part(ligne([(11, 5), (11, 27)], 1), 'blanc', mode='plat', lo=3, hi=3)
    p.part(ligne([(6, 16), (27, 16)], 1), 'bois', mode='plat', lo=3, hi=3)
    p.part(poly([(26, 13), (30, 16), (26, 19)]), 'argent', R=1, lo=2, hi=4)
    p.part(poly([(3, 13), (8, 15), (8, 17), (3, 19), (5, 16)]), 'rouge', R=1, lo=2, hi=4)


@picto('mission-relic')
def m_relic(p):
    """Relique : une amulette ancienne, d'or et de saphir, qui luit."""
    p.part(ligne([(8, 3), (15.5, 10)], 1) | ligne([(23, 3), (15.5, 10)], 1), 'or', mode='plat', lo=3, hi=3)
    a = cercle(15.5, 18, 10)
    p.part(a, 'or', R=2.5, lo=1, hi=4)
    p.creuse(anneau(15.5, 18, 7.5, 6.5), 1)
    p.part(poly([(15.5, 12), (20.5, 18), (15.5, 24), (10.5, 18)]), 'bleu', mode='boule', R=6, centre=(17, 16), lo=1, hi=4)
    p.eclat(17, 15)
    p.etincelle(26, 9, True)


@picto('mission-siege')
def m_siege(p):
    """Siège : une catapulte chargée d'une pierre."""
    p.part(poly([(4, 21), (27, 21), (27, 25), (4, 25)]), 'bois', R=2, lo=1, hi=4)
    p.part(poly([(11, 21), (15, 10), (17, 10), (16, 21)]), 'bois', R=1.5, lo=1, hi=3)
    p.part(ligne([(7, 20), (24, 7)], 2), 'bois', R=1, lo=2, hi=4)
    p.part(ellipse(25, 6, 3.5, 2) & (Y >= 5), 'bois', R=1.5, lo=1, hi=3)
    p.part(cercle(25, 4, 2.8), 'pierre', R=2, lo=1, hi=4)
    for cx in (8, 23):
        p.part(cercle(cx, 26, 3.5), 'bois', R=2, lo=1, hi=4)
        p.plat(cercle(cx, 26, 1), 'fer', 3)


# ---------- les ligues de l'arène ----------

def ligue(p, gamme, ailes=False, gemme='rouge', etoiles=0):
    if ailes:
        for s in (1, -1):
            aile = poly([(15.5 + s * 7, 8), (15.5 + s * 14, 5), (15.5 + s * 13, 12), (15.5 + s * 14.5, 13), (15.5 + s * 12, 19), (15.5 + s * 8, 20)])
            p.part(aile, 'blanc' if gamme != 'blanc' else 'ciel', R=2, lo=1, hi=4)
            p.creuse(ligne([(15.5 + s * 9, 13), (15.5 + s * 13, 12)]) | ligne([(15.5 + s * 9, 17), (15.5 + s * 12, 17)]), 1)
    ecu = poly([(8, 5), (23, 5), (23, 17), (15.5, 28), (8, 17)])
    p.part(ecu, gamme, R=3, lo=1, hi=4)
    p.creuse(ecu & ~ronge(ecu, 2) & ~decale(ecu, -1, 1), 0)
    interieur = ronge(ecu, 2)
    p.creuse(interieur & ~ronge(interieur, 1), 1)
    p.part(poly([(15.5, 9), (19.5, 14.5), (15.5, 20), (11.5, 14.5)]), gemme, mode='boule', R=5, centre=(17, 13), lo=1, hi=4)
    p.eclat(16, 12)
    for i in range(etoiles):
        x = 15.5 + (i - (etoiles - 1) / 2) * 5
        p.part(etoile(x, 3.5, 2.8, 1.2), 'or', R=1, lo=2, hi=4)


@picto('league-bronze')
def l_bronze(p):
    ligue(p, 'bronze', gemme='vert')


@picto('league-silver')
def l_silver(p):
    ligue(p, 'argent', gemme='bleu')


@picto('league-gold')
def l_gold(p):
    ligue(p, 'or', ailes=True, gemme='rouge')


@picto('league-platinum')
def l_platinum(p):
    ligue(p, 'cyan', ailes=True, gemme='violet', etoiles=1)


@picto('league-diamond')
def l_diamond(p):
    ligue(p, 'bleu', ailes=True, gemme='rose', etoiles=3)
    p.etincelle(26, 24)


# ---------- les bâtiments ----------

@picto('goldMine')
def gold_mine(p):
    """Mine d'or : un wagonnet plein d'or."""
    p.part(ellipse(15.5, 11, 11, 5) & (Y <= 13), 'or', R=3, lo=1, hi=4)
    for x, y in ((9, 9), (15, 7), (21, 9), (18, 11)):
        p.plat(ellipse(x, y, 2, 1.2), 'or', 4)
    p.part(poly([(3, 11), (28, 11), (25, 24), (6, 24)]), 'fer', R=2.5, lo=1, hi=4)
    p.part(rect(3, 11, 28, 13), 'bronze', R=1, lo=2, hi=4)
    p.creuse(rect(8, 17, 23, 17), 1)
    for cx in (10, 21):
        p.part(cercle(cx, 25, 3), 'fer', R=2, lo=1, hi=3)
        p.plat(cercle(cx, 25, 0.8), 'bronze', 3)
    p.part(rect(2, 28, 29, 29), 'bois', R=1, lo=1, hi=3)
    p.etincelle(26, 4)


@picto('essenceSpring')
def essence_spring(p):
    """Source d'essence : une vasque de pierre d'où jaillit l'essence."""
    jet = ellipse(15.5, 9, 3, 7) | ellipse(15.5, 4, 2, 2)
    p.part(jet, 'cyan', R=2, lo=2, hi=4)
    for x, y in ((10, 6), (21, 5), (8, 11), (23, 10)):
        p.part(cercle(x, y, 1.2), 'cyan', lo=3, hi=4, ombre=False)
    p.part(ellipse(15.5, 17, 13, 4), 'pierre', R=2.5, lo=1, hi=4)
    p.plat(ellipse(15.5, 16.5, 10.5, 2.5), 'cyan', 3)
    p.plat(ellipse(17, 16, 4, 1), 'cyan', 4)
    p.part(poly([(4, 18), (27, 18), (22, 24), (9, 24)]), 'pierre', R=2.5, lo=1, hi=3)
    p.part(rect(12, 24, 19, 26) | rrect(8, 26, 23, 29, 1), 'pierre', R=2, lo=1, hi=4)


@picto('summonAltar')
def summon_altar(p):
    """Autel d'invocation : un cristal violet qui flotte au-dessus d'un autel de pierre."""
    cr = poly([(15.5, 2), (21, 9), (15.5, 18), (10, 9)])
    p.part(cr, 'violet', mode='plat', lo=2, hi=2)
    p.plat(cr & (X < 15.5), 'violet', 1)
    p.plat(cr & (X >= 16) & (Y < 9), 'violet', 4)
    p.plat(cr & (X >= 16) & (Y >= 9), 'violet', 3)
    p.part(rrect(5, 20, 26, 23, 1), 'pierre', R=2, lo=1, hi=4)
    p.part(rect(8, 23, 23, 27), 'pierre', R=2.5, lo=1, hi=3)
    p.part(rrect(4, 26, 27, 29, 1), 'pierre', R=2, lo=1, hi=4)
    p.relief(etoile(15.5, 25, 2.5, 1, 4), 1)
    p.etincelle(25, 6); p.eclat(7, 12, '#cc86ff'); p.eclat(24, 15, '#cc86ff')


@picto('summonPortal')
def summon_portal(p):
    """Portail d'invocation : une arche de pierre où tourne la magie."""
    arc = rrect(3, 2, 28, 29, 12)
    p.part(arc, 'pierre', R=3, lo=1, hi=4)
    dedans = rrect(7, 6, 24, 29, 8)
    p.part(dedans, 'violet', mode='boule', R=12, centre=(18, 14), lo=0, hi=3, ombre=False)
    p.eclaire(spirale(15.5, 16, 1, 8, 1.4, 2, 0.5) & dedans, 1)
    p.plat(cercle(15.5, 16, 2), 'mauve', 4)
    p.part(cercle(15.5, 3, 2.2), 'cyan', R=1.5, lo=2, hi=4)
    p.part(rect(2, 27, 29, 29), 'pierre', R=1.5, lo=1, hi=3)


if __name__ == '__main__':
    lance()
