// Base commune des scènes de combat (Phaser) : décor, personnages, barres de vie, coups et chiffres.
// Le moteur (src/core/battle) calcule ; ces scènes animent ce qu'il raconte.
import Phaser from 'phaser';
import type { Battle } from '../core/battle/engine';
import { ENERGY_MAX, LEADER_SLOT, TICK_MS, type BattleEvent, type Hit, type Slot, type Unit } from '../core/battle/types';
import { HEROES } from '../core/data/heroes';
import type { Element } from '../core/types';
import { ELEMENT_COLOR, artUrl, cardUrl, hasArt, heroCanvas, monsterCanvas } from './art';
import { ART_META } from './art-meta';
import { t } from './i18n';
import { battleLook, monsterArtId, type Look } from './look';

export const W = 720;
export const FONT = '"Baloo 2", "Trebuchet MS", "Segoe UI", Roboto, sans-serif';
export const C = { panel: 0x1f2340, panelLight: 0x2c3260, green: 0x3ccf7a, red: 0xe5484d, blue: 0x4c8dff, energy: 0x4fd1ff, gold: 0xffc94a };

const HERO_X: Record<Slot, number> = { 3: 110, 4: 110, 2: 215, 0: 315, 1: 315 };
const ENEMY_X: Record<Slot, number> = { 0: 405, 1: 405, 2: 505, 3: 610, 4: 610 };
/** Hauteur des rangées, mesurée depuis le haut du sol (`groundTop`). */
const ROW_DY: Record<Slot, number> = { 0: 90, 3: 90, 2: 180, 1: 270, 4: 270 };

const HERO_IDS = new Set(HEROES.map((h) => h.id));

/** Couleur des statuts affichés au-dessus des combattants. */
const STATUS_COLOR: Partial<Record<string, string>> = {
  burn: '#ff8a3d', poison: '#9be15d', bleed: '#ff5a6a', regen: '#5dff9a', stun: '#ffe27a', silence: '#c39bff',
  slow: '#7fc8ff', taunt: '#ffb15c', atkUp: '#ffcf5a', atkDown: '#b0b7d6', defUp: '#7fc8ff', defDown: '#b0b7d6',
  speedUp: '#9be15d', critUp: '#ffcf5a',
};

function hex(color: string): number {
  return Number.parseInt(color.slice(1), 16);
}

export interface View {
  unit: Unit;
  body: Phaser.GameObjects.Container;
  sprite: Phaser.GameObjects.Image;
  bars: Phaser.GameObjects.Graphics;
  homeX: number;
  /** Hauteur et largeur de la barre de vie (au-dessus de la tête du dessin). */
  barY: number;
  barW: number;
  /** Vie affichée : elle baisse quand le coup est montré, pas quand les règles l'ont calculé. */
  hp: number;
}

/**
 * Chacun son tour : pendant qu'un coup se joue, le combat est en pause (les règles ne changent pas, seul l'affichage
 * attend). Durée d'un tour, en ms à vitesse ×1 ; ×2 et ×3 les raccourcissent.
 */
const TURN_MS = { attack: 430, skill: 980, passive: 260, wave: 550 };

/** Taille des dessins Hailuo : pixels de l'écran par unité du repère du dessin (un héros mesure ~190 unités). */
const UNIT_PX = 0.64;
/** Les pieds sont un peu sous le centre du conteneur (comme les anciens dessins). */
const FEET = 47;

type FxName = keyof typeof ART_META.fx;
/** Largeur d'affichage de chaque effet (pixels) et point d'ancrage : centre, ou sol (le bas de l'effet aux pieds). */
const FX: Record<FxName, [number, 'c' | 'g']> = {
  slash: [180, 'c'], crossSlash: [195, 'c'], claw: [170, 'c'], impact: [120, 'c'], shockwave: [230, 'g'], pierce: [200, 'c'],
  fireball: [110, 'c'], explosion: [175, 'c'], flamePillar: [130, 'g'], fireSlash: [180, 'c'], meteor: [150, 'c'], emberBurst: [150, 'c'],
  waterBolt: [115, 'c'], splash: [165, 'g'], iceSpikes: [170, 'g'], frostBurst: [150, 'c'], tornado: [130, 'g'], windBlades: [170, 'c'],
  lightning: [150, 'g'], electricOrb: [80, 'c'], featherGust: [170, 'c'], sonicRing: [130, 'c'], rockSpikes: [170, 'g'], quake: [210, 'g'],
  poison: [140, 'c'], thornVines: [140, 'c'], leafStorm: [170, 'c'], boulder: [115, 'c'], heal: [130, 'c'], holyBeam: [120, 'g'],
  goldShield: [105, 'c'], darkOrb: [130, 'c'],
};
/**
 * Compétences (attaques spéciales) : les images Hailuo, chacune avec sa petite chorégraphie (voir `skillFx`).
 * Les combattants au corps à corps et à distance n'ont pas les mêmes ; la compétence choisit dans sa liste.
 * Les attaques de base, elles, restent discrètes et sont dessinées par le code (`basicMelee`, `basicShot`).
 */
