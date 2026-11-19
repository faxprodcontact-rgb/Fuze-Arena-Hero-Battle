# Essai d'images par IA (19/11/2026)

Question du propriétaire : peut-on avoir un plus beau rendu avec un outil gratuit ? Essai fait avec les 10 crédits
gratuits de son compte Higgsfield (modèle `nano_banana_pro`, 2 crédits par image en 2k, soit 5 images). Les crédits
sont épuisés : **toujours demander avant d'en dépenser d'autres**.

## Les 5 essais

| N° | Contenu | Modèle fourni | Résultat |
|---|---|---|---|
| 1 | 5 héros en ligne | `modeles/ref-heroes.png` (dessins par code) | Très beau rendu peint. Proportions devenues « semi-chibi » (3 têtes). |
| 2 | 5 gobelins en ligne | `modeles/ref-enemies.png` + essai 1 pour le style | Beau, mais tournés du mauvais côté et proportions presque réalistes. |
| 3 | Décor de combat | `modeles/ref-bg.png` | Même cadrage que le jeu, plate-forme vide : utilisable tel quel. |
| 4 | Les 10 personnages, grosses têtes | `modeles/ref-all.png` + essais 1 et 2 pour le style | Gobelins bien chibi et bien orientés. Héros restés semi-chibi. |
| 5 | Le guerrier dans 4 poses (repos, élan, coup, touché) | le guerrier de l'essai 4 | Même personnage reconnaissable dans les 4 poses : l'animation par poses est possible. |

Résultats dans `images/` (personnages découpés sur fond transparent, décor, vues dans l'écran du jeu, animation).

## Ce qu'on a appris

- **Donner nos dessins par code comme modèle** fait garder l'ordre, les poses, les armes et les couleurs.
- **Fond magenta uni** (`#FF00FF`) demandé dans la description : découpe propre avec `cut.py` (bords doux, couleur
  corrigée, un fichier par personnage). Dire « no ground line » : l'IA a déjà ajouté un trait noir sous les pieds.
- Une image de style très réaliste « tire » les proportions : pour des têtes plus grosses, donner un modèle de style
  qui a déjà ces proportions (les gobelins de l'essai 4).
- L'orientation (gauche / droite) n'est pas toujours respectée : on retourne l'image après coup.
- Erreurs vues, à vérifier à chaque image avec la liste de contrôle de `../LISEZMOI.md` : deux carquois, cheveux qui
  dépassent d'une capuche fermée, main posée sur la lame, hache à deux têtes mal placées, ceinture absente d'une pose
  à l'autre.
- **Originalité** : un archer elfe blond en vert ressemble trop à un héros de jeu très connu. Il a été changé
  (capuche bleu canard, cheveux argentés). Vérifier chaque personnage avant de le garder.
- 10 personnages dans une seule image 2k restent assez grands (environ 5 fois la taille à l'écran).

## Refaire l'essai

1. `node refs.cjs` ou `node refs-all.cjs` : planches modèles (HTML), à photographier avec Playwright.
2. Générer l'image avec le modèle en référence (description en anglais : personnages un par un, règles de cohérence,
   fond magenta uni, pas de texte).
3. `python3 cut.py image.png nom` : fond transparent + un fichier par personnage.
4. `python3 prep.py a|b` puis `node scene-ia.cjs` : la scène du jeu (720 × 980) avec ces personnages aux vraies places.

Les adresses `upload.higgsfield.ai`, `d2ol7oe51mr4n9.cloudfront.net` et `d8j0ntlcm91z4.cloudfront.net` ont été
autorisées dans l'environnement « AVA » pour envoyer les modèles et récupérer les images.
