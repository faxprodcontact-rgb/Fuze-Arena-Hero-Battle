# Recherche graphique (proposition en cours, pas encore dans le jeu)

Personnages « chibi » de trois-quarts dessinés par le code, aux positions réelles du combat (5 contre 5 sur 3 rangées).

- `kit.cjs` : outils de peinture (lumière, ombre, volume, contre-jour, contour par grande partie).
- `chibi.cjs` : le personnage paramétrable (coiffure, tenue, arme, pose, oreilles, visage…).
- `cast.cjs` : les 5 héros et les 5 ennemis de la planche.
- `scene.cjs` : la scène du jeu (720 × 980) ; `sheet.cjs` et `big.cjs` : planches des personnages (petit / grand).

Pour régénérer : `node big.cjs` ou `node scene.cjs` (écrit un `.html`), puis une capture d'écran avec Playwright.

## Demandes du propriétaire (style)

- Inspiration : les héros d'Idle Heroes (grosse tête, trois-quarts, très soignés), mais personnages originaux.
- Pas d'effet « formes posées les unes sur les autres » : un contour par grande partie, membres d'un seul tenant.
- Peu d'éléments par personnage (3 ou 4 éléments forts), simples mais bien faits.
- Proportions soignées : front haut, yeux bas dans la tête. Mains en moufle.
- À l'écran : personnages plutôt petits, les deux camps bien écartés, placés comme dans le combat du jeu.

## Liste de contrôle de cohérence (à vérifier EN GRAND sur chaque personnage, avant de le montrer)

1. **Cheveux** : toute la chevelure visible est UNE seule forme, qui suit le crâne (dessus, côtés, nuque). Aucune mèche
   ou pique qui repart d'ailleurs, rien qui dépasse au-dessus de la tête par-derrière, aucun trait isolé.
2. **Capuche** : un anneau fermé autour du visage, qui descend jusqu'aux épaules (col). Elle ne s'arrête jamais dans le vide.
3. **Ce qui fait le tour de quelque chose va d'un bord à l'autre** : ceinture, écharpe de taille, ourlet, bandeau,
   diadème, masque. On les peint DANS la forme qu'ils entourent (découpe), jamais posés par-dessus avec une longueur fixe.
4. **Écharpe / cache-cou** : fait le tour du cou ; les pans partent bien du nœud.
5. **Mains et objets** : chaque objet tenu passe dans une main ; chaque main est au bout d'un bras visible (ou cachée
   derrière l'objet, comme pour le bouclier). Pas de main qui flotte, pas d'arme qui flotte.
6. **Arc** : une main sur la poignée, l'autre sur la corde à l'encoche de la flèche ; la corde relie les deux bouts.
7. **Oreilles** : attachées à la tête (aucun trait à la base, la racine se fond dans la peau, bord net seulement côté
   extérieur) ; devant les cheveux de la nuque ; avec une capuche, la base est sur le visage, dans l'ouverture.
8. **Casques et coiffes** : posés sur le crâne, bord net, ils couvrent ce qu'ils doivent couvrir (oreille sous un casque).
9. **Articulations** : pas de trait au coude, au genou, à la cheville ; pas de contour entre deux pièces de même matière.
10. **Visage** : deux yeux à l'intérieur du visage (l'œil du fond plus étroit), sourcils au-dessus, rien ne cache les yeux.
11. **Lumière** : vient du même côté pour tous (y compris les ennemis retournés) ; ombre portée au sol sous chacun.
12. **Lisibilité** : vérifier aussi à la taille réelle du jeu (personnage d'environ 65 px de haut sur un téléphone).

## Priorités de superposition (qui passe devant quoi)

Règle générale, de l'arrière vers l'avant. À revérifier pour CHAQUE personnage, car l'ordre dépend de ce qu'il porte :

1. Derrière le corps : cape, pans d'écharpe, cheveux longs du dos, carquois, oreille du fond.
2. Bras du fond (sauf s'il croise devant le buste, comme pour l'épée à deux mains : alors il passe devant la tunique).
3. Jambes, puis tunique ou robe, ceinture, plastron.
4. Bras avant (la manche) : il passe sur le corps…
5. …mais SOUS tout ce qui se porte par-dessus l'épaule ou autour du cou : épaulière, puis arme posée sur l'épaule
   (son manche repose sur l'épaulière), puis cache-cou / écharpe / col de capuche.
6. Tête : visage, barbe (elle tombe devant le cache-cou et l'épaulière), cheveux, puis casque ou capuche par-dessus les
   cheveux ; l'écharpe d'un personnage à capuche se noue par-dessus la capuche.
7. Ce que tient la main du fond et qui est devant le corps : bouclier, arc, bâton (la main sur l'objet, sauf le bouclier
   qui la cache).
8. Tout devant : la main avant et son arme.

Questions à se poser pour un nouvel équipement : est-il porté dessous ou dessus (une cape passe sur les épaulières, un
plastron sous l'écharpe) ? Fait-il le tour de quelque chose (alors il se peint dans cette forme) ? Est-il tenu (alors une
main est dessus) ? Cache-t-il quelque chose (un casque cache l'oreille, un masque cache le nez et la bouche) ?

## Essai d'images par IA

Voir `essai-ia/LISEZMOI.md` : 5 images d'essai (héros, ennemis, décor, version grosses têtes, poses d'animation),
les outils de découpe et ce qu'on a appris.

## Version épurée (v5, 20/11/2026)

Demande du propriétaire après l'essai par IA : rester sur le dessin par code, mais **plus petit, plus épuré, un ou deux
éléments forts par personnage, cohérent, avec un minimum d'allure**.

- `mini.cjs` : le gabarit (boîte 200 × 240, pieds à y = 228). Peu de formes : dos → bras du fond → jambes + buste →
  manche de devant → ce qui repose sur l'épaule ou entoure le cou → tête (visage, coiffe) → main et arme en dernier.
- `cast5.cjs` : les 5 héros et les 5 gobelins. `sheet5.cjs` : planche en grand. `scene5.cjs` : la scène du jeu.
- Chaque personnage se reconnaît à sa silhouette : bouclier + casque à cornes, grande épée + écharpe, arc + capuche,
  bâton à orbe + longue chevelure, deux dagues + écharpe au vent ; gobelins : massue, dagues, grande hache, bâton à
  crâne, arc.
- Regard dur : œil en amande coupé par une paupière en biais, sourcil épais (`calm` pour un regard doux).
- Pas de petits détails (boucles, galons, épaulières, carquois). Les membres sont d'un seul tenant (`limb`).
- Les halos (orbe, lame de feu) sont rendus à part, derrière le personnage, sinon le contour les salit.
- La liste de contrôle de cohérence ci-dessus s'applique toujours.
