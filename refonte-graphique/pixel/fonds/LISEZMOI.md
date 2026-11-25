# Fonds de combat HD animés — l'atelier commun (à lire avant de dessiner un fond)

La demande et les règles du propriétaire sont dans `../hd/consignes/fond.md` (à relire aussi). Ce fichier explique
l'outillage commun, les mesures, le format des calques animés et la méthode, pour que les 8 fonds soient faits de la
même façon. **L'exemple complet : `kael/build.py`** (le volcan, fait par le pilote). Le point de départ : `_gabarit.py`.

## 1. Les fichiers

| Fichier | Rôle |
|---|---|
| `fondlib.py` | l'atelier : mesures, toile, bruit, formes toutes faites, morceaux animés communs, calques, export, contrôles |
| `apercu.py` | l'aperçu pour le propriétaire : le fond animé à la taille d'un téléphone avec des personnages HD en pose |
| `_gabarit.py` | un fond minimal qui marche (ciel, nuages, falaise, cascade, bannière, arène, eau qui défile, lucioles) |
| `<clan>/build.py` | un fond (copie du gabarit) ; écrit à côté de lui `fond-<clan>.json`, `fond-<clan>-anim.webp` (+ `.png`) |
| `public/art/px/fond-<clan>.webp` | l'image fixe pour le jeu (×2) |
| `../sortie/fond-<clan>.gif` / `.png` | l'aperçu pour le propriétaire (une période entière, sans couture) / une image fixe |

Lancer : `python3 refonte-graphique/pixel/fonds/<clan>/build.py` (export + aperçu + contrôles, ~1 min) ;
`--fixe` = seulement l'image fixe ×2 dans le brouillon (rapide, pour composer) ; `--brouillon` = en plus des zooms et
les bandes d'images de chaque boucle. Le brouillon : `$BROUILLON/fond-<clan>/` (variable d'environnement `BROUILLON` =
votre dossier de brouillon). Ne jamais toucher à `src/`, aux personnages, ni aux fonds des autres clans.

## 2. Les mesures (toutes en pixels du fond)

**Un pixel du fond = un pixel d'un personnage HD en combat** : l'image fait **590 × 1100**, le jeu l'affiche sur 720
unités de large (1,2203 unité par pixel ; les héros HD : 1,22). Le **bas de l'image = le bas du terrain** (juste
au-dessus du panneau bleu nuit). Les images du jeu sont agrandies ×2 (`UP`), comme les planches des héros HD.

| Repère | y | |
|---|---|---|
| `VISIBLE['court']` / `['moyen']` / `['long']` | 377 / 148 / 50 | ce qu'on voit du haut selon le téléphone (16:9 / 19,5:9 / 21:9) : **tout ce qui compte entre 377 et 1100** |
| `HZ` | 789 | l'horizon des anciens décors (bas du paysage lointain) |
| `P0` | 819 | le bord arrière de la plateforme de combat |
| `RANGS` | 860 / 934 / 1007 | les pieds des trois rangs (fond, milieu, devant) |
| `P1` | 1047 | le bord avant de la plateforme ; dessous : son flanc, puis ce qui coule (lave, eau…) jusqu'à 1100 |

Places (x des pieds) : héros 67 / 134 / 201 (bord, milieu, centre), ennemis 389 / 456 / 523 ; `F.place('heros', 2)`
donne (x, y). Les personnages font ~70 à 115 px de haut : les têtes du rang du fond montent jusqu'à y ≈ 745, celles du
rang de devant jusqu'à ≈ 900. `verifie_mesures()` relit le code du jeu et prévient si ces mesures ont changé.

**La plateforme** : un rectangle de `P0` à `P1`, d'un bord à l'autre, **calme** (valeur moyenne, peu de contraste,
joints à peine visibles) : les personnages ont un contour presque noir et beaucoup sont sombres. Le contrôle mesure
l'écart de luminosité du sol (Kael : moyenne 113, écart 12). Les détails et les animations vont **autour** : le ciel,
le paysage, les côtés au-dessus de `P0`, la bande sous `P1`, les deux coins du bas.

## 3. L'atelier (`fondlib.py`)