const SKILL_FX: Record<Element, { melee: readonly FxName[]; ranged: readonly FxName[] }> = {
  fire: { melee: ['fireSlash', 'explosion', 'flamePillar'], ranged: ['fireball', 'meteor', 'flamePillar'] },
  water: { melee: ['slash', 'iceSpikes', 'splash'], ranged: ['waterBolt', 'frostBurst', 'iceSpikes'] },
  wind: { melee: ['windBlades', 'crossSlash', 'tornado'], ranged: ['lightning', 'tornado', 'featherGust'] },
  earth: { melee: ['claw', 'rockSpikes', 'quake'], ranged: ['boulder', 'rockSpikes', 'thornVines'] },
};
/** Ce qui éclate à l'arrivée d'un projectile de compétence. */
const ARRIVAL_FX: Partial<Record<FxName, FxName>> = { fireball: 'explosion', meteor: 'explosion', waterBolt: 'splash', electricOrb: 'sonicRing', boulder: 'quake' };
type Pt = { x: number; y: number; feet: number };
/** Temps avant l'impact (projectiles, météore : ils doivent d'abord voyager). */
const TRAVEL: Partial<Record<FxName, number>> = { meteor: 300, fireball: 260, waterBolt: 260, electricOrb: 260, boulder: 260 };
const STATUS_FX: Partial<Record<string, FxName>> = {
  poison: 'poison', burn: 'emberBurst', stun: 'sonicRing', silence: 'darkOrb', atkDown: 'darkOrb', defDown: 'darkOrb',
  slow: 'frostBurst', regen: 'leafStorm', atkUp: 'emberBurst', critUp: 'emberBurst',
};
const hash = (s: string) => [...s].reduce((h, c) => (h * 31 + c.charCodeAt(0)) >>> 0, 7);

export abstract class FightScene extends Phaser.Scene {
  protected battle!: Battle;
  protected views = new Map<string, View>();
  /** Haut du sol : tout le terrain se place à partir de là. */
  protected groundTop = 380;
  /** Les boss des combats « au score » sont dessinés plus gros. */
  protected bigBoss = false;
  /** Resserre le terrain vers le centre (écran d'accueil, plus étroit). */
  protected xSquash = 1;
  /** Terrain et famille de monstres de ce combat. */
  protected look: Look = battleLook('arena', '');

  /** Les combattants à charger avant le combat (les autres arrivent plus tard, avec l'ancien dessin en attendant). */
  protected abstract preloadUnits(): { defId: string; element: string }[];

  preload() {
    const terrain = this.look.terrain;
    if (!this.textures.exists(`t-${terrain}`)) this.load.image(`t-${terrain}`, `art/t/${terrain}.jpg`);
    for (const name of Object.keys(ART_META.fx)) if (!this.textures.exists(`fx-${name}`)) this.load.image(`fx-${name}`, `art/fx/${name}.webp`);
    for (const u of this.preloadUnits()) {
      const id = this.charId(u);
      if (hasArt(id) && !this.textures.exists(`p-${id}`)) this.load.image(`p-${id}`, artUrl(id));
      if (hasArt(id) && HERO_IDS.has(u.defId) && !this.textures.exists(`c-${id}`)) this.load.image(`c-${id}`, cardUrl(id));
    }
  }

  /** Le dessin d'un combattant : un héros, ou le monstre de la famille de ce décor. */
  protected charId(u: { defId: string; element: string }): string {
    return HERO_IDS.has(u.defId) ? u.defId : monsterArtId(u.defId, u.element as Element, this.look);
  }

  protected text(x: number, y: number, value: string, size = 28, color = '#ffffff') {
    return this.add
      .text(x, y, value, { fontFamily: FONT, fontSize: `${size}px`, color, fontStyle: 'bold', align: 'center' })
      .setOrigin(0.5)
      .setShadow(0, 2, '#000000', 3, false, true);
  }

  /** Les adversaires d'arène sont des héros : le dessin dépend de ce qu'est le combattant, pas de son camp. */
  protected texture(u: { defId: string; element: string }): string {
    const isHero = HERO_IDS.has(u.defId);
    const key = isHero ? `h-${u.defId}` : `m-${u.defId}-${u.element}`;
    if (!this.textures.exists(key)) {
      this.textures.addCanvas(key, isHero ? heroCanvas(u.defId) : monsterCanvas(u.defId, u.element as never));
    }
    return key;
  }

  /** Le terrain : l'image du décor, le centre de son arène au milieu des rangées de combattants. */
  protected drawArena(bottom: number) {
    const key = `t-${this.look.terrain}`;
    const m = ART_META.terrains[this.look.terrain];
    if (this.textures.exists(key) && m) {
      const cy = this.groundTop + (ROW_DY[0] + ROW_DY[1]) / 2;
      const k = Math.max(W / m.w, cy / (m.cy * m.h), (bottom - cy) / ((1 - m.cy) * m.h));
      return this.add.image(W / 2, cy - m.cy * m.h * k, key).setOrigin(0.5, 0).setScale(k).setDepth(-10);
    }
    const g = this.add.graphics().setDepth(-10);
    const top = this.groundTop;
    g.fillGradientStyle(0x2b3a78, 0x2b3a78, 0x6b5ca8, 0x6b5ca8, 1);
    g.fillRect(0, 0, W, top + 40);
    g.fillStyle(0x4a5a9a, 0.6);
    for (let i = 0; i < 6; i++) g.fillTriangle(i * 150 - 40, top + 10, i * 150 + 60, top - 70 - (i % 2) * 40, i * 150 + 160, top + 10);
    g.fillGradientStyle(0x3d6b4a, 0x3d6b4a, 0x274a34, 0x274a34, 1);
    g.fillRect(0, top, W, bottom - top);
    g.fillStyle(0xffffff, 0.06);
    g.fillEllipse(W / 2, top + 180, 760, 330);
    return g;
  }

