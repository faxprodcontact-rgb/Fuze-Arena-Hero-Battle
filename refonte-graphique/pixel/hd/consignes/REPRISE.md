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
  faits le 25/11 (en attente de son avis). Restent 11 spéciales d'équipe : Rook, Nerith, Minotaure, Bérold, Corvin,
  Solenn, Garvin, Mira, Célia, Anubis — Rook, Nerith, Minotaure faits ; Bérold, Corvin, Solenn faits ; Garvin, Mira, Célia, Anubis en cours (+ vérifier la provocation de Bérold/Corvin/Solenn/Garvin/Mira). Elyon (affaiblit/ralentit les ennemis), Lilou, Auriel, Ysolde : déjà cohérents.
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
