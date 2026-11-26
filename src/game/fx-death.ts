// La mort d'un combattant (demande du propriétaire, 26/11 : « plus professionnelle ») et son retour à la vie.
// 1. le coup qui tue : il s'arrête net, devient blanc un instant et recule d'un pas ;
// 2. il s'effondre en arrière (loin de celui qui l'a frappé), s'écrase un peu en touchant le sol ;
// 3. son corps s'illumine de la couleur de son élément et se défait en lueurs qui montent en courbes ;
//    son ombre rétrécit, sa barre de vie s'efface.
// Un monstre part vite ; un héros plus doucement (une plus grosse lueur, son âme, monte plus haut) ; un boss plus
// longtemps, l'écran tremble, la gerbe est plus grande ; un grand boss encore plus.
// Rien n'attend la fin de l'animation : le combat continue pendant ce temps. Tout est divisé par la vitesse (×1, ×2, ×3).
import Phaser from 'phaser';
import type { Element } from '../core/types';
import { ELEMENT_LIGHT, dotTex, sparkTex } from './fx-tex';

export type DeathTier = 'monster' | 'hero' | 'boss' | 'bigBoss';

/** Ce qu'il faut savoir d'un combattant pour le faire tomber. */
export interface DeathView {
  body: Phaser.GameObjects.Container;
  fig: Phaser.GameObjects.Container;
  shadow?: Phaser.GameObjects.Shape;
  bars: Phaser.GameObjects.Graphics;
  /** Le dessin (une image dans `fig`). */
  img?: Phaser.GameObjects.Image;
  /** Le sens du dessin (-1 pour un ennemi, retourné). */
  sx: number;
  side: 'hero' | 'enemy';
  element: Element;
  feet: number;
  h: number;
  w: number;
}

/** Durées (ms à ×1) et force de chaque sorte de mort. */
const TIER: Record<DeathTier, { len: number; tilt: number; motes: number; shake: number; bloom: number }> = {
  monster: { len: 1, tilt: 26, motes: 22, shake: 0, bloom: 0 },
  hero: { len: 1.2, tilt: 20, motes: 26, shake: 0, bloom: 0 },
  boss: { len: 1.5, tilt: 16, motes: 36, shake: 0.006, bloom: 1 },
  bigBoss: { len: 2, tilt: 12, motes: 56, shake: 0.009, bloom: 1.6 },
};

const rnd = (a: number, b: number) => a + Math.random() * (b - a);

/** Les tweens et la copie lumineuse d'un combattant qui tombe (pour pouvoir tout reprendre s'il se relève). */
const LIT = new WeakMap<DeathView['fig'], Phaser.GameObjects.Image>();
/** Les étapes à venir d'une chute (annulées s'il se relève avant la fin). */
const STEPS = new WeakMap<DeathView['fig'], Phaser.Time.TimerEvent[]>();

/** Une copie du dessin, toute de la couleur donnée, posée sur le dessin (mélange ordinaire : dans un conteneur, la lumière ajoutée est mal rendue). */
function litCopy(scene: Phaser.Scene, v: DeathView, color: number): Phaser.GameObjects.Image | undefined {
  const img = v.img;
  if (!img) return undefined;
  LIT.get(v.fig)?.destroy();
  const lit = scene.add.image(img.x, img.y, img.texture.key, img.frame.name).setOrigin(0).setScale(img.scaleX, img.scaleY)
    .setTintFill(color).setAlpha(0);
  v.fig.add(lit);
  LIT.set(v.fig, lit);
  return lit;
}

/** Un point du dessin (repère du corps : x en travers, `up` de 0 aux pieds à 1 en haut), une fois le dessin penché. */
function figPoint(v: DeathView, x: number, up: number) {
  const a = v.fig.rotation, dy = -up * v.h * Math.abs(v.fig.scaleY);
  return { x: v.body.x + v.fig.x + x * Math.cos(a) - dy * Math.sin(a), y: v.body.y + v.fig.y + x * Math.sin(a) + dy * Math.cos(a) };
}

/** Une lueur qui monte en courbe (elle ondule de côté en montant), puis s'éteint. */
function mote(scene: Phaser.Scene, x: number, y: number, color: number, size: number, rise: number, life: number, delay: number, depth: number) {
  const m = scene.add.image(x, y, sparkTex(scene)).setTint(color).setBlendMode(Phaser.BlendModes.ADD).setDepth(depth).setAlpha(0).setDisplaySize(size, size);
  const ph = rnd(0, Math.PI * 2), sway = rnd(8, 22) * (Math.random() < 0.5 ? -1 : 1), drift = rnd(-14, 14);
  scene.tweens.addCounter({
    from: 0, to: 1, delay, duration: life, ease: 'Linear',
    onUpdate: (tw) => {
      const u = tw.getValue() ?? 0;
      const e = 1 - (1 - u) * (1 - u);
      m.setPosition(x + Math.sin(ph + u * 4.2) * sway * u + drift * u, y - rise * e);
      const d = size * (1 - 0.55 * u);
      m.setDisplaySize(d, d).setAlpha(Math.min(1, u * 8) * (1 - u * u));
    },
    onComplete: () => m.destroy(),
  });
}