  protected slotPos(unit: Unit): { x: number; y: number } {
    const hero = unit.side === 'hero';
    const x = hero ? HERO_X[unit.slot] : ENEMY_X[unit.slot];
    return { x: W / 2 + (x - W / 2) * this.xSquash, y: this.groundTop + ROW_DY[unit.slot] };
  }

  protected addView(unit: Unit, enter = false) {
    const hero = unit.side === 'hero';
    const { x, y } = this.slotPos(unit);
    const body = this.add.container(enter ? x + 320 : x, unit.boss && this.bigBoss ? y - 30 : y).setDepth(y);
    const id = this.charId(unit);
    let sprite: Phaser.GameObjects.Image;
    let shadow: Phaser.GameObjects.Ellipse;
    let barY: number;
    let barW = unit.boss ? 130 : 86;
    if (this.textures.exists(`p-${id}`)) {
      // dessin Hailuo : les pieds (point 106, 228 du repère) sur la ligne de sol ; retourné autour de ce point
      const [ox, oy, w, h, sc] = ART_META.chars[id as keyof typeof ART_META.chars];
      const k = UNIT_PX * Math.max(0.85, Math.min(1.35, sc)) * (unit.boss ? (this.bigBoss ? 1.45 : 1.12) : 1);
      sprite = this.add.image(0, FEET, `p-${id}`).setDisplaySize(w * k, h * k).setOrigin((106 - ox) / w, (228 - oy) / h).setFlipX(!hero);
      shadow = this.add.ellipse(0, FEET, Math.min(160, w * k * 0.55), 20, 0x000000, 0.3);
      barY = FEET - (228 - Math.max(oy, 228 - 330)) * k - 6;
      barW = unit.boss ? 130 : 86;
    } else {
      const scale = unit.boss ? (this.bigBoss ? 2 : 1.45) : 0.95;
      shadow = this.add.ellipse(0, 50 * scale, 90 * scale, 22, 0x000000, 0.3);
      sprite = this.add.image(0, 0, this.texture(unit)).setScale(scale).setFlipX(!hero);
      barY = unit.boss ? -100 : -72;
    }
    const bars = this.add.graphics();
    body.add([shadow, sprite, bars]);
    if (hero && unit.slot === LEADER_SLOT && unit.talent) body.add(this.text(0, barY - 22, '♛', 26, '#ffe27a'));
    this.views.set(unit.id, { unit, body, sprite, bars, homeX: x, barY, barW, hp: unit.hp });
    if (enter) this.tweens.add({ targets: body, x, duration: 450, ease: 'Back.easeOut' });
  }

  protected clearViews(side?: 'hero' | 'enemy') {
    for (const [id, v] of this.views) {
      if (side && v.unit.side !== side) continue;
      v.body.destroy();
      this.views.delete(id);
    }
  }

  protected syncUnits() {
    for (const v of this.views.values()) {
      const u = v.unit;
      const g = v.bars;
      g.clear();
      if (v.hp <= 0 && u.hp <= 0) continue;
      const w = v.barW;
      const y = v.barY;
      g.fillStyle(0x000000, 0.6);
      g.fillRoundedRect(-w / 2 - 2, y - 2, w + 4, 16, 5);
      g.fillStyle(u.side === 'hero' ? C.green : C.red);
      g.fillRoundedRect(-w / 2, y, w * (Math.max(0, v.hp) / u.maxHp), 12, 4);
      if (u.shield > 0) {
        g.fillStyle(0x9fd8ff, 0.85);
        g.fillRoundedRect(-w / 2, y, Math.min(w, w * (u.shield / u.maxHp)), 6, 3);
      }
      g.fillStyle(C.energy);
      g.fillRect(-w / 2, y + 15, w * (u.energy / ENERGY_MAX), 4);
      v.sprite.setAngle(u.stun > 0 ? Math.sin(this.time.now / 60) * 8 : 0);
    }
  }

  /** Ce que chaque scène fait de plus quand une vague arrive, qu'un combattant tombe, ou à la fin. */
  protected onWave(index: number): void {
    void index;
  }
  protected onDeath(unit: Unit): void {
    void unit;
  }
  protected abstract onEnd(win: boolean): void;

  private queue: { e: BattleEvent; speed: number }[] = [];
  private busy = 0;
  private stepAcc = 0;

