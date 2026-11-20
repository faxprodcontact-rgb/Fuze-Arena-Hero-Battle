// Base commune des scènes de combat (Phaser) : décor, personnages, barres de vie, coups et chiffres.
// Le moteur (src/core/battle) calcule ; ces scènes animent ce qu'il raconte.
import Phaser from 'phaser';
import type { Battle } from '../core/battle/engine';
import { ENERGY_MAX, LEADER_SLOT, type BattleEvent, type Hit, type Slot, type Unit } from '../core/battle/types';
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
}

/** Taille des dessins Hailuo : pixels de l'écran par unité du repère du dessin (un héros mesure ~190 unités). */
const UNIT_PX = 0.64;
/** Les pieds sont un peu sous le centre du conteneur (comme les anciens dessins). */
const FEET = 47;

type FxName = keyof typeof ART_META.fx;
/** Largeur d'affichage de chaque effet (pixels) et point d'ancrage : centre, ou sol (le bas de l'effet aux pieds). */
const FX: Record<FxName, [number, 'c' | 'g']> = {
  slash: [150, 'c'], crossSlash: [165, 'c'], claw: [140, 'c'], impact: [120, 'c'], shockwave: [230, 'g'], pierce: [200, 'c'],
  fireball: [110, 'c'], explosion: [175, 'c'], flamePillar: [130, 'g'], fireSlash: [150, 'c'], meteor: [150, 'c'], emberBurst: [150, 'c'],
  waterBolt: [115, 'c'], splash: [165, 'g'], iceSpikes: [170, 'g'], frostBurst: [150, 'c'], tornado: [130, 'g'], windBlades: [140, 'c'],
  lightning: [110, 'g'], electricOrb: [80, 'c'], featherGust: [170, 'c'], sonicRing: [130, 'c'], rockSpikes: [170, 'g'], quake: [210, 'g'],
  poison: [140, 'c'], thornVines: [140, 'c'], leafStorm: [170, 'c'], boulder: [80, 'c'], heal: [130, 'c'], holyBeam: [120, 'g'],
  goldShield: [105, 'c'], darkOrb: [130, 'c'],
};
/** Coup au corps à corps, projectile et son impact, compétences : selon l'élément de celui qui frappe. */
const MELEE_FX: Record<Element, FxName> = { fire: 'fireSlash', wind: 'windBlades', water: 'slash', earth: 'claw' };
const SHOT_FX: Record<Element, FxName> = { fire: 'fireball', wind: 'electricOrb', water: 'waterBolt', earth: 'boulder' };
const SHOT_HIT_FX: Record<Element, FxName> = { fire: 'explosion', wind: 'impact', water: 'splash', earth: 'impact' };
const SKILL_FX: Record<Element, readonly FxName[]> = {
  fire: ['flamePillar', 'meteor', 'explosion'], water: ['iceSpikes', 'frostBurst', 'splash'],
  wind: ['lightning', 'tornado', 'featherGust'], earth: ['rockSpikes', 'quake', 'thornVines'],
};
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
    this.views.set(unit.id, { unit, body, sprite, bars, homeX: x, barY, barW });
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
      if (u.hp <= 0) continue;
      const w = v.barW;
      const y = v.barY;
      g.fillStyle(0x000000, 0.6);
      g.fillRoundedRect(-w / 2 - 2, y - 2, w + 4, 16, 5);
      g.fillStyle(u.side === 'hero' ? C.green : C.red);
      g.fillRoundedRect(-w / 2, y, w * (u.hp / u.maxHp), 12, 4);
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

  /** Un effet (image d'effet Hailuo) qui grossit un peu puis s'efface. `ground` = posé aux pieds. */
  protected fx(name: FxName, x: number, y: number, o: { size?: number; flip?: boolean; dur?: number; depth?: number } = {}) {
    const key = `fx-${name}`;
    if (!this.textures.exists(key)) return;
    const [size, anchor] = FX[name];
    const img = this.add.image(x, y, key).setOrigin(0.5, anchor === 'g' ? 0.95 : 0.5).setFlipX(!!o.flip).setDepth(o.depth ?? 1500);
    const k = (size * (o.size ?? 1)) / img.width;
    img.setScale(k * 0.7).setAlpha(0.95);
    const dur = o.dur ?? 420;
    this.tweens.add({ targets: img, scale: k, duration: dur * 0.35, ease: 'Back.easeOut' });
    this.tweens.add({ targets: img, alpha: 0, delay: dur * 0.5, duration: dur * 0.5, onComplete: () => img.destroy() });
  }

  /** Le centre du corps d'un combattant (là où les coups portent) et ses pieds. */
  private chest(v: View) {
    return { x: v.body.x, y: v.body.y + (FEET + v.barY) / 2 + 10, feet: v.body.y + FEET };
  }

  private animateAttack(sourceId: string, hit: Hit, speed: number) {
    const src = this.views.get(sourceId);
    const dst = this.views.get(hit.target);
    if (!src || !dst) return;
    const dir = src.unit.side === 'hero' ? 1 : -1;
    const el = src.unit.element;
    const to = this.chest(dst);
    if (src.unit.ranged) {
      const from = this.chest(src);
      const key = `fx-${SHOT_FX[el]}`;
      const shot = this.textures.exists(key)
        ? this.add.image(from.x + 30 * dir, from.y, key).setDisplaySize(FX[SHOT_FX[el]][0], (FX[SHOT_FX[el]][0] * this.textures.getFrame(key).height) / this.textures.getFrame(key).width)
        : this.add.circle(from.x + 30 * dir, from.y, 7, hex(ELEMENT_COLOR[el]));
      shot.setDepth(1000).setRotation(Math.atan2(to.y - from.y, to.x - from.x - 30 * dir));
      this.tweens.add({ targets: shot, x: to.x, y: to.y, duration: 220 / speed, onComplete: () => shot.destroy() });
      this.time.delayedCall(220 / speed, () => this.fx(SHOT_HIT_FX[el], to.x, el === 'water' ? to.feet : to.y, { size: 0.65, dur: 360 / speed }));
    } else {
      this.tweens.add({ targets: src.body, x: src.homeX + 46 * dir, duration: 90 / speed, yoyo: true, ease: 'Quad.easeOut' });
      this.time.delayedCall(110 / speed, () => {
        this.fx(hit.kind === 'damage' && hit.crit ? 'crossSlash' : MELEE_FX[el], to.x - 6 * dir, to.y, { flip: dir < 0, dur: 320 / speed });
        if (hit.kind === 'damage' && hit.crit) this.fx('impact', to.x, to.y, { size: 0.7, dur: 300 / speed });
      });
    }
    this.time.delayedCall(140 / speed, () => this.showHit(hit, false));
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
    // l'effet de la compétence sur chaque cible touchée (un même effet pour toute la compétence)
    const list = SKILL_FX[src.unit.element];
    const fxName = list[hash(skillId) % list.length]!;
    const seen = new Set<string>();
    hits.forEach((h, i) => {
      if (h.kind !== 'damage' || seen.has(h.target)) return;
      seen.add(h.target);
      const v = this.views.get(h.target);
      if (!v) return;
      const p = this.chest(v);
      this.time.delayedCall((140 + i * 40) / speed, () => this.fx(fxName, p.x, FX[fxName][1] === 'g' ? p.feet : p.y, { flip: !hero, dur: 560 / speed }));
    });
    this.time.delayedCall(200 / speed, () => hits.forEach((h) => this.showHit(h, true)));
  }

  private showHit(hit: Hit, big: boolean) {
    const v = this.views.get(hit.target);
    if (!v) return;
    if (hit.kind === 'status' && hit.status && STATUS_FX[hit.status]) this.fx(STATUS_FX[hit.status]!, v.body.x, this.chest(v).y, { size: 0.8, dur: 600 });
    if (hit.kind === 'revive') this.fx('holyBeam', v.body.x, v.body.y + FEET, { dur: 800 });
    if (hit.kind === 'heal' && !hit.dot) this.fx('heal', v.body.x, this.chest(v).y, { size: 0.85, dur: 600 });
    if (hit.kind === 'shield') this.fx('goldShield', v.body.x, this.chest(v).y, { dur: 600 });
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
