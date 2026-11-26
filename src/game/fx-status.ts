// Les altérations se voient sur le combattant (demande du propriétaire, 26/11) : chaque effet en cours a sa petite
// animation en boucle, dessinée par le code (fx-tex.ts), qui suit le combattant quand il bouge.
//   poison = bulles vertes qui montent en ondulant et éclatent ; brûlure = petites flammes qui lèchent le corps, des
//   braises ; saignement = gouttes qui tombent au sol ; soin continu = lueurs vertes qui montent en spirale ;
//   étourdi = trois étoiles qui tournent autour de la tête ; silence = un sceau violet près de la tête ;
//   lenteur = lueurs bleues qui tournent lentement autour des jambes (et il respire au ralenti) ;
//   provocation = un halo rouge qui bat derrière lui ; bonus / malus = chevrons qui montent / descendent ;
//   bouclier = une bulle transparente autour de lui.
// À chaque coup d'une brûlure, d'un poison… l'effet repart plus fort un instant (`pulse`).
import Phaser from 'phaser';
import { bubbleTex, chevronTex, dotTex, dropTex, flameTex, plusTex, sealTex, shieldTex, sparkTex, starTex } from './fx-tex';

/** Ce que l'effet sait du combattant : son conteneur, son dessin, la place de ses pieds, sa taille. */
export interface FxTarget {
  body: Phaser.GameObjects.Container;
  fig: Phaser.GameObjects.Container;
  feet: number;
  h: number;
  w: number;
  /** Vers le milieu du terrain : 1 pour un héros, -1 pour un ennemi (les signes y restent dans l'écran). */
  inward: number;
}

type Img = Phaser.GameObjects.Image;
type FxKind = 'burn' | 'poison' | 'bleed' | 'regen' | 'stun' | 'silence' | 'slow' | 'taunt' | 'arrows' | 'shield';
interface Particle { img: Img; age: number; life: number; step: (u: number) => void; end?: () => void }
interface Loop {
  kind: FxKind;
  t: number;
  next: number;
  every: number;
  ps: Particle[];
  fixed: Img[];
  /** 0 → 1 à l'arrivée, 1 → 0 au départ. */
  fade: number;
  ending: boolean;
  spawn?: () => void;
  frame?: (l: Loop) => void;
}

const BUFFS: Record<string, { color: number; up: boolean }> = {
  atkUp: { color: 0xff8a3d, up: true }, atkDown: { color: 0xff8a3d, up: false },
  defUp: { color: 0x5aa8ff, up: true }, defDown: { color: 0x5aa8ff, up: false },
  speedUp: { color: 0x6fe05a, up: true }, critUp: { color: 0xffd34a, up: true },
};
const LOOP_OF: Record<string, FxKind> = { burn: 'burn', poison: 'poison', bleed: 'bleed', regen: 'regen', stun: 'stun', silence: 'silence', slow: 'slow', taunt: 'taunt' };

const rnd = (a: number, b: number) => a + Math.random() * (b - a);
const pick = <T>(xs: readonly T[]): T => xs[Math.floor(Math.random() * xs.length)]!;
const ADD = Phaser.BlendModes.ADD;

export class StatusFx {
  private loops = new Map<FxKind, Loop>();
  private buffs: string[] = [];
  private buffTurn = 0;
  /** Les grands combattants (boss) ont plus de particules, un peu plus grandes. */
  private big: number;

  constructor(private scene: Phaser.Scene, private tg: FxTarget) {
    this.big = Phaser.Math.Clamp(tg.h / 120, 1, 2.4);
  }

  /** Les effets en cours (les statuts des règles, et le bouclier s'il en reste). */
  sync(kinds: readonly string[], shield: boolean) {
    const want = new Set<FxKind>();
    for (const k of kinds) {
      if (LOOP_OF[k]) want.add(LOOP_OF[k]);
      else if (BUFFS[k]) want.add('arrows');
    }
    if (shield) want.add('shield');
    this.buffs = kinds.filter((k) => BUFFS[k]);
    for (const k of want) {
      const l = this.loops.get(k);
      if (!l) this.loops.set(k, this.create(k));
      else l.ending = false;
    }
    for (const [k, l] of this.loops) if (!want.has(k)) l.ending = true;
  }

  /** Le coup d'une brûlure, d'un poison, d'un saignement, d'un soin continu : une bouffée de l'effet. */
  pulse(kind: string) {
    const l = this.loops.get(LOOP_OF[kind] ?? ('' as FxKind));
    if (!l?.spawn) return;
    const n = kind === 'bleed' ? 2 : kind === 'burn' ? 6 : 4;
    for (let i = 0; i < n; i++) l.spawn();
  }

