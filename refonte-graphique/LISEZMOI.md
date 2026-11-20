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

### Animations (aperçu sur le site de test)

- Chaque personnage est fabriqué en **morceaux** (`parts` : dos, bras du fond, jambes, buste, manche, épaule, tête,
  main du fond, main + arme) avec un **squelette** (`rig` dans `cast5.cjs` : quels morceaux suivent le bras qui frappe,
  le bras du fond, type d'attaque, angles d'élan et de frappe).
- `node refonte-graphique/export5.cjs` écrit `public/apercu/a/*.png` (une planche par personnage), `data.js` et `bg.jpg`.
- `public/apercu/apercu.js` : petit moteur de démonstration (respiration, élan, bond, coup, tir, sort, soin, touché,
  chute, compétence en touchant un personnage). Le contour de la silhouette est refait à l'écran à chaque image.
- Remarques du propriétaire (20/11/2026) à toujours vérifier : **les pics des cheveux vont tous dans le même sens**
  (couchés vers l'arrière, aucun qui repart vers l'avant), et **le sens des armes** (tête de marteau en travers du
  manche, lames pointées vers l'adversaire).

## Les 72 héros (20/11/2026)

Demande du propriétaire : 72 héros **très différents les uns des autres**, inspirés des **mythologies et légendes**,
« badass » en priorité, avec toutes les règles ci-dessus.

- Liste complète (identifiant du jeu, nom provisoire, rareté, rôle, inspiration) : `HEROS.md`.
- **Version 6 (refaite le 20/11/2026)** après la remarque du propriétaire : corps, jambes, visages et poses trop
  semblables, doublons (« l'archer d'une autre couleur »), bras qui passent dans une barbe, museaux cassants.
  Chaque héros est maintenant dessiné pour lui-même : aucun ne part d'un autre.
- `fig6.cjs` : le gabarit. Carrures (`BODY` : normal, heavy, brute, slim, curvy, round, small, tall, plus `shape`
  pour régler à la main), mains placées librement (`near` / `far` : `hand`, `el`, ou une pose toute faite), ordre des
  couches, et le squelette d'animation (quel bras frappe, articulations selon la carrure).
- `face6.cjs` : visages (12 regards, sourcils, bouches, nez, barbes, moustaches, mâchoires) et têtes d'animaux
  **d'une seule courbe du crâne au museau** (chacal, lion, taureau, requin, lézard, dragon, singe, belette, crâne),
  aigle, tortue, golem, cyclope.
- `legs6.cjs` : jambes (droites, nues, bouffantes, épaisses, fines, hakama ; 12 sortes de pieds ; 4 appuis), pattes
  de bête, danse, lévitation, pierre, queue de poisson, serpent, volute, tentacules, scorpion, araignée, robes.
- `wear6.cjs` : cheveux, coiffes, dos (capes, ailes, queues…), cou. `items6.cjs` : armes et objets tenus.
- `heroes6.cjs` : le registre ; `h6-fire.cjs`, `h6-wind.cjs`, `h6-water.cjs`, `h6-earth.cjs` : 18 héros chacun, dans
  l'ordre de `ELEMENT_ROSTER` (rôle, rareté et chef viennent du jeu, on ne les change pas ici).
- `node sheet72.cjs fire` : planche d'un élément ; `node zoom6.cjs "fire:4,wind:9" sortie.html` : vue en grand pour
  le contrôle ; `node export72.cjs` : export vers le site de test (galerie + animations) et `HEROS.md`.
- **Contrôle de chaque héros, en grand** (demande du propriétaire) : rien ne passe à travers autre chose (bras dans
  une barbe → `over: true` ou une autre pose ; arme devant le visage, le museau ou la bouche → la déplacer) ; rien de
  coupé ni de flottant ; pan de ceinture ni trop long ni trop court ; coiffe à la taille de la tête ; arme dans le
  bon sens ; pics de cheveux vers l'arrière ; museau et bec dans la continuité du crâne.
- **Pas de doublon** : avant d'ajouter un héros, compter ce qui existe déjà (coiffe, arme, pose, carrure, jambes,
  regard). Deux héros ne partagent jamais à la fois la silhouette, la pose et l'arme. Variété : humains, bêtes et
  esprits, plusieurs cultures, tailles différentes (`scale`).