- **Toile** : `Toile()` = le fond entier, `Toile((x0, y0, x1, y1))` = un morceau ; on dessine toujours en coordonnées du
  fond. Hérite de `pix.Canvas` : `ellipse`, `poly`, `limb` (membre/branche/coulée : `[(x, y, rayon), …]`), `rect`,
  `fill`, `px`, `line`, `stamp` (tampon texte). En plus : `peint(m, idx, gamme)`, `efface(m)`.
- **Couleurs** : `rampe('#…', …)` (du plus sombre au plus clair, ombres vers le violet/bleu, lumières vers le chaud),
  `mix(a, b, t)`, `brume(gamme, air, t)` (la même gamme vue de loin). Partir des palettes du général et de ses monstres
  (`../hd/<général>.txt`, `../hd/monstres/*.txt`) : on doit reconnaître le clan.
- **Bruit** : `bruit(X, Y, échelle, graine, octaves, px=, py=)` (0…1, doux ; `px`/`py` = période exacte pour ce qui
  boucle), `bruit1(x, …)`, `cellules(X, Y, taille, graine, px=)` (Voronoï : dalles, plaques, facettes), `flou(a, r)`.
- **Lumière (en haut à droite, `LUMIERE`)** :
  - `relief(t, m, gamme, …)` : ombre une masse (colline, montagne lointaine, rocher arrondi) ;
  - `roche(t, m, gamme, graine, taille, etire, fentes, bas_sombre)` : **roche naturelle en grands pans** (falaises,
    éperons) — la grande forme domine, quelques fentes côté ombre, un fil clair côté lumière ;
  - `blocs_roche(…)` : maçonnerie en blocs empilés (murailles, murets — **pas** pour une falaise naturelle : ça fait mur) ;
  - `lobes(t, boules, gamme, plat=, uni=True)` : nuages, fumée, (uni=False) feuillage, boules ;
  - `bandes(t, m, champ, gamme, seuils)` : un champ peint en bandes (ciel : y + lueurs + bruit, **bords ondulés**) ;
  - `halo(…)` : lueur EN PALIERS (pas de dégradé) ; `chauffe(t, source, portée, couleur)` : la lumière d'une lave, d'un
    feu, d'une lanterne sur ce qui est tout près.
  - `perspective(t, P0, P1, avant=1.45)` : un repère (u, v) pour paver le sol (plus grand devant).
  - `nettoie(t, m)` : enlève les pixels orphelins des grandes surfaces faites au bruit (pas sur les détails à la main).
