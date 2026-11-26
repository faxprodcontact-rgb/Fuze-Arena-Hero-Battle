# Consigne : exporter un personnage HD animé vers le jeu (format « jeu »)

Demande du propriétaire (25/11/2026) : en combat, le corps à corps va jusqu'à sa cible et frappe ; le tir vole jusqu'à
la VRAIE cible (même au fond en bas à droite) et y fait son effet ; une spéciale qui charge montre une petite lumière
douce. Essai fait sur Eldra, Jinn, Myrr, matelot, salamandre, sorcier-oni (combat « Combat HD (essai) » des Outils de
test). Cette consigne dit comment faire pareil pour chacun des autres personnages.

Ce qu'on NE touche PAS : le dessin (`.txt`), `hd.py`, les GIF et la planche du personnage (ils doivent rester
identiques), les dossiers des personnages qu'un autre agent est en train d'animer.

## 1. Le principe (rien à réécrire)

`refonte-graphique/pixel/hd/anim/jeu_export.py` importe le `build.py`, remplace un instant sa fonction `compose(...)`
pour garder l'image qu'elle rend (exactement celle du GIF : quels que soient ses arguments, positionnels ou nommés,
`obj`, `solid`, `ghosts`, `veil`, `shake`, `tint`…, et avec ses calques translucides déjà mélangés), et appelle son
`build_all()`. Il découpe ensuite chaque image, par colonnes, en trois : **le personnage en place** (avec ses effets « sur lui »), **ce qui est sur la cible** (posé aux
pieds de la vraie cible par le jeu), **le projectile** (que le jeu fait voler). Il écrit la planche
`public/art/hd/<id>.webp` (images rognées, ×2 sans flou) et la met dans `src/game/hd-meta.ts` (généré, ne pas modifier
à la main).

