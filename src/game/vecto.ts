// Essai du 26/11 (demande du propriétaire) : un héros redessiné en VECTORIEL lisse, dans le style de l'interface
// (refonte-graphique/ui-moderne/heros/), à comparer avec son pixel art dans les menus. Rien ne change par défaut :
// l'adresse `?vecto=1` allume l'essai (gardé sur le téléphone), `?vecto=0` l'éteint. Le combat reste en pixel art.
// À retirer (ou à généraliser) après l'avis du propriétaire.
import { artUrl } from './art-url';

const VECTO_ON = (() => {
  try {
    const q = new URLSearchParams(location.search).get('vecto');
    if (q === '1') localStorage.setItem('fuze-vecto', '1');
    if (q === '0') localStorage.removeItem('fuze-vecto');
    return localStorage.getItem('fuze-vecto') === '1';
  } catch { return false; }
})();

/** Par héros : [largeur, hauteur de l'image, x et y des pieds dans l'image], en pixels du dessin pixel art (même
 * échelle : il se pose au même endroit). Mesures écrites par refonte-graphique/ui-moderne/heros/kael/kael.py. */
const VECTO: Record<string, readonly [number, number, number, number]> = {
  'demons-3': [133, 122, 68, 120],
  'myths-3': [130, 124, 63, 121],
  'angels-1': [118, 113, 58, 110],
  'assassins-2': [133, 122, 67, 120],
  'assassins-5': [136, 126, 69, 124],
  'demons-8': [102, 125, 52, 122],
  'angels-2': [106, 122, 63, 120],
  'assassins-3': [127, 110, 62, 108],
  'myths-10': [130, 125, 64, 122],
  'myths-6': [133, 113, 67, 110],
  'mages-8': [133, 122, 65, 120],
  'mages-3': [137, 121, 71, 118],
  'angels-11': [128, 121, 60, 118],
  'knights-9': [98, 115, 53, 112],
  'angels-6': [108, 124, 55, 122],
  'myths-7': [88, 125, 40, 122],
  'myths-9': [114, 124, 56, 122],
  'mon-lenore-sorts': [84, 96, 22, 93],
  'demons-5': [125, 119, 61, 117],
  'knights-3': [98, 110, 34, 107],
  'mon-eldra-sorts': [93, 99, 47, 95],
  'mon-arachne-tisseuse': [126, 103, 60, 99],
  'mages-11': [128, 119, 67, 116],
  'mages-4': [132, 123, 68, 120],
  'myths-4': [126, 124, 66, 122],
  'knights-7': [110, 120, 62, 118],
  'knights-5': [129, 102, 63, 99],
  'demons-12': [118, 118, 52, 114],
};

export interface VectoFig { w: number; h: number; fx: number; fy: number; big: string; small: string }

/** Le dessin vectoriel d'un héros si l'essai est allumé et qu'il en a un ; sinon rien (on garde le pixel art). */
export function vectoFig(id: string): VectoFig | undefined {
  const m = VECTO_ON ? VECTO[id] : undefined;
  if (!m) return undefined;
  const [w, h, fx, fy] = m;
  return { w, h, fx, fy, big: artUrl(`art/vecto/${id}.webp`), small: artUrl(`art/vecto/${id}-160.webp`) };
}
