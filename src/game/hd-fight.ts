// Personnages HD animés au combat : les planches de refonte-graphique/pixel/hd/anim/jeu_export.py
// (public/art/hd/, hd-meta.ts) et leur chorégraphie. Le personnage est dessiné « en place » : c'est le jeu qui le
// déplace (corps à corps), fait voler le projectile jusqu'à la vraie cible (tir) et pose l'impact sur la cible.
import Phaser from 'phaser';
import type { Hit, SkillDef } from '../core/battle/types';
import type { Element } from '../core/types';
import { HD_ANIM } from './hd-meta';
import { meleeTempo, plainTempo, tirTempo } from './hd-tempo';

type Rect = readonly number[];
/** Une animation exportée (voir l'en-tête de hd-meta.ts). */
interface Anim {
  genre: 'pose' | 'melee' | 'tir' | 'sort' | 'rayon' | 'equipe';
  ms: readonly number[];
  f: readonly number[];
  coup?: number;
  cible?: readonly number[];
  portee?: number;
  haut?: number;
  charge?: readonly number[];
  avance?: readonly number[];
  elan?: readonly number[];
  proj?: readonly number[];
  projMs?: readonly number[];
  depart?: number;
  bouche?: readonly number[];
  vitesse?: number;
  pente?: number;
  arc?: number;
  rase?: number;
  retour?: readonly number[];
  retourDe?: number;
  rayon?: readonly number[];
  longueur?: number;
}
interface Char {
  name: string;
  top: number;
  avant?: number;
  sol: readonly number[];
  frames: readonly Rect[];
  anims: { pose: Anim; attaque: Anim; speciale: Anim };
}
interface Fx {
  ms: readonly number[];
  dos: readonly number[];
  devant: readonly number[];
  frames: readonly Rect[];
  eclat: readonly [string, Record<string, number>];
}
/** L'avant du corps d'un ennemi « ordinaire » (pixels du dessin) : celui que les animateurs ont imaginé en face. */
const AVANT = 40;
const CHARS = HD_ANIM.chars as unknown as Record<string, Char>;
const FXS = HD_ANIM.fx as unknown as Record<string, Fx>;
const UP = HD_ANIM.up;
/** Les éléments dans le nom des effets reçus (refonte-graphique/pixel/hd/anim/effets). */
const FX_ELEMENT: Record<Element, string> = { fire: 'feu', wind: 'vent', water: 'eau', earth: 'terre' };
/** La lumière de la charge, à la couleur de l'élément (douce : elle se reconnaît sans éblouir). */
const CHARGE_COLOR: Record<Element, number> = { fire: 0xffa04a, wind: 0x8cf0c0, water: 0x7cc4ff, earth: 0xe8c070 };

export const hasHd = (id: string): boolean => id in CHARS;
export const hdChar = (id: string): Char => CHARS[id]!;

/** Ce qu'une scène de combat prête au metteur en scène HD. */
export interface HdView {
  unit: { id: string; side: 'hero' | 'enemy'; element: Element; boss?: boolean };
  body: Phaser.GameObjects.Container;
  sprite: Phaser.GameObjects.Container;
  homeX: number;
  homeY: number;
  hd?: HdActor;
}
export interface HdHost {
  view(id: string): HdView | undefined;
  allies(side: 'hero' | 'enemy'): HdView[];
  showHit(hit: Hit, big: boolean): void;
  recoil(v: HdView, dir: number, px: number, t: number): void;
  flash(x: number, y: number, color: number, r: number, t: number): void;
  feetY: number;
}

/** Charge la planche d'un personnage HD (et, pour un sort d'équipe, les effets reçus de son élément). */
export function loadHd(scene: Phaser.Scene, id: string, element: Element) {
  if (!scene.textures.exists(`hd-${id}`)) scene.load.image(`hd-${id}`, `art/hd/${id}.webp`);
  if (CHARS[id]?.anims.speciale.genre === 'equipe') {
    for (const key of Object.keys(FXS)) {
      if ((key.endsWith(`-${FX_ELEMENT[element]}`) || !key.includes('-')) && !scene.textures.exists(`hdfx-${key}`)) scene.load.image(`hdfx-${key}`, `art/hd/fx/${key}.webp`);
    }
  }
}