  update(dt: number) {
    for (const [k, l] of this.loops) {
      l.t += dt;
      l.fade = Phaser.Math.Clamp(l.fade + (l.ending ? -dt / 260 : dt / 200), 0, 1);
      if (l.spawn && !l.ending) {
        l.next -= dt;
        while (l.next <= 0) {
          l.spawn();
          l.next += l.every * rnd(0.7, 1.3);
        }
      }
      for (let i = l.ps.length - 1; i >= 0; i--) {
        const p = l.ps[i]!;
        p.age += dt;
        if (p.age >= p.life) {
          p.end?.();
          p.img.destroy();
          l.ps.splice(i, 1);
        } else p.step(p.age / p.life);
      }
      l.frame?.(l);
      if (l.ending && l.fade <= 0 && !l.ps.length) {
        l.fixed.forEach((f) => f.destroy());
        this.loops.delete(k);
      }
    }
  }

  destroy() {
    for (const l of this.loops.values()) {
      l.ps.forEach((p) => p.img.destroy());
      l.fixed.forEach((f) => f.destroy());
    }
    this.loops.clear();
  }

  /** Les images posées derrière le dessin. */
  private behind = new WeakSet<Img>();

  /**
   * Une image de l'effet, devant ou derrière le combattant. Elles sont posées dans la scène (pas dans le conteneur du
   * combattant : la lumière ajoutée y est mal rendue) et suivent le combattant à chaque image (`at`).
   */
  private add(key: string, front: boolean): Img {
    const img = this.scene.add.image(0, 0, key).setVisible(false);
    if (!front) this.behind.add(img);
    return img;
  }

  /** Place une image de l'effet en (x, y) du repère du combattant (pieds à `feet`), à sa profondeur. */
  private at(img: Img, x: number, y: number): Img {
    const b = this.tg.body;
    return img.setPosition(b.x + x, b.y + y).setDepth(b.depth + (this.behind.has(img) ? -0.5 : 0.5)).setVisible(b.visible && b.alpha > 0);
  }

