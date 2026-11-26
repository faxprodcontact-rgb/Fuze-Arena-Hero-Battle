// L'habillage de l'interface : « moderne », choisi par le propriétaire le 26/11/2026 (« J'adore le mode moderne. On part
// là-dessus. »). Il n'y en a plus qu'un : style.css. On pose seulement <html data-skin="moderne"> (des règles des sections
// peuvent s'en servir) et on oublie l'ancien choix gardé sur le téléphone par l'essai (« pixel », « hybride »).

export type Skin = 'moderne';
export const SKIN_DEFAULT: Skin = 'moderne';

/** Pose l'habillage sur <html> (avant le premier dessin). */
export function installSkin(): Skin {
  try { localStorage.removeItem('fuze-skin'); } catch { /* sans mémoire : rien à oublier */ }
  document.documentElement.dataset.skin = SKIN_DEFAULT;
  return SKIN_DEFAULT;
}

/** L'habillage en cours (il n'y en a qu'un). */
export function currentSkin(): Skin {
  return SKIN_DEFAULT;
}