/** Les cases d'une planche (une seule fois par texture). */
function cut(scene: Phaser.Scene, key: string, rects: readonly Rect[]) {
  const tex = scene.textures.get(key);
  if (tex.has('0')) return;
  rects.forEach((r, i) => tex.add(String(i), 0, r[0]! * UP, r[1]! * UP, r[2]! * UP, r[3]! * UP));
}

/** Pose la case `i` d'une planche : son coin haut-gauche à (ax, ay) × k du repère (pieds, bout du projectile…). */
function setCell(img: Phaser.GameObjects.Image, key: string, rects: readonly Rect[], i: number, k: number) {
  if (i < 0) {
    img.setVisible(false);
    return;
  }
  const r = rects[i]!;
  img.setTexture(key, String(i)).setOrigin(0).setPosition(r[4]! * k, r[5]! * k).setScale(k / UP).setVisible(true);
}

/** Lumière douce (dégradé rond) partagée par toutes les charges. */
function glowTexture(scene: Phaser.Scene): string {
  const key = 'hd-glow';
  if (scene.textures.exists(key)) return key;
  const c = scene.textures.createCanvas(key, 128, 128)!;
  const ctx = c.getContext();
  const g = ctx.createRadialGradient(64, 64, 0, 64, 64, 64);
  g.addColorStop(0, 'rgba(255,255,255,1)');
  g.addColorStop(0.35, 'rgba(255,255,255,0.55)');
  g.addColorStop(1, 'rgba(255,255,255,0)');
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, 128, 128);
  c.refresh();
  return key;
}

type Play = { name: keyof Char['anims']; ms: number[]; i: number; t: number; loop: boolean; onFrame?: (i: number) => void; onTick?: (i: number, u: number) => void; onEnd?: () => void };

/** Un personnage HD : une image dans son conteneur (retourné pour les ennemis), qui joue ses animations. */
export class HdActor {
  readonly img: Phaser.GameObjects.Image;
  readonly key: string;
  readonly ch: Char;
  /** Taille d'un pixel du dessin, en unités du jeu. */
  readonly k: number;
  private play?: Play;
  private glow?: { back: Phaser.GameObjects.Image; ground: Phaser.GameObjects.Image; lit: Phaser.GameObjects.Image; t: number; on: boolean; a: number };

  constructor(private scene: Phaser.Scene, readonly fig: Phaser.GameObjects.Container, readonly id: string, k: number, private element: Element) {
    this.key = `hd-${id}`;
    this.ch = CHARS[id]!;
    this.k = k;
    cut(scene, this.key, this.ch.frames);
    this.img = scene.add.image(0, 0, this.key, '0');
    fig.add(this.img);
    const pose = this.ch.anims.pose;
    this.start('pose', pose.ms.slice(), true);
    this.play!.i = Math.floor(Math.random() * pose.f.length);
    this.show();
  }

  /** Joue une animation ; `ms` = durée de chaque image (déjà divisée par la vitesse du combat). */
  start(name: keyof Char['anims'], ms: number[], loop = false, cb: Pick<Play, 'onFrame' | 'onTick' | 'onEnd'> = {}) {
    this.play = { name, ms, i: 0, t: 0, loop, ...cb };
    this.show();
    cb.onFrame?.(0);
  }

  private show() {
    const p = this.play!;
    const a = this.ch.anims[p.name];
    setCell(this.img, this.key, this.ch.frames, a.f[p.i]!, this.k);
    const ch = a.charge;
    this.setCharge(!!ch && p.name !== 'pose' && p.i >= ch[0]! && p.i <= ch[1]!);
  }