/**
 * Fait tomber un combattant. `speed` = vitesse du combat. `done` est appelé à la fin (le conteneur est alors
 * invisible). Renvoie la durée totale (ms réelles).
 */
export function playDeath(scene: Phaser.Scene, v: DeathView, tier: DeathTier, speed: number, done?: () => void): number {
  const T = TIER[tier];
  const k = T.len / speed;
  const back = v.side === 'hero' ? -1 : 1;
  const color = ELEMENT_LIGHT[v.element];
  const { body, fig } = v;
  const depth = body.depth + 1;
  const steps: Phaser.Time.TimerEvent[] = [];
  STEPS.set(fig, steps);
  const later = (ms: number, fn: () => void) => steps.push(scene.time.delayedCall(ms, fn));
  scene.tweens.killTweensOf([fig, body]);
  body.setAlpha(1);
  fig.setAlpha(1);

  // 1. le coup qui tue : blanc un instant, un pas en arrière, la tête qui part
  v.img?.setTintFill(0xffffff);
  later(80 * k, () => v.img?.clearTint());
  scene.tweens.add({ targets: fig, x: back * 12, angle: back * 7, duration: 130 * k, ease: 'Quad.easeOut' });
  // la barre de vie et les pictos s'effacent
  scene.tweens.add({ targets: v.bars, alpha: 0, duration: 320 * k });

  // 2. il s'effondre en arrière, s'écrase en touchant le sol, puis se pose
  const t1 = 130 * k, t2 = 520 * k;
  scene.tweens.add({ targets: fig, angle: back * T.tilt, x: back * 20, scaleY: 0.86, scaleX: v.sx * 1.05, delay: t1, duration: t2 - t1, ease: 'Quad.easeIn' });
  scene.tweens.add({ targets: fig, scaleY: 0.92, scaleX: v.sx * 1.02, delay: t2, duration: 140 * k, ease: 'Sine.easeOut' });
  later(t2, () => {
    // un peu de poussière au sol, de chaque côté
    const p = { x: body.x + back * 20, y: body.y + v.feet };
    for (let i = 0; i < 4; i++) {
      const d = scene.add.image(p.x, p.y - 4, dotTex(scene)).setTint(0xd8c8b0).setDepth(depth).setAlpha(0.5).setDisplaySize(16, 10);
      const side = i % 2 ? 1 : -1;
      scene.tweens.add({ targets: d, x: p.x + side * rnd(18, 34) * Math.sqrt(T.len), y: p.y - rnd(6, 14), displayWidth: 30, displayHeight: 18, alpha: 0, duration: 420 * k, ease: 'Quad.easeOut', onComplete: () => d.destroy() });
    }
    if (T.shake) scene.cameras.main.shake(260 * T.len / speed, T.shake);
  });

  // 3. le corps s'illumine de son élément, puis se défait en lueurs qui montent
  const t3 = 330 * k, fadeMs = 560 * k;
  const lit = litCopy(scene, v, color);
  if (lit) {
    scene.tweens.add({ targets: lit, alpha: 0.8, delay: t3, duration: 220 * k, ease: 'Quad.easeOut' });
    scene.tweens.add({ targets: lit, alpha: 0, delay: t3 + 220 * k, duration: fadeMs, ease: 'Quad.easeIn' });
  }
  scene.tweens.add({ targets: fig, alpha: 0, delay: t3 + 120 * k, duration: fadeMs, ease: 'Quad.easeIn' });
  if (v.shadow) scene.tweens.add({ targets: v.shadow, scaleX: 0.2, scaleY: 0.4, alpha: 0, delay: t3, duration: fadeMs + 120 * k });
  const big = Math.sqrt(v.h / 110);
  // les lueurs partent du corps, de bas en haut, pendant qu'il s'efface (on les place au moment où elles partent)
  later(t3, () => {
    for (let i = 0; i < T.motes; i++) {
      const p = figPoint(v, rnd(-v.w * 0.4, v.w * 0.4), rnd(0.05, 0.9));
      const c = i % 3 === 0 ? 0xffffff : color;
      mote(scene, p.x, p.y, c, rnd(14, 24) * big, rnd(50, 110) * big, rnd(650, 1050) * Math.sqrt(T.len) / speed, (i / T.motes) * fadeMs * 0.9, depth + 1);
    }
    if (tier === 'hero') {
      // l'âme du héros : une lueur plus grosse qui monte plus haut, lentement
      const p = figPoint(v, 0, 0.6);
      mote(scene, p.x, p.y, 0xffffff, 26, v.h * 1.1, 1400 / speed, 120 * k, depth + 2);
      mote(scene, p.x, p.y, color, 44, v.h * 1.1, 1400 / speed, 120 * k, depth + 1);
    }
    if (T.bloom) {
      // boss : une grosse bouffée de lumière douce, et une gerbe de lueurs qui part en éventail
      const p = figPoint(v, 0, 0.45);
      const g = scene.add.image(p.x, p.y, dotTex(scene)).setTint(color).setBlendMode(Phaser.BlendModes.ADD).setDepth(depth).setAlpha(0.9).setDisplaySize(v.w, v.h * 0.6);
      scene.tweens.add({ targets: g, displayWidth: v.w * 2.4 * T.bloom, displayHeight: v.h * 1.4 * T.bloom, alpha: 0, duration: 700 * k, ease: 'Cubic.easeOut', onComplete: () => g.destroy() });
      for (let i = 0; i < 14 * T.bloom; i++) {
        const a = -Math.PI / 2 + rnd(-1.3, 1.3), r = rnd(60, 140) * T.bloom;
        const m = scene.add.image(p.x, p.y, dotTex(scene)).setTint(i % 2 ? 0xffffff : color).setBlendMode(Phaser.BlendModes.ADD).setDepth(depth + 1).setDisplaySize(14, 14);
        const bend = rnd(-30, 30);
        scene.tweens.addCounter({
          from: 0, to: 1, duration: rnd(600, 900) * k, ease: 'Cubic.easeOut',
          onUpdate: (tw) => {
            const u = tw.getValue() ?? 0;
            m.setPosition(p.x + Math.cos(a) * r * u + bend * u * u, p.y + Math.sin(a) * r * u + 30 * u * u).setAlpha(1 - u).setDisplaySize(14 * (1 - u * 0.5), 14 * (1 - u * 0.5));
          },
          onComplete: () => m.destroy(),
        });
      }
    }
  });

  const total = t3 + 120 * k + fadeMs;
  later(total, () => {
    body.setAlpha(0);
    done?.();
  });
  return total;
}

