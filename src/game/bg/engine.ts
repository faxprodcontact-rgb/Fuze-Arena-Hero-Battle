// Les décors des combats, dessinés par le code (même trait que les décors des menus) puis changés en images pour Phaser.
//
// Un décor = des calques fixes et des éléments animés, du fond vers le devant :
//   le ciel (texture « sky ») ; ce qui bouge dans le ciel (nuages, oiseaux…) ; le paysage et le sol (« land ») ;
//   ce qui bouge devant le paysage (fumée, cascade, fanions, lueurs…) ; [le voile des compétences, profondeur 5] ;
//   les combattants ; le premier plan (« front », il passe devant eux et s'efface pendant les compétences) ; ce qui bouge devant.
// Les dessins sont refaits pour la taille exacte de l'écran (le ciel s'allonge sur un téléphone plus haut) ; une fois
// changés en images, ils sont gardés pour les combats suivants.
//
// Les animations sont calculées à chaque image d'après l'heure (pas d'après la vitesse du combat : ×2 et ×3 ne les
// accélèrent pas) : dérive (nuages), balancement, rotation, flamme qui vacille, lueur qui respire, cascade qui coule.
import Phaser from 'phaser';
import type { VNode } from 'preact';
import { BW, svgString, type Ctx, type Particles, type Scene, type Sprite } from './core';

export { BW, svgString };
export type { Anim, Ctx, Particles, Scene, Sprite } from './core';

/** Les images déjà faites, gardées d'un combat à l'autre (chaque combat a son propre Phaser). */
const DONE = new Map<string, HTMLImageElement | HTMLCanvasElement>();

interface Piece { key: string; w: number; h: number; draw: () => VNode }

/** Un décor à une taille donnée : les dessins dépendent de la place (le ciel s'allonge, un éclair aussi). */
const tagOf = (name: string, c: Ctx) => `${name}:${Math.round(c.hz)}:${Math.round(c.bottom)}`;

/** On ne garde que les images des derniers décors vus (l'accueil et un combat, le plus souvent). */
const KEEP = 3;
const recent: string[] = [];
function touch(tag: string) {
  const i = recent.indexOf(tag);
  if (i >= 0) recent.splice(i, 1);
  recent.unshift(tag);
  for (const old of recent.splice(KEEP)) for (const k of [...DONE.keys()]) if (k.includes(`-${old}-`)) DONE.delete(k);
}

function pieces(name: string, scene: Scene, c: Ctx): { layers: Piece[]; sprites: Sprite[]; parts: Particles[] } {
  const tag = tagOf(name, c);
  const layers: Piece[] = [
    { key: `bg-${tag}-sky-`, w: BW, h: Math.ceil(c.hz + 60), draw: () => scene.sky(c) },
    { key: `bg-${tag}-land-`, w: BW, h: Math.ceil(c.bottom), draw: () => scene.land(c) },
  ];
  if (scene.front) layers.push({ key: `bg-${tag}-front-`, w: BW, h: Math.ceil(c.bottom), draw: () => scene.front!(c) });
  return { layers, sprites: scene.sprites?.(c) ?? [], parts: scene.particles?.(c) ?? [] };
}

/** À appeler dans `preload` : met en file les dessins du décor qui ne sont pas encore prêts. */
export function loadBackdrop(sc: Phaser.Scene, name: string, scene: Scene, c: Ctx) {
  const { layers, sprites, parts } = pieces(name, scene, c);
  const tag = tagOf(name, c);
  touch(tag);
  const all: Piece[] = [
    ...layers,
    ...sprites.map((s) => ({ key: `bgs-${tag}-${s.id}`, w: s.w, h: s.h, draw: s.draw })),
    ...parts.map((p) => ({ key: `bgp-${tag}-${p.id}`, w: p.size, h: p.size, draw: p.draw })),
  ];
  for (const p of all) {
    if (sc.textures.exists(p.key)) continue;
    const ready = DONE.get(p.key);
    if (ready) {
      if (ready instanceof HTMLCanvasElement) sc.textures.addCanvas(p.key, ready);
      else sc.textures.addImage(p.key, ready);
      continue;
    }
    let url = '';
    try {
      url = URL.createObjectURL(new Blob([svgString(p.draw(), p.w, p.h)], { type: 'image/svg+xml' }));
    } catch {
      continue;
    }
    sc.load.svg(p.key, url, { width: p.w, height: p.h });
    sc.load.once(`filecomplete-svg-${p.key}`, () => {
      URL.revokeObjectURL(url);
      const img = sc.textures.get(p.key).getSourceImage();
      if (img instanceof HTMLImageElement || img instanceof HTMLCanvasElement) DONE.set(p.key, img);
    });
  }
}

/** Ce qui est posé : les objets du premier plan (ils s'effacent pendant les compétences), et l'animation. */
export interface Placed {
  front: Phaser.GameObjects.GameObject[];
  ok: boolean;
}

const TAU = Math.PI * 2;
/** Un bruit doux (somme de sinus) : pour les flammes. */
const wobble = (t: number, p: number) => 0.5 + 0.25 * Math.sin(t * 7.3 + p) + 0.15 * Math.sin(t * 13.1 + p * 2.1) + 0.1 * Math.sin(t * 23.7 + p * 0.7);

