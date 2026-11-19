# Simulations de progression

Des joueurs virtuels jouent le jeu en accéléré pendant 2 ans : ils récoltent leur butin, invoquent, fusionnent,
montent leurs héros et leur équipement, et avancent en campagne. On vérifie ainsi le rythme **avant** d'écrire le
jeu. Les règles utilisées sont exactement celles de `src/core/` (pas une copie).

Relancer : `npm run simuler` (environ 3 minutes). Recalculer la difficulté de la campagne :
`npm run simuler -- --calibrer`, puis recopier les points d'ancrage dans `src/core/data/campaign.ts`.

## Les trois joueurs simulés

| Joueur | Temps de jeu | Invocations par jour | Invocations simples par jour |
|---|---|---|---|
| Régulier (référence) | 3 × 5 min | 2,5 (+ 5 par chapitre) | 4 |
| 5 minutes par jour | 1 × 5 min, pas de pub | 2 (+ 5 par chapitre) | 3 |
| Petit payeur | 3 × 5 min | 5 (+ 30 au départ) | 4 |

Le premier jour, le régulier joue 45 minutes, le joueur « 5 minutes » en joue 20.
Chaque résultat est la médiane de 30 joueurs (tirages différents).

## Résultats (réglages du 19/11/2026)

**Niveau de campagne atteint**

| Moment | Régulier | 5 minutes | Petit payeur |
|---|---|---|---|
| 10 premières minutes | 30 | 30 | 30 |
| Jour 1 | 119 | 60 | 134 |
| Semaine 1 | 360 | 150 | 362 |
| Mois 1 | 586 | 466 | 635 |
| Mois 3 | 800 | 694 | 803 |
| Mois 6 | 950 | 823 | 991 |
| An 1 | 1 088 | 1 005 | 1 151 |
| An 2 | 1 267 | 1 178 | 1 355 |

**Étapes des étoiles (jour médian)**

| Étape | Régulier | 5 minutes | Petit payeur | Visé |
|---|---|---|---|---|
| Premier Légendaire | 1 | 3 | 0 | semaine 1 |
| Premier héros ★5 | 20 | 27 | 12 | mois 1 |
| Première étoile rouge | 135 | 156 | 95 | mois 6 |
| Section entière en étoiles rouges | 256 | 333 | 149 | vers 1 an |
| Premier ★5 rouge | 600 | 676 | 450 | — |
| Premier Mythique | 600 | 676 | 450 | — |

**Blocages** : entre le jour 8 et le jour 365, le joueur régulier ne gagne aucun niveau de campagne un jour sur
trois environ, mais jamais plus de 5 jours de suite. Les autres modes (tour, donjons, missions, boss du jour)
prennent le relais ces jours-là.

## Ce que les simulations ont appris

1. **Les combats doivent durer environ 20 secondes** (vitesse ×2 comprise). À 30 secondes, le joueur n'a
   matériellement pas le temps de faire 120 niveaux le premier jour.
2. **L'équipement est indispensable.** Sans lui, les héros atteignent leur niveau maximum et le joueur restait
   jusqu'à 57 jours sans gagner un niveau de campagne. L'équipement donne une progression continue entre deux étoiles.
3. **Il faut une invocation simple** (Communs et Rares seulement, gagnée en jouant). Sans elle, les héros à
   sacrifier manquent, les étoiles rouges dépendent uniquement des jokers, et un joueur qui paie n'avance
   presque pas plus vite.
4. **Les étoiles rouges coûtent plus cher que prévu** : 4, 4, 5, 5, puis 6 héros ★5 à sacrifier (au lieu de
   2, 2, 3, 3, 4), sinon toute la section est en rouge en 4 mois.
5. **Jokers ★5** : un tous les 45 jours à partir du jour 90. Ce sont eux qui donnent la première étoile rouge.

## Limites connues

- 30 héros seulement (6 Légendaires). Plus de héros au lancement = copies plus rares : à relancer avec la vraie liste.
- L'équipement est résumé par un seul niveau par héros.
- La force d'une section est la somme de la force des héros : ni éléments, ni bonus de faction, ni talent de chef.
  Le vrai moteur de combat remplacera ce calcul au prototype.
- Le Mythique arrive en même temps que le ★5 rouge : les 900 cristaux d'éveil sont déjà réunis à ce moment-là.
- La campagne prévue (1 200 niveaux) est finie vers 2 ans : il faudra ajouter des chapitres avec les mises à jour.