/** Le retour à la vie : des lueurs descendent en courbes vers lui, il réapparaît dans une lumière et se redresse. */
export function playRevive(scene: Phaser.Scene, v: DeathView, speed: number): number {
  const { body, fig } = v;
  const color = ELEMENT_LIGHT[v.element];
  STEPS.get(fig)?.forEach((e) => e.remove(false));
  STEPS.delete(fig);
  scene.tweens.killTweensOf([fig, body, v.bars]);
  if (v.shadow) scene.tweens.killTweensOf(v.shadow);
  v.img?.clearTint();
  body.setAlpha(1);
  fig.setPosition(0, v.feet).setAngle(0).setScale(v.sx * 0.9, 1.08).setAlpha(0);
  v.bars.setAlpha(0);
  const k = 1 / speed;
  const depth = body.depth + 2;
  // les lueurs arrivent d'en haut et se rejoignent sur lui
  for (let i = 0; i < 14; i++) {
    const tx = body.x + rnd(-v.w * 0.3, v.w * 0.3), ty = body.y + v.feet - v.h * rnd(0.15, 0.8);
    const sx = tx + rnd(-60, 60), sy = ty - rnd(70, 130);
    const m = scene.add.image(sx, sy, dotTex(scene)).setTint(i % 3 ? color : 0xffffff).setBlendMode(Phaser.BlendModes.ADD).setDepth(depth).setDisplaySize(12, 12).setAlpha(0);
    const bend = rnd(-40, 40);
    scene.tweens.addCounter({
      from: 0, to: 1, delay: i * 18 * k, duration: 380 * k, ease: 'Quad.easeIn',
      onUpdate: (tw) => {
        const u = tw.getValue() ?? 0;
        m.setPosition(sx + (tx - sx) * u + bend * Math.sin(Math.PI * u), sy + (ty - sy) * u).setAlpha(Math.min(1, u * 4));
      },
      onComplete: () => m.destroy(),
    });
  }
  const t0 = 380 * k;
  const lit = litCopy(scene, v, color);
  if (lit) {
    scene.tweens.add({ targets: lit, alpha: 0.9, delay: t0, duration: 120 * k });
    scene.tweens.add({ targets: lit, alpha: 0, delay: t0 + 120 * k, duration: 420 * k, onComplete: () => { lit.destroy(); LIT.delete(fig); } });
  }
  scene.tweens.add({ targets: fig, alpha: 1, delay: t0, duration: 200 * k });
  scene.tweens.add({ targets: fig, scaleX: v.sx, scaleY: 1, delay: t0, duration: 380 * k, ease: 'Back.easeOut' });
  scene.tweens.add({ targets: v.bars, alpha: 1, delay: t0 + 200 * k, duration: 250 * k });
  if (v.shadow) {
    v.shadow.setScale(0.2, 0.4).setAlpha(0);
    scene.tweens.add({ targets: v.shadow, scaleX: 1, scaleY: 1, alpha: 1, delay: t0, duration: 300 * k });
  }
  return t0 + 540 * k;
}
