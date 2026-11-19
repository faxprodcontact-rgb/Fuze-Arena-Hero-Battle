# Simulations de progression

Des joueurs virtuels jouent le jeu en accéléré pendant 300 jours : ils récoltent leur butin, invoquent,
fusionnent, montent leurs héros et leur équipement, et avancent en campagne. On vérifie ainsi le rythme
**avant** d'écrire le jeu. Les règles utilisées sont exactement celles de `src/core/` (pas une copie).

Relancer : `npm run simuler` (environ 5 minutes). Recalculer la difficulté de la campagne :
`npm run simuler -- --calibrer` (environ 15 minutes), puis recopier les points d'ancrage dans
`src/core/data/campaign.ts`.

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