/** À appeler dans `create` : pose les calques et les éléments animés. Renvoie false si les dessins n'ont pas pu être faits. */
export function placeBackdrop(sc: Phaser.Scene, name: string, scene: Scene, c: Ctx): Placed {
  const { layers, sprites, parts } = pieces(name, scene, c);
  const tag = tagOf(name, c);
  const front: Phaser.GameObjects.GameObject[] = [];
  const [sky, land, fr] = layers;
  if (!sky || !land || !sc.textures.exists(sky.key) || !sc.textures.exists(land.key)) return { front, ok: false };
  sc.add.image(0, 0, sky.key).setOrigin(0).setDepth(-30);
  sc.add.image(0, 0, land.key).setOrigin(0).setDepth(-20);
  if (fr && sc.textures.exists(fr.key)) front.push(sc.add.image(0, 0, fr.key).setOrigin(0).setDepth(1300));

  // les éléments animés : chacun a sa formule, calculée à chaque image
  const tick: ((t: number) => void)[] = [];
  sprites.forEach((s, si) => {
    const key = `bgs-${tag}-${s.id}`;
    if (!sc.textures.exists(key)) return;
    s.at.forEach(([x, y], i) => {
      const k = s.scale?.[i] ?? 1;
      const ph = (si * 1.7 + i * 2.39) % TAU;
      const a = s.anim;
      if (a.k === 'flow') {
        const h = s.flowH ?? s.h;
        const ts = sc.add.tileSprite(x, y, s.w, h, key).setOrigin(s.origin?.[0] ?? 0.5, 0).setScale(k).setDepth(s.depth);
        if (s.alpha !== undefined) ts.setAlpha(s.alpha);
        if (s.add) ts.setBlendMode(Phaser.BlendModes.ADD);
        if (s.depth > 1290) front.push(ts);
        tick.push((t) => { ts.tilePositionY = -((t * a.speed) / k) % s.h; });
        return;
      }
      const img = sc.add.image(x, y, key).setOrigin(s.origin?.[0] ?? 0.5, s.origin?.[1] ?? 0.5).setScale(k).setDepth(s.depth);
      const alpha = s.alpha ?? 1;
      img.setAlpha(alpha);
      if (s.add) img.setBlendMode(Phaser.BlendModes.ADD);
      if (s.depth > 1290) front.push(img);
      switch (a.k) {
        case 'drift': {
          const span = a.to - a.from, off = x - a.from;
          tick.push((t) => { img.x = a.from + ((((off + t * a.speed) % span) + span) % span); });
          break;
        }
        case 'bob': tick.push((t) => { img.y = y + Math.sin((t / a.period) * TAU + ph) * a.amp; }); break;
        case 'sway': tick.push((t) => { img.angle = Math.sin((t / a.period) * TAU + ph) * a.deg; }); break;
        case 'spin': tick.push((t) => { img.angle = ((t / a.period) * 360 + ph * 57) % 360; }); break;
        case 'pulse': tick.push((t) => { img.alpha = alpha * (a.min + (1 - a.min) * (0.5 + 0.5 * Math.sin((t / a.period) * TAU + ph))); }); break;
        case 'flicker': tick.push((t) => {
          const w = wobble(t / a.period, ph * 3);
          img.alpha = alpha * (a.min + (1 - a.min) * w);
          img.setScale(k * (0.94 + 0.08 * w), k * (0.9 + 0.16 * w));
        }); break;
        case 'flash': {
          img.alpha = 0;
          const strike = () => {
            if (!img.active) return;
            img.alpha = alpha;
            sc.tweens.add({ targets: img, alpha: 0, duration: 420, ease: 'Quad.easeIn' });
            sc.time.delayedCall(140, () => { if (img.active && Math.random() < 0.5) { img.alpha = alpha * 0.8; sc.tweens.add({ targets: img, alpha: 0, duration: 300 }); } });
            sc.time.delayedCall((a.every * (0.6 + Math.random() * 0.8)) * 1000, strike);
          };
          sc.time.delayedCall((a.every * (0.3 + Math.random() * 0.5)) * 1000, strike);
          break;
        }
        default: break;
      }
    });
  });

  // les particules
  for (const p of parts) {
    const key = `bgp-${tag}-${p.id}`;
    if (!sc.textures.exists(key)) continue;
    const [x0, y0, x1, y1] = p.area;
    const life = (p.life[0] + p.life[1]) / 2;
    const em = sc.add.particles(0, 0, key, {
      x: { min: x0, max: x1 }, y: { min: y0, max: y1 },
      speedX: { min: p.vx[0], max: p.vx[1] }, speedY: { min: p.vy[0], max: p.vy[1] },
      lifespan: { min: p.life[0], max: p.life[1] },
      scale: { start: p.scale[1], end: p.scale[0] },
      alpha: { values: [0, p.alpha[1], p.alpha[1], p.alpha[0], 0] } as never,
      rotate: p.spin ? { start: 0, end: (p.spin * life) / 1000 } : undefined,
      frequency: life / p.count,
      quantity: 1,
      blendMode: p.add ? Phaser.BlendModes.ADD : Phaser.BlendModes.NORMAL,
    }).setDepth(p.depth);
    // déjà en place à l'ouverture : on avance le temps des particules
    em.fastForward(life);
    if (p.depth > 1290) front.push(em);
  }

  // le premier plan est coupé au bas du terrain : rien ne passe sur le panneau des héros
  if (front.length) {
    const mask = sc.make.graphics({}, false).fillStyle(0xffffff).fillRect(-40, -200, BW + 80, c.bottom + 200).createGeometryMask();
    for (const o of front) (o as unknown as Phaser.GameObjects.Components.Mask).setMask(mask);
  }

  if (tick.length) {
    const t0 = sc.time.now;
    const run = () => { const t = (sc.time.now - t0) / 1000 + 37; for (const f of tick) f(t); };
    run();
    sc.events.on(Phaser.Scenes.Events.UPDATE, run);
    sc.events.once(Phaser.Scenes.Events.SHUTDOWN, () => sc.events.off(Phaser.Scenes.Events.UPDATE, run));
  }
  return { front, ok: true };
}