  private create(kind: FxKind): Loop {
    const l: Loop = { kind, t: 0, next: 0, every: 1e9, ps: [], fixed: [], fade: 0, ending: false };
    const { feet: F, h, w } = this.tg;
    // sz : tout est dessiné assez gros pour se lire sur un téléphone (le terrain y est réduit de moitié)
    const s = this.scene, big = this.big, sz = Math.sqrt(big) * 1.5, inward = this.tg.inward;
    const part = (img: Img, life: number, step: (u: number) => void, end?: () => void) => {
      const p: Particle = { img, age: 0, life, step, end };
      step(0);
      l.ps.push(p);
    };
    switch (kind) {
      case 'poison': {
        const key = bubbleTex(s);
        l.every = 190 / big;
        l.spawn = () => {
          const x0 = rnd(-w * 0.32, w * 0.32), y0 = F - h * rnd(0.12, 0.62), size = rnd(10, 16) * sz, rise = rnd(30, 50) * sz, ph = rnd(0, 6.3);
          const img = this.add(key, Math.random() < 0.65).setTint(pick([0x8fe04a, 0x5ccf3a, 0xb8f060]));
          part(img, rnd(850, 1150), (u) => {
            const pop = u > 0.86 ? (u - 0.86) / 0.14 : 0;
            this.at(img, x0 + Math.sin(ph + u * 5) * 6, y0 - rise * u);
            const d = size * (0.55 + 0.45 * Math.min(1, u * 4)) * (1 + pop * 0.7);
            img.setDisplaySize(d, d).setAlpha(Math.min(1, u / 0.12) * (1 - pop));
          });
        };
        break;
      }
      case 'burn': {
        const key = flameTex(s), dot = dotTex(s);
        // une lueur chaude derrière lui, qui vacille
        const glow = this.add(dot, false).setTint(0xff7a2a).setBlendMode(ADD);
        glow.setDisplaySize(w * 2 + 40, h * 1.1);
        l.fixed.push(glow);
        l.frame = (lp) => this.at(glow, 0, F - h * 0.35).setAlpha(lp.fade * (0.26 + 0.08 * Math.sin(lp.t / 70) * Math.sin(lp.t / 113)));
        l.every = 75 / big;
        let n = 0;
        l.spawn = () => {
          const x0 = rnd(-w * 0.38, w * 0.38), y0 = F - h * rnd(0.04, 0.62), ph = rnd(0, 6.3);
          if (++n % 4 === 0) {
            // une braise qui monte en courbe
            const img = this.add(sparkTex(s), true).setTint(0xffc04a).setBlendMode(ADD);
            const rise = rnd(50, 80) * sz, d = rnd(5, 8) * sz;
            part(img, rnd(700, 1000), (u) => {
              this.at(img, x0 + Math.sin(ph + u * 4) * 10 * u, y0 - rise * u).setDisplaySize(d, d).setAlpha(Math.min(1, u * 5) * (1 - u));
            });
            return;
          }
          const sw = rnd(13, 19) * sz, rise = rnd(20, 34) * sz;
          const img = this.add(key, Math.random() < 0.6).setTint(pick([0xff6a24, 0xff9a3a, 0xffc84e])).setBlendMode(ADD);
          part(img, rnd(420, 620), (u) => {
            this.at(img, x0 + Math.sin(ph + u * 7) * 3 * u, y0 - rise * u);
            img.setDisplaySize(sw * (1 - u * 0.55), sw * 1.5 * (1 - u * 0.3)).setAlpha(Math.min(1, u / 0.18) * (1 - u) * 1.1);
          });
        };
        break;
      }
      case 'bleed': {
        const key = dropTex(s), dot = dotTex(s);
        l.every = 300 / big;
        l.spawn = () => {
          const x0 = rnd(-w * 0.26, w * 0.26), y0 = F - h * rnd(0.32, 0.62), d = rnd(11, 13) * sz;
          const img = this.add(key, true);
          part(img, rnd(480, 600), (u) => {
            const grow = Math.min(1, u * 5);
            this.at(img, x0, y0 + (F - 3 - y0) * u * u).setDisplaySize(d * 0.75 * grow, d * 1.1 * grow).setAlpha(1);
          }, () => {
            // une petite éclaboussure sur le sol
            for (const side of [-1, 1]) {
              const sp = this.add(dot, true).setTint(0xc81e3a);
              part(sp, 260, (u) => this.at(sp, x0 + side * 9 * u, F - 3 - Math.sin(Math.PI * u) * 6).setDisplaySize(5, 5).setAlpha(1 - u));
            }
          });
        };
        break;
      }
      case 'regen': {
        const dot = sparkTex(s);
        const plus = plusTex(s);
        let n = 0;
        l.every = 170 / big;
        l.spawn = () => {
          // une petite croix verte de temps en temps, des lueurs le reste du temps
          if (++n % 3 === 0) {
            const x0 = rnd(-w * 0.4, w * 0.4), y0 = F - h * rnd(0.2, 0.6), d = rnd(13, 16) * sz;
            const img = this.add(plus, true).setTint(0x5dff8a);
            part(img, 900, (u) => this.at(img, x0, y0 - 40 * sz * u).setDisplaySize(d, d).setAlpha(Math.min(1, u * 6) * Math.min(1, (1 - u) * 3)));
            return;
          }
          const a0 = rnd(0, 6.3), r = w * 0.48 + 6, d0 = rnd(12, 17) * sz;
          const img = this.add(dot, true).setTint(pick([0x5dff9a, 0xa6ffb8, 0x3be07a])).setBlendMode(ADD);
          part(img, rnd(1000, 1300), (u) => {
            const a = a0 + u * 4.2, depth = Math.sin(a);
            this.at(img, Math.cos(a) * r * (1 - u * 0.35), F - h * (0.06 + 0.9 * u));
            const d = d0 * (0.8 + 0.2 * depth) * (1 - u * 0.35);
            img.setDisplaySize(d, d).setAlpha(Math.min(1, u * 5) * Math.sqrt(1 - u) * (0.75 + 0.25 * depth));
          });
        };
        break;
      }
      case 'stun': {
        const key = starTex(s);
        const stars = [0, 1, 2].map(() => this.add(key, true));
        l.fixed.push(...stars);
        const rx = Math.max(30, w * 0.42), ry = 6 * sz, y = F - h * 0.86;
        l.frame = (lp) => {
          stars.forEach((st, i) => {
            const a = lp.t / 260 + (i * Math.PI * 2) / 3, depth = Math.sin(a);
            const d = 19 * sz * (0.78 + 0.26 * depth);
            this.at(st, Math.cos(a) * rx, y + depth * ry).setDisplaySize(d, d).setAngle(lp.t / 6 + i * 40)
              .setAlpha(lp.fade * (0.7 + 0.3 * depth));
          });
        };
        break;
      }
      case 'silence': {
        const dot = dotTex(s);
        const glow = this.add(dot, true).setTint(0x9a5cff).setBlendMode(ADD);
        const seal = this.add(sealTex(s), true);
        l.fixed.push(glow, seal);
        const x = inward * (w * 0.42 + 8), y = F - h * 0.84;
        l.frame = (lp) => {
          const yy = y + Math.sin(lp.t / 320) * 3, pop = 0.6 + 0.4 * lp.fade;
          this.at(seal, x, yy).setDisplaySize(22 * sz * pop, 22 * sz * pop).setAngle(Math.sin(lp.t / 520) * 10).setAlpha(lp.fade);
          this.at(glow, x, yy).setDisplaySize(40 * sz, 40 * sz).setAlpha(lp.fade * (0.3 + 0.1 * Math.sin(lp.t / 200)));
        };
        break;
      }
      case 'slow': {
        // cinq lueurs qui tournent lentement autour des jambes en descendant, chacune avec sa traîne
        const dot = sparkTex(s);
        const motes = Array.from({ length: 15 }, () => this.add(dot, true).setTint(0x7fc8ff).setBlendMode(ADD));
        l.fixed.push(...motes);
        const rx = w * 0.5 + 6;
        l.frame = (lp) => {
          for (let i = 0; i < 5; i++) {
            for (let j = 0; j < 3; j++) {
              const m = motes[i * 3 + j]!;
              const a = -lp.t / 620 + (i * Math.PI * 2) / 5 + j * 0.22;
              const f = (lp.t / 2600 + i / 5) % 1, depth = Math.sin(a);
              const yy = F - h * (0.46 - 0.38 * f) + depth * 6;
              const d = (10 - j * 2.4) * sz * (0.8 + 0.2 * depth);
              this.at(m, Math.cos(a) * rx, yy).setDisplaySize(d, d)
                .setAlpha(lp.fade * Math.min(1, Math.sin(Math.PI * f) * 2) * (0.78 + 0.22 * depth) * (1 - j * 0.25));
            }
          }
        };
        break;
      }
      case 'taunt': {
        // (un halo ordinaire, plus large que lui : il dépasse de sa silhouette, sur un sol clair comme sombre)
        const glow = this.add(dotTex(s), false).setTint(0xff3020);
        l.fixed.push(glow);
        l.frame = (lp) => {
          const b = 0.5 + 0.5 * Math.sin(lp.t / 190);
          this.at(glow, 0, F - h * 0.48).setDisplaySize((w * 2.1 + 50) * (0.94 + 0.1 * b), h * 1.55 * (0.94 + 0.1 * b)).setAlpha(lp.fade * (0.4 + 0.25 * b));
        };
        break;
      }
      case 'arrows': {
        const key = chevronTex(s);
        l.every = 520;
        l.spawn = () => {
          if (!this.buffs.length) return;
          const kd = this.buffs[this.buffTurn % this.buffs.length]!;
          const b = BUFFS[kd]!;
          const side = this.buffTurn++ % 2 ? 1 : -1;
          const x = side * (w * 0.46 + 8), yA = F - h * 0.32, yB = F - h * 0.78;
          const img = this.add(key, true).setTint(b.color).setFlipY(!b.up);
          const d = 17 * sz;
          part(img, 820, (u) => {
            this.at(img, x, b.up ? yA + (yB - yA) * u : yB + (yA - yB) * u).setDisplaySize(d, d * 0.78)
              .setAlpha(Math.min(1, u * 5) * Math.min(1, (1 - u) * 3));
          });
        };
        break;
      }
      case 'shield': {
        const img = this.add(shieldTex(s), true).setTint(0xd8f2ff).setBlendMode(ADD);
        l.fixed.push(img);
        const bw = Math.max(w * 1.3, 72) + 14, bh = h * 1.12 + 12;
        l.frame = (lp) => {
          // à l'arrivée elle gonfle depuis le corps ; au départ elle s'élargit et s'efface
          const k = lp.ending ? 1 + (1 - lp.fade) * 0.25 : 0.6 + 0.4 * Phaser.Math.Easing.Back.Out(lp.fade);
          this.at(img, 0, F - h * 0.52).setDisplaySize(bw * k, bh * k).setAlpha(lp.fade * (0.6 + 0.15 * Math.sin(lp.t / 330)));
        };
        break;
      }
    }
    return l;
  }
}