  update(dt: number) {
    const p = this.play;
    if (!p) return;
    p.t += dt;
    while (p.t >= p.ms[p.i]!) {
      p.t -= p.ms[p.i]!;
      p.i += 1;
      if (p.i >= p.ms.length) {
        if (p.loop) p.i = 0;
        else {
          const end = p.onEnd;
          this.start('pose', this.ch.anims.pose.ms.slice(), true);
          end?.();
          return;
        }
      }
      this.show();
      p.onFrame?.(p.i);
    }
    p.onTick?.(p.i, Math.min(1, p.t / p.ms[p.i]!));
    this.updateGlow(dt);
  }

  /** La charge : un halo doux de l'élément derrière lui, une flaque de lumière au sol, le dessin qui s'éclaire un peu, en pulsant. */
  private setCharge(on: boolean) {
    if (on && !this.glow) {
      const key = glowTexture(this.scene);
      const color = CHARGE_COLOR[this.element];
      const h = this.ch.top * this.k;
      const back = this.scene.add.image(0, -h * 0.48, key).setTint(color).setBlendMode(Phaser.BlendModes.ADD).setAlpha(0);
      back.setDisplaySize(h * 1.15, h * 1.25);
      const ground = this.scene.add.image(0, 0, key).setTint(color).setBlendMode(Phaser.BlendModes.ADD).setAlpha(0);
      ground.setDisplaySize(h * 1.3, h * 0.26);
      const lit = this.scene.add.image(0, 0, this.key, this.img.frame.name).setOrigin(0).setBlendMode(Phaser.BlendModes.ADD).setTint(color).setAlpha(0);
      this.fig.addAt(ground, 0);
      this.fig.addAt(back, 0);
      this.fig.add(lit);
      this.glow = { back, ground, lit, t: 0, on: true, a: 0 };
    }
    if (this.glow) this.glow.on = on;
  }

  private updateGlow(dt: number) {
    const g = this.glow;
    if (!g) return;
    g.t += dt;
    g.a = Phaser.Math.Clamp(g.a + (g.on ? dt / 140 : -dt / 220), 0, 1);
    if (!g.on && g.a <= 0) {
      g.back.destroy();
      g.ground.destroy();
      g.lit.destroy();
      this.glow = undefined;
      return;
    }
    const pulse = 0.5 + 0.5 * Math.sin(g.t / 120);
    g.back.setAlpha(g.a * (0.32 + 0.16 * pulse));
    g.ground.setAlpha(g.a * (0.4 + 0.2 * pulse));
    const h = this.ch.top * this.k * (0.96 + 0.06 * pulse);
    g.back.setDisplaySize(h * 1.15, h * 1.25);
    // le dessin lui-même s'éclaire (même image, en lumière ajoutée)
    g.lit.setTexture(this.key, this.img.frame.name).setPosition(this.img.x, this.img.y).setScale(this.img.scaleX, this.img.scaleY).setVisible(this.img.visible);
    g.lit.setAlpha(g.a * (0.12 + 0.12 * pulse));
  }
}

/**
 * La mise en scène d'un coup HD. Renvoie sa durée (ms réelles) : le combat attend la fin avant le coup suivant.
 * `which` : attaque de base ou spéciale ; `hits` : ce que les règles ont décidé.
 */
