// L'image fixe d'un décor de combat pour les menus (dessinée par le code, voir bg/compose.ts) : elle arrive à la demande,
// sans charger Phaser ; en attendant, le cadre garde sa couleur de fond.
import { useEffect, useState } from 'preact/hooks';

const READY = new Map<string, string>();

export function useTerrainImage(terrain: string): string | undefined {
  const [url, setUrl] = useState(READY.get(terrain));
  useEffect(() => {
    if (READY.has(terrain)) { setUrl(READY.get(terrain)); return; }
    let live = true;
    import('../bg/compose').then((m) => m.terrainImage(terrain)).then((u) => { READY.set(terrain, u); if (live) setUrl(u); }).catch(() => {});
    return () => { live = false; };
  }, [terrain]);
  return url;
}

/** Le style d'un cadre qui montre le décor en image de fond. */
export const sceneBg = (url: string | undefined) => (url ? { backgroundImage: `url(${url})` } : undefined);
/** La même image, passée par la variable `--scene` (cartes et en-tête des donjons). */
export const sceneVar = (url: string | undefined) => (url ? ({ '--scene': `url(${url})` } as never) : undefined);
