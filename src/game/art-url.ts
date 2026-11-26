// L'adresse d'une image de public/art/ avec son empreinte (?h=…) : quand un dessin change, son adresse change aussi,
// et le téléphone ne peut plus garder l'ancienne image en mémoire avec les nouvelles mesures (bug du 26/11 : Garvin
// coupé au combat). Les empreintes sont calculées à chaque construction par vite.config.ts (module virtual:art-hash).
import ART_HASH from 'virtual:art-hash';

/** `path` relatif au site, ex. `art/hd/knights-8.webp`. */
export function artUrl(path: string): string {
  const h = (ART_HASH as Record<string, string>)[path];
  return h ? `${path}?h=${h}` : path;
}
