# Consigne : exporter un personnage HD animé vers le jeu (format « jeu »)

Demande du propriétaire (25/11/2026) : en combat, le corps à corps va jusqu'à sa cible et frappe ; le tir vole jusqu'à
la VRAIE cible (même au fond en bas à droite) et y fait son effet ; une spéciale qui charge montre une petite lumière
douce. Essai fait sur Eldra, Jinn, Myrr, matelot, salamandre, sorcier-oni (combat « Combat HD (essai) » des Outils de
test). Cette consigne dit comment faire pareil pour chacun des autres personnages.

Ce qu'on NE touche PAS : le dessin (`.txt`), `hd.py`, les GIF et la planche du personnage (ils doivent rester
identiques), les dossiers des personnages qu'un autre agent est en train d'animer.

## 1. Le principe (rien à réécrire)

`refonte-graphique/pixel/hd/anim/jeu_export.py` importe le `build.py`, remplace un instant sa fonction
`compose(hero, fx_back, fx_front, …)` pour garder les calques à part, et appelle son `build_all()`. Il découpe ensuite
chaque image en trois : **le personnage en place** (avec ses effets « sur lui »), **ce qui est sur la cible** (posé aux
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

Choisir le genre d'après le GIF : un coup porté au contact → `melee` (même si l'arme est longue) ; un objet qui part de
l'arme et traverse la toile → `tir` ; un effet qui tombe ou jaillit sur l'ennemi sans traverser → `sort` ; un jet
continu → `rayon` ; une spéciale qui ne frappe pas (soin, bouclier, bonus, provocation) → `equipe`.

## 3. Lancer, contrôler

```
python3 refonte-graphique/pixel/hd/anim/jeu_export.py --voir <BROUILLON>/export <nom>
```

(depuis la racine du dépôt ; 10 à 30 s par personnage ; plusieurs noms possibles ; `--effets` réécrit aussi les effets
reçus). La planche de contrôle `<BROUILLON>/export/export-<nom>.png` montre chaque image : le personnage en place, en
ROUGE ce qui sera posé sur la cible, en BLEU le projectile, la ligne rouge pâle = `coupe`, le rond rouge = `cible`,
« COUP » et « charge » sur les images clés. Vérifier :

- le personnage reste à sa place sur toutes les images (pieds sur la ligne verte), sans morceau coupé ;
- en rouge : seulement l'impact, ce qui tombe sur l'ennemi, la flèche plantée ;
- en bleu (vol) : le projectile entier sur au moins une image, rien du personnage ;
- `COUP` sur la bonne image, `charge` sur la préparation de la spéciale.

Puis regarder le combat dans le jeu (les vrais déplacements) : ajouter le personnage au combat d'essai
(`src/game/state/actions.ts`, `hdTrialBattle` : un héros par son id, un monstre par `hdArt` ; `src/game/hd-trial.ts` :
la suite des coups), `npm run dev`, Réglages → Outils de test → « Combat HD (essai) ». Le jeu ne prend un personnage HD
que dans ce combat d'essai pour l'instant (les autres modes gardent les anciens dessins).

Ne rien publier, ne rien envoyer : dire à l'orchestrateur quels fichiers ont changé (`build.py` du personnage,
`public/art/hd/<id>.webp`, `src/game/hd-meta.ts`).
