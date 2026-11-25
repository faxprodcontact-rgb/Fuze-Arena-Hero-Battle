#!/bin/bash
# La planche du style (toutes les pièces de ui/px.ts) → refonte-graphique/pixel/sortie/ui/style-kit.png
# Usage (depuis la racine du projet) : bash refonte-graphique/pixel/ui/outils/kit.sh
set -e
D=refonte-graphique/pixel/ui/outils
T=$(mktemp -d)
node_modules/.bin/esbuild src/game/ui/px.ts --bundle --format=iife --global-name=PXK --outfile="$T/px.js" --log-level=warning
cp "$D/kit.html" "$T/kit.html"
NODE_PATH=$(npm root -g) node "$D/kit-shot.cjs" "$T/kit.html" refonte-graphique/pixel/sortie/ui/style-kit.png 2
echo "→ refonte-graphique/pixel/sortie/ui/style-kit.png"