export function hdStrike(scene: Phaser.Scene, host: HdHost, src: HdView, which: 'attaque' | 'speciale', hits: Hit[], speed: number, skill?: SkillDef): number {
  const actor = src.hd!;
  const a = actor.ch.anims[which];
  const dir = src.unit.side === 'hero' ? 1 : -1;
  const k = actor.k;
  const sp = speed;
  // attaque de base : tempo commun à tous (hd-tempo.ts) ; spéciale : les durées de l'animateur
  const even = which === 'attaque';
  let ms = plainTempo(a, sp, even);
  const coup = a.coup ?? 0;
  const color = CHARGE_COLOR[src.unit.element];
  // les cibles touchées (une seule fois chacune), dans l'ordre des règles
  const targets: { v: HdView; hits: Hit[] }[] = [];
  for (const h of hits) {
    const v = host.view(h.target);
    if (!v) continue;
    const t = targets.find((x) => x.v === v);
    if (t) t.hits.push(h);
    else targets.push({ v, hits: [h] });
  }
  const foes = targets.filter((t) => t.v.unit.side !== src.unit.side);
  const friends = targets.filter((t) => t.v.unit.side === src.unit.side);
  const feet = (v: HdView) => ({ x: v.body.x, y: v.body.y + host.feetY });
  const T = (i: number) => ms.slice(0, i).reduce((s, m) => s + m, 0);
  let total = T(ms.length);

  /** Les images « sur la cible » d'une animation, posées aux pieds de la cible (retournées comme le lanceur). */
  const onTarget = (v: HdView, from: number, delay: number) => {
    const cells = a.cible;
    if (!cells || !cells.slice(from).some((c) => c >= 0)) return 0;
    const c = scene.add.container(0, 0).setDepth(v.body.depth + 2);
    const img = scene.add.image(0, 0, actor.key, '0');
    c.add(img).setScale(dir, 1).setVisible(false);
    let t = delay;
    for (let i = from; i < cells.length; i++) {
      const at = t;
      scene.time.delayedCall(at, () => {
        const p = feet(v);
        c.setPosition(p.x, p.y).setVisible(true).setDepth(v.body.depth + 2);
        setCell(img, actor.key, actor.ch.frames, cells[i]!, k);
      });
      t += ms[i]!;
    }
    scene.time.delayedCall(t, () => c.destroy());
    return t - delay;
  };
  /** Le coup porte : chiffres, recul, éclair doux (s'il n'y a pas d'impact dessiné). */
  const land = (tg: { v: HdView; hits: Hit[] }, drawn: boolean) => {
    tg.hits.forEach((h) => host.showHit(h, which === 'speciale'));
    if (tg.hits.some((h) => h.kind === 'damage')) {
      host.recoil(tg.v, dir, which === 'speciale' ? 18 : 10, 1 / sp);
      const p = feet(tg.v);
      host.flash(p.x - dir * 6, p.y - (a.haut ?? 40) * k, color, drawn ? 14 : 24, 1 / sp);
      if (which === 'speciale') scene.cameras.main.shake(120 / sp, 0.004);
    }
  };

  if (a.genre === 'melee' && foes.length) {
    const dst = foes[0]!.v;
    const av = a.avance;
    // la distance de l'animation, plus la carrure de la cible quand elle est plus large qu'un homme (crabe, araignée…)
    const bulk = Math.max(0, (dst.hd?.ch.avant ?? AVANT) - AVANT) * (dst.hd?.k ?? k);
    const reach = Math.max(56, ((a.portee ?? 100) - (av ? av[coup]! : 0)) * k + bulk);
    const home = { x: src.homeX, y: src.homeY };
    const strike = { x: dst.homeX - dir * reach, y: dst.homeY };
    const dist = Math.hypot(strike.x - home.x, strike.y - home.y);
    // les durées : l'élan (dessiné ou non) a le temps de couvrir la vraie distance, au tempo commun pour une attaque de base
    const tp = meleeTempo(a, dist, sp, even);
    ms = tp.ms;
    const { back, overlap, hop } = tp;
    let frac: (i: number, u: number) => number;
    if (!hop) {
      // le personnage avance au rythme que l'animateur a dessiné (l'élan cuit dans le GIF, ramené à la vraie distance)
      const f = av!.map((x) => Phaser.Math.Clamp(x / Math.max(1, av![coup]!), 0, 1));
      frac = (i, u) => f[i]! + ((f[i + 1] ?? 0) - f[i]!) * u;
    } else {
      // pas d'élan dessiné : il bondit jusqu'à la cible pendant la préparation du coup, puis revient en courant
      const t0 = T(tp.e0), t1 = T(tp.e1);
      frac = (i, u) => {
        const t = T(i) + u * ms[i]!;
        const x = Phaser.Math.Clamp((t - t0) / Math.max(1, t1 - t0), 0, 1);
        return x < 0.5 ? 2 * x * x : 1 - (-2 * x + 2) ** 2 / 2;
      };
    }
    // le retour en courant (sans élan dessiné) : après l'animation, ou pendant la fin de la récupération (attaque de base)
    let returning = false;
    const goBack = () => {
      if (returning) return;
      returning = true;
      scene.tweens.add({ targets: src.body, x: home.x, y: home.y, duration: back, ease: 'Quad.easeInOut',
        onUpdate: (tw) => { src.body.y -= Math.sin(Math.PI * tw.progress) * 10; },
        onComplete: () => src.body.setDepth(home.y) });
    };
    if (back > 0 && overlap > 0) scene.time.delayedCall(T(ms.length) - overlap, goBack);
    actor.start(which, ms, false, {
      onTick: (i, u) => {
        if (returning) return;
        const fr = frac(i, u);
        // sans élan dessiné, un petit bond pendant la course (les pieds quittent le sol)
        const lift = hop && i < coup ? Math.sin(Math.PI * fr) * 14 : 0;
        src.body.setPosition(home.x + (strike.x - home.x) * fr, home.y + (strike.y - home.y) * fr - lift);
        src.body.setDepth(Math.max(home.y + (strike.y - home.y) * fr, dst.homeY) + 1);
      },
      onFrame: (i) => {
        if (i === coup) foes.forEach((t) => land(t, !!a.cible && a.cible[coup]! >= 0));
      },
      onEnd: () => {
        if (back > 0) goBack();
        else src.body.setPosition(home.x, home.y).setDepth(home.y);
      },
    });
    foes.forEach((t, n) => onTarget(t.v, 0, n * 60 / sp));
    total = T(ms.length) + back - overlap;
    return total;
  }

  if (a.genre === 'tir' && a.proj && foes.length) {
    const dep = a.depart ?? 0;
    // il tire de sa place : le départ et l'arrivée se calculent tout de suite (la cible peut reculer d'un pas, pas plus)
    const p0 = { x: src.homeX + dir * a.bouche![0]! * k, y: src.homeY + host.feetY + a.bouche![1]! * k };
    const path = (tg: { v: HdView }) => {
      // au ras du sol (vague, pics) : il garde sa hauteur au-dessus du sol jusqu'aux pieds de la cible
      const p1 = { x: tg.v.homeX - dir * 8, y: tg.v.homeY + host.feetY + (a.rase ? a.bouche![1]! * k : -(a.haut ?? 40) * k) };
      const dist = Math.hypot(p1.x - p0.x, p1.y - p0.y);
      return { p1, fly: Phaser.Math.Clamp((dist / Math.max(60, (a.vitesse ?? 400) * k)) * 1000, 140, 650) / sp };
    };
    // le personnage suit son projectile : les images du vol durent le temps du vol jusqu'à la première cible (le
    // coup tombe quand il arrive) ; l'arme qui revient (boomerang) met le même temps pour revenir
    const first = path(foes[0]!);
    const tp = tirTempo(a, first.fly, sp, even);
    ms = tp.ms;
    first.fly = tp.fly;
    const ret = a.retour, r0 = a.retourDe ?? 0;
    total = T(ms.length);
    actor.start(which, ms, false, {});
    const tDep = T(dep);
    foes.forEach((tg, n) => {
      const delay = tDep + n * 70 / sp;
      const { p1, fly } = n ? path(tg) : first;
      const after = a.cible ? ms.slice(coup).reduce((s, m) => s + m, 0) : 220 / sp;
      total = Math.max(total, delay + fly + after);
      scene.time.delayedCall(delay, () => {
        const c = scene.add.container(p0.x, p0.y).setDepth(Math.max(src.body.depth, tg.v.body.depth) + 3);
        const img = scene.add.image(0, 0, actor.key, '0');
        c.add(img);
        const ang = a.rase ? 0 : Math.atan2(p1.y - p0.y, Math.abs(p1.x - p0.x)) - (a.pente ?? 0);
        c.setScale(dir, 1).setRotation(dir * ang);
        const pm = (a.projMs ?? []).map((m) => m / sp);
        const loop = a.proj!.length > 1 ? a.proj!.slice(1) : a.proj!;
        const lms = a.proj!.length > 1 ? pm.slice(1) : pm;
        setCell(img, actor.key, actor.ch.frames, a.proj![0]!, k);
        const arc = a.rase ? 0 : (a.arc ?? 0) * k;
        scene.tweens.addCounter({
          from: 0, to: 1, duration: fly, ease: 'Linear',
          onUpdate: (tw) => {
            const u = tw.getValue() ?? 0;
            const el = tw.elapsed;
            if (el >= (pm[0] ?? 0)) {
              const per = lms.reduce((s, m) => s + m, 0) || 1;
              let r = (el - (pm[0] ?? 0)) % per, j = 0;
              while (r >= lms[j]! && j < lms.length - 1) r -= lms[j++]!;
              setCell(img, actor.key, actor.ch.frames, loop[j]!, k);
            }
            c.setPosition(p0.x + (p1.x - p0.x) * u, p0.y + (p1.y - p0.y) * u - arc * 4 * u * (1 - u));
          },
          onComplete: () => {
            c.destroy();
            const drawn = onTarget(tg.v, coup, 0) > 0;
            land(tg, drawn);
          },
        });
      });
    });
    if (ret) {
      // l'arme revient de la première cible jusqu'à la main, en jouant ses images du retour
      const tg = foes[0]!.v;
      const q0 = { x: tg.homeX - dir * 8, y: tg.homeY + host.feetY - (a.haut ?? 40) * k };
      const t0 = T(r0), dur = T(r0 + ret.length) - t0;
      const c = scene.add.container(q0.x, q0.y).setScale(dir, 1).setVisible(false);
      const img = scene.add.image(0, 0, actor.key, '0');
      c.add(img);
      scene.time.delayedCall(t0, () => {
        c.setDepth(Math.max(src.body.depth, tg.body.depth) + 3).setVisible(true);
        scene.tweens.addCounter({
          from: 0, to: 1, duration: dur, ease: 'Sine.easeIn',
          onUpdate: (tw) => {
            const u = tw.getValue() ?? 0;
            setCell(img, actor.key, actor.ch.frames, ret[Math.min(ret.length - 1, Math.floor((tw.elapsed / Math.max(1, dur)) * ret.length))]!, k);
            c.setPosition(q0.x + (p0.x - q0.x) * u, q0.y + (p0.y - q0.y) * u);
          },
          onComplete: () => c.destroy(),
        });
      });
    }
    return total + 100 / sp;
  }

  if (a.genre === 'equipe') {
    actor.start(which, ms, false, {});
    const tCoup = T(coup);
    const fx = receptionFx(skill, src.unit.element);
    let end = 0;
    friends.forEach((tg, n) => {
      const d = tCoup + n * 60 / sp;
      scene.time.delayedCall(d, () => tg.hits.forEach((h) => host.showHit(h, false)));
      fx.forEach((name, m) => { end = Math.max(end, d + m * 180 / sp + playReception(scene, tg.v, name, k, sp, d + m * 180 / sp, host.feetY)); });
    });
    return Math.max(total, end);
  }

  // 'sort' et 'rayon' : il lance sur place, l'effet apparaît sur chaque cible (le jet s'étire jusqu'à elle)
  actor.start(which, ms, false, {});
  const tCoup = T(coup);
  foes.forEach((tg, n) => {
    const d = n * 60 / sp;
    const drawn = onTarget(tg.v, 0, d) > 0;
    scene.time.delayedCall(tCoup + d, () => land(tg, drawn));
    if (a.genre === 'rayon' && a.rayon) beam(scene, host, src, tg.v, a, actor, ms, dir, d);
  });
  return total + (foes.length - 1) * 60 / sp;
}

