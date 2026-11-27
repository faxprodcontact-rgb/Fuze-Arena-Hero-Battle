# refonte-graphique/pixel/ : ce qui reste après la suppression du pixel art (v0.65.0, 27/11/2026)

Le jeu est **entièrement en vectoriel** depuis la v0.65.0 (outils : `refonte-graphique/ui-moderne/`). Le pixel art
(personnages HD `hd/`, fonds `fonds/`, essai `persos/`, outils de contrôle) et ses sorties sont supprimés ; on les
retrouve dans l'historique git si besoin (commit de la v0.65.0 et ceux d'avant).

Ce qui reste ici :

- `ui/` : le plan et le style de l'interface (`PLAN.md`, `STYLE.md`), l'écran de chargement (`chargement.py`,
  `paysage.py`, qui se sert de `fondlib.py`), le logo, l'icône, les anciens pictos pixel (`pictos/assemble.py --pixel`) ;
- `pix.py` : l'atelier de formes pixel dont `ui/fondlib.py` a besoin (paysage du chargement) ;
- `sortie/ui/` : les captures de l'interface et, dans `sortie/ui/vecto/`, **toutes les sorties vectorielles** (vidéos,
  planches de contrôle, avis, combat, têtes, fonds).
