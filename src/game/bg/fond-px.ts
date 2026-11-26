// Les fonds de combat HD animés, en pixel art (un par clan de monstres : refonte-graphique/pixel/fonds/, LISEZMOI.md).
// Un fond = une image fixe (590 × 1100 pixels) et des calques animés pris dans une planche (fond-meta.ts) :
//   boucle      un morceau posé à un endroit fixe qui joue ses images en boucle (bannière, cascade, lanterne) ;
//   défilé      une tuile qui coule sans fin dans un rectangle (rivière, lave, mer, brume) ;
//   particules  braises, bulles, pétales… (chacune renaît au même endroit à chaque période, comme dans l'aperçu).
// Un pixel du fond = un pixel d'un personnage HD (720 unités pour 590 pixels) ; le bas de l'image = le bas du terrain.
// Agrandi sans flou (plus proche voisin) ; chaque calque est calé sur la grille de pixels de l'image fixe.
// Les animations suivent l'heure, pas la vitesse du combat (×2 et ×3 ne les accélèrent pas).
import Phaser from 'phaser';
import { FOND_META } from '../fond-meta';
import { artUrl } from '../art-url';

export type PxFond = keyof typeof FOND_META;

interface Boucle { id: string; g: 'b'; z: number; x: number; y: number; w: number; h: number; ms: number; f: readonly (readonly number[])[] }
interface Defile { id: string; g: 'd'; z: number; x: number; y: number; w: number; h: number; f: readonly number[]; vx: number; vy: number }
interface Parts {
  id: string; g: 'p'; z: number; f: readonly (readonly number[])[]; zone: readonly number[]; n: number;
  vie: readonly number[]; vx: readonly number[]; vy: readonly number[]; ondule: readonly number[]; ms: number;
}
type Layer = Boucle | Defile | Parts;

const GAME_W = 720;
/** Au-delà, un calque passe devant les combattants (le premier plan, qui s'efface pendant les compétences). */
const FRONT_DEPTH = 1290;

const key = (fond: string) => `pxf-${fond}`;

/** À appeler dans `preload` : l'image fixe et la planche du fond. */
export function loadPxFond(sc: Phaser.Scene, fond: PxFond) {
  if (!sc.textures.exists(key(fond))) sc.load.image(key(fond), artUrl(`art/px/fonds/${fond}.webp`));
  if (!sc.textures.exists(`${key(fond)}-anim`)) sc.load.image(`${key(fond)}-anim`, artUrl(`art/px/fonds/${fond}-anim.webp`));
}

/** Un hasard à graine (le même à chaque combat : les particules ont toujours le même ballet). */
function rng(seed: string) {
  let a = [...seed].reduce((h, c) => (Math.imul(h, 31) + c.charCodeAt(0)) >>> 0, 991);
  return (lo = 0, hi = 1) => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return lo + (((t ^ (t >>> 14)) >>> 0) / 4294967296) * (hi - lo);
  };
}

/**
 * À appeler dans `create` : pose le fond, son bas sur `bottom` (le bas du terrain). Renvoie le premier plan (il passe
 * devant les combattants et s'efface pendant les compétences), ou ok = false si les images ne sont pas arrivées.
 */