/** Le jet (souffle, rayon) : chaque image part de la bouche, tournée vers la cible et étirée jusqu'à elle. */
function beam(scene: Phaser.Scene, host: HdHost, src: HdView, dst: HdView, a: Anim, actor: HdActor, ms: number[], dir: number, delay: number) {
  const k = actor.k;
  const c = scene.add.container(0, 0).setVisible(false);
  const img = scene.add.image(0, 0, actor.key, '0');
  c.add(img);
  let t = delay;
  a.rayon!.forEach((cell, i) => {
    scene.time.delayedCall(t, () => {
      if (cell < 0) {
        c.setVisible(false);
        return;
      }
      const p0 = { x: src.body.x + dir * a.bouche![0]! * k, y: src.body.y + host.feetY + a.bouche![1]! * k };
      const p1 = { x: dst.body.x, y: dst.body.y + host.feetY - (a.haut ?? 40) * k };
      const len = Math.hypot(p1.x - p0.x, p1.y - p0.y);
      // étiré jusqu'à la cible ; un peu plus épais quand il va loin (étiré seulement en long, il paraîtrait écrasé)
      const stretch = Phaser.Math.Clamp(len / Math.max(20, (a.longueur ?? 100) * k), 0.5, 3);
      c.setPosition(p0.x, p0.y).setScale(dir * stretch, Phaser.Math.Clamp(Math.sqrt(stretch), 0.85, 1.35)).setRotation(dir * Math.atan2(p1.y - p0.y, Math.abs(p1.x - p0.x)))
        .setDepth(Math.max(src.body.depth, dst.body.depth) + 3).setVisible(true);
      setCell(img, actor.key, actor.ch.frames, cell, k);
    });
    t += ms[i]!;
  });
  scene.time.delayedCall(t, () => c.destroy());
}

