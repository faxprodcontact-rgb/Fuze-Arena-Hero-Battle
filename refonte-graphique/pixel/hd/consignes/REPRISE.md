# Reprendre la refonte HD dans une nouvelle conversation

À lire en premier par Claude. Tout l'état du travail est dans le dépôt : rien ne dépend de l'ancienne conversation.

## Où on en est (24/11/2026)

- États de chaque héros : `../suivi.py` (`VALIDES`, `RETOUCHES` avec le retour du propriétaire, `FAITES` = retouche
  faite, en attente de son avis). Page de suivi : `python3 ../suivi.py`, puis republier `../sortie/suivi.html` sur
  https://claude.ai/artifact/SB9xsSLSYbExWSV89HQfaj (outil Artifact, avec `url`). Les héros animés y jouent leur
  enchaînement : suivi.py écrit aussi `../sortie/anim/<nom>.gif` (depuis `pixel/sortie/anim-<nom>-jeu.gif`) ; les publier avec
  la page (paramètre `files` : `{"anim/<nom>.gif": "refonte-graphique/pixel/hd/sortie/anim/<nom>.gif", ...}`).
- Les 36 héros HD sont dessinés et validés (24/11 ; Lenore, Garvin, Nerith, Ysolde, Rook, Velith, Minotaure validés sans remarque) (2 ou 3 agents
  en parallèle : même coût qu'un par un quand le propriétaire ne regarde pas entre deux).
- Test d'animation (24/11) sur Eldra : respiration, attaque, attaque spéciale — sources `../anim/eldra/build.py`, GIF
  `../../sortie/anim-eldra-*.gif`. Validé (« Super, j'aime bien »). Puis Kael (feu), Isis (terre) et Ilian
  (eau) faits et validés (« Super »), puis Sable, Elyon, Arachné validés, puis Myrr, Zaroth, Méduse validés, puis Astérion (cyclope), Célia, Tybalt validés, puis Kesha, Orin, Bérold validés, puis Zéphyre, Barzul, Aldric validés, puis Lilou, Gabryel, Mira validés, puis Tessa, Solenn, Anubis validés, puis Corvin, Jinn, Auriel validés, puis Rook, Nerith validés ; Arcan retouché (« plus de cheveux, enlever la corne, la remplacer par des cheveux », dessin et animation refaits) puis validé ; Lenore, Garvin, Velith validés ; Ysolde et Minotaure faits (25/11) : **les 36 héros sont animés** (Ysolde et Minotaure en attente de son avis) ; 3 agents, consigne `animation.md` (+ héros, élément et idée de spéciale). Rien n'est branché dans le jeu.
- **Spéciales d'équipe** (décision du 25/11, option 1) : 14 héros ont un sort qui ne frappe pas (soin, bouclier,
  défense, attaque/énergie) ; on refait leur spéciale pour montrer le vrai effet (consigne `speciale-equipe.md`).
  Liste et effet en jeu (`src/core/data/heroes.ts`, skillFor) : Rook, Myrr (soin de tous + purifie + ressuscite) ;
  Nerith, Minotaure (soin du plus blessé + régénération) ; Bérold, Corvin, Solenn (bouclier d'équipe + provocation) ;
  Garvin, Mira, Zaroth (défense d'équipe + se soigne + provocation) ; Arcan, Célia, Anubis (attaque d'équipe + énergie).
  Myrr, Zaroth, Arcan faits puis repris (effet en cercle autour du lanceur, règle du 25/11). Effets REÇUS par les alliés : génériques
  (soin, régénération, purification, résurrection, bouclier, défense, attaque, énergie, provocation, débuffs ennemis × 4
  éléments), joués par le jeu sur chaque case occupée : dossier `../anim/effets/` (build.py ; `sortie/` = images du jeu + effets.json ;
  aperçu d'équipe : `python3 equipe.py --lanceur myrr --case 3 --effet soin,purification --equipe zaroth,eldra,kael,isis`),
  faits le 25/11. Spéciales refaites (25/11) : Rook, Nerith, Minotaure, Bérold, Corvin,
  Solenn, Garvin, Mira, Célia, Anubis — Rook, Nerith, Minotaure faits ; Bérold, Corvin, Solenn, Garvin, Mira, Célia, Anubis faits : **les 14 spéciales d'équipe sont refaites** (25/11) (+ vérifier la provocation de Bérold/Corvin/Solenn/Garvin/Mira). Elyon (affaiblit/ralentit les ennemis), Lilou, Auriel, Ysolde : déjà cohérents.
- Plus tard (pas encore demandé) : mettre les héros HD dans le jeu (`../../jeu.py` sait déjà les lire) et publier.

## Méthode (validée par le propriétaire)

1. Lancer **2 ou 3 agents à la fois au plus** (pour économiser les crédits), un par héros, en arrière-plan.
   Message de l'agent = contenu de `nouveau-heros.md` (ou `retouche.md` + le retour exact du propriétaire), avec
   `<BROUILLON>` remplacé par le dossier de brouillon de la session, puis « Ton héros : <nom> (<id>), <thème> ».
   Pour une petite retouche, un agent neuf coûte moins cher que reprendre un ancien agent.
2. Quand un agent a fini : `python3 ../hd.py controle <nom>` (zéro FAUTE), image avant/après
   `python3 avantapres.py <nom> <id>` (→ `../../sortie/hd-<nom>-premier-jet.png`), mettre à jour `../suivi.py`,
   régénérer (`python3 ../suivi.py` écrit `../sortie/suivi.html`, dossier `hd/sortie/`) et republier la page, commit + envoi sur la branche, envoyer l'image au propriétaire avec un court
   résumé en français (ce qui a changé, ce qu'il doit regarder).
3. Les héros que le propriétaire ne mentionne pas dans son retour sont considérés validés.
4. Règles de dessin : `../GUIDE.md` (section 2 : règles ajoutées d'après ses retours).

- Œil rouge de provocation (DÉCIDÉ 25/11 : le propriétaire GARDE l'œil rouge, ne rien enlever) : dessiné dans les spéciales de Zaroth, Corvin et Bérold, ET ajouté par l'effet générique
  « provocation » → en double en jeu. Garvin et Mira ne le dessinent plus. À retirer chez Zaroth/Corvin/Bérold si le
  propriétaire est d'accord (proposé le 25/11).

## Monstres HD (décision du 25/11/2026)

- Les 72 anciens dessins de monstres sont remplacés par **8 clans** (2 par élément) : chaque clan a pour chef un héros HD
  (il joue le boss, affiché plus grand, sans nouveau dessin) et **3 monstres nouveaux** à son image (rapide, costaud,
  tireur ou lanceur de sorts) = 24 monstres à dessiner puis animer. Plus loin dans la campagne : des équipes de héros
  ennemis. Peut-être plus tard : quelques grands boss sans héros.
- Fichiers : `../monstres/<nom>.txt` (même format que les héros, `id: mon-<clan>-<rôle>`), outils hd.py avec le chemin
  (`python3 hd.py voir monstres/<nom>.txt`). Consigne des agents : `nouveau-monstre.md`.
- Page de suivi : `python3 ../monstres/suivi.py` → `../sortie/suivi-monstres.html`, publiée sur
  https://claude.ai/artifact/K6sefe6A2HDRodc9ci84W6 (ROSTER, VALIDES, RETOUCHES, FAITES dans suivi.py ; les monstres
  animés : `sortie/anim-monstres/<nom>.gif` à publier avec `files`).
- Le jeu choisit aujourd'hui les dessins de monstres par famille (`src/game/look.ts`) : à changer au branchement.
- En cours (25/11) : les 24 monstres lancés en même temps (20 agents au plus à la fois) ; tengu-eventail, singe-voleur,
  gorille-guerrier, singe-chaman à lancer dès qu'une place se libère.

### Animation des monstres (demande du 25/11/2026) — FAIT : les 24 monstres sont animés (25/11)
- Consigne : `animation-monstre.md` (s'appuie sur `animation.md`). Sorties comme les héros : `anim/<nom>/build.py`,
  `pixel/sortie/anim-<nom>-*.gif` ; la page des monstres montre le GIF dès qu'il existe.
- Lancées le 25/11 : les 3 araignées, les 3 du clan de Méduse, de Kesha, de Lenore, de Kael, matelot et canonnier (17).
- Lancées ensuite : tireur-pirate, corbeau-tengu, moine-tengu, singe-voleur. tengu-eventail, gorille-guerrier, singe-chaman : les 24 sont lancées.
- Une animation finie : ajouter le nom à ANIMES dans `monstres/suivi.py`, puis publier la page avec `files` {"anim-monstres/<nom>.gif": ...}.

## Combat test HD (demande du 25/11/2026)
- Le propriétaire veut un combat d'essai avec les nouvelles animations : corps à corps = le personnage va jusqu'à sa
  cible et frappe (impact + dégâts jolis) ; à distance = le projectile va jusqu'à la vraie cible (même au fond en bas
  à droite) ; spéciales qui chargent = petit effet de lumière reconnaissable, sans excès. Tester tous les héros et
  monstres.
- Essai fait (25/11) sur Eldra, Jinn, Myrr, matelot, salamandre, sorcier-oni : export `anim/jeu_export.py` (dictionnaire
  `JEU` ajouté à chaque build.py → `public/art/hd/<id>.webp` + `src/game/hd-meta.ts`), mise en scène
  `src/game/hd-fight.ts`, scénario `src/game/hd-trial.ts`, Réglages → Outils de test → « Combat HD (essai) ». GIF
  `pixel/sortie/combat-hd-essai.gif`. Pour les autres : consigne `consignes/export-jeu.md` (un agent peut en faire
  plusieurs ; ajouter chacun au combat d'essai pour le voir).
- 25/11 : le propriétaire valide l'essai (« ça me convient ») → export des 54 autres lancé en 6 lots de 9
  (brief : scratchpad brief-export.md = consigne export-jeu.md + ne pas toucher actions.ts / hd-trial.ts).
  Ensuite : ajouter au combat d'essai un choix des personnages pour les tester tous, vérifier, publier.
- 25/11 : les 60 personnages sont exportés (public/art/hd/, src/game/hd-meta.ts). En cours : choix des personnages
  dans le combat d'essai + mode « tous à la suite », corrections de jeu_export.py (arguments de compose, calques
  transparents, vitesse/pente des projectiles, tengu-eventail non déterministe), contrôle des 60 dans le jeu
  (sortie/combat-hd-tous.gif, -planche.png). Ensuite : publier (version, journal) et montrer au propriétaire.
- 25/11 : FAIT. Réglages → Outils de test → « Combat HD (essai) » ouvre le choix des combattants
  (`src/game/ui/screens/hd-pick.tsx`, `src/game/hd-roster.ts`) : 5 héros et 5 monstres au plus, « Au hasard », ou
  « Les 60 à la suite » (6 manches de 5 contre 5 : 5 héros contre 4 monstres et 1 héros ; chacun son attaque puis sa
  spéciale, cibles variées, fond en bas compris). Export : nouvelles clés `rase`, `retour`, `vitesse`, `pente`
  (consigne export-jeu.md, partie 4). Contrôle : `pixel/sortie/combat-hd-tous.gif` et `combat-hd-tous-planche.png`.

## Fonds de combat pixel art HD animés (demande du 25/11/2026)
- 8 fonds, un par clan / général (consigne `fond.md`), outillage commun `refonte-graphique/pixel/fonds/` (LISEZMOI.md).
- Pilote Kael VALIDÉ (« C'est parfait », 25/11). Les 7 autres lancés le 25/11 (brief scratchpad brief-fond.md) (arachne, meduse, kesha, barzul,
  lenore, orin, eldra), puis le branchement dans le jeu (décor par clan à la place des décors dessinés par le code).
- 25/11 : les 8 fonds sont dessinés (aperçus pixel/sortie/fond-<clan>.gif). v0.54.0 publiée (60 personnages dans le combat
  d'essai, choix + « les 60 à la suite »). En cours : branchement des 8 fonds dans le jeu (régions de la campagne,
  accueil, combat d'essai, outil « fond imposé »), capture pixel/sortie/fonds-en-jeu.png/.gif, puis publier.
- 25/11 : v0.55.0 publiée (8 fonds branchés : régions de la campagne, accueil, essai HD, outil « Décor des combats »).

## Grands boss (« big boss », demande du 25/11/2026)
- 4 grands boss, un par élément, ≈ 2× la hauteur d'un héros, seuls côté ennemi (consigne `grand-boss.md`).
- Pilote en cours : dragon de lave (feu), `boss/dragon.txt`, + case agrandie dans hd.py (`cadre:`), aperçu
  `pixel/sortie/boss-dragon-echelle.png`. Ensuite : léviathan (eau), titan de pierre (terre), oiseau-tempête (vent),
  puis animations et branchement (boss du jour, de guilde, fins de région).
- 25/11 : dragon VALIDÉ (taille, tête) avec 2 retouches demandées : pattes plus cohérentes, intérieur de la bouche
  TRANSPARENT (on voit le fond entre les mâchoires ; vaut pour tous les boss, remplace « gorge rouge sombre »).
  Retouche du dragon en cours ; léviathan, titan, oiseau-tempête lancés (brief scratchpad brief-boss.md).
- 25/11 : dragon retouché et VALIDÉ (« Super ») → animation du dragon lancée (anim/dragon/build.py + JEU, jeu_export adapté à la grande case si besoin).
- 25/11 : léviathan VALIDÉ (« Parfait ») → animation lancée (anim/leviathan/). Titan et oiseau retouchés (oiseau : jonction aile / corps en cours). 24 monstres validés.

## Jeu propre, tout en HD (demande du 25/11/2026)
- Le propriétaire : supprimer anciens fonds et anciens personnages, tout brancher en HD dans tous les modes, retirer
  TOUS les outils de test (menu de l'avatar), supprimer jusqu'au bout. Décidé : le jeu ne garde que les 36 héros HD
  (les 36 autres sont retirés, compensation par courrier dans les vieilles sauvegardes).
- En cours dans une copie de travail séparée (worktree) par un agent : héros, monstres/boss par clan, 8 fonds partout,
  combat HD partout, portraits HD, outils de test retirés, vieux fichiers supprimés, captures `pixel/sortie/jeu-propre/`.
  À la fin : fusionner sa branche, régénérer hd-meta.ts si les boss ont été exportés entre-temps, publier v0.56.0.
- 25/11 : titan VALIDÉ → animation lancée (anim/titan/). Oiseau : plumes (pas écailles) sur l'aile en cours.
- 25/11 : oiseau VALIDÉ → animation lancée (anim/oiseau-tempete/). Dragon : attaque de base refaite sur place (coup de patte, griffure sur la cible) ; règle pour les boss : l'attaque de base ne se déplace pas.
- 25/11 : animations du dragon (avec coup de patte sur place) et du léviathan VALIDÉES (« Super »). Planches boss ≈ 4074 px : à alléger au branchement si besoin (up=1 pour les boss).
- 25/11 : animation du titan VALIDÉE (« Super »).

## Nouveaux noms de héros (VALIDÉS par le propriétaire le 25/11 : « Parfait les noms on garde »)
À appliquer APRÈS la fusion de la mise au propre HD (src/core/data/heroes.ts OLD_NAMES, i18n, pages de suivi, consignes,
noms des clans) ; les identifiants (myths-6, fichiers .txt, mon-<clan>-*) ne changent pas.
Minotaure → Néfira ; Astérion → Taurok ; Méduse → Ophira ; Arachné → Soyane ; Anubis → Malgrave ; Isis → Sylvar ;
Gabryel → Dardane ; Elyon → Elvyn ; Auriel → Aurelle ; Jinn → Jarek.
- 25/11 : oiseau-tempête animé VALIDÉ (« Super »). Les 4 grands boss sont faits. Retouche de Tessa (héroïne aigle) : jonction tête / corps en cours.
- 25/11 : FAIT dans la copie de travail (journal v0.56.0, brouillon) : 36 héros, monstres et généraux par clan, grands
  boss (boss du jour, de guilde, fins de région : les 4 sont branchés), 8 décors partout, combats HD
  partout, visages et héros en pied dans les menus (`hd/anim/vignettes.py`, à relancer après chaque export), outils de
  test et vieux fichiers supprimés. Reste : fusionner la branche (si `hd-meta.ts` a encore changé, relancer
  `vignettes.py`), `npx tsc --noEmit`, `npm test`, `npm run build`, publier v0.56.0, puis les nouveaux noms ci-dessus.
- 25/11 : v0.56.0 publiée (jeu propre tout en HD, noms renouvelés). Worktree de l'agent fusionné et supprimé.

## Interface dans la nouvelle DA (demande du 25/11/2026)
- Tout repasser en pixel art HD, partie par partie, et brancher au jeu. Partie 1 en cours : inventaire + plan
  (`refonte-graphique/pixel/ui/PLAN.md`), page de chargement, logo, icônes d'application. Ensuite les autres parties du plan.

## Nouvelle interface (demande du 26/11/2026) — brief : scratchpad brief-da-ui.md
- Vague 1 (en cours, 4 agents) : fondation du style + section Campagne (worktree, STYLE.md à venir dans pixel/ui/) ;
  pictos de l'interface (pipeline refonte-graphique/pixel/ui/pictos/, assemble.py → icons.webp + icons-meta.ts) ;
  pictos armes / équipements / éléments / rôles / stats ; vitesse des attaques de base harmonisée (hd-fight.ts) +
  bouche transparente de Kesha.
- Vague 2 (après validation du style) : sections Héros (avec la nouvelle fiche héros : héros en grand sur fond sobre
  et classe, niveau bien visible, caractéristiques et attaques en pictos, épuré), Invoquer (avec l'animation
  d'ouverture du portail), Aventure, Guilde.
- 26/11 : v0.58.0 publiée (vague 1). Le propriétaire trouve l'interface un peu « ancienne » (agencement, couleurs) et veut
  essayer « un peu moins pixel mais cohérent, actuel » → essai de 2 habillages (A Moderne, B Hybride) dans un worktree,
  captures `pixel/sortie/ui/essai-style/`. Vague 2 (Héros, Invoquer, Aventure, Guilde) EN ATTENTE du choix du style.
  En parallèle : audit des pictos restants (`pixel/ui/AUDIT-PICTOS.md`).
- 26/11 : le propriétaire CHOISIT le style « Moderne » (« J'adore le mode moderne, on part là-dessus »). Pictos à refaire
  dans ce style (lisses, HD), puis les pages suivantes. Lancés en parallèle, chacun dans un worktree (brief scratchpad
  brief-moderne.md) : Socle (style par défaut, pièces communes, HUD des combats, Campagne + fenêtres de l'accueil),
  Héros (+ nouvelle fiche héros), Invoquer (+ animation d'ouverture du portail), Aventure, Guilde, Pictos modernes.
  À la fin : fusionner les 6 branches (le Socle d'abord), régler les conflits, vérifier, publier v0.59.0.
