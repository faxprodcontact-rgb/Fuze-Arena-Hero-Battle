/// <reference types="vitest" />
import { createHash } from 'node:crypto';
import { readdirSync, readFileSync, statSync } from 'node:fs';
import { join, relative, sep } from 'node:path';
import { defineConfig, type Plugin } from 'vite';

// Numéro unique de chaque construction : écrit dans version.json et dans le jeu.
// Le jeu compare les deux et se recharge tout seul quand une mise à jour est en ligne.
const BUILD_ID = String(Date.now());

function versionFile(): Plugin {
  return {
    name: 'version-file',
    apply: 'build',
    generateBundle() {
      this.emitFile({ type: 'asset', fileName: 'version.json', source: JSON.stringify({ build: BUILD_ID }) });
    },
  };
}

// Empreinte de chaque image de public/art/ (8 caractères de son md5) : src/game/art-url.ts l'ajoute à l'adresse,
// pour que le téléphone recharge une image dès qu'elle change (jamais une vieille image avec de nouvelles mesures).
function artHash(): Plugin {
  const ID = 'virtual:art-hash';
  return {
    name: 'art-hash',
    resolveId: (id) => (id === ID ? '\0' + ID : null),
    load(id) {
      if (id !== '\0' + ID) return null;
      const root = join(process.cwd(), 'public');
      const map: Record<string, string> = {};
      const walk = (dir: string) => {
        for (const n of readdirSync(dir)) {
          const f = join(dir, n);
          if (statSync(f).isDirectory()) walk(f);
          else if (/\.(webp|png|jpg)$/.test(n)) map[relative(root, f).split(sep).join('/')] = createHash('md5').update(readFileSync(f)).digest('hex').slice(0, 8);
        }
      };
      walk(join(root, 'art'));
      return `export default ${JSON.stringify(map)};`;
    },
  };
}

export default defineConfig({
  base: './',
  define: { __BUILD__: JSON.stringify(BUILD_ID) },
  plugins: [versionFile(), artHash()],
  // Phaser (les deux tiers du code) a son propre fichier : il ne change pas d'une mise à jour à l'autre, les téléphones le gardent.
  // Tests : ignorer les copies de travail des agents (.claude/worktrees), sinon chaque test compte deux fois.
  test: { exclude: ['**/node_modules/**', '**/dist/**', '.claude/**'] },
  build: { outDir: 'dist', assetsInlineLimit: 0, chunkSizeWarningLimit: 2000, rollupOptions: { output: { manualChunks: { phaser: ['phaser'] } } } },
});