/** Les effets reçus par les alliés, d'après ce que fait la compétence (soin, purification, résurrection…). */
function receptionFx(skill: SkillDef | undefined, element: Element): string[] {
  const el = FX_ELEMENT[element];
  const out: string[] = [];
  for (const e of skill?.effects ?? []) {
    const name = e.type === 'heal' ? 'soin' : e.type === 'cleanse' ? 'purification' : e.type === 'revive' ? 'resurrection'
      : e.type === 'shield' ? 'bouclier' : e.type === 'energy' ? 'energie'
        : e.type === 'status' && e.status === 'atkUp' ? 'attaque' : e.type === 'status' && e.status === 'defUp' ? 'defense'
          : e.type === 'status' && e.status === 'regen' ? 'regeneration' : '';
    if (name && name !== 'resurrection' && !out.includes(name)) out.push(name);
  }
  return out.map((n) => `${n}-${el}`).filter((n) => n in FXS);
}

/** Un effet reçu sur un allié : le calque de dos derrière lui, celui de devant devant lui, l'éclat en lumière ajoutée. */
function playReception(scene: Phaser.Scene, v: HdView, name: string, k: number, sp: number, delay: number, feetY: number): number {
  const fx = FXS[name];
  const key = `hdfx-${name}`;
  if (!fx || !scene.textures.exists(key)) return 0;
  cut(scene, key, fx.frames);
  const kk = v.hd?.k ?? k;
  const mk = (dz: number) => {
    const c = scene.add.container(0, 0).setVisible(false);
    const img = scene.add.image(0, 0, key, '0');
    c.add(img);
    return { c, img, dz };
  };
  const back = mk(-1), front = mk(1);
  const [col, per] = fx.eclat;
  const glow = scene.add.image(0, 0, glowTexture(scene)).setBlendMode(Phaser.BlendModes.ADD).setTint(Phaser.Display.Color.HexStringToColor(col).color).setVisible(false);
  let t = delay;
  fx.ms.forEach((m, i) => {
    scene.time.delayedCall(t, () => {
      const x = v.body.x, y = v.body.y + feetY;
      for (const L of [back, front]) {
        L.c.setPosition(x, y).setDepth(v.body.depth + L.dz).setVisible(true);
        setCell(L.img, key, fx.frames, (L === back ? fx.dos : fx.devant)[i]!, kk);
      }
      const p = per[String(i)] ?? 0;
      glow.setPosition(x, y - 55).setDisplaySize(130, 150).setDepth(v.body.depth + 2).setVisible(p > 0).setAlpha(p / 45);
    });
    t += m / sp;
  });
  scene.time.delayedCall(t, () => { back.c.destroy(); front.c.destroy(); glow.destroy(); });
  return t - delay;
}