- **Morceaux animés communs** : `cascade_masque` / `cascade(t, c, phase, gamme)` (chute d'eau ou de lave),
  `mat(…)` + `banniere(t, x, y, phase, sens, tissu, traverse, signe, légende)` (bannière qui ondule, signe du clan),
  `images_braise(gamme)` (braise, étincelle, luciole), `images_bouffee(gamme, chaud=)` (fumée, vapeur, poussière).

## 4. Les calques animés (le format)

`fd = F.Fond('<clan>', periode_ms=9600)` ; `fd.fixe` = la toile de l'image fixe. **Chaque calque est aussi dessiné
dans l'image fixe à sa phase 0** (l'image fixe sert aux menus et tant que le jeu n'anime pas). Trois genres :

1. **`fd.boucle(id, plan, box, n, ms, dessin, dessous=, plein=)`** — un morceau à un endroit fixe qui joue `n` images
   de `ms` ms en boucle : `dessin(toile, phase, i)`, phase = i/n de 0 à 1 (exclu) ; **le dessin doit être périodique**
   (la phase n vaut la phase 0) : texture qui avance d'une période entière (`py=` / `px=`), `sin(2π·phase)`…
   `dessous = fd.fixe.col.copy()` pris **juste avant** de dessiner ce morceau dans l'image fixe : un bord qui ondule
   découvre ce qu'il y a derrière. `plein=True` : chaque image part de tout le rectangle (une lueur qui éclaire autour).
   `n × ms` doit diviser `periode_ms`.
2. **`fd.defile(id, plan, box, (tw, th), dessin, vx=, vy=)`** — une surface qui coule sans fin (rivière, lave, mer,
   brume lointaine) : UNE tuile que le jeu fait défiler à `vx`/`vy` px/s dans le rectangle `box`. La tuile doit se
   répéter exactement (`bruit(…, px=tw)`, `cellules(…, px=tw)`) : le contrôle le vérifie. Pour un aperçu sans couture,
   `vx = tw × 1000 / periode_ms` (ou un multiple). Ce qui doit rester devant (les rives d'une rivière tordue, le bord
   d'une plateforme) est remis par-dessus avec `fd.morceau(id, plan, masque, prof=…)` (une boucle d'une image).
3. **`fd.particules(id, plan, images, zone, nombre, vie, vx, vy, ondule=(amp, période), images_ms=)`** — braises,
   bulles, feuilles, plumes, fumée : `nombre` à la fois, nées dans `zone`, vitesses en px/s, `images` jouées sur la vie
   (ou en boucle tous les `images_ms`).

`fd.morceau(id, plan, masque)` sert aussi au **premier plan** (plan `premier`, devant les combattants : discret, dans
les coins du bas) et à remettre un morceau du paysage devant un calque `derriere` (une falaise devant la fumée).

**Plans et profondeurs** (journal v0.38.0) : l'image fixe à −30 ; `ciel` −29 ; `derriere` −25 (−29…−21) ; `paysage`
−20 (−20…−16) ; `devant` −15 (−15…−11) ; combattants (profondeur = y des pieds) ; `premier` 1300. `prof=` précise
l'ordre entre calques d'un même plan.

**Fin** : `fd.regroupe(7)` (fond les couleurs presque pareilles), `fd.exporte()`, `apercu.apercu(fd, persos,
pas_ms=150)`, `F.controle(fd)` : **zéro FAUTE**. La planche doit rester **≤ 2048 px de côté dans le jeu** (au pire 4096,
le contrôle refuse au-delà) : peu d'images pour ce qui bouge lentement, des boîtes serrées, un défilé plutôt qu'une
boucle pour une grande surface qui coule.

`fond-<clan>.json` (lu plus tard par le jeu, coordonnées en pixels du fond, la planche est ×`up`) :
```
{ "clan", "w": 590, "h": 1100, "up": 2, "unite": 1.22034, "image": "art/px/fond-<clan>.webp",
  "planche": "fond-<clan>-anim.webp", "reperes": {hz, p0, p1, rangs}, "periode_ms",
  "calques": [
    {"id", "genre": "boucle", "plan", "prof", "x", "y", "w", "h", "ms", "cases": [[sx, sy], …]},      (ms 0 = fixe)
    {"id", "genre": "defile", "plan", "prof", "x", "y", "w", "h", "case": [sx, sy, tw, th], "vx", "vy"},
    {"id", "genre": "particules", "plan", "prof", "cases": [[sx, sy, w, h], …], "zone": [x0, y0, x1, y1],
     "nombre", "vie": [min, max], "vx": [min, max], "vy": [min, max], "ondule": [amp, période], "images": "vie"|"boucle"} ] }
```
**Branchement dans le jeu (fait)** — après avoir refait un fond avec son `build.py`, relancer
`python3 refonte-graphique/pixel/fonds/jeu.py` : il écrit `public/art/px/fonds/<clan>.webp` (l'image fixe **×1**,
590 × 1100), `public/art/px/fonds/<clan>-anim.webp` (la planche ×1, toutes sous 2048 px) et `src/game/fond-meta.ts`
(les calques des 8 fonds, ~26 Ko, dans le code des combats seulement). Le jeu (`src/game/bg/fond-px.ts`) agrandit
lui-même sans flou (plus proche voisin) : 720 / 590 unités par pixel, le bas de l'image 430 unités sous le haut du sol
(= le bas du terrain du combat ; l'accueil en coupe 10 unités). Chaque fond est chargé seulement quand on le voit.
- boucle = une image de la planche posée en (x, y) × 720/590, qui change toutes les `ms` (heure réelle : ×2 et ×3
  n'accélèrent pas le décor) ; défilé = un TileSprite dont `tilePositionX/Y` avance d'un pixel entier à la fois ;
  particules = des images posées sur la grille des pixels du fond, avec exactement la règle de `particules_a` (chaque
  place renaît au même endroit à chaque période) ; profondeurs = `prof` ; au-delà de 1290 (premier plan), le calque
  s'efface pendant les compétences comme le premier plan des décors dessinés par le code.
- Où on les voit : les 8 régions de la campagne (`REGIONS` dans `src/game/look.ts` : prairie → eldra, ronciers →
  arachne, bayou → meduse, cendres → kael, toundra → orin, orage → barzul, temple → lenore, abysses → kesha) et donc
  l'accueil ; le combat d'essai HD (le clan le plus nombreux chez les ennemis, sinon un général en face, sinon au
  hasard) ; l'outil de test « Décor des combats » des réglages (ou `#fond=<clan>` dans l'adresse) impose un des 8.
  Les autres modes (tour, donjons, boss, arène) gardent leurs décors dessinés par le code.
- Les images ×2 de `public/art/px/fond-<clan>.webp` restent l'entrée de `jeu.py` (le jeu ne les lit plus).

## 5. La méthode (chaque fond)

1. Lire `../hd/consignes/fond.md`, `../hd/GUIDE.md` (les règles de couleur et de lumière), regarder le général et ses
   monstres (`../sortie/anim-<nom>-jeu.gif`) : matières, couleurs, signes. Inventer **le signe du clan** (jamais une
   lettre). Écrire en tête du `build.py` : ce qu'on voit, ce qui bouge, le signe.
2. Copier `_gabarit.py` dans `<clan>/build.py`, changer `CLAN`, les gammes, les personnages de l'aperçu (le général +
   2 héros à gauche, ses 3 monstres à droite, `F.place`).
3. Composer l'image fixe avec `--fixe`, en regardant des **morceaux** recadrés (économie : peu d'images, petites) :
   d'abord les grandes masses et les valeurs (le ciel, le lointain clair et brumeux, le milieu plus sombre, le sol
   calme), puis la lumière, puis les détails posés (bannières, statues, lanternes…).
