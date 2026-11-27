# Le signe du repos (27/11/2026)

Demande du propriétaire : « J'aimerais que l'animation au repos des héros soit un peu plus visible. Légèrement, chaque
héros a quelque chose en particulier, une arme, des cheveux, etc. J'aimerais une petite animation de cet élément, lente
mais visible, qui sera visible partout, même quand on obtient le héros. »

Pilote : **Kael** (`kael/`) — la crinière de flammes ondule plus fort (deux vagues par boucle), la lame rougeoie
lentement (tranchant qui s'éclaire, lueur douce autour).

## Ce qu'un héros doit avoir

1. **`anim.py`**
   - `IDLE_T = 3.0` : la boucle du repos (s). La respiration (`idle_offsets`) passe sur cette période (`u = 2π T / IDLE_T`).
   - `def signe(T): → dict` : une **pose partielle** pour `build()` (seulement les réglages de SON élément : mèches,
     cape, arme, flamme, ailes, queue, oreilles, gemme…), **périodique sur `IDLE_T`** (sinus de `2π T / IDLE_T` et de ses
     multiples entiers). Lent, ample, lisible à la taille du téléphone ; un seul élément (deux au plus), le reste immobile.
   - `pose_at()` ajoute `signe(T)` au repos, pondéré par `w` (le poids de la respiration, qui s'efface pendant les coups).
2. **`<nom>.py`** : `build()` lit ces réglages (ajoutés à `REST` avec la valeur 0 = le dessin actuel, inchangé).
   Si l'élément n'a pas encore de réglage, en ajouter un (une matrice autour d'un pivot pour une cape, une onde sur une
   mèche, une lueur `fig.glow` + un détail plus clair pour une arme…). Toujours les règles du dessin : un seul contour,
   pas de flou SVG, une seule lumière en haut à droite. Au repos (`signe` à 0), l'image doit rester identique.
3. **`jeu.py`** : `'pose': dict(periode=3000, images=12)`.

## Les commandes

```
python3 refonte-graphique/ui-moderne/heros/repos.py heros/<nom>          # menus : art/vecto/repos/<id>-base.webp + <id>-<k>.webp, repos.json
python3 refonte-graphique/ui-moderne/jeu_export_vecto.py heros/<nom>     # combat : planche (budget 4,2 Mo)
```

`repos.py` dessine la boucle (16 images, sans la respiration : le CSS la fait), garde seulement les **zones qui bougent**
(au plus 3 rectangles) et écrit `src/game/vecto-repos.ts` (toutes les `repos.json`). Il affiche la mémoire graphique du
héros dans les menus : **au plus 8 Mo** (base + bandes) ; sinon resserrer le signe (un élément plus petit) — la lueur
d'une arme doit rester proche d'elle. Contrôle : `pixel/sortie/ui/vecto/<nom>/repos.gif`.

## Où on le voit

- au combat (la boucle du repos de la planche) ;
- dans les menus, là où le héros est en grand : sa fiche (`hero-detail.tsx`), le tirage (`summon-reveal.tsx`, le héros
  obtenu), l'estrade de l'onglet Héros (`heroes.tsx`) — par `VectoImage` (`src/game/ui/vecto-live.tsx`) ;
- **pas** dans les petites cases des grilles (règle de mémoire iPhone du 26/11 : jamais de bande animée par carte).
