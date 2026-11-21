# Découper un personnage en morceaux animés (guide)

Les 144 dessins Hailuo (`public/art/p/<id>.webp`) sont découpés en morceaux qui tournent autour de leurs articulations
pendant les combats (repos, attaque de base, attaque spéciale). Exemple fini : `refonte-graphique/rig/knights-4.json`
(légionnaire : bras de l'épée, tête, bouclier).

## Les étapes, pour un personnage

1. `python3 refonte-graphique/rig.py grille <id>` puis regarder `refonte-graphique/rig-out/<id>-grille.png` (dessin agrandi ×1,6,
   quadrillé tous les 20 px, chiffres = pixels de l'image d'origine ; le rond violet = les pieds).
2. Écrire `refonte-graphique/rig/<id>.json` (format ci-dessous).
3. `python3 refonte-graphique/rig.py <id>` puis regarder `refonte-graphique/rig-out/<id>.png`, de gauche à droite :
   contours et articulations | corps rebouché | repos | élan | coup | attaque spéciale.
4. Corriger et recommencer jusqu'à ce que tout passe le contrôle ci-dessous (2 à 4 passes en général).

## Format

```json
{ "parts": [
  { "name": "queue", "kind": "tail", "poly": [[x,y], …], "pivot": [x,y], "behind": true },
  { "name": "tete", "kind": "head", "poly": […], "pivot": [x,y] },
  { "name": "epee", "kind": "weapon", "poly": […], "pivot": [x,y], "swing": [-35, 80, 130] },
  { "name": "bouclier", "kind": "offhand", "poly": […], "pivot": [x,y], "swing": [-3, 4, -18], "move": [10, 0] }
] }
```

- Coordonnées en pixels de l'image d'origine (lire la grille). Le personnage regarde vers la DROITE.
- `poly` : le contour du morceau, un peu large dans le vide (le fond transparent ne coûte rien), mais **serré là où le morceau
  touche le corps** (sinon un bout de corps part avec lui). L'outil ajoute tout seul le trait de contour sombre (5 px).
- `pivot` : l'articulation (épaule, coude, poignet, cou, base de la queue, attache de l'aile). Elle doit être sur le corps,
  pas dans le vide, sinon le morceau « décolle ».
- `kind` : `head` (tête), `weapon` (bras ou main qui porte l'arme principale + l'arme), `offhand` (bouclier, deuxième arme,
  objet dans l'autre main), `limb` (membre libre : bras sans arme, patte avant, pince), `tail` (queue), `wing` (aile).
- `swing` : [élan, coup, spéciale] en degrés, positif = sens des aiguilles d'une montre. Par défaut : weapon [-35, 80, 130],
  head [-4, 6, 8], offhand [6, -10, -20], limb [-12, 25, 35], tail [10, -15, -25], wing [-15, 20, 30].
  **Choisir le sens qui a l'air juste pour CE dessin** : une épée levée s'abat vers l'avant (positif) ; une lance tenue à
  l'horizontale se pousse plutôt (`move`: [30, 0] et un petit `swing`) ; un arc ou un bâton magique bouge peu (±10°) ;
  une arme tenue vers le bas remonte en frappant (négatif). Plus l'arme est grande, plus l'angle doit rester raisonnable.
- `move` : décalage en pixels au moment du coup (estoc, coup de bouclier, morsure en avant).
- `behind` : true pour un morceau qui doit passer DERRIÈRE le corps (aile ou bras du fond, queue derrière les jambes).
- `fill` : false pour un morceau fin posé sur le vide à côté du corps (manche de faux, hampe, lance) : sinon un « fantôme »
  plein reste à son ancienne place quand il bouge (le corps est prolongé jusqu'à ~20 px derrière les morceaux).
- L'ordre de la liste = l'ordre d'affichage devant le corps (le dernier est tout devant). Si deux contours se recouvrent,
  le pixel commun va au morceau le plus en avant.

## Quels morceaux

- Héros : en général 3 morceaux : la **tête** (avec cheveux, casque, chapeau, cornes), le **bras armé + l'arme**, et un
  troisième selon le dessin : bouclier / deuxième arme / objet de l'autre main (`offhand`), ou l'autre bras (`limb`),
  ou ailes / queue s'il y en a. Pas plus de 5 morceaux.
- Monstres : la **tête** (avec la gueule, les cornes, les défenses), puis selon la bête : queue, ailes, pinces, patte avant,
  tentacules, arme. Une créature sans tête distincte (méduse, feu follet, lanterne, tambour) : découper ce qui peut bouger
  (tentacules, flamme, baguettes, bras) ; la tête n'est pas obligatoire.
- Si un membre est caché (sous une cape, derrière le corps), couper là où il redevient visible (poignet, coude) et mettre
  l'articulation à cet endroit.
- Une arme tenue à deux mains : un seul morceau `weapon` avec les deux mains, pivot entre les mains ou à l'épaule avant,
  angles plus petits (±25°).

## Contrôle (sur la planche `rig-out/<id>.png`)

- **Corps rebouché** (2e case) : aucun reste reconnaissable d'un morceau (bout de lame, œil, morceau de crête, pointe de
  corne, doigt). Les zones « rebouchées » floues ou en aplats sont normales : elles sont cachées par les morceaux.
- **Repos** (3e case) : identique au dessin d'origine (pas de trou, pas de bord coupé net, pas de double).
- **Élan / coup / spéciale** : le geste a du sens (l'arme frappe vers l'avant, vers la droite ; la tête reste sur le cou ;
  rien ne se détache) ; aucun trou ni bord coupé tout droit ne devient visible ; les morceaux ne sortent pas du cou ou de
  l'épaule de façon grotesque. Si une zone rebouchée floue devient trop visible, réduire l'angle ou élargir le contour.
- Un morceau mal découpé vaut moins que pas de morceau : en cas de doute, moins de morceaux, angles plus petits.

## Lancer tout

`python3 refonte-graphique/rig.py tout` puis `python3 refonte-graphique/art-jeu.py` (met à jour `src/game/art-meta.ts`).

Le corps et les morceaux d'un personnage sont regroupés dans **une seule image** `public/art/r/<id>.webp` (moins de
fichiers à télécharger) ; la place de chaque morceau dans cette image est dans `rig-out/<id>.json` (`base`, `ax`, `ay`).