  /**
   * Fait avancer le combat un coup à la fois : on joue le coup suivant de la file, on attend qu'il soit fini, et
   * quand la file est vide les règles avancent jusqu'au prochain coup. Les coups calculés au même instant passent
   * donc l'un après l'autre, héros comme ennemis.
   */
  protected advance(delta: number, speed: number) {
    if (this.busy > 0) {
      this.busy -= delta;
      return;
    }
    while (this.queue.length) {
      const q = this.queue.shift()!;
      this.handle([q.e], q.speed);
      const ms = q.e.type === 'attack' ? TURN_MS.attack : q.e.type === 'skill' ? TURN_MS.skill : q.e.type === 'passive' ? TURN_MS.passive : q.e.type === 'wave' ? TURN_MS.wave : 0;
      if (ms) {
        this.busy = ms / q.speed;
        return;
      }
    }
    // file vide : les barres de vie rattrapent les règles (brûlures, etc.), puis les règles avancent
    for (const v of this.views.values()) v.hp = v.unit.hp;
    this.stepAcc = Math.min(this.stepAcc + delta * speed, 1000);
    while (this.stepAcc >= TICK_MS && !this.battle.over) {
      this.stepAcc -= TICK_MS;
      const events = this.battle.step();
      for (const e of events) this.queue.push({ e, speed });
      if (events.some((e) => e.type !== 'tick')) {
        this.stepAcc = 0;
        break;
      }
    }
  }

  protected handle(events: BattleEvent[], speed: number) {
    for (const e of events) {
      switch (e.type) {
        case 'attack':
          this.animateAttack(e.source, e.hit, speed);
          break;
        case 'skill':
          this.animateSkill(e.source, e.skill.id, e.hits, speed);
          break;
        case 'passive':
          this.time.delayedCall(250 / speed, () => e.hits.forEach((h) => this.showHit(h, false)));
          break;
        case 'tick':
          e.hits.forEach((h) => this.showHit(h, false));
          break;
        case 'death': {
          const v = this.views.get(e.unit);
          if (v) {
            this.tweens.add({ targets: v.body, alpha: 0, y: v.body.y + 20, angle: v.unit.side === 'hero' ? -20 : 20, duration: 450 });
            this.onDeath(v.unit);
          }
          break;
        }
        case 'wave':
          this.clearViews('enemy');
          for (const u of e.units) this.addView(u, true);
          this.onWave(e.index);
          break;
        case 'end':
          this.onEnd(e.win);
          break;
      }
    }
  }

  /** Une image d'effet posée en (x, y), à sa taille de base (`k` = échelle correspondante). */
  private fxImage(name: FxName, x: number, y: number, flip = false, ground = FX[name][1] === 'g') {
    const key = `fx-${name}`;
    if (!this.textures.exists(key)) return null;
    const img = this.add.image(x, y, key).setOrigin(0.5, ground ? 0.95 : 0.5).setFlipX(flip).setDepth(1500);
    const k = FX[name][0] / img.width;
    img.setScale(k);
    return { img, k };
  }

  /** Effet simple (soin, bouclier, statut) : il grossit un peu puis s'efface. */
  protected fx(name: FxName, x: number, y: number, o: { size?: number; flip?: boolean; dur?: number } = {}) {
    const f = this.fxImage(name, x, y, o.flip);
    if (!f) return;
    const { img } = f, k = f.k * (o.size ?? 1), dur = o.dur ?? 420;
    img.setScale(k * 0.7).setAlpha(0.95);
    this.tweens.add({ targets: img, scale: k, duration: dur * 0.35, ease: 'Back.easeOut' });
    this.tweens.add({ targets: img, alpha: 0, delay: dur * 0.5, duration: dur * 0.5, onComplete: () => img.destroy() });
  }

  /** Un éclair de lumière bref au point d'impact. */
  private flashAt(x: number, y: number, color = 0xffffff, r = 34, t = 1) {
    const c = this.add.circle(x, y, r, color, 0.8).setDepth(1600).setBlendMode(Phaser.BlendModes.ADD);
    this.tweens.add({ targets: c, scale: 1.8, alpha: 0, duration: 180 * t, onComplete: () => c.destroy() });
  }