- **Élément qui brille** (demande du 20/11/2026) : **pas sur tous les héros, et pas d'étoile**. Seulement ceux qui ont
  un petit élément lumineux (flamme, perle, lanterne, regard, disque solaire…) : cet élément entier s'illumine, par un
  halo doux posé par-dessus. Dans la fiche : `shine: true` (sur l'objet tenu) ou `shine: [[x, y, 'near' | 'far' |
  'head' | 'torso', taille, couleur]]`. Exporté à part (morceau `shine`), sa lumière respire en combat.
- **Aura** : les Épiques (violet) et les Légendaires (or) ont un halo autour de la silhouette, sur les planches, dans la
  galerie et en combat (`aura` dans `public/apercu/apercu.js`, ombre portée de la silhouette).
- Animation : `both: true` = arme tenue à deux mains (les deux bras bougent ensemble) ; `main: 'far'` = c'est le bras
  du fond qui frappe ; `grp: { top: 'swing' }` = un effet suit un bras (ou `head`, `far`).
- Dents de scie (`saw`) : toujours parcourir la ligne **du bas vers le haut**, sinon les pointes rentrent dans la forme.
- Originalité : on s'inspire des mythes (domaine public), jamais du dessin d'un autre jeu, film ou manga.


## Les monstres (commencés le 20/11/2026)

Demande du propriétaire : des **familles de 6 monstres**, beaucoup, pour tous les niveaux, et **pas de famille vue partout**
(pas de squelettes ni de gobelins) ; plutôt de **vraies créatures** que des objets du quotidien qui prennent vie.

- 12 familles validées, 3 par élément (72 monstres) — Feu : Parade des pétards, Fauves de cendre, Idoles d'airain ·
  Vent : Épouvantails, Ruche, Volière d'orage · Eau : Abysses, Horde des glaces, Bayou · Terre : Échiquier, Cuirassés,
  Ronciers. Écartées : grenouilles, potager, jouets, objets oubliés, fanfare, cirés, forge.
- Dans chaque famille, 6 places : rapide, costaud (devant) · tireur, sorts ou soin (derrière) · élite · boss.
- `mon6.cjs` : le petit gabarit des créatures (morceaux animables `G(nom, …)`, œil de bête `eye`, dents `teeth`, registre
  `Mo(famille, place, nom, réglages, dessin)`), une famille par fichier `m-<famille>.cjs`.
- `node zoomM.cjs abysses sortie.html` : la famille en grand (contrôle) ; ajouter `planche` pour la planche à montrer.
- `node exportM.cjs` : export vers `public/apercu/m/` + `monstres.js` ; la page d'animations fait affronter les héros et
  une famille (avec son élite, puis son boss).
- Mêmes contrôles que pour les héros : rien ne passe devant un œil ou une gueule, rien de coupé, pattes lisibles (pas
  d'enchevêtrement), silhouette différente pour chacun des 6.
- **À vérifier sur CHAQUE monstre** (remarque du propriétaire) : une gueule ouverte est **découpée dans la silhouette**
  (le corps a une vraie encoche jusqu'au coin de la bouche, l'intérieur sombre est dessiné derrière avec un bord avant
  creusé : aucun trait ne referme la bouche) ; pattes, pinces, tiges d'yeux, tentacules et « trompes » partent de **sous
  le corps** (dessinés avant lui, il recouvre leur attache) et à un endroit naturel : jamais posés dessus avec un contour.
  Deux parties du même corps (manteau et tête du calmar) = une seule forme.
- Style validé par le propriétaire sur les Abysses (20/11/2026) ; il demande de **se vérifier à chaque fois**.
- Bêtes à quatre pattes : trapues (grosse tête, pattes courtes), pattes par `beast({ front, hind, top, w, … })` (cuisse,
  jarret, patte ; à dessiner avant le corps), fourrure hérissée par `fringe(…)` dans le chemin du corps.
- L'intérieur sombre d'une gueule recule vers le coin de la bouche (bord avant très creusé) : rien ne « bouche » l'avant.
- Doubles évités entre familles (changements par rapport à la liste annoncée) : Fauves → Buffle de braise (au lieu du
  rhinocéros, déjà dans les Glaces) ; Volière → Paon d'orage (au lieu du hibou, harfang dans les Glaces) ; Cuirassés →
  Scarabée-rhinocéros (au lieu de la tortue, déjà dans le Bayou) ; Ronciers → Blaireau de mousse (au lieu du sanglier,
  phacochère dans les Fauves) et Phalène d'écorce (au lieu de la chouette).
- Familles faites : Abysses, Horde des glaces, Bayou. Restent : Parade des pétards, Fauves de cendre, Idoles d'airain,
  Épouvantails, Ruche, Volière d'orage, Échiquier, Cuirassés, Ronciers.
