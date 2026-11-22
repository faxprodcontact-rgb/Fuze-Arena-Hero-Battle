// Un décor de combat en une seule image fixe, pour les menus (page du boss, des donjons, de la tour, du Colisée) : les
// calques et chaque élément animé à sa place, dans l'ordre où le combat les superpose. Sans Phaser.
import { BW, svgString, type Ctx, type Scene, type Sprite } from './core';
import { SCENES } from './scenes';

/** La mise en page d'un écran de combat standard (720 × 1280) : c'est elle que l'image reprend. */
function menuCtx(): Ctx {
  const groundTop = 452, bottom = 882, feet = 47;
  return { hz: groundTop + 50, bottom, cx: BW / 2, cy: groundTop + 180 + feet, p0: groundTop + 90 + feet - 50, p1: groundTop + 270 + feet + 48 };
}

function load(svg: string): Promise<HTMLImageElement> {
  return new Promise((ok, ko) => {
    const url = URL.createObjectURL(new Blob([svg], { type: 'image/svg+xml' }));
    const img = new Image();
    img.onload = () => { URL.revokeObjectURL(url); ok(img); };
    img.onerror = () => { URL.revokeObjectURL(url); ko(new Error('svg')); };
    img.src = url;
  });
}

interface Layer { depth: number; img: Promise<HTMLImageElement>; place: { x: number; y: number; w: number; h: number; alpha: number; add: boolean }[] }

async function compose(scene: Scene, c: Ctx): Promise<string> {
  const layers: Layer[] = [
    { depth: -30, img: load(svgString(scene.sky(c), BW, Math.ceil(c.hz + 60))), place: [{ x: 0, y: 0, w: BW, h: Math.ceil(c.hz + 60), alpha: 1, add: false }] },
    { depth: -20, img: load(svgString(scene.land(c), BW, c.bottom)), place: [{ x: 0, y: 0, w: BW, h: c.bottom, alpha: 1, add: false }] },
  ];
  if (scene.front) layers.push({ depth: 1300, img: load(svgString(scene.front(c), BW, c.bottom)), place: [{ x: 0, y: 0, w: BW, h: c.bottom, alpha: 1, add: false }] });
  for (const s of (scene.sprites?.(c) ?? []) as Sprite[]) {
    if (s.anim.k === 'flow' || s.anim.k === 'flash') continue;
    const [ox, oy] = s.origin ?? [0.5, 0.5];
    layers.push({
      depth: s.depth,
      img: load(svgString(s.draw(), s.w, s.h)),
      place: s.at.map(([x, y], i) => { const k = s.scale?.[i] ?? 1; return { x: x - ox * s.w * k, y: y - oy * s.h * k, w: s.w * k, h: s.h * k, alpha: (s.alpha ?? 1) * (s.anim.k === 'pulse' || s.anim.k === 'flicker' ? 0.8 : 1), add: !!s.add }; }),
    });
  }
  layers.sort((a, b) => a.depth - b.depth);
  const canvas = document.createElement('canvas');
  canvas.width = BW;
  canvas.height = c.bottom;
  const g = canvas.getContext('2d')!;
  for (const l of layers) {
    let img: HTMLImageElement;
    try { img = await l.img; } catch { continue; }
    for (const p of l.place) {
      g.globalAlpha = p.alpha;
      g.globalCompositeOperation = p.add ? 'lighter' : 'source-over';
      g.drawImage(img, p.x, p.y, p.w, p.h);
    }
  }
  return new Promise((ok, ko) => canvas.toBlob((b) => (b ? ok(URL.createObjectURL(b)) : ko(new Error('blob'))), 'image/jpeg', 0.86));
}

const MADE = new Map<string, Promise<string>>();

/** L'image fixe d'un décor (adresse d'un fichier en mémoire), faite une seule fois. */
export function terrainImage(terrain: string): Promise<string> {
  let p = MADE.get(terrain);
  if (!p) {
    const scene = SCENES[terrain];
    p = scene ? compose(scene, menuCtx()) : Promise.reject(new Error(terrain));
    MADE.set(terrain, p);
  }
  return p;
}