  /**
   * La chorégraphie d'une compétence sur une cible : chaque image a sa façon d'arriver, de frapper et de partir
   * (la lame balaie et percute, l'éclair tombe et claque, les pics jaillissent du sol, le météore s'écrase…).
   * `t` = 1 / vitesse du combat. Renvoie le moment de l'impact (ms), pour y caler les chiffres de dégâts.
   */
  private skillFx(name: FxName, from: Pt, to: Pt, dir: number, t: number): number {
    const flip = dir < 0;
    const end = (img: Phaser.GameObjects.Image, delay: number, dur: number, extra: Record<string, unknown> = {}) =>
      this.tweens.add({ targets: img, alpha: 0, delay, duration: dur, ...extra, onComplete: () => img.destroy() });
    const shake = (ms: number, k: number) => this.cameras.main.shake(ms, k);
    switch (name) {
      case 'slash': case 'fireSlash': case 'claw': case 'windBlades': case 'crossSlash': {
        // la lame arrive de derrière en tournant, s'écrase sur la cible en grossissant, puis file en s'étirant
        const f = this.fxImage(name, to.x - dir * 60, to.y, flip);
        if (!f) return 0;
        const { img, k } = f, cross = name === 'crossSlash';
        img.setScale(k * (cross ? 1.7 : 0.35), k * (cross ? 1.7 : 0.9)).setAngle(cross ? dir * 90 : -dir * 40).setAlpha(0.3);
        this.tweens.add({ targets: img, x: to.x + dir * 8, angle: 0, scaleX: k * 1.15, scaleY: k * 1.15, alpha: 1, duration: 120 * t, ease: 'Cubic.easeOut' });
        this.time.delayedCall(110 * t, () => { this.flashAt(to.x, to.y, 0xffffff, 26, t); shake(70, 0.004); });
        end(img, 170 * t, 200 * t, { x: to.x + dir * 50, scaleX: k * 1.5, scaleY: k * 0.5 });
        return 110 * t;
      }
      case 'pierce': {
        const f = this.fxImage(name, to.x - dir * 160, to.y, flip);
        if (!f) return 0;
        const { img, k } = f;
        img.setScale(k * 0.4, k);
        this.tweens.add({ targets: img, x: to.x + dir * 40, scaleX: k * 1.3, duration: 150 * t, ease: 'Quad.easeIn' });
        this.time.delayedCall(140 * t, () => this.flashAt(to.x, to.y, 0xcfe8ff, 28, t));
        end(img, 170 * t, 160 * t, { x: to.x + dir * 90 });
        return 140 * t;
      }
      case 'fireball': case 'waterBolt': case 'electricOrb': case 'boulder': {
        // le projectile part du lanceur, grossit en approchant (le rocher tourne sur lui-même), puis éclate
        const f = this.fxImage(name, from.x + dir * 30, from.y, false);
        if (!f) return 0;
        const { img, k } = f, travel = 260 * t;
        img.setScale(k * 0.6).setRotation(Math.atan2(to.y - from.y, to.x - from.x));
        this.tweens.add({ targets: img, x: to.x, y: to.y, scale: k * 1.1, duration: travel, ease: 'Quad.easeIn', onComplete: () => img.destroy() });
        if (name === 'boulder') this.tweens.add({ targets: img, angle: img.angle + dir * 540, duration: travel });
        if (name === 'electricOrb') this.tweens.add({ targets: img, alpha: 0.6, yoyo: true, repeat: 3, duration: travel / 8 });
        this.time.delayedCall(travel, () => this.skillFx(ARRIVAL_FX[name]!, from, to, dir, t));
        return travel;
      }
      case 'meteor': {
        // tombe du ciel en diagonale, de plus en plus vite, puis s'écrase : explosion, sol fendu, secousse
        const f = this.fxImage(name, to.x - dir * 230, to.y - 360, flip);
        if (!f) return 0;
        const { img, k } = f, fall = 300 * t;
        img.setScale(k * 0.55);
        this.tweens.add({ targets: img, x: to.x - dir * 20, y: to.y - 30, scale: k * 1.05, duration: fall, ease: 'Quad.easeIn', onComplete: () => img.destroy() });
        this.time.delayedCall(fall, () => { this.skillFx('explosion', from, to, dir, t); this.skillFx('quake', from, to, dir, t); shake(220, 0.012); });
        return fall;
      }
      case 'lightning': {
        // l'éclair jaillit d'un coup jusqu'au sol, clignote, claque (flash + secousse), puis s'amincit
        const f = this.fxImage(name, to.x, to.feet, flip, true);
        if (!f) return 0;
        const { img, k } = f;
        img.setScale(k * 0.8, 0);
        this.tweens.add({ targets: img, scaleY: k * 1.3, duration: 70 * t, ease: 'Expo.easeOut' });
        this.tweens.add({ targets: img, alpha: 0.35, delay: 80 * t, duration: 45 * t, yoyo: true, repeat: 2 });
        this.time.delayedCall(70 * t, () => { this.flashAt(to.x, to.feet - 10, 0xfff3a0, 44, t); this.flashAt(to.x, to.y, 0xffffff, 30, t); shake(140, 0.01); });
        end(img, 380 * t, 160 * t, { scaleX: 0 });
        return 70 * t;
      }
      case 'flamePillar': case 'iceSpikes': case 'rockSpikes': case 'splash': case 'holyBeam': {
        // jaillit du sol en s'étirant vers le haut (avec un rebond), tient un instant, puis rentre dans le sol
        const f = this.fxImage(name, to.x, to.feet, flip, true);
        if (!f) return 0;
        const { img, k } = f, beam = name === 'holyBeam';
        img.setScale(beam ? 0 : k * 0.7, beam ? k * 1.2 : 0);
        this.tweens.add({ targets: img, scaleX: k, scaleY: k * (beam ? 1.2 : 1.15), duration: 170 * t, ease: 'Back.easeOut' });
        this.tweens.add({ targets: img, scaleY: k * (beam ? 1.2 : 1), delay: 170 * t, duration: 120 * t });
        if (name === 'rockSpikes' || name === 'iceSpikes') this.time.delayedCall(90 * t, () => shake(110, 0.007));
        if (name === 'flamePillar') this.tweens.add({ targets: img, scaleX: k * 1.08, delay: 200 * t, duration: 70 * t, yoyo: true, repeat: 2 });
        this.time.delayedCall(90 * t, () => this.flashAt(to.x, to.feet - 20, beam ? 0xfff3b0 : 0xffffff, 30, t));
        end(img, 480 * t, 200 * t, beam ? { scaleX: 0 } : { scaleY: 0 });
        return 90 * t;
      }
      case 'quake': case 'shockwave': {
        // l'onde part des pieds et s'élargit au ras du sol pendant que l'écran tremble
        const f = this.fxImage(name, to.x, to.feet + 6, flip, true);
        if (!f) return 0;
        const { img, k } = f;
        img.setScale(k * 0.25, k * 0.4);
        this.tweens.add({ targets: img, scaleX: k * 1.35, scaleY: k * 1.05, duration: 260 * t, ease: 'Cubic.easeOut' });
        shake(200, 0.009);
        end(img, 220 * t, 260 * t);
        return 60 * t;
      }
      case 'explosion': case 'emberBurst': case 'impact': case 'sonicRing': case 'frostBurst': {
        // éclate d'un petit point à plus grand que nature, en tournant un peu, puis se dissipe en gonflant
        const f = this.fxImage(name, to.x, to.y, flip);
        if (!f) return 0;
        const { img, k } = f;
        img.setScale(k * 0.2).setAngle(name === 'frostBurst' ? -40 : Phaser.Math.Between(-15, 15));
        this.tweens.add({ targets: img, scale: k * 1.15, angle: name === 'frostBurst' ? 30 : img.angle, duration: 150 * t, ease: 'Back.easeOut' });
        this.flashAt(to.x, to.y, name === 'frostBurst' ? 0xcff4ff : 0xfff0c0, 36, t);
        if (name === 'explosion') shake(160, 0.01);
        end(img, 200 * t, 240 * t, { scale: k * 1.4 });
        return 20 * t;
      }
      case 'tornado': {
        // la tornade naît au sol, grandit, oscille de gauche à droite en se retournant, puis s'évanouit
        const f = this.fxImage(name, to.x, to.feet, flip, true);
        if (!f) return 0;
        const { img, k } = f;
        img.setScale(k * 0.2);
        this.tweens.add({ targets: img, scale: k * 1.1, duration: 200 * t, ease: 'Back.easeOut' });
        this.tweens.add({ targets: img, x: to.x + 14, delay: 120 * t, duration: 90 * t, yoyo: true, repeat: 3, onRepeat: () => img.toggleFlipX() });
        end(img, 640 * t, 200 * t, { scaleX: 0 });
        return 160 * t;
      }
      case 'featherGust': case 'leafStorm': {
        // la rafale traverse la cible depuis le lanceur, en s'étirant (les feuilles tournent)
        const f = this.fxImage(name, to.x - dir * 150, to.y, flip);
        if (!f) return 0;
        const { img, k } = f;
        img.setScale(k * 0.6, k * 0.8).setAlpha(0.2);
        this.tweens.add({ targets: img, x: to.x + dir * 30, scaleX: k * 1.15, scaleY: k, alpha: 1, duration: 260 * t, ease: 'Sine.easeOut' });
        if (name === 'leafStorm') this.tweens.add({ targets: img, angle: dir * 120, duration: 600 * t });
        end(img, 300 * t, 260 * t, { x: to.x + dir * 120 });
        return 200 * t;
      }
      case 'thornVines': {
        // la liane fouette : elle part couchée en arrière et claque sur la cible
        const f = this.fxImage(name, to.x, to.y, flip);
        if (!f) return 0;
        const { img, k } = f;
        img.setScale(k * 0.5).setAngle(-dir * 75);
        this.tweens.add({ targets: img, angle: dir * 12, scale: k * 1.1, duration: 170 * t, ease: 'Back.easeOut' });
        this.time.delayedCall(150 * t, () => { this.flashAt(to.x, to.y, 0xd8ffb0, 28, t); shake(80, 0.005); });
        end(img, 320 * t, 200 * t, { scale: k * 0.8 });
        return 150 * t;
      }
      case 'darkOrb': case 'poison': {
        // tourbillon qui se resserre sur la cible (orbe), ou nuage qui gonfle et monte (poison)
        const f = this.fxImage(name, to.x, to.y, flip);
        if (!f) return 0;
        const { img, k } = f, orb = name === 'darkOrb';
        img.setScale(orb ? k * 1.5 : k * 0.4).setAlpha(orb ? 0.2 : 1);
        this.tweens.add({ targets: img, scale: orb ? k * 0.8 : k * 1.1, angle: orb ? -360 : 0, y: orb ? to.y : to.y - 18, alpha: 1, duration: 420 * t, ease: 'Sine.easeInOut' });
        end(img, 420 * t, 220 * t);
        return 200 * t;
      }
      case 'heal': {
        const f = this.fxImage(name, to.x, to.y + 20, flip);
        if (!f) return 0;
        const { img, k } = f;
        img.setScale(k * 0.6);
        this.tweens.add({ targets: img, y: to.y - 30, scale: k, duration: 500 * t, ease: 'Sine.easeOut' });
        end(img, 300 * t, 300 * t);
        return 0;
      }
      case 'goldShield': {
        // le bouclier se pose d'un coup (grand → normal), brille, puis se resserre sur le héros
        const f = this.fxImage(name, to.x, to.y, flip);
        if (!f) return 0;
        const { img, k } = f;
        img.setScale(k * 1.7).setAlpha(0);
        this.tweens.add({ targets: img, scale: k, alpha: 1, duration: 200 * t, ease: 'Back.easeOut' });
        this.tweens.add({ targets: img, alpha: 0.6, delay: 220 * t, duration: 110 * t, yoyo: true });
        end(img, 520 * t, 200 * t, { scale: k * 0.5 });
        return 0;
      }
    }
    return 0;
  }