export function placePxFond(sc: Phaser.Scene, fond: PxFond, bottom: number, zoom = 1): { front: Phaser.GameObjects.GameObject[]; ok: boolean } {
  const front: Phaser.GameObjects.GameObject[] = [];
  const m = FOND_META[fond];
  const k = key(fond), ak = `${k}-anim`;
  if (!sc.textures.exists(k) || !sc.textures.exists(ak)) return { front, ok: false };
  // `zoom` : le décor agrandi (centré, ses bords coupés) ; le combat s'en sert pour que le sol aille jusqu'en bas
  const U = (GAME_W / m.w) * zoom, ox = (GAME_W - m.w * U) / 2;
  const top = bottom - m.h * U;
  const X = (px: number) => ox + px * U, Y = (py: number) => top + py * U;
  for (const t of [k, ak]) sc.textures.get(t).setFilter(Phaser.Textures.FilterMode.NEAREST);
  sc.add.image(ox, top, k).setOrigin(0).setScale(U).setDepth(-30);

  const sheet = sc.textures.get(ak);
  const frame = (sx: number, sy: number, w: number, h: number) => {
    const name = `${sx},${sy},${w},${h}`;
    if (!sheet.has(name)) sheet.add(name, 0, sx, sy, w, h);
    return name;
  };
  const tick: ((t: number) => void)[] = [];
  const P = m.periode;

  for (const c of m.calques as readonly Layer[]) {
    if (c.g === 'b') {
      const names = c.f.map(([sx, sy]) => frame(sx!, sy!, c.w, c.h));
      const img = sc.add.image(X(c.x), Y(c.y), ak, names[0]).setOrigin(0).setScale(U).setDepth(c.z);
      if (c.z > FRONT_DEPTH) front.push(img);
      if (names.length > 1 && c.ms > 0) {
        let cur = 0;
        tick.push((t) => {
          const i = Math.floor(t / c.ms) % names.length;
          if (i !== cur) img.setFrame(names[(cur = i)]!);
        });
      }
    } else if (c.g === 'd') {
      const [sx, sy, tw, th] = c.f as [number, number, number, number];
      const ts = sc.add.tileSprite(X(c.x), Y(c.y), c.w, c.h, ak, frame(sx, sy, tw, th)).setOrigin(0).setScale(U).setDepth(c.z);
      if (c.z > FRONT_DEPTH) front.push(ts);
      // au pixel près : la tuile avance d'un pixel entier du fond à la fois (comme dans l'aperçu)
      tick.push((t) => {
        if (c.vx) ts.tilePositionX = -(Math.round((t / 1000) * c.vx) % tw);
        if (c.vy) ts.tilePositionY = -(Math.round((t / 1000) * c.vy) % th);
      });
    } else {
      // les particules : comme fondlib.particules_a (chaque place renaît au même endroit à chaque période)
      const r = rng(`${fond}-${c.id}`);
      const names = c.f.map(([sx, sy, w, h]) => frame(sx!, sy!, w!, h!));
      const life0 = (c.vie[0]! + c.vie[1]!) / 2;
      const slots = Math.max(c.n, Math.ceil((c.n * P) / life0));
      const [amp, per] = c.ondule as [number, number];
      for (let s = 0; s < slots; s++) {
        const life = Math.min(P, r(c.vie[0], c.vie[1]));
        const born = ((s + r()) * P) / slots;
        const x0 = r(c.zone[0], c.zone[2]), y0 = r(c.zone[1], c.zone[3]);
        const vx = r(c.vx[0], c.vx[1]), vy = r(c.vy[0], c.vy[1]);
        const ph = r(0, 6.283);
        const img = sc.add.image(0, 0, ak, names[0]).setOrigin(0).setScale(U).setDepth(c.z).setVisible(false);
        if (c.z > FRONT_DEPTH) front.push(img);
        let cur = 0;
        tick.push((t) => {
          const age = (((t - born) % P) + P) % P;
          if (age >= life) {
            img.setVisible(false);
            return;
          }
          const sec = age / 1000;
          const x = x0 + vx * sec + amp * Math.sin(ph + (2 * Math.PI * age) / Math.max(1, per));
          const y = y0 + vy * sec;
          const i = c.ms ? Math.floor((age + ph * 100) / c.ms) % names.length : Math.min(names.length - 1, Math.floor((age / life) * names.length));
          if (i !== cur) img.setFrame(names[(cur = i)]!);
          const f = c.f[i]!;
          // posée sur la grille des pixels du fond
          img.setPosition(X(Math.round(x - f[2]! / 2)), Y(Math.round(y - f[3]! / 2))).setVisible(true);
        });
      }
    }
  }

  // les animations suivent l'heure : à l'instant 0, le fond est celui de l'image fixe
  const t0 = sc.time.now;
  const run = () => { const t = sc.time.now - t0; for (const f of tick) f(t); };
  run();
  sc.events.on(Phaser.Scenes.Events.UPDATE, run);
  sc.events.once(Phaser.Scenes.Events.SHUTDOWN, () => sc.events.off(Phaser.Scenes.Events.UPDATE, run));
  return { front, ok: true };
}
