# Consigne : passer un personnage VECTORIEL dans le combat du jeu

Demande du propriétaire (27/11/2026) : « Connecte tous les nouveaux héros, monstres et fonds au jeu de test, supprime
les anciens pour gagner de la place. » Pilote fait sur **Kael** (`assassins-2`, corps à corps), **Jarek**
(`assassins-9`, tir) et le **golem de lave** (`mon-kael-costaud`, monstre). Cette consigne dit comment faire pareil pour
chacun des ~75 autres personnages, un par un, plusieurs agents en même temps.

Pour l'instant tout est derrière `?vecto=1` (gardé sur le téléphone ; `?vecto=0` l'éteint) : un personnage exporté
remplace son pixel art au combat (campagne, tour, donjons, boss, Colisée, accueil, aperçu de compétence) ; un
personnage pas encore exporté garde son pixel art.

## 1. Le format choisi (et pourquoi)

On **garde le format du pixel art** (`HD_ANIM` de `src/game/hd-meta.ts`) : une planche par personnage + une table
générée. `src/game/hd-fight.ts` sert tel quel (même chorégraphie : course jusqu'à la cible, projectile qui vole
jusqu'à la vraie case, impact posé aux pieds de la cible, lumière de charge, tempo commun des attaques de base). Seules
différences, lues par `hd-fight.ts` :

- la planche est `public/art/vecto/jeu/<id>.webp`, rendue lisse à ×`up` (1 pixel de planche par pixel du dessin ;
  le combat montre ~1,16 pixel d'écran par pixel du dessin) ;
- dans la table `src/game/vecto-anim.ts` (GÉNÉRÉE), les cases `[x, y, l, h]` sont en pixels de la planche et
  `(ax, ay)` en pixels du dessin ; chaque personnage porte son `up`.

Pourquoi pas autre chose : animer le dessin vectoriel en direct dans le jeu (SVG ou morceaux) coûterait bien plus cher
au téléphone et demanderait de réécrire chaque `anim.py` en TypeScript ; une vidéo par personnage interdit de séparer
le personnage, l'impact et le projectile. La planche garde la mémoire sous contrôle et réutilise tout ce qui marche.

### Budget mémoire (OBLIGATOIRE : l'iPhone a déjà planté par manque de mémoire graphique)

**Au plus 4,2 Mo de mémoire graphique par planche** (largeur × hauteur × 4 octets ; 2048 × 512), comme le pixel art
(~3 Mo). Un combat charge ~9 planches : ~30 Mo, comme avant. L'outil affiche la mémoire de chaque planche, écrit
`ATTENTION : BUDGET MÉMOIRE DÉPASSÉ` au-delà de 4,2 Mo (ne pas rendre le personnage dans cet état) et refuse au-delà de
6 Mo.

Réglages par défaut (choisis sur le pilote, à ne pas relever sans raison) :

| réglage | défaut | pourquoi |
|---|---|---|
| `up` | 1,0 | le combat montre ~1,16 pixel d'écran par pixel du dessin : sur un dessin lisse, la différence avec 1,25 ne se voit pas à la taille du téléphone (−36 % de mémoire) |
| repos | 8 images par boucle | la respiration est lente : 8 images suffisent |
| coups | 6 images/s loin du coup, **14 images/s de 180 ms avant à 260 ms après le coup** | le geste qui compte reste fluide ; la préparation et le retour, lents, se lisent bien avec moins d'images |
| fusion | deux images de suite presque identiques (écart moyen < 4/255 sur les pixels peints) n'en font qu'une | tenues, arrêts sur image |
| rangement | la largeur de planche (1024 à 2048) qui donne la plus petite surface | |
| effets | `fx_max` 150 : éclairs plein écran et longues fissures retirés | le jeu a son éclair et sa secousse |

Un autre moment fort que le coup (le revers de Kael, un éclair, un saut) : ajouter une fenêtre serrée avec `dense`
(liste de `(t0, t1)` ; remplace celle du coup, à remettre dans la liste). Si la planche dépasse : d'abord `fps`
(5), puis `images` du repos (6), puis retirer des effets (`fx_max`) ; `up` en dernier (jamais sous 0,9).

Pilote (27/11) : Kael 3,5 Mo, Jarek 3,3 Mo, golem de lave 3,6 Mo (pixel art : 3,0 / 2,4 / 3,2 Mo).

## 2. Ce qu'il faut écrire : `jeu.py` dans le dossier du personnage

Un petit fichier, à côté de `<nom>.py` et `anim.py` (`heros/<nom>/jeu.py` ou `monstres/<nom>/jeu.py`). Modèles :
`heros/kael/jeu.py` (corps à corps + sort), `heros/jarek/jeu.py` (tir + sort), `monstres/golem-lave/jeu.py` (monstre).

```python
import anim as A
import kael as K                      # le dessin (pour un monstre chargé par anim.py : DESSIN = A.K)

ID = 'assassins-2'                    # l'id du JEU (table VECTO de src/game/vecto.ts)
ANIM, DESSIN = A, K
JEU = {
    'pose': dict(periode=2000, images=10),
    'attaque': dict(genre='melee', coup=A.ATTACK_HIT, cible=(150, 85), coupe=108),
    'speciale': dict(genre='sort', coup=1485, cible=(A.GEYSER_X, 75), coupe=106, charge=(120, 900), fx_max=100),
}
```

Les **instants** sont en ms depuis le début du coup (ceux d'`anim.py` : `ATTACK`, `SPECIAL`, `ATTACK_HIT`…), les
**x, y** en pixels du dessin (le repère d'`anim.py`, où le personnage regarde à droite, pieds en `FEET`).

| clé | sens |
|---|---|
| `genre` | `'melee'` : le jeu l'amène devant sa cible, il frappe, il revient. `'tir'` : il tire de sa place, le jeu fait voler le projectile jusqu'à la vraie cible. `'sort'` : il lance sur place, ce qui est « sur la cible » apparaît sur chaque cible. `'equipe'` : sort d'équipe (soin, bouclier, bonus) : le jeu pose les effets reçus sur les alliés. `'rayon'` : un jet continu (souffle, rayon) tendu de sa bouche à chaque cible (voir `rayon`). |
| `coup` | l'instant où les dégâts tombent (chiffre, recul). Il tombe toujours pile au début d'une image. Tir : l'arrivée du projectile. |
| `cible` | `(x, y)` : l'ennemi imaginé par l'animation. x = ses pieds, y = la hauteur où le coup le touche. Corps à corps : `x − FEET[0]` est la distance pieds à pieds au moment du coup (l'arme doit toucher un ennemi dont l'avant est à 40 px de ses pieds). |
| `coupe` | colonne : un effet (élément de `fig.fx_back` / `fig.fx_front`) dont le MILIEU est à droite part « sur la cible » (posé aux pieds de la vraie cible). Un nombre, ou une fonction de l'instant (`lambda t: 150 if t < A.S_BURST else 112`). Un effet n'est jamais coupé en deux. |
| `charge` | `(t0, t1)` : la préparation de la spéciale ; le jeu y ajoute sa lumière douce de l'élément. |
| `elan` | (corps à corps, facultatif) `(t0, t1)` : quand il bondit jusqu'à la cible (défaut : de la fin de la charge au coup). |
| `avance` | (corps à corps, ajouté le 27/11 par le lot 2, modèles `monstres/araignee-bondissante/jeu.py`, `monstres/matelot/jeu.py`, `heros/sarvik/jeu.py`) le personnage FONCE dans sa propre animation (`anim.py` déplace tout le corps : `spx`, `Tx`, `tx`, `shift`, `dash`…). Une fonction de l'instant (ms) qui rend ce déplacement vers l'avant en pixels du dessin, presque toujours la clé d'`anim.py` : `avance=lambda t: A.keyed(A.ATTACK, t)['tx']`. L'outil ancre chaque image du corps aux pieds DÉPLACÉS (le corps reste sur place dans la planche) et écrit la liste `avance` (une valeur par image) : `hd-fight.ts` (déjà prêt) fait avancer le personnage au rythme dessiné, ramené à la vraie distance (`portee` − `avance` au coup), et le ramène comme l'animation le ramène (l'animation doit finir à 0 : sinon il se téléporte chez lui). Sans `avance` (ou s'il avance de 3 px au plus), il bondit. `cible` reste celle de l'animation (repère non déplacé). Ce qui est « près de lui » suit son corps ; ce qui part sur la cible ne bouge plus. Planche de contrôle : le corps est dessiné à sa place dans l'animation, `avance N` écrit. Deux images de suite ne fusionnent pas si l'avance change. |
| `tir`, `depuis`, `bouche`, `projectile` | (tir) `tir` = l'instant où le projectile part ; pendant le vol, les effets à droite de la colonne `depuis` sont le projectile (retirés du personnage) ; `bouche` = `(x, y)` d'où il part (bout de l'arme) ; `projectile(fig, i)` dessine le projectile SEUL, pointe en (0, 0), vers la droite (ex. `fig.fx_front.append(A.arrow_fx(fig, (0, 0), 0))`). `proj_images` (2), `proj_ms`. |
| `arc`, `rase`, `vitesse`, `pente` | (tir, facultatifs) hauteur de la cloche (le projectile bascule le long de la courbe), vol au ras du sol, vitesse (défaut : celle de l'animation), angle du dessin. |
| `rayon`, `bouche`, `depuis`, `rayon_max`, `vue_rayon` | (genre `'rayon'`, ajouté le 27/11, modèle `monstres/salamandre/jeu.py`) `rayon` = `(t0, t1)` : quand le jet est dessiné ; `bouche` = `(x, y)` d'où il part (OBLIGATOIRE ; souvent `ctx['mouth']` du dessin à l'instant du coup) ; pendant la fenêtre, un effet dont le milieu est entre `depuis` (défaut : `bouche` − 4) et `coupe` est le jet, rendu à part, couché à l'horizontale depuis la bouche (l'outil le tourne de l'angle bouche → `cible`). Le jeu (`beam` de `hd-fight.ts`) le tourne vers la vraie cible et l'étire de `longueur` (bouche → `cible` du dessin) jusqu'à elle. Ce qui est au-delà de `coupe` (l'impact, l'ennemi qui s'embrase) part sur la cible comme d'habitude. Le jet n'est pas retiré par `fx_max` (seulement s'il est plus long que `rayon_max`, 400, ou plus haut que 0,6 × `fx_max`) ; `vue_rayon` : le cadre de rendu du jet (défaut : de 40 px derrière la bouche à 60 px après la cible, 120 de haut). Planche de contrôle : le jet en BLEU, tourné. |
| `retour`, `revient`, `retour_images`, `arme` | (tir, ajouté le 27/11 par le lot 7, modèles `heros/sable/jeu.py`, `heros/zephyre/jeu.py`, `heros/aldric/jeu.py`) l'arme qui REVIENT (boomerang, khopesh, anneau). `retour` = `(t0, t1)` : elle quitte la cible à `t0` (souvent `coup`) et arrive dans la main à `t1` (la prise) ; pendant cette fenêtre comme pendant l'aller, elle est retirée du personnage. `revient(fig, i)` dessine l'arme seule qui revient (centre en (0, 0), sa traînée à DROITE ; défaut : `projectile`), `retour_images` images (défaut `proj_images`). Le jeu (`hd-fight.ts`, déjà prêt : `retour`, `retourDe`) la fait voler de la 1re cible à la bouche pendant les images de la fenêtre, avec la durée du vol. `arme` = liste des NOMS de morceaux du dessin qui sont l'arme lancée quand elle est dessinée en morceaux (`fig.part`, pas un effet : le khopesh `fk…` de Sable, le shuriken `fstar` de Zéphyre) : retirés du corps pendant le vol (aller et retour), posés sur la cible s'ils sont au-delà de `coupe` (le shuriken planté), sinon gardés. `projectile` / `revient` peuvent dessiner des morceaux (`S.khopesh(fig, …)`, `Z.add_star(fig, …)`) : ils sont rendus. |
| `vol`, `sur_cible`, `depuis` (fonction) | (facultatifs, lot 7) quand la colonne ne suffit pas à trier les effets (l'arme qui revient passe sur l'impact ; la fumée du canon est devant lui). `depuis` peut être une fonction de l'instant (`lambda t: x`, ex. la place de l'arme − 14). `vol(t, x, y, couche, el)` → vrai si l'effet est l'arme en vol (remplace `depuis` ; x, y = milieu de l'effet, couche = `'b'` (derrière) ou `'f'` (devant), el = son SVG : on peut reconnaître une couleur de contour, un genre de forme). `sur_cible(t, x, y, couche, el)` → vrai s'il part sur la cible (remplace `coupe`, toujours après `cible_des`). Ex. Jessa : `sur_cible=lambda t, x, y, c, el: x > 120 and A.SINK not in el` (tout ce qui est devant le canon, sauf la fumée de poudre). |
| `fx_max` | (150) un effet plus large (ou large ET haut) que ça est retiré : éclair plein écran (le jeu a son éclair et sa secousse), longues fissures qui iraient du lanceur à la cible. |
| `cible_des` | (facultatif) avant cet instant, rien ne part sur la cible. |
| `periode`, `images` | (`pose`) la durée d'une respiration (ms ; défaut `IDLE_T`/`IDLE` d'anim.py) et le nombre d'images (8). |
| `fps`, `fps_coup`, `dense` | (facultatifs) images par seconde loin du coup (6) et dans les fenêtres serrées (14) ; `dense` = les fenêtres serrées, liste de `(t0, t1)` en ms (défaut : de 180 ms avant à 260 ms après le coup). |
| `duree`, `action` | (facultatifs) durée du coup (défaut : dernière clé de `ATTACK`/`SPECIAL`), nom de l'action dans `anim.py` (`'attack'`, `'special'`). |
| `vue`, `up`, `pieds`, `sol`, `rendu` | (rarement) la scène rendue (défaut `VIEW` d'anim.py), la finesse, les pieds (`FEET`), le sol (`GRD`), une fonction `rendu(T, segs)` si `frame_svg` a une autre signature (3 anim.py : `alg`, `cc`, `la`). |

Comment c'est rendu (rien à changer dans `anim.py`) : l'outil appelle `frame_svg(T, segs)` aux bons instants (l'action
finit sur la phase 0 de la respiration : pas d'à-coup au retour au repos), attrape la figure construite par `build`,
peint chaque effet d'une couleur à part pour mesurer sa place, puis rend le personnage avec ses effets proches, et à
part ce qui est sur la cible. Il rogne, retire les doublons, fusionne les images identiques qui se suivent (tenue,
arrêt sur image).

## 3. Lancer, contrôler

```
python3 refonte-graphique/ui-moderne/jeu_export_vecto.py --voir <BROUILLON>/export heros/<nom>     # 20 à 40 s
```

(plusieurs dossiers possibles ; chacun tourne dans son propre processus.) Il écrit `public/art/vecto/jeu/<id>.webp`,
`<dossier>/jeu.json`, puis réassemble `src/game/vecto-anim.ts` à partir de TOUS les `jeu.json` (plusieurs agents en
même temps : chacun n'écrit que son `jeu.json` ; la table est refaite entière à chaque fois). Seulement la table :
`--assembler`. Il affiche, par animation, le nombre d'images, la durée, l'image du coup, les effets retirés, la taille
de la planche et **sa mémoire graphique** (budget : 4,2 Mo, voir section 1).

La planche de contrôle `<BROUILLON>/export/export-<nom>.png` montre chaque image : le personnage en place (ligne verte
= sol, croix jaune = pieds), en ROUGE ce qui sera posé sur la cible (à la place imaginée), en BLEU le projectile, la
colonne `coupe`, le rond rouge = `cible`, « COUP » et « charge ». Vérifier :

- le personnage ne bouge pas de ses pieds, rien de lui n'est rouge ;
- en rouge : l'impact, ce qui tombe ou jaillit sur l'ennemi, la flèche plantée ; rien ne saute du personnage à la cible
  au milieu d'un geste (sinon déplacer `coupe`, ou une fonction de l'instant) ;
- tir : pendant le vol, plus de projectile sur le personnage ; le projectile bleu entier ;
- COUP sur la bonne image.

Puis le **vrai combat** (obligatoire avant de dire « fait ») :

```
npx vite build --outDir <BROUILLON>/dist      # jamais npm run build
npx vite preview --outDir <BROUILLON>/dist --port <port> &
HEROS=<id>,<id> CLEARED=<n> node refonte-graphique/ui-moderne/combat-video.cjs <BROUILLON>/video <port> 30 25
```

`combat-video.cjs` joue le combat en temps virtuel et capture chaque image (×2, 390 × 844) : aucune image manquée.
Un monstre : `CLEARED` = l'étape d'avant un combat de son clan avec son rôle (`src/game/look.ts` : campagne, rôle
`ROLE_OF` ; ex. 25 → étape 26, clan de Kael, 3 golems). Les spéciales arrivent quand l'énergie est pleine (souvent
après 20 à 40 s). Vérifier sur une planche de quelques images : bonne taille (comme ses voisins), pieds sur la
plateforme, il regarde l'ennemi (un monstre est retourné), le coup et l'effet tombent ensemble, l'impact sur la vraie
cible (même au rang du fond). Arrêter l'aperçu à la fin.

Ne rien publier ni envoyer : dire quels fichiers ont changé (`jeu.py`, `jeu.json`, `public/art/vecto/jeu/<id>.webp`,
`src/game/vecto-anim.ts`).

### Temps par personnage

Export : 20 à 40 s de calcul. Écrire `jeu.py` (lire `anim.py` : les clés, l'instant du coup, où est l'ennemi, ce que
dessinent les effets), regarder la planche, retoucher `coupe` une ou deux fois, regarder le vrai combat : **15 à 30 min
d'agent par personnage** (un peu plus pour un tir).

### Pas encore géré par l'outil (à ajouter au premier personnage qui en a besoin)

- ~~`rayon`~~ : fait le 27/11 (lot 6, voir la clé `rayon` plus haut ; `hd-fight.ts` n'a pas changé) ;
- ~~`retour`~~ : fait le 27/11 (lot 7, voir les clés `retour`, `arme`, `vol`, `sur_cible` plus haut ; `hd-fight.ts` n'a pas changé) ;
- ~~`avance`~~ : fait le 27/11 (lot 2, voir la clé `avance` plus haut ; `hd-fight.ts` n'a pas changé). Le même jour, deux
  défauts de l'outil corrigés (lot 2) : la mesure des effets lisait parfois le numéro d'à côté sur les bords lissés ou
  là où deux effets se recouvrent (une ombre au sol mesurée 158 px, retirée « trop grande » ; des gouttes classées
  au mauvais endroit) : numéros espacés + clé de contrôle (`id_color`), pixels isolés écartés, un morceau caché sous
  le suivant prend la boîte de son effet (`hidden_parts`) ; et une image de la fenêtre serrée trop proche d'un instant
  clé était retirée avec le pas LENT (167 ms) : le bond juste avant le coup perdait toutes ses images ;
- les effets reçus d'un sort d'équipe (`genre='equipe'`) sont encore ceux du pixel art (`public/art/hd/fx/`) : à
  redessiner une fois, dans le même style, pour les 4 éléments.

Remarque : la spéciale de Kael (« Soif de combat ») est un bonus d'équipe dans les règles : quand elle ne vise aucun
ennemi, le mur de flammes n'a pas de cible et seul le geste se voit (déjà le cas en pixel art).

## 4. Inventaire : ce que le jeu prend encore dans le pixel art, et son remplaçant

| usage (fichier de src/) | images | remplaçant vectoriel |
|---|---|---|
| combat : personnages (`hd-fight.ts`, `hd-meta.ts` GÉNÉRÉ, `hd-tempo.ts`, `fight-view.ts`) | `public/art/hd/<id>.webp` (64 planches) | `public/art/vecto/jeu/<id>.webp` + `src/game/vecto-anim.ts` (cette consigne) |
| combat : effets reçus des sorts d'équipe (`hd-fight.ts` : `receptionFx`, `playReception`) | `public/art/hd/fx/` (35) | à faire : effets vectoriels (soin, bouclier, bonus…) × 4 éléments, même format `fx` |
| cartes du bas du combat (`battle-scene.ts`) | (ancienne bande `public/art/hd/pied/`) | fait (27/11) : la tête vectorielle `art/vecto/v/<id>.webp` (`heroImage`, `heros/tetes.py`), sans drapeau |
| héros en pied des menus (`ui/hero-figure.tsx`, `ui/sections/hero-fig.tsx`, `CardFigure` de `ui/kit.tsx`) | `public/art/hd/pied/`, `public/art/hd/pose/` (`hcard-still`) | `art/vecto/<id>.webp` et `-160.webp` (`vectoFig`, déjà branché avec `?vecto=1` dans `kit.tsx`, `hero-figure.tsx`, `hero-detail.tsx`) ; `hero-fig.tsx` reste à brancher |
| visages carrés partout (`art.ts` : `faceUrl`, `heroImage`, `monsterImage` ; listes, courrier, amis, Colisée, prép.) | `public/art/hd/v/` | `public/art/vecto/v/<id>.webp` (faits par `heros/tetes.py`, 47 héros) ; **à faire pour les monstres et grands boss** ; puis `faceUrl` → toujours `art/vecto/v/` |
| savoir qu'un personnage est dessiné / qu'un grand boss existe (`look.ts` : `hasFigure`, `bigBoss` ; `vecto.ts`) | `src/game/hd-figures.ts` (GÉNÉRÉ par `vignettes.py`) | `VECTO` de `vecto.ts` / `VECTO_ANIM` |
| fonds de combat (`bg/fond-px.ts`, `fond-meta.ts` GÉNÉRÉ, `look.ts`) | `public/art/px/fonds/` (8 clans) | `public/art/vecto/fonds/` + `src/game/fond-vecto.ts` (fait, derrière `?vecto=1`) |
| décors des cartes de modes des menus (`ui/fond-image.ts` : `sceneVar`, aventure, donjons) | `public/art/px/fonds/<clan>.webp` | `public/art/vecto/fonds/<clan>.webp` (image fixe du fond vectoriel) |
| CSS (`ui/style.css` : `img[src^="art/hd/"] { image-rendering: pixelated }`) | — | à retirer avec `art/hd/` |
| tests (`tests/heros-de-clan.test.ts`, `clans.test.ts`, `effets.test.ts`, `dragons.test.ts`) | lisent `HD_FIG` / `HD_ANIM` / `figureUrl` | à réécrire sur `VECTO` / `VECTO_ANIM` au moment de la bascule |
| pictos (`icons.webp`, `art/icons/`), chargement (`art/ui-px/`), logo (`art/ui/`) | style moderne, pas du pixel art de personnage | **à garder** |

## 5. La bascule finale, puis ce qu'on supprimera (quand TOUS seront passés)

Bascule (une seule conversation, quand les ~75 personnages, les effets reçus et les visages des monstres sont faits) :
`vectoOn()` vrai par défaut (ou retiré), `CHARS` de `hd-fight.ts` = `VECTO_ANIM.chars` seul, `faceUrl` sur
`art/vecto/v/`, `hasFigure` / `bigBoss` sur `VECTO`, `fond-px.ts` et `fond-image.ts` sur les fonds vectoriels, tests
réécrits, puis la suppression ci-dessous. Vérifier un combat de chaque mode, l'accueil, le Colisée et un vieux
téléphone avant d'envoyer.

**À supprimer à la fin** (pas avant) :

- images : `public/art/hd/` en entier (planches, `fx/`, `v/`, `pied/`, `pose/`), `public/art/px/` en entier (`fonds/`) ;
- code généré : `src/game/hd-meta.ts`, `src/game/hd-figures.ts`, `src/game/fond-meta.ts` ;
- code : la partie pixel de `bg/fond-px.ts` (`pxf-`, `FOND_META`, filtre NEAREST), `figureUrl` de `art.ts`, `ui/sections/hero-fig.tsx` et la bande de `ui/hero-figure.tsx` (remplacés par l'image
  vectorielle), `hcard-still` (`art/hd/pose`) de `ui/kit.tsx`, `stillFig` / `stillStrike` de `fight-view.ts` (inutiles
  quand les dragons ont leur planche), la règle CSS `img[src^="art/hd/"]` de `ui/style.css`, l'essai `?vecto=` de
  `vecto.ts` ;
- chaînes de fabrication du pixel art : `refonte-graphique/pixel/hd/` (dessins `.txt`, `anim/*/build.py`,
  `anim/jeu_export.py`, `anim/vignettes.py`, `anim/controle_coupes.py`, `anim/vitesse-attaques.ts`, `boss/`,
  `consignes/`, `suivi.py`), `refonte-graphique/pixel/fonds/` (décors pixel), `refonte-graphique/pixel/persos/`,
  `refonte-graphique/pixel/controle.py` (et, après avoir vérifié avec `grep` que `pixel/ui/` ne s'en sert plus :
  `pixel/pix.py`, `pixel/scene.py`, `pixel/voir.py`, `pixel/GUIDE.md`), et dans `refonte-graphique/pixel/sortie/` les sorties du pixel art
  (`anim-*.gif`, `anim-*-planche.png`, `controle-speciales/`, `coupes-verticales.md`, `vitesse-attaques.md`…).

**À garder** :

- `refonte-graphique/pixel/sortie/ui/vecto/` : les sorties VECTORIELLES (vidéos, planches, avis, `jeu-pilote/`) ;
- `refonte-graphique/pixel/ui/` (plan et style de l'interface : `PLAN.md`, `STYLE.md`) tant qu'il sert de référence ;
- `refonte-graphique/ui-moderne/` en entier (dessins, animations, `jeu.py`, `jeu.json`, cet outil) ;
- `public/art/vecto/` (images fixes, `v/`, `fonds/`, `jeu/`), `public/art/icons*`, `public/art/ui*` ;
- `src/game/hd-fight.ts` et `src/game/hd-tempo.ts` (ils servent au vectoriel ; seulement renommer plus tard si on veut).

## 6. Le plan pour les ~75 personnages

Ordre : d'abord ceux qui jouent le plus (les 47 héros, puis les 24 monstres de clan, puis les 4 grands boss, qui
demandent `up` plus petit : ils sont dessinés deux fois plus grands). Lots de 5 à 8 personnages par agent, en
parallèle (chacun n'écrit que ses `jeu.py` / `jeu.json` / planches ; la table se refait seule). Regrouper par genre
pour aller vite : corps à corps (modèle Kael, golem), tirs (modèle Jarek), sorts, sorts d'équipe. Le premier agent qui
tombe sur un `rayon`, un `retour` ou une `avance` ajoute ce cas à l'outil (et à cette consigne) avant les autres de ce
genre. Les 3 dragons (Brasyr, Rocvar, Venthys) passent comme les autres : ils remplacent alors `stillStrike`.
Ensuite : effets reçus vectoriels, visages des monstres, puis la bascule et la suppression (section 5).