  /** Le centre du corps d'un combattant (là où les coups portent) et ses pieds. */
  private chest(v: View) {
    return { x: v.body.x, y: v.body.y + (FEET + v.barY) / 2 + 10, feet: v.body.y + FEET };
  }

  /** Attaque de base au corps à corps : petit élan et une courte traînée de coup, discrète, à la couleur de l'élément. */
  private basicMelee(to: Pt, dir: number, color: number, t: number) {
    const g = this.add.graphics().setDepth(1400).setPosition(to.x - dir * 4, to.y);
    g.lineStyle(5, color, 0.9).beginPath().arc(0, 0, 24, dir > 0 ? -1.2 : Math.PI - 1.2, dir > 0 ? 1.0 : Math.PI + 1.0).strokePath();
    g.lineStyle(2, 0xffffff, 0.9).beginPath().arc(0, 0, 24, dir > 0 ? -1.0 : Math.PI - 1.0, dir > 0 ? 0.8 : Math.PI + 0.8).strokePath();
    g.setScale(0.6).setAngle(dir * -20);
    this.tweens.add({ targets: g, scale: 1.1, angle: dir * 15, alpha: 0, duration: 200 * t, ease: 'Quad.easeOut', onComplete: () => g.destroy() });
  }

  /** Attaque de base à distance : une petite boule d'énergie avec une traînée, et un petit anneau à l'arrivée. */
  private basicShot(from: Pt, to: Pt, dir: number, color: number, t: number) {
    const x0 = from.x + dir * 30;
    const tail = this.add.ellipse(x0, from.y, 22, 6, color, 0.5).setDepth(1000);
    const ball = this.add.circle(x0, from.y, 6, color).setStrokeStyle(2, 0xffffff, 0.9).setDepth(1001);
    tail.setRotation(Math.atan2(to.y - from.y, to.x - x0));
    this.tweens.add({ targets: [ball, tail], x: to.x, y: to.y, duration: 220 * t, onComplete: () => { ball.destroy(); tail.destroy(); } });
    this.time.delayedCall(220 * t, () => {
      const ring = this.add.circle(to.x, to.y, 8).setStrokeStyle(3, color).setDepth(1400);
      this.tweens.add({ targets: ring, scale: 2.2, alpha: 0, duration: 220 * t, onComplete: () => ring.destroy() });
    });
  }