4. Ajouter les calques animés (prendre les `dessous` au bon moment), puis lancer sans option : aperçu + contrôles.
5. **Relire au moins 4 fois** : l'image entière (`--fixe`, réduite), des zooms ×3 (coins, sol, objets du clan),
   l'animation image par image (`--brouillon` : `bande-<id>.png` ; le raccord de la dernière à la première), l'aperçu
   avec les personnages (`../sortie/fond-<clan>.png`) : se lisent-ils ? rien ne bouge trop près d'eux ?

## 6. Leçons du premier fond (Kael) — à ne pas refaire

- Fumée et nuages en boules toutes ombrées comme des sphères = une **grappe de billes** : `lobes(uni=True)` (seul le
  bord extérieur haut-droit est éclairé). Ombrage d'une boule par la formule « x − y » = des **bandes droites** (rayures) :
  toujours des cercles décalés.
- Roche en petites facettes de tons au hasard = du camouflage ; en blocs empilés = un mur. Falaise : `roche()` (grands
  pans, la forme générale domine) + un dessus éclairé.
- Une chute dont le clair suit les bords = des **bandes verticales** : des paquets de bruit qui descendent, le bord
  seulement un peu plus sombre (`cascade`).
- Un bord de masque coupé droit (`X < 215`) = une falaise découpée au couteau : bords toujours bruités.
- Tout objet posé : calculer son pied **sur le profil** de la roche (`eperon_ligne(x) + 3`), sinon il flotte devant la
  paroi. Ce qui tient au sol a un socle ou une ombre.
- Les périodes : `bruit(…, px=)` et `cellules(…, px=)` doivent recevoir exactement la largeur de la tuile.
- Une lueur (`halo`) dans une boucle `plein=True` doit tenir dans sa boîte, avec de la marge (sinon un rectangle se voit).
- La lave/l'eau au bas de l'écran est à côté du rail d'or du panneau : la garder moins vive que la lave du paysage
  (plus de croûte, moins de blanc).
