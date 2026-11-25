# Consigne commune : un FOND DE COMBAT en pixel art HD, animé, pour un clan

Demande du propriétaire (25/11/2026) : refaire tous les fonds de combat en pixel art professionnel HD, détaillés,
ANIMÉS, chacun en rapport avec un groupe de monstres et son général (le chef du clan, un héros HD). 8 clans
(`../monstres/suivi.py`, ROSTER) → 8 fonds :

| clan (général) | élément | idée de lieu (à enrichir, rester original) |
|---|---|---|
| arachne (Arachné) | terre | le repaire des araignées : carrière / grotte de pierre, grandes toiles en courbes, cristaux grenat, cocons |
| meduse (Méduse) | terre | temple englouti dans la jungle, statues pétrifiées, serpents de pierre, or et jade |
| kesha (Kesha) | eau | récif des abysses : coraux, algues, bulles, épaves, lumière douce venue d'en haut (pas de rayons droits) |
| barzul (Barzul) | eau | crique pirate : pont / ponton de bois, navire au mouillage, mer, mouettes |
| lenore (Lenore) | feu | forteresse des oni : murailles, lanternes, braseros, toits recourbés, ciel crépusculaire |
| kael (Kael) | feu | volcan : roche noire, rivières et chutes de lave, braises qui montent, fumée |
| orin (Orin) | vent | sommet sacré des tengu : pins tordus, temple sur les pics, mer de nuages, plumes |
| eldra (Eldra) | vent | montagne des singes : cascades, falaises fleuries, pêchers, bambous, nuages |

## Règles du propriétaire (toutes obligatoires)
- Même qualité que les 36 héros et 24 monstres HD (`refonte-graphique/pixel/hd/GUIDE.md` : rampes de couleurs décalées
  en teinte, une seule lumière EN HAUT À DROITE, pas de noir pur à l'intérieur, détails soignés).
- Plus aucune rayure ni hachure, ni rayons répétés (pas de rayons de soleil en traits droits, pas de pluie en traits) ;
  formes courbes ; signes inventés, jamais de lettres.
- Tout élément est POSÉ (rien ne flotte, sauf ce qui flotte vraiment : nuages, bulles, braises, feuilles qui volent).
- **Une plateforme RECTANGULAIRE d'un bord à l'autre de l'écran pour le combat, JAMAIS de rond au sol.** Le sol où se
  tiennent les combattants est CALME (peu de détails, contrastes doux) pour que les personnages et les chiffres se
  lisent ; les détails et les animations sont autour (fond, côtés, premier plan bas). De l'air autour.
- Ordre des calques (journal v0.38.0) : ciel < ce qui est derrière le paysage < paysage et sol < ce qui bouge devant le
  paysage < combattants < premier plan (bas de l'écran, discret).
- Animé : plusieurs éléments vivent en boucle sans couture (lave qui coule, eau, vagues, cascades, flammes, lanternes
  qui se balancent, nuages qui dérivent, feuilles/braises/bulles qui passent, toiles qui ondulent…), doucement, sans
  distraire du combat. Rien ne clignote fort.
- Le fond est lié à son clan et à son général : on doit reconnaître le domaine (matières, couleurs, signes du clan,
  bannières aux signes inventés, statues…), sans copier un lieu ou une œuvre existante.

## Mesures
L'écran de combat et les places des combattants sont dans `src/game/fight-view.ts` (5 places en losange de chaque côté,
3 rangées de profondeur : voir HERO_X, ROW_DY) ; l'ancien fond pixel `refonte-graphique/pixel/fond.py` donne les repères
à l'échelle 1/3 (240 × 420, sol G = 277, horizon G + 17, bord arrière de l'arène G + 29, pieds des trois rangs
G + 46 / 76 / 106, bord avant G + 122, bas G + 143 ; sur un téléphone peu allongé on ne voit le ciel qu'à partir de
y ≈ 126). **La taille d'un pixel du fond doit être la même que celle d'un pixel des personnages HD en combat**
(mesurer dans `src/game/hd-fight.ts` / le combat HD d'essai) : un fond « HD » à la même finesse que les personnages.

## Fichiers (le pilote crée l'outillage commun, les suivants le réutilisent)
- `refonte-graphique/pixel/fonds/<clan>/build.py` (commentaires en français) → le fond fixe + les calques animés.
- Outils communs dans `refonte-graphique/pixel/fonds/` (module partagé, export, aperçu), décrits dans
  `refonte-graphique/pixel/fonds/LISEZMOI.md` par le pilote.
- Sorties pour le jeu : `public/art/px/fond-<clan>.webp` (+ planche des morceaux animés et leur description en JSON à
  côté du build.py ; le branchement dans le code du jeu se fera ensuite, en une fois).
- Aperçu pour le propriétaire : `refonte-graphique/pixel/sortie/fond-<clan>.gif` (l'animation du fond à la taille d'un
  écran de téléphone, AVEC quelques personnages HD en pose posés sur les places du combat, pour juger la lisibilité et
  l'échelle) + `fond-<clan>.png` (une image fixe).
- Brouillons uniquement dans `<BROUILLON>/fond-<clan>/`.
- Ne pas toucher au code du jeu (`src/`), aux dessins des personnages, ni aux fonds des autres clans. Pas de commit.

## Relecture
Au moins 4 passes : image entière, zooms (coins, sol, éléments animés), animation image par image (boucle sans
couture), aperçu avec les personnages à la taille du téléphone → corriger.
Réponse finale : courte, en français simple pour le propriétaire (ce qu'on voit, ce qui bouge, ce qu'il doit
regarder), puis une partie technique (fichiers, format des calques animés).