  private animateAttack(sourceId: string, hit: Hit, speed: number) {
    const src = this.views.get(sourceId);
    const dst = this.views.get(hit.target);
    if (!src || !dst) return;
    const dir = src.unit.side === 'hero' ? 1 : -1;
    const color = hex(ELEMENT_COLOR[src.unit.element]);
    const t = 1 / speed;
    const to = this.chest(dst);
    if (src.unit.ranged) {
      this.basicShot(this.chest(src), to, dir, color, t);
    } else {
      this.tweens.add({ targets: src.body, x: src.homeX + 46 * dir, duration: 90 * t, yoyo: true, ease: 'Quad.easeOut' });
      this.time.delayedCall(100 * t, () => this.basicMelee(to, dir, color, t));
    }
    this.time.delayedCall(140 * t, () => this.showHit(hit, false));
  }

  private animateSkill(sourceId: string, skillId: string, hits: Hit[], speed: number) {
    const src = this.views.get(sourceId);
    if (!src) return;
    const hero = src.unit.side === 'hero';
    this.tweens.add({ targets: src.sprite, scale: src.sprite.scale * 1.25, yoyo: true, duration: 160 / speed });
    const name = this.text(src.body.x, src.body.y - 130, t(`skill.${skillId}`), 30, hero ? '#ffe27a' : '#ff8a8a').setDepth(2000);
    this.tweens.add({ targets: name, y: name.y - 40, alpha: 0, delay: 500 / speed, duration: 500 / speed, onComplete: () => name.destroy() });
    const flash = this.add.circle(src.body.x, src.body.y, 30, hero ? 0xffe27a : 0xff6b6b, 0.6).setDepth(999);
    this.tweens.add({ targets: flash, scale: 4, alpha: 0, duration: 380 / speed, onComplete: () => flash.destroy() });
    if (hits.filter((h) => h.kind === 'damage').length > 1) this.cameras.main.shake(180, 0.006);
    // la chorégraphie de la compétence sur chaque cible touchée (une même image pour toute la compétence)
    const list = SKILL_FX[src.unit.element][src.unit.ranged ? 'ranged' : 'melee'];
    const fxName = list[hash(skillId) % list.length]!;
    const tm = 1 / speed;
    const from = this.chest(src);
    let impact = 200 * tm;
    // au corps à corps, le héros fonce sur sa première cible, frappe, puis revient à sa place
    const first = hits.find((h) => h.kind === 'damage' && this.views.get(h.target));
    if (!src.unit.ranged && first) {
      const tgt = this.views.get(first.target)!, dir = hero ? 1 : -1;
      this.tweens.add({ targets: src.body, x: tgt.body.x - dir * 85, y: tgt.body.y, duration: 120 * tm, ease: 'Quad.easeOut' });
      this.tweens.add({ targets: src.body, x: src.homeX, y: this.slotPos(src.unit).y, delay: 520 * tm, duration: 200 * tm, ease: 'Quad.easeInOut' });
    }
    const seen = new Set<string>();
    hits.forEach((h) => {
      if (h.kind !== 'damage' || seen.has(h.target)) return;
      const v = this.views.get(h.target);
      if (!v) return;
      const delay = (120 + seen.size * 70) * tm;
      seen.add(h.target);
      const at = this.skillFx.bind(this, fxName, from, this.chest(v), hero ? 1 : -1, tm);
      // l'impact (et les chiffres) arrive quand l'effet touche : on l'estime avant de lancer
      impact = Math.max(impact, delay + (TRAVEL[fxName] ?? 100) * tm);
      this.time.delayedCall(delay, at);
    });
    this.time.delayedCall(impact, () => hits.forEach((h) => this.showHit(h, true)));
  }