Le `build.py` doit donc : avoir `SOL` (le point « sol » sur la toile), `compose(...)` et `build_all()` qui renvoie
`{'pose': [(image, ms)…], 'attaque': […], 'speciale': […]}` où chaque image est le résultat direct d'un appel à
`compose` (c'est le cas de tous les build.py actuels). Si une image est retouchée APRÈS compose (copie, filtre),
l'export s'arrête avec un message : déplacer la retouche avant compose (sur la grille de lettres).

## 2. Ce que le build.py doit ajouter : le dictionnaire `JEU`

Juste avant `if __name__ == '__main__':`, un bloc comme celui-ci (exemples réels : `anim/eldra/build.py`,
`anim/jinn/build.py`, `anim/myrr/build.py`, `anim/matelot/build.py`, `anim/salamandre/build.py`,
`anim/sorcier-oni/build.py`) :

```python
# ---------------------------------------------------------------- export vers le jeu (../jeu_export.py, consigne export-jeu.md)
JEU = {
    'attaque': dict(genre='tir', tir=(2, 4), depuis=122, coup=4, cible=(ENEMY_X - 8, GROUND - 50), coupe=185),
    'speciale': dict(genre='sort', coup=9, cible=(ENEMY_X, GROUND - 46), coupe=[None] * 7 + [150] * 9, charge=(1, 3)),
}
```

Les numéros d'image commencent à 0 (ceux de la planche `anim-<nom>-planche.png`). Les x, y sont ceux de la TOILE du
build.py (celle où `SOL` est posé), pas de la grille du dessin.

| clé | sens |
|---|---|
| `genre` | `'melee'` : le jeu l'amène devant sa cible, il frappe, il revient. `'tir'` : il tire sur place, le projectile vole jusqu'à la cible. `'sort'` : il lance sur place, l'effet apparaît directement sur chaque cible (pluie de flèches, éclair, colonne…). `'rayon'` : jet continu de la bouche à la cible (souffle de feu) : le jeu l'oriente et l'étire jusqu'à elle. `'equipe'` : sort d'équipe (soin, bouclier, bonus) : rien sur l'ennemi, le jeu pose les effets reçus (`anim/effets/`) sur les alliés. |
| `coup` | l'image où les dégâts tombent (le chiffre s'affiche, la cible recule). Pour `'tir'` : la première image de l'impact, juste après le vol. Pour `'equipe'` : l'image où l'effet part vers les alliés. |
| `cible` | `(x, y)` : l'ennemi tel que l'animateur l'a imaginé. x = ses pieds (`ENEMY_X`, `FOE[0]`…), y = la hauteur où le coup le touche (sa poitrine). Le jeu pose ce point sur la vraie cible. Pour un corps à corps, `x − SOL[0]` est la distance pieds à pieds au moment du coup : il faut que l'arme touche bien l'ennemi à cette distance. |
| `coupe` | la colonne à partir de laquelle tout (effets ET personnage : une flèche plantée dans l'ennemi est souvent dessinée avec lui) est « sur la cible ». Défaut : `cible x − 36`. Une liste (une valeur par image, `None` = rien sur la cible) quand l'effet passe d'abord près du personnage puis sur la cible (Jinn, salamandre). Rien de ce qui appartient au personnage (corps, arme, effets autour de lui) ne doit passer cette colonne, sauf au moment du coup d'un corps à corps (le jeu aligne alors exactement les deux morceaux). |
| `avance` | (corps à corps qui fonce, facultatif) le déplacement vers l'avant cuit dans chaque image, en pixels, souvent `[f.get('tx', 0) for f in ATTAQUE]`. L'export le retire (le personnage revient en place) ; le jeu le déplace vers la vraie cible au même rythme. Sans `avance`, le jeu le fait bondir jusqu'à la cible pendant les images de préparation (`elan`, défaut : de la fin de la charge au coup). |
| `elan` | (facultatif, corps à corps sans `avance`) `(i0, i1)` : images pendant lesquelles il va jusqu'à la cible. |
| `tir` | `(i0, i1)` : images où le projectile vole (i0 = la première où il a quitté l'arme ; i1 = `coup`). |
| `rayon` | `(i0, i1)` : images du jet continu. |
| `depuis` | (`tir`, `rayon`) la colonne où le projectile quitte le personnage : tout ce qui est à droite pendant le vol devient le projectile. Prendre le bout de l'arme / la bouche au repos + 2 ou 3 pixels. |
| `charge` | `(i0, i1)` (incluses) : les images où il se concentre avant la spéciale. Le jeu y ajoute une lumière douce de l'élément (halo rond qui pulse, flaque de lumière au sol, le dessin s'éclaire un peu). Ne pas la dessiner en plus. |
| `arc` | (`tir`, facultatif) hauteur de la cloche du vol, en pixels (0 = droit). |
| `retour` | (`tir`, facultatif) `(i0, i1)` : images où l'arme lancée revient à la main (boomerang, khopesh) : ce qui est à droite de `depuis` vole de la cible jusqu'à la main (sinon elle réapparaît d'un coup à mi-chemin). |
| `rase` | (`tir`, facultatif) `True` : le projectile court au ras du sol (vague, pics de glace) : il glisse à plat jusqu'aux pieds de la cible au lieu de monter vers sa poitrine. |
| `calques` | (facultatif, conseillé dès qu'un effet traverse `coupe` ou `depuis`) `True` : la coupe ne touche plus le personnage (il n'est JAMAIS coupé, arme comprise) et les effets partent par **morceaux entiers** (pixels qui se touchent) : un morceau part s'il commence à droite de la colonne, sinon il reste en entier. Ce que le personnage cachait d'un effet qui part est complété. Plus aucun bord droit vertical. Il faut que `compose` reçoive les effets par ses arguments `fx_…` (le cas de tous les build.py). Au corps à corps, l'arme reste avec le personnage (il est devant la cible au moment du coup). |
| `vitesse`, `pente` | (`tir`, facultatifs) la vitesse du projectile (pixels du dessin par seconde) et l'angle de son dessin (radians, positif = il descend). Mesurés tout seuls sur le mouvement du bout du projectile d'une image de vol à l'autre (avec une seule image de vol : de sa queue au bord `depuis` à son bout, sur cette image). À donner seulement si la mesure est fausse (projectile qui grossit, qui tourne…). |

Choisir le genre d'après le GIF : un coup porté au contact → `melee` (même si l'arme est longue) ; un objet qui part de
l'arme et traverse la toile → `tir` ; un effet qui tombe ou jaillit sur l'ennemi sans traverser → `sort` ; un jet
continu → `rayon` ; une spéciale qui ne frappe pas (soin, bouclier, bonus, provocation) → `equipe`.

## 3. Lancer, contrôler

```
python3 refonte-graphique/pixel/hd/anim/jeu_export.py --voir <BROUILLON>/export <nom>
```

(depuis la racine du dépôt ; 10 à 30 s par personnage ; plusieurs noms possibles ; `--effets` réécrit aussi les effets
reçus). La planche de contrôle `<BROUILLON>/export/export-<nom>.png` montre chaque image : le personnage en place, en
ROUGE ce qui sera posé sur la cible, en BLEU le projectile, en VERT l'arme qui revient (`retour`), la ligne rouge pâle = `coupe`, le rond rouge = `cible`,
« COUP » et « charge » sur les images clés. Vérifier :

- le personnage reste à sa place sur toutes les images (pieds sur la ligne verte), sans morceau coupé ;
- en rouge : seulement l'impact, ce qui tombe sur l'ennemi, la flèche plantée ;
- en bleu (vol) : le projectile entier sur au moins une image, rien du personnage ;
- `COUP` sur la bonne image, `charge` sur la préparation de la spéciale.

L'export écrit aussi `visage` (le carré de la tête au repos). Après chaque export, relancer
`python3 refonte-graphique/pixel/hd/anim/vignettes.py` : il refait les images des menus (visage `public/art/hd/v/<id>.webp`,
respiration en pied `public/art/hd/pied/<id>.webp`) et `src/game/hd-figures.ts` (le jeu s'en sert aussi pour savoir
qu'un grand boss est exporté).

Puis regarder le combat dans le jeu (les vrais déplacements) : `npm run dev`, puis un combat où le personnage joue
(depuis la v0.56.0, tout le jeu est en HD et il n'y a plus de combat d'essai) : un héros dans la section ; un monstre
dans un combat de son clan (`src/game/look.ts` : campagne, tour, donjons) ; un grand boss au boss de guilde (feu) ou au
boss du jour de son élément.

Ne rien publier, ne rien envoyer : dire à l'orchestrateur quels fichiers ont changé (`build.py` du personnage,
`public/art/hd/<id>.webp`, `src/game/hd-meta.ts`, et ce qu'a refait `vignettes.py`).

## 4. Changements de l'export (25/11/2026)

- `compose` : l'export garde l'image finale rendue par `compose` (plus de calques reconstruits). Avant, un argument
  positionnel en plus (`obj`, `solid` d'Anubis, Célia, Minotaure) était mal lu, et `shake`, `tint`, `flash`… ne
  touchaient que le personnage ; un effet translucide de devant remplaçait le personnage au lieu de se mélanger (Bérold,
  spéciale 4 à 9). Le voile de Corvin (`veil`) n'est plus nécessaire pour l'export, mais il est sans effet sur le GIF :
  on le laisse.
- `vitesse` et `pente` des projectiles : mesurées sur le mouvement du bout du projectile (voir le tableau), réglables
  dans `JEU`.
- Un `build.py` doit rendre la même image à chaque lancement : jamais `max(set(...), key=...)` (l'ordre d'un `set`
  change d'un lancement à l'autre) ; à égalité, un ordre fixe (exemple : `majority` de `anim/tengu-eventail/build.py`).
  Encore à reprendre de la même façon (leur GIF peut changer d'un pixel caché d'un lancement à l'autre) : `arachne`,
  `araignee-cuirassee`, `araignee-tisseuse`, `gabryel` (`fill_under` / bouchage des trous).


## 5. Même vitesse pour toutes les attaques de base (25/11/2026)

Demande du propriétaire : « tous les héros tapent à peu près à la même vitesse sur l'attaque basique » (le golem de
lave mettait 1,9 s, l'homme-poisson 0,8 s). Rien à refaire dans les `build.py` ni dans l'export : c'est le jeu qui
règle le tempo au moment de jouer l'attaque (`src/game/hd-tempo.ts`, appelé par `hdStrike` de `src/game/hd-fight.ts`).
Les règles du combat (`src/core/battle/`) ne changent pas : seul l'affichage est plus court ou plus long.

- Le coup tombe vers 0,44 s et tout est fini vers 0,98 s (vitesse ×1, course, vol et retour compris ; réglages dans
  `EVEN` en tête de `hd-tempo.ts`).
- Les images gardent leur rythme : avant le coup, elles sont toutes raccourcies (ou allongées) dans la même proportion ;
  après le coup, la récupération est raccourcie davantage que l'image du coup et celle de l'impact. Une image ne descend
  jamais sous 45 ms (sauf si l'animateur l'a faite plus courte) ; une attaque rapide est allongée au plus de ×1,25 ;
  une attaque lente est raccourcie au plus de ×0,45 avant le coup (l'élan reste lisible) et ×0,3 après.
- Corps à corps : la course jusqu'à la cible garde le temps qu'il lui faut (les images de l'élan ne sont jamais plus
  rapides que la course) ; sans élan dessiné, le retour en courant commence pendant la fin de la récupération.
- Tir : le vol d'un projectile d'attaque de base dure entre 0,12 et 0,38 s (le projectile va un peu plus vite de loin).
- Les spéciales gardent exactement les durées de l'animateur.

Contrôle : `npx tsx refonte-graphique/pixel/hd/anim/vitesse-attaques.ts` (depuis la racine) réécrit
`refonte-graphique/pixel/sortie/vitesse-attaques.md` : durée de l'attaque de base de chaque personnage avant / après.
Un nouveau personnage exporté y passe tout seul ; si son attaque paraît trop pressée, ralentir son GIF ne sert à rien
(le jeu la remet au tempo commun) : régler plutôt `EVEN`, pour tout le monde.


## 6. Jamais de dessin coupé en ligne droite (26/11/2026)

Bug vu par le propriétaire : la vague d'Ilian (spéciale) laissait un coin d'eau bleu coupé net devant le trident, et la
vague posée sur la cible était coupée net à gauche : la colonne `coupe` passait au milieu de la vague. Quand une coupe
traverse un dessin, le morceau de gauche reste près du lanceur et celui de droite part sur la cible (ou vole) : au
combat, deux bords droits verticaux, d'autant plus visibles que la cible est loin.

- Un effet qui **court au sol** du lanceur à la cible (vague, ligne de feu, gerbes) : `genre='tir'`, `rase=True`, les
  images où il avance dans `tir`, `calques=True` (Ilian, oni-brute, canonnier, Kael). Avec `rase`, chaque image du
  projectile est repérée par son bout ET le sol : sa base reste au sol quand l'image change.
- Un effet qui **sort de terre** devant la cible en ligne (pics, cristaux, fissure) : `sort` + `calques=True` et une
  `coupe` juste devant le lanceur : la ligne entière se pose devant la vraie cible (naga-bouclier, araignée cuirassée,
  golem de lave).
- Sinon, choisir la colonne là où rien n'est traversé (Velith 176, Sable 142, Tybalt 144) : essayer quelques colonnes
  et garder celle où la planche de contrôle ne montre aucun bord droit.
- Un jet (`rayon`) est coupé exprès à la bouche (le jeu l'étire depuis là) : la couper où il est le plus fin.
- Au corps à corps, le jeu recolle les morceaux au moment du coup (même contre une cible large : `hd-fight.ts` décale ce
  qui est posé sur la 1re cible de la même distance que le lanceur) ; avec `calques`, l'arme n'est même plus coupée
  (une 2e cible, « rang de devant », ne reçoit plus un bout d'arme).

Contrôles :

- l'export écrit `ATTENTION <nom> <anim> <image> : coupe … tranche un dessin sur N rangées` quand une coupe traverse un
  dessin sur au moins 8 rangées (deux contours sombres qui se touchent ne comptent pas ; ni le corps à corps ni les
  jets) : corriger avant d'envoyer ;
- `python3 refonte-graphique/pixel/hd/anim/controle_coupes.py [--calcul] [noms…]` : planches « comme au combat »
  (`refonte-graphique/pixel/sortie/controle-speciales/<nom>.png` : chaque image de l'attaque et de la spéciale contre
  une cible proche, en haut, et une cible au fond, en bas ; cadre rouge = suspect) et la liste
  `refonte-graphique/pixel/sortie/coupes-verticales.md`. `--calcul` refait la découpe de chaque build.py (20 min pour
  les 64).
