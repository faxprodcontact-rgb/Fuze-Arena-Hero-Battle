// Base commune des scènes de combat (Phaser) : décor, personnages, barres de vie, coups et chiffres.
// Le moteur (src/core/battle) calcule ; ces scènes animent ce qu'il raconte.
import Phaser from 'phaser';
import type { Battle } from '../core/battle/engine';
import { ENERGY_MAX, LEADER_SLOT, type BattleEvent, type Hit, type Slot, type Unit } from '../core/battle/types';
import { HEROES } from '../core/data/heroes';
import { ELEMENT_COLOR, heroCanvas, monsterCanvas } from './art';
import { t } from './i18n';

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
}

export abstract class FightScene extends Phaser.Scene {
  protected battle!: Battle;
  protected views = new Map<string, View>();
  /** Haut du sol : tout le terrain se place à partir de là. */
  protected groundTop = 380;
  /** Les boss des combats « au score » sont dessinés plus gros. */
  protected bigBoss = false;
  /** Resserre le terrain vers le centre (écran d'accueil, plus étroit). */
  protected xSquash = 1;

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

  /** Ciel, sol et cercle d'arène. */
  protected drawArena(bottom: number) {
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
    const scale = unit.boss ? (this.bigBoss ? 2 : 1.45) : 0.95;
    const body = this.add.container(enter ? x + 320 : x, unit.boss && this.bigBoss ? y - 30 : y).setDepth(y);
    const shadow = this.add.ellipse(0, 50 * scale, 90 * scale, 22, 0x000000, 0.3);
    const sprite = this.add.image(0, 0, this.texture(unit)).setScale(scale).setFlipX(!hero);
    const bars = this.add.graphics();
    body.add([shadow, sprite, bars]);
    if (hero && unit.slot === LEADER_SLOT && unit.talent) body.add(this.text(0, -66 * scale - 30, '♛', 26, '#ffe27a'));
    this.views.set(unit.id, { unit, body, sprite, bars, homeX: x });
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
      const w = u.boss ? 130 : 86;
      const y = u.boss ? -100 : -72;
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

  private animateAttack(sourceId: string, hit: Hit, speed: number) {
    const src = this.views.get(sourceId);
    const dst = this.views.get(hit.target);
    if (!src || !dst) return;
    const dir = src.unit.side === 'hero' ? 1 : -1;
    if (src.unit.ranged) {
      const shot = this.add.circle(src.body.x + 30 * dir, src.body.y - 10, 7, hex(ELEMENT_COLOR[src.unit.element])).setDepth(1000);
      this.tweens.add({ targets: shot, x: dst.body.x, y: dst.body.y - 10, duration: 220 / speed, onComplete: () => shot.destroy() });
    } else {
      this.tweens.add({ targets: src.body, x: src.homeX + 46 * dir, duration: 90 / speed, yoyo: true, ease: 'Quad.easeOut' });
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
    this.time.delayedCall(200 / speed, () => hits.forEach((h) => this.showHit(h, true)));
  }

  private showHit(hit: Hit, big: boolean) {
    const v = this.views.get(hit.target);
    if (!v) return;
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
      v.sprite.setTintFill(0xffffff);
      this.time.delayedCall(70, () => v.sprite.clearTint());
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
