# Consigne commune : refaire l'attaque spéciale d'un héros en SORT D'ÉQUIPE (soin, bouclier, défense, attaque, énergie)

Décision du propriétaire (25/11/2026) : l'animation de la spéciale doit montrer ce que le sort fait VRAIMENT en combat.
14 héros ont un sort qui ne frappe pas l'ennemi (soin, bouclier, renfort) alors que leur première spéciale animée frappait.

You are the top-tier pixel-art ANIMATOR who made this hero's animations. Project: /home/user/Fuze-Arena-Hero-Battle.
Your hero already has 3 VALIDATED animations built by refonte-graphique/pixel/hd/anim/<name>/build.py (pose, attaque,
spéciale). Task: REDO ONLY THE SPÉCIALE so it shows the real in-game effect given below. Keep `pose` and `attaque`
pixel-identical (do not touch their code paths), keep the same file outputs, re-run build.py.

- Read first: refonte-graphique/pixel/hd/consignes/animation.md (quality bar, owner's taste, outputs, self-review),
  refonte-graphique/pixel/hd/GUIDE.md, your hero's build.py and current GIFs (refonte-graphique/pixel/sortie/anim-<name>-*).
  Keep a copy of the current build.py and GIFs in <BROUILLON>/anim-<name>-equipe/avant/ before editing.
- **RÈGLE DE PLACEMENT (décision du propriétaire, 25/11, remplace l'ancienne règle « vers la gauche »)** : l'équipe est
  en losange de 5 cases (2 devant côté ennemi, 1 au milieu, 2 derrière) ; le lanceur peut être à n'importe quelle case
  et ses alliés peuvent être devant, derrière, au-dessus ou en dessous de lui. Donc la spéciale du LANCEUR ne vise
  aucune direction : l'effet naît sur lui et s'étend EN CERCLE tout autour de lui (onde, anneau, souffle, pluie de
  particules dans toutes les directions, un peu aplati comme posé au sol), puis se referme ou s'éteint sur lui. Rien
  ne part spécialement vers la gauche ni vers la droite, rien ne frappe l'ennemi (sauf « affaiblit / ralentit les
  ennemis » : là, l'effet part vers la droite). Ne dessine jamais d'alliés.
- Ce que reçoit chaque allié (lueur de soin, bulle de bouclier, armure, aura d'attaque, orbe d'énergie…) n'est PAS
  ton travail : ce sont des effets génériques communs (dossier `anim/effets/`), joués par le jeu sur chaque case
  occupée au bon moment. Ta spéciale doit donc avoir un « moment de lancement » net (le temps fort tenu) : indique
  dans tes notes (commentaire en tête de build.py) le numéro de l'image où l'effet part vers l'équipe.
- Visual language (same for every hero, in the hero's element and colours):
  * soin : lumière douce qui monte, gouttes / pétales / plumes / grains lumineux qui retombent, la silhouette du héros
    s'éclaire un instant ; « purifie » = des petites taches sombres qui se détachent et s'évaporent ; « ressuscite » =
    une grande colonne de lumière qui part vers la gauche (vers l'équipe) en fin de sort.
  * bouclier : une bulle / un voile translucide de son élément (contour lumineux, intérieur à peine teinté, AUCUN
    quadrillage, aucune alvéole régulière) qui se forme autour de lui puis se propage en vague vers la gauche.
  * défense en hausse : une armure de lumière de son élément (plaques / écailles / cristaux) qui se pose sur lui un
    instant, avec une onde qui part vers la gauche.
  * attaque en hausse : une aura ascendante rouge-orangé / or (flammes douces, braises), un cri ou un geste guerrier.
  * énergie : des orbes lumineux (bleu-blanc / or) qui jaillissent et filent vers la gauche.
  * provocation (« attire les coups sur lui ») : geste de défi vers l'ennemi (poing levé, frappe sur le bouclier, cri),
    une marque / onde rouge qui pulse sur lui. Signes inventés seulement, jamais de lettres ni de « + ».
  * affaiblit / ralentit les ennemis : effet qui part vers la DROITE et retombe sur les ennemis (hors cadre / au sol).
- Toujours : formes courbes, aucun rayon droit répété, une seule lumière en haut à droite, un temps fort tenu
  (arrêt sur image ~200 ms), durée 1,5 à 2,3 s, retour exact à la pose. Garde l'identité de la spéciale précédente
  quand elle s'y prête (même geste, même élément, même nom ou un nom proche), en la tournant vers l'équipe.
- Do NOT modify <name>.txt, hd.py, jeu.py, game code or other heroes' folders. Do not commit/push.
- Final answer (short, plain French): what the new spéciale shows, step by step, and what the owner should look at.

Ton héros : … (voir le message de l'orchestrateur : nom, élément, effet exact du sort).
