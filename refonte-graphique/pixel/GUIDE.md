# Personnages en pixel art « gros pixels encrés » — le guide à suivre (à lire AVANT de dessiner)

> **Depuis la v0.56.0, ce style n'est plus dans le jeu** : le jeu est entièrement en pixel art HD (`hd/`, lire `hd/GUIDE.md`).
> `jeu.py`, `fond.py` et `page.py` (qui mettaient ces 72 héros et le fond « prairie » dans le jeu) sont supprimés ; les
> dessins `persos/` et les outils de contrôle restent pour mémoire.

Demande du propriétaire (23/11/2026) : « un dossier à suivre pour ne pas se tromper sur la prochaine génération, que tout
soit cohérent : la DA, la taille des têtes, leur position, les articulations pas visibles, la cohérence des premiers et
seconds plans… je ne peux pas repasser 10 fois sur chaque personnage ». Ce guide rassemble **toutes ses consignes**
(§ 11 : l'historique des refus). Un personnage ne lui est montré que lorsque `controle.py` dit « OK » et que la liste
du § 9 est cochée.

Le dossier :
- `GUIDE.md` : ce guide.
- `persos/_gabarit.py` : **le mannequin à recopier** (proportions de référence + ordre de dessin, commenté étape par étape).
- `controle.py` : le contrôle automatique et la planche de comparaison (`sortie/planche-controle.png`).
- `pix.py` : l'atelier (`c.part(masque, matière, 'ink')`, `c.sprite()` pour les dessins pixel par pixel, `sheet()`).
- `persos/<nom>.py` : un fichier par personnage ; `persos/tetes.py` : têtes de Kael, Sable et Eldra.
- `jeu.py` : met les personnages dans le jeu.

## 1. Le style (la DA)

- **Gros pixels encrés** (référence du propriétaire : un chevalier en pixel art à gros traits). Un héros debout fait
  **64 à 72 pixels** de haut ; au combat, un pixel vaut 1,8 unité (`SCALE['ink']` de `jeu.py`).
- **Un trait noir** (`#1e1424`) **autour de chaque pièce** : `c.part(masque, matière, 'ink')`. Pas de contour ajouté
  en plus autour du personnage (un héros encré a un `ORIGIN` : `sheet()` le sait).
- **Une seule lumière, en haut à droite** : l'ombre en bas à gauche de chaque pièce, un liseré clair en haut à droite
  (automatique avec `'ink'`). Quelques reflets à la main (`c.line(…, matière.hi)`), toujours en haut à droite.
- **Matières** : une gamme de 5 tons par matière (`Ramp`), l'or commun (`GOLD`) ; des couleurs franches.
- **Interdits** (demandes du propriétaire) : rayures, hachures, rayons répétés, lettres ; le feu en pics séparés ; des
  ailes faites de rayons ; un sourire sur un visage de combat.

## 2. Le repère et la case

- Toile **128 × 120**, `ORIGIN = (24, 45)` (ne pas changer) : on dessine avec **le sol en y = 71** et **le milieu du
  corps en x = 40**. On peut dessiner de x = -24 à 103 et de y = -45 à 74 : **rien ne doit toucher le bord** (vérifié).
- Tourné **vers la droite**, vu de trois quarts. **La droite et la gauche sont celles du personnage** : son bras droit
  est à gauche de l'image, c'est le plus proche (devant le torse) ; son bras gauche est à droite de l'image et passe
  derrière le torse à l'épaule.
- Animation de repos, 8 images : le haut du corps monte d'un pixel (`BREATH`), les yeux clignent à l'image 6 (`BLINK`),
  cape, flammes et ailes ondulent. Les jambes ne bougent pas (elles restent posées).

## 3. Les proportions (le squelette du mannequin)

Les points de `_gabarit.py` (debout, garde large) ; pour une autre pose, on **déplace les points**, on ne change pas les
épaisseurs.

| Repère | Valeur |
|---|---|
| Tête | grille de **18 à 24 de large, ~20 de haut** ; haut de la tête vers y = 3 à 10 ; **≈ 1/3 de la hauteur** (27 à 40 %) |
| Place de la tête | **au-dessus du torse**, le visage un peu en avant (x ≈ 40 à 44) ; jamais à côté du corps |
| Cou | sous le menton (le menton le recouvre de 1 à 2 pixels), trapèzes qui montent vers lui |
| Épaules | vers y = 32 ; épaules larges (± 15 autour du milieu pour un costaud, ± 10 pour un fin) |
| Ceinture | vers y = 49 à 55 ; hanches vers y = 56 |
| Genoux / chevilles | vers y = 62 / 68 ; les pieds touchent y = 71 à 73 |
| Écart des jambes | **garde moyenne (`'moyen'`) ou jambes droites (`'droit'`) pour la plupart** ; jambes très écartées (`'large'`) ou élan (`'fente'`) **seulement pour quelques-uns** (protecteurs, colosses, un assassin) |
| Bras | rayon **5,6 → 4,6** (jamais plus fin que 4) ; de l'épaule au poignet ≈ 18 à 22 pixels ; **assez gros pour le torse** |
| Jambes | cuisse **6 → 5,2**, mollet **4,8 → 4,4** (jamais plus fin) |
| Mains | poings de **7 à 8 pixels** dessinés pixel par pixel (`FIST`, `PUNCH`) |
| Pieds, bottes | à peine plus larges que le mollet (**au plus 14 pixels**) |

## 4. La tête (toujours dessinée pixel par pixel)

- Une grille de lettres + une légende (`HEAD`, `HEAD_C`), posée par `c.sprite(x, y - b, HEAD, HEAD_C, …)`.
- **Les deux yeux ont la même forme** (l'un retourné), **cerclés de noir** pour se lire (un iris clair ou qui brille
  au milieu) ; sourcils **en V vers le nez** ; regard dur ; bouche qui gronde ou crie (jamais un sourire).
- **Des cheveux devant** (frange, mèches de chaque côté du visage) ; une couronne ou un bandeau **posé sur les
  cheveux**, qui épouse la tête (jamais en l'air) ; une barbe tombe **sur** la poitrine.
- Le clignement : `HEAD_BLINK` remplace les lettres des yeux par un trait sombre.

## 5. Les articulations

- **Peau et fourrure : pas de trait aux articulations.** Un bras = **une seule forme** de l'épaule au poignet ; une jambe
  = **une seule forme** de la hanche à la cheville (`c.limb([épaule, coude, poignet])` en une fois, la main ou la patte
  réunie au même masque si c'est de la fourrure).
- **Seules les pièces d'équipement ont leur propre trait** : épaulières, brassards (`bracer()`), genouillères et pièces
  d'armure, bottes, ceinture, jupe, armes. Un personnage en armure peut montrer ses plaques ; un corps nu ou de fourrure non.

## 6. Premier plan, second plan : l'ordre de dessin (du fond vers le devant)

**Le haut du bras ne passe jamais devant le vêtement** (le « tee-shirt ») : le bras de devant est posé **deux fois**,
d'abord entier AVANT le torse (`arm()`), puis APRÈS le torse **sans sa racine** (`arm_front()` de `kit.py`, ou `in_front()`
pour une pièce à part) : l'épaule reste sous le vêtement, le reste du bras (coude, avant-bras, poing) passe devant.

1. Tout au fond : cape, queue, aile du fond, crinière ou flammes qui volent derrière.
2. Le bras du fond (son bras gauche) et son brassard ; **le bras de devant une première fois, entier** (`arm()`).
3. **Les jambes, avant la jupe et la ceinture** : le bas des habits passe devant le haut des cuisses. Une jambe levée
   est aussi dessinée **derrière** la jupe et la ceinture (elle en sort, elle ne passe jamais devant).
4. Le bas de la tunique ou la jupe, puis le torse, puis la ceinture (par-dessus).
5. **Le cou AVANT le torse** (`neck()` : le col en couvre le bas, le menton le haut ; il ne se voit que sur 2 ou 3
   pixels, jamais long, jamais devant le torse), puis **la tête** (la barbe recouvre la poitrine).
6. L'épaulière du fond.
   Un **bouclier ou un objet** tenu par le bras du fond se pose ici : devant le torse, mais **derrière** le bras de
   devant, les épaulières et la tête (son coin du haut passe sous l'épaulière) ; regarder chaque coin.
7. Le bras de devant **sans sa racine** (`arm_front()`), **puis son épaulière par-dessus** le haut du bras.
8. L'arme tenue, **puis le poing par-dessus** (les doigts sur le manche).
9. Ce qui est tout devant : l'aile de devant d'une créature ailée, les effets (boule de feu…).

Et toujours : **rien ne passe devant le visage ni la barbe** ; les bras restent loin de la tête.

## 7. Les poses

- **Chaque personnage a une pose différente**, à silhouette simple et lisible. Déjà prises : Kael (élan, épée traînée
  derrière), Sable (un genou à terre, lames tendues), Eldra (sur une jambe, bâton levé), Rook (ailes en V, debout),
  Ilian (bien campé, trident planté, poing tendu).
- Interdit : une pose accroupie « en boule » (illisible). L'arme et les mains doivent se lire d'un coup d'œil.

## 8. Les matières difficiles

- **Le feu** (Kael, Rook) : **une seule masse** (les langues réunies en un masque, encré une fois), puis l'intérieur
  rogné (`erode`) en orange puis en jaune, et quelques braises. Jamais des pics séparés.
- **Les ailes** (Rook) : une **forme pleine** (du bord d'attaque jusqu'au bout des grandes plumes, au bord festonné),
  une rangée de plumes de couverture (leur propre trait), le bout des plumes plus clair. Jamais des rayons.
- **Une créature non humaine** (harpie, lionne…) suit les mêmes règles : tête pixel par pixel, trait noir par pièce,
  pas de trait aux articulations de la peau ou de la fourrure.

## 9. Avant de montrer un personnage (obligatoire)

1. `python3 controle.py <nom>` : **tout doit être OK** (rien de coupé, pieds au sol, largeur et taille de la tête,
   tête au-dessus du corps, deux yeux pareils, clignement).
2. Regarder **une fois** `sortie/planche-controle.png` (le personnage à côté des autres, à la même échelle) :
   - [ ] la tête (cadre rouge) a la même taille que celles des autres et se pose sur le cou ;
   - [ ] les épaules près de la ligne bleue, la ceinture près de la ligne orange, les pieds sur la ligne verte ;
   - [ ] les bras sont aussi épais que ceux des autres et se lisent (épaule → poing) ;
   - [ ] aucun trait noir au coude ni au genou sur la peau ou la fourrure ;
   - [ ] l'ordre du § 6 est respecté (jupe devant les cuisses, épaulière sur le bras, poing sur le manche) ;
   - [ ] **le haut des bras passe sous le vêtement** (pas de rond d'épaule posé sur le torse) ;
   - [ ] **le cou** : court, sous le menton, derrière le col (jamais long ni devant) ;
   - [ ] chaque coin d'un bouclier ou d'un objet : devant ou derrière, comme dans la réalité ;
   - [ ] les jambes : pas tous très écartés ;
   - [ ] rien devant le visage ; cheveux visibles devant ; couronne posée ;
   - [ ] les deux yeux pareils et lisibles ; regard dur, pas de sourire ;
   - [ ] la pose est différente de celles déjà prises ;
   - [ ] pas de rayures, pas de pics pour le feu, pas de rayons pour les ailes.
3. Seulement ensuite : le mettre dans le jeu (§ 10) et le montrer.

## 10. Le mettre dans le jeu

`python3 jeu.py` (sans `| head` : il s'arrêterait en route), puis le changement de version, `npx tsc --noEmit`,
`npm test`, `npm run build`, une note dans `docs/journal.md`, l'envoi, et la copie claude.ai (publier les fichiers
`art/px/` changés et les nouveaux `assets/`, retirer les anciens). Le nom de l'atelier → l'identifiant du jeu : `CHARS`
de `jeu.py`.

Les **monstres** ne sont pas encore dans ce style : mêmes règles, mais plus petits que les héros (au combat, les anciens
monstres de ces familles mesuraient ~86 unités contre ~124 pour les héros, soit environ 48 pixels de haut).

## 11. Historique des refus du propriétaire (pour ne pas les refaire)

- Têtes trop petites ; visages brouillons (formes assemblées) → têtes **pixel par pixel**, ≈ 1/3 de la hauteur.
- Tête qui flotte, posée à côté du corps → cou et trapèzes, tête au-dessus du torse.
- Bras incompréhensibles, trop petits, trop brouillons (morceaux séparés) → un bras = une forme épaisse, un brassard, un poing.
- Jambes trop fines → cuisses et mollets épais ; pieds trop gros → bottes à peine plus larges que le mollet.
- Torse plat → pectoraux, abdominaux, ceinture large.
- Articulations visibles (traits au genou, au coude) → une seule forme par membre.
- Jambe levée qui passe devant la ceinture ; haut des cuisses devant la jupe → ordre du § 6.
- Cheveux de feu en pics → une masse de flammes ; ailes en rayons → une aile pleine.
- Poses toutes pareilles → une pose par personnage ; pose accroupie illisible → silhouettes simples.
- Barbe mal placée, bras qui passe devant la barbe, pas de cheveux devant, couronne à peine posée (Ilian, v0.43).
- Jambes trop écartées chez tous ; haut des bras devant le tee-shirt ; cou trop long ou devant ; coins de bouclier
  mal placés (v0.47, premiers chevaliers) → § 3 (écart des jambes) et § 6 (`arm_front`, `neck` avant le torse).
