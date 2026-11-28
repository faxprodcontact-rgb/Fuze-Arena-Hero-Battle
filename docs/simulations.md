# Simulations de progression

Des joueurs virtuels jouent le jeu en accéléré pendant 300 jours : ils récoltent leur butin, invoquent,
fusionnent, montent leurs héros et leur équipement, et avancent en campagne. On vérifie ainsi le rythme
**avant** d'écrire le jeu. Les règles utilisées sont exactement celles de `src/core/` (pas une copie).

Relancer : `npm run simuler` (environ 5 minutes). Recalculer la difficulté de la campagne :
`npm run simuler -- --calibrer` (environ 15 minutes), puis recopier les points d'ancrage dans
`src/core/data/campaign.ts`.

## Grand réglage du 28/11/2026 (sur le VRAI jeu)

**Objectif (décidé par le propriétaire le 28/11)** : un joueur qui joue 3 fois 20 minutes par jour (environ 1 h) voit
tout le jeu en **5 à 7 mois** (fin des 1 200 niveaux, premier Mythique) ; un joueur qui paie (carte mensuelle, passe de
saison, offre de départ, fonds de croissance, un paquet de gemmes par mois, ≈ 25 € par mois) avance **environ 2 fois
plus vite** sur les étoiles et les héros.

**Outils** (ils remplacent l'ancien modèle ci-dessous, qui ne suivait plus le vrai jeu) :
- `npx tsx simulations/vrai-jeu.ts regulier|payeur [jours] [graine]` : un joueur automatique joue le vrai jeu (mêmes
  actions que les boutons : tirages, fusions, équipement, niveaux, campagne, tour, donjons, Événement, arène, guilde,
  quêtes, passe, connexion, pubs, boutiques) ; environ 1 minute pour 180 jours ;
- `npx tsx simulations/calibrer-vrai.ts [passes] [graines]` : règle `CAMPAIGN_ANCHORS` (src/core/data/campaign.ts) pour
  que le joueur de référence atteigne chaque niveau visé au jour visé ; affiche aussi le plus long « mur » (jours sans
  gagner un niveau) et les étapes des étoiles. En fin de partie la puissance monte lentement : la courbe oscille d'une
  passe à l'autre, prendre la moyenne de deux passes qui encadrent la cible ;
- `npx tsx simulations/heros.ts [combats] [niveau] [étoiles]` : la force de chaque héros (combats 5 contre 5 au hasard,
  tous au même niveau et aux mêmes étoiles).

**Niveaux visés (joueur de référence)** : jour 1 : 150 ; jour 3 : 260 ; semaine 1 : 380 ; semaine 2 : 500 ; mois 1 :
680 ; mois 2 : 860 ; mois 3 : 980 ; mois 4 : 1 070 ; mois 5 : 1 140 ; jour 175 : 1 200.

**Résultats (réglages de la v0.72.0, médiane de 3 joueurs gratuits ; 2 payeurs)**

| Moment | Visé | Joueur gratuit (3 × 20 min) |
|---|---|---|
| Jour 1 | 150 | 158 |
| Jour 3 | 260 | 283 |
| Semaine 1 | 380 | 386 |
| Semaine 2 | 500 | 464 |
| Mois 1 | 680 | 633 |
| Mois 2 | 860 | 862 |
| Mois 3 | 980 | 921 |
| Mois 4 | 1 070 | 1 016 |
| Mois 5 | 1 140 | 1 082 |
| Jour 175 | 1 200 | 1 082 (fin vers le 7e mois) |

| Étape (jour) | Joueur gratuit | Payeurs (2 joueurs) |
|---|---|---|
| Premier ★5 | 5 | 2 |
| Première étoile rouge | 17 | 6 et 12 |
| 5 héros en étoiles rouges | 38 | 24 et 27 |
| Premier ★5 rouge, premier Mythique | 158 | 84 et 88 |
| Fin de la campagne | ≈ 200 | 84 et 100 |

Le payeur va donc environ 1,8 fois plus vite sur les étoiles et 2 fois plus vite sur la campagne. Les joueurs gratuits
sont très différents selon la chance aux tirages : à réglages égaux, l'un a fini la campagne vers le jour 60, un autre
vers le jour 170. Reste à surveiller : un palier lent vers le niveau 1 080 (environ 25 jours), et le plus long « mur »
mesuré (10 jours vers le niveau 911). Invocations : environ 9 par jour pour le joueur gratuit (≈ 1 600 en 6 mois).

**Ce que le réglage a appris**
1. Le joueur automatique doit jouer comme un vrai joueur : garder les copies de ses Légendaires (ne faire monter que la
   meilleure), acheter les fragments de son héros. Sinon les étoiles rouges paraissent impossibles.
2. Les « murs » (des semaines sans gagner un niveau) venaient de la structure, pas de la courbe : le grand boss de fin
   de région usé par deux vagues avant lui, l'attaque pleine des boss (le dragon frappe toute l'équipe), et le premier
   niveau d'un chapitre (une seule vague, plus forte). Réglages : `BALANCE` de src/core/stages.ts.
3. La force des monstres se règle sur des sections ordinaires (`monsterScale` 1,25), pas sur une équipe idéale : sinon la
   puissance conseillée ne veut rien dire.
