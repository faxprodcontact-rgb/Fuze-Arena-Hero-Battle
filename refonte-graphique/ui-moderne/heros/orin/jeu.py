# Orin au combat : ce que l'outil commun doit savoir (../../jeu_export_vecto.py, consigne ../../EXPORT-JEU.md).
# Les instants sont en ms depuis le début du coup (ceux d'anim.py) ; les x, y en pixels du dessin (repère d'anim.py).
import math

import anim as A
import orin as O

ID = 'mages-3'
ANIM, DESSIN = A, O
# les points de départ (anim.py les calcule à la 1re image du coup ; la respiration n'y joue pas)
A.HIT0['fan_tip'] = O.build(pose=A.pose_at(A.A_BLADE / 1000, 'attack', 0.0)).ctx['fan_tip']
A.SP_STORE['fan_tip'] = O.build(pose=A.pose_at(A.S_STORM / 1000, 'special', 0.0)).ctx['fan_tip']
X, Y = A.FOE
TIR = 560                                  # la lame de vent a quitté l'éventail (l'éclat de sa naissance est passé)
SP_TIR = 850                               # la tête de la rafale a quitté l'éventail


def blade_c(t):
    k = (t - A.A_BLADE) / (A.A_HIT - A.A_BLADE)
    x0, y0 = A.HIT0['fan_tip']
    x0 += 4
    kk = A.ease(k) * 0.85 + 0.15 * k
    return x0 + (X - 14 - x0) * kk, y0 + (Y - 6 - y0) * kk


def lame(fig, i):
    """La lame de vent en croissant, son avant vers (0, 0), deux volutes derrière elle."""
    c = (-6.0, 0.0)
    fig.fx_back.append(A.gust(fig, (c[0] - 40, c[1] - 9), (c[0] - 30, c[1] - 15), (c[0] - 18, c[1] - 16), (c[0] - 8, c[1] - 11),
                              3.0, curl=2.8 + 0.4 * i, up=False))
    fig.fx_back.append(A.gust(fig, (c[0] - 36, c[1] + 11), (c[0] - 26, c[1] + 16), (c[0] - 15, c[1] + 15), (c[0] - 7, c[1] + 10),
                              2.6, curl=2.6 + 0.4 * i, up=True))
    fig.fx_front.append(A.moon(fig, c, 19, 0, 8.5))


def rafale(fig, i):
    """La tête de la rafale (grand croissant, volutes) et quelques plumes noires emportées, avant vers (0, 0)."""
    c = (-8.0, 0.0)
    fig.fx_back.append(A.gust(fig, (c[0] - 30, c[1] - 14), (c[0] - 20, c[1] - 22), (c[0] - 8, c[1] - 22), (c[0], c[1] - 15), 3.0,
                              curl=3.4, up=False))
    fig.fx_back.append(A.gust(fig, (c[0] - 30, c[1] + 14), (c[0] - 20, c[1] + 22), (c[0] - 8, c[1] + 22), (c[0], c[1] + 15), 2.8,
                              curl=3.2, up=True))
    fig.fx_front.append(A.moon(fig, c, 20, 0, 8.5))
    for j, (dx, dy, big) in enumerate(((-26, -6, True), (-38, 7, False), (-48, -3, True), (-18, 10, False))):
        fig.fx_front.append(A.crow(fig, dx, dy + 2 * math.sin(i * 2 + j), 25 * math.sin(i * 1.7 + j), 1.35 if big else 1.0))


JEU = {
    'pose': dict(periode=3000, images=8),   # la boucle du repos : anim.IDLE_T, signe du héros (anim.signe) ; 8 images
    # seulement : avec 10 ou 12, la planche dépasse le budget de 4,2 Mo (4,3 et 4,4 Mo)
    'vue_proj': (-64, -36, 96, 72),
    # coup de sabre puis coup d'éventail : la lame de vent file jusqu'à l'ennemi (le jeu la fait voler) et le frappe
    # (éclat, croissant, volutes, bouffée posés sur la vraie cible)
    'attaque': dict(genre='tir', tir=TIR, coup=A.A_HIT, cible=(X, Y - 6), bouche=blade_c(TIR),
                    vol=lambda t, x, y, couche, el: math.hypot(x - blade_c(t)[0] + 14, y - blade_c(t)[1]) < 32,
                    coupe=170, cible_des=A.A_HIT, projectile=lame, proj_images=2, proj_ms=[90, 90]),
    # « Tempête du tengu » : il s'envole, frappe l'air de l'éventail ; la rafale et sa volée de plumes filent en cloche
    # jusqu'à l'ennemi (projectile) ; elle le balaie, les plumes tournoient et retombent (sur la vraie cible)
    'speciale': dict(genre='tir', tir=SP_TIR, coup=A.S_HIT, cible=(X, Y - 4), charge=A.S_GATHER,
                     bouche=(A.SP_STORE['fan_tip'][0] + 2, A.SP_STORE['fan_tip'][1]), arc=18,
                     vol=lambda t, x, y, couche, el: x > 118 and y < O.GRD - 15, coupe=150, cible_des=A.S_HIT,
                     projectile=rafale, proj_images=3, proj_ms=[80, 80, 80]),
}
# la vue élargie (27/11) : des images touchaient son bord et étaient coupées net (bords_combat)
JEU['vue'] = (-80, -86, 350, 210)
