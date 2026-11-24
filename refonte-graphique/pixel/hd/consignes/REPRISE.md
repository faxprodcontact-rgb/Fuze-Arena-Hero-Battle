# Reprendre la refonte HD dans une nouvelle conversation

À lire en premier par Claude. Tout l'état du travail est dans le dépôt : rien ne dépend de l'ancienne conversation.

## Où on en est (24/11/2026)

- États de chaque héros : `../suivi.py` (`VALIDES`, `RETOUCHES` avec le retour du propriétaire, `FAITES` = retouche
  faite, en attente de son avis). Page de suivi : `python3 ../suivi.py`, puis republier `../sortie/suivi.html` sur
  https://claude.ai/artifact/SB9xsSLSYbExWSV89HQfaj (outil Artifact, avec `url`).
- Corvin, Jinn, Zéphyre : retouchés puis validés (24/11). Eldra validée. **Mira, Tessa et Orin** dessinés, en attente de son avis (3 agents en parallèle, accord du
  propriétaire : même coût qu'un par un quand il ne regarde pas entre deux).
- Restent à dessiner (vent) : Arcan, Myrr (thèmes et ids dans `ROSTER` de `../suivi.py`).
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
