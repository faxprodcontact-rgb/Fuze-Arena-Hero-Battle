// L'habillage de l'interface (essai du 26/11/2026, demande du propriétaire : « un peu moins pixel, mais cohérent ; actuel »).
// Trois habillages à comparer, choisis par un seul réglage (pas de bouton visible) :
// - « pixel »   : la v0.58.0, pièces en pixel art (px.ts) ;
// - « moderne » : formes lisses arrondies, dégradés doux, ombres douces, couleurs vives sur un fond profond (skin.css) ;
// - « hybride » : la même mise en page et les mêmes couleurs que « moderne », avec un rappel du pixel (coins en escalier
//   de 2 px, contour net, ombres sans flou).
// Choix : `?skin=moderne` (ou pixel, hybride) dans l'adresse ; il est gardé sur le téléphone. Sinon : SKIN_DEFAULT.
// Les personnages, monstres, boss, décors et pictos ne changent pas (pixel art HD, validé).

export const SKINS = ['pixel', 'moderne', 'hybride'] as const;
export type Skin = (typeof SKINS)[number];

/** L'habillage par défaut (tant que le propriétaire n'a pas choisi). */
export const SKIN_DEFAULT: Skin = 'pixel';

const KEY = 'fuze-skin';
const isSkin = (v: unknown): v is Skin => typeof v === 'string' && (SKINS as readonly string[]).includes(v);

/** Lit l'habillage voulu (adresse, puis mémoire du téléphone) et le pose sur <html data-skin="…">. */
export function installSkin(): Skin {
  let skin: Skin = SKIN_DEFAULT;
  try {
    const q = new URLSearchParams(location.search).get('skin');
    if (isSkin(q)) { skin = q; localStorage.setItem(KEY, q); }
    else { const saved = localStorage.getItem(KEY); if (isSkin(saved)) skin = saved; }
  } catch { /* sans mémoire : l'habillage par défaut */ }
  document.documentElement.dataset.skin = skin;
  return skin;
}

/** L'habillage en cours (pour les rares dessins faits par le code qui en dépendent). */
export function currentSkin(): Skin {
  const v = typeof document !== 'undefined' ? document.documentElement.dataset.skin : undefined;
  return isSkin(v) ? v : SKIN_DEFAULT;
}
