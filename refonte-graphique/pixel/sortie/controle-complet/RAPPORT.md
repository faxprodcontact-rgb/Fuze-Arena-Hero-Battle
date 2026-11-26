# Contrôle complet du jeu — 26/11/2026

Ce qui a été regardé : les 44 héros un par un (page du héros, case de la grille, plateau de la formation, salle des
héros, invocation ×1 et ×10, Chances, choix du portrait, cartes du bas du combat, dessins en combat), chaque clan de
monstres, chaque général et chaque grand boss en vrai combat, puis **tous les écrans et toutes les fenêtres** (70 écrans)
sur deux téléphones : grand avec encoche (390 × 844) et petit (360 × 640). Tout a été fait par un robot qui joue
(Playwright) et qui vérifie seul : défilement de la page, textes coupés ou sortis de l'écran, mots techniques à la place
du texte, anglais dans le jeu en français, pictos absents, images manquantes, erreurs. Puis j'ai regardé chaque image.

Résultat général : **aucune erreur, aucune image manquante, aucun picto absent, aucun texte anglais ou technique, aucune
page qui défile** sur les deux tailles. Les dessins des héros (fichiers, tailles, images de respiration et visages)
sont tous complets et justes pour les 64 personnages.

## Bugs trouvés et réparés

| # | Où | Le bug | Réparation | Image |
|---|---|---|---|---|
| 1 | Portraits ronds (en haut à gauche, choix du portrait, amis, guilde…) | Plusieurs visages mal cadrés : Bao montrait son bâton, Sorai son éventail, Oboro sa lanterne, Aurelle (le cyclope) coupé à l'œil, le crabe et 4 monstres costauds montraient leur carapace ou leur ventre | Visage replacé à la main pour chacun | `avant-apres/portraits-tous.png` |
| 2 | Tous les portraits (demande du propriétaire) | Trop zoomés : seulement le visage | Tête **et haut du buste**, avec de l'air autour, tête dans le haut du rond ; pareil pour les 64 personnages | `avant-apres/portraits-tous.png`, `planches/07-portraits-ronds.jpg` |
| 3 | Onglet Héros, salle | Les boutons **Fusion** et **Renaissance** n'avaient plus de picto (seuls les mots restaient, depuis longtemps) | Le médaillon de pierre et son picto sont revenus | `avant-apres/salle-heros-fusion-renaissance.png` |
| 4 | Combat (téléphone à encoche) | Les boutons ronds **AUTO** et **×3** se posaient sur le dernier ennemi du bas | Le terrain remonte de la hauteur de la barre du bas du téléphone | `avant-apres/combat-auto-sur-ennemi.png` |
| 5 | Guilde, Membres | Ta propre ligne était en **bleu clair** (règle : plus de bleu clair) | Ligne dorée, comme dans le Classement | `avant-apres/guilde-membres-ma-ligne.png` |
| 6 | Tous les textes en français | Le « ? » ou le « ! » partait parfois **seul à la ligne** (« …du chapitre 5 / ? ») | L'espace avant ? ! : ; ne se coupe plus | `avant-apres/tchat-point-d-interrogation.png` |
| 7 | Amis, Suggestions | Deux joueurs proposés pouvaient avoir **le même nom** (« Orsolya » deux fois) | Les noms proposés sont toujours différents | `avant-apres/amis-suggestions-doublon.png` |

(Le bug de départ — les 8 monstres devenus héros en visage géant sur leur page — était déjà réparé ; le visage de Sarvik
aussi. Les deux ont été revérifiés : tout va bien.)

## Regardé, rien à réparer

- Page de chaque héros (44 × 2 tailles) : tous en pied, dans leur scène, pieds sur la même ligne, ni coupés, ni géants.
  Gribou paraît plus petit que les autres : c'est un singe, il est dessiné petit (même échelle pour tous, voulu).
  Oboro est un peu décalé à droite : sa lanterne est tenue devant lui (le dessin est centré sur ses pieds).
- Grille des héros, plateau de la formation, salle des héros, invocation ×1 et ×10, Chances, cartes du combat : tous bien.
- Combats : 9 équipes (les 44 héros), les 8 clans (24 monstres), les 8 généraux, les 4 grands boss : rien de coupé ni
  de mal placé. Les tailles des planches de combat correspondent toutes aux images (plus de « vieille planche » comme
  Garvin).
- Sac : la rangée des filtres (Tous, Arme, Armure, Casque, Bottes) dépasse à droite : c'est une rangée qu'on fait
  glisser du doigt, c'est voulu.

## Pas réparé (à décider)

- Rien de cassé n'est resté. Une remarque seulement : la fenêtre **Fragments** est vide si on n'a aucun fragment (on ne
  peut l'ouvrir que lorsqu'on en a, donc le joueur ne la voit jamais vide).

## Planches (pour regarder soi-même)

`planches/` : 01 page des héros (deux tailles), 02 grille, 03 plateau de formation, 04 salle, 05-06 invocations,
07 portraits ronds, 08 cartes du combat, 09 boss et généraux, 10 monstres des clans, 11 portrait et Chances,
12 tous les écrans (4 planches par taille de téléphone).