4. Une récompense fixe d'or ou d'essence vaut des centaines d'heures au début et rien à la fin : on la compte en heures de
   butin (`goldH`, `essenceH`).
5. Les fragments achetés en boutique doivent aller au même héros (le Légendaire visé, sinon celui qui en a le plus).

**Force des héros** (`simulations/heros.ts`, niveau 60, ★5) : Légendaires 58 % de victoires, Épiques 52 %, Rares 47 %,
Communs 43 % ; dans une rareté, la plupart à ± 6 points. Encore à part : Eldra (65 %, le plus fort des Légendaires),
Nyrra, Jessa et Jarek (35 à 39 %, les plus faibles).

---

## Ancien modèle (19/11/2026, joueur de 3 × 5 min, avant le vrai jeu)

## Objectif (décidé le 19/11/2026)

72 héros au lancement. Un joueur régulier voit **tout le jeu en 6 à 7 mois** : fin de la campagne
(1 200 niveaux) et premier Mythique. Du contenu sera ajouté ensuite pour allonger la durée de vie
(nouveaux chapitres, nouvelles étoiles, mettre toute la section en Mythique).

## Les trois joueurs simulés

| Joueur | Temps de jeu | Invocations par jour | Invocations simples par jour |
|---|---|---|---|
| Régulier (référence) | 3 × 5 min | 7 (+ 5 par chapitre) | 12 |
| 5 minutes par jour | 1 × 5 min, pas de pub | 5,5 (+ 5 par chapitre) | 9 |
| Petit payeur | 3 × 5 min | 11 (+ 30 au départ) | 12 |

Le premier jour, le régulier joue 45 minutes, le joueur « 5 minutes » en joue 20.
Chaque résultat est la médiane de 30 joueurs (tirages différents).

## Résultats (réglages du 19/11/2026)

**Niveau de campagne atteint**

| Moment | Régulier | 5 minutes | Petit payeur |
|---|---|---|---|
| 10 premières minutes | 30 | 30 | 30 |
| Jour 1 | 134 | 60 | 134 |
| Semaine 1 | 360 | 150 | 361 |
| Mois 1 | 700 | 495 | 708 |
| Mois 2 | 899 | 717 | 938 |
| Mois 4 | 1 080 | 972 | 1 113 |
| Jour 200 | 1 178 | 1 111 | 1 200 (fini) |

**Étapes (jour médian)**

| Étape | Régulier | 5 minutes | Petit payeur | Visé |
|---|---|---|---|---|
| Premier Légendaire | 1 | 3 | 0 | jour 1 |
| Premier héros ★5 | 13 | 19 | 9 | semaine 2 |
| Première étoile rouge | 45 | 51 | 41 | mois 2 |
| Section entière en étoiles rouges | 174 | 211 | 122 | mois 4 à 6 |
| Premier ★5 rouge | 210 | 215 | 168 | mois 6 à 7 |
| Premier Mythique | 210 | 225 | 172 | mois 6 à 7 |
| Fin de la campagne | 212 | après 300 | 174 | mois 6 à 7 |
| Section entière Mythique | après 300 | après 300 | après 300 | contenu des mises à jour |

**Blocages** : de la semaine 2 à la fin de la campagne, le joueur régulier passe 47 jours sans gagner de niveau de
campagne, jamais plus de 3 jours de suite. Les autres modes prennent le relais ces jours-là.

## Réglages qui en découlent

- **72 héros** : 6 factions × (2 Communs, 3 Rares, 4 Épiques, 3 Légendaires). `src/core/data/heroes.ts`.
- **Étoiles rouges** : 3, 3, 4, 4 puis 5 héros ★5 à sacrifier ; copies 1, 1, 2, 2, 3. Éveil Mythique :
  2 copies + 600 cristaux. `src/core/data/stars.ts`.
- **Récompenses** (`REWARDS` dans `src/core/data/economy.ts`) : 20 fragments par jour (1 copie du
  Légendaire choisi tous les 2 ou 3 jours), un joker ★5 tous les 15 jours dès le jour 30,
  5 cristaux par jour dès le niveau 900.
- **Invocations** : 7 par jour pour un joueur régulier sans payer, plus 12 invocations simples.
  Avec 72 héros, c'est nécessaire : un Légendaire précis sort environ une fois sur 500 invocations.

## Ce que les simulations ont appris

1. **Les combats doivent durer environ 20 secondes** (vitesse ×2 comprise), sinon 120 niveaux le premier jour
   sont impossibles.
2. **L'équipement est indispensable** : sans lui, les héros plafonnent et le joueur restait jusqu'à 57 jours
   sans gagner un niveau de campagne.
3. **L'invocation simple est indispensable** : sans elle, il manque des héros à sacrifier et un joueur qui
   paie n'avance presque pas plus vite.
4. **Plus il y a de héros, plus il faut d'invocations et de fragments** pour garder le même rythme.

## Limites connues

- L'équipement est résumé par un seul niveau par héros.
- La force d'une section est la somme de la force des héros : ni éléments, ni bonus de faction, ni talent de chef.
  Le vrai moteur de combat remplacera ce calcul au prototype.
- Le Mythique arrive en même temps que le ★5 rouge : les cristaux sont déjà réunis à ce moment-là.