  private showHit(hit: Hit, big: boolean) {
    const v = this.views.get(hit.target);
    if (!v) return;
    if (hit.kind === 'damage') v.hp = Math.max(0, v.hp - hit.amount);
    else if (hit.kind === 'heal') v.hp = Math.min(v.unit.maxHp, v.hp + hit.amount);
    else if (hit.kind === 'revive') v.hp = v.unit.hp;
    // les images d'effets ne viennent qu'avec les compétences (big) ; le reste reste discret
    if (big) {
      const p = this.chest(v), dir = v.unit.side === 'hero' ? 1 : -1;
      if (hit.kind === 'status' && hit.status && STATUS_FX[hit.status]) this.fx(STATUS_FX[hit.status]!, p.x, p.y, { size: 0.8, dur: 600 });
      if (hit.kind === 'revive') this.skillFx('holyBeam', p, p, dir, 1);
      if (hit.kind === 'heal' && !hit.dot) this.skillFx('heal', p, p, dir, 1);
      if (hit.kind === 'shield') this.skillFx('goldShield', p, p, dir, 1);
    }
    if (hit.kind === 'miss' || hit.kind === 'status' || hit.kind === 'revive') {
      if (hit.kind === 'revive') this.tweens.add({ targets: v.body, alpha: 1, y: this.slotPos(v.unit).y, angle: 0, duration: 400 });
      const label = hit.kind === 'miss' ? t('fx.miss') : hit.kind === 'revive' ? '✚' : t(`st.${hit.status}`, { n: '' }).replace(/[+−-]\s*%/, '').trim();
      const color = hit.kind === 'miss' ? '#c8d0ff' : hit.kind === 'revive' ? '#5dff9a' : STATUS_COLOR[hit.status ?? 'stun'] ?? '#ffe27a';
      const n = this.text(v.body.x, v.body.y - 92, label, 22, color).setDepth(2000);
      this.tweens.add({ targets: n, y: n.y - 34, alpha: 0, duration: 800, onComplete: () => n.destroy() });
      return;
    }
    const x = v.body.x + Phaser.Math.Between(-18, 18);
    const y = v.body.y - 40;
    let color: string;
    let label = hit.amount.toLocaleString('fr-FR');
    if (hit.kind === 'heal') {
      color = '#5dff9a';
      label = `+${label}`;
    } else if (hit.kind === 'shield') {
      // Un bouclier se voit à son anneau bleu, sans chiffre (sinon la scène devient illisible).
      const ring = this.add.circle(v.body.x, v.body.y, 70).setStrokeStyle(5, 0x9fd8ff).setDepth(998);
      this.tweens.add({ targets: ring, scale: 1.3, alpha: 0, duration: 500, onComplete: () => ring.destroy() });
      return;
    } else {
      color = hit.crit ? '#ffe27a' : hit.advantage ? '#ffb15c' : v.unit.side === 'hero' ? '#ff9b9b' : '#ffffff';
      // touché : le dessin rougit un instant (un flash tout blanc effaçait les grands dessins)
      v.sprite.setTint(0xff9a9a);
      this.time.delayedCall(90, () => v.sprite.clearTint());
      if (hit.stun) {
        const star = this.text(v.body.x + 30, v.body.y - 70, '✦', 28, '#ffe27a').setDepth(2000);
        this.tweens.add({ targets: star, angle: 360, alpha: 0, duration: 900, onComplete: () => star.destroy() });
      }
    }
    if (hit.dot) color = hit.kind === 'heal' ? '#5dff9a' : STATUS_COLOR[hit.status ?? 'burn'] ?? color;
    const n = this.text(x, y, hit.crit ? `${label}!` : label, hit.dot ? 20 : (big ? 34 : 26) + (hit.crit ? 8 : 0), color).setDepth(2000);
    this.tweens.add({ targets: n, y: y - 60, alpha: 0, duration: 750, ease: 'Quad.easeOut', onComplete: () => n.destroy() });
  }

  protected banner(label: string, y = 300) {
    const b = this.text(W / 2, y, label, 56).setDepth(3000).setScale(0.5);
    this.tweens.add({ targets: b, scale: 1, duration: 250, ease: 'Back.easeOut' });
    this.tweens.add({ targets: b, alpha: 0, delay: 800, duration: 300, onComplete: () => b.destroy() });
  }
}
