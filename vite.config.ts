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

export default defineConfig({
  base: './',
  define: { __BUILD__: JSON.stringify(BUILD_ID) },
  plugins: [versionFile()],
  build: { outDir: 'dist', assetsInlineLimit: 0, chunkSizeWarningLimit: 2000 },
});
