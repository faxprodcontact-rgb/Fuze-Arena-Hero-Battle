// Le module des empreintes des images (vite.config.ts, artHash) : chemin de public/ → 8 caractères.
declare module 'virtual:art-hash' {
  const map: Record<string, string>;
  export default map;
}
