// Écran de combat (Phaser) : le moteur de src/core/battle calcule, cette scène anime ce qu'il raconte.
// Il sert à tous les modes ; les récompenses sont affichées ensuite par les menus.
import Phaser from 'phaser';
import { Battle } from '../core/battle/engine';
import { ENERGY_MAX, LEADER_SLOT, TICK_MS, type BattleEvent, type Hit, type Slot, type Unit } from '../core/battle/types';
import { HEROES } from '../core/data/heroes';
import { heroCanvas, monsterCanvas, ELEMENT_COLOR } from './art';
import { t } from './i18n';
import { setAuto, setSpeed, type BattleRequest, type BattleResult } from './state/actions';
import { getState } from './state/store';

export const W = 720;
export const H = 1280;
const FONT = '"Trebuchet MS", "Segoe UI", Roboto, sans-serif';

const HERO_X: Record<Slot, number> = { 3: 110, 4: 110, 2: 215, 0: 315, 1: 315 };
const ENEMY_X: Record<Slot, number> = { 0: 405, 1: 405, 2: 505, 3: 610, 4: 610 };
const ROW_Y: Record<Slot, number> = { 0: 470, 3: 470, 2: 560, 1: 650, 4: 650 };
const PORTRAIT_ORDER: Slot[] = [3, 4, 2, 0, 1];
const C = { panel: 0x1f2340, panelLight: 0x2c3260, green: 0x3ccf7a, red: 0xe5484d, blue: 0x4c8dff, energy: 0x4fd1ff, gold: 0xffc94a };

function hex(color: string): number {
  return Number.parseInt(color.slice(1), 16);
}

interface View {
  unit: Unit;
  body: Phaser.GameObjects.Container;
  sprite: Phaser.GameObjects.Image;
  bars: Phaser.GameObjects.Graphics;
  homeX: number;
}

interface Portrait {
  unit: Unit;
  x: number;
  ring: Phaser.GameObjects.Graphics;
  glow: Phaser.GameObjects.Arc;
  img: Phaser.GameObjects.Image;
}

export interface BattleSceneData {
  request: BattleRequest;
  done: (result: BattleResult) => void;
}

export class BattleScene extends Phaser.Scene {
  private req!: BattleRequest;
  private done!: (r: BattleResult) => void;
  private battle!: Battle;
  private views = new Map<string, View>();
  private portraits: Portrait[] = [];
  private acc = 0;
  private ended = false;
  private waveLabel!: Phaser.GameObjects.Text;
  private damageLabel?: Phaser.GameObjects.Text;

  constructor() {
    super('battle');
  }

  init(data: BattleSceneData) {
    this.req = data.request;
    this.done = data.done;
    this.views.clear();
    this.portraits = [];
    this.acc = 0;
    this.ended = false;
  }

  private text(x: number, y: number, value: string, size = 28, color = '#ffffff') {
    return this.add
      .text(x, y, value, { fontFamily: FONT, fontSize: `${size}px`, color, fontStyle: 'bold', align: 'center' })
      .setOrigin(0.5)
      .setShadow(0, 2, '#000000', 3, false, true);
  }

  /** Les adversaires d'arène sont des héros : on choisit le dessin selon ce qu'est le combattant, pas son camp. */
  private texture(u: { defId: string; element: string }): string {
    const isHero = HEROES.some((h) => h.id === u.defId);
    const key = isHero ? `h-${u.defId}` : `m-${u.defId}-${u.element}`;
    if (!this.textures.exists(key)) {
      this.textures.addCanvas(key, isHero ? heroCanvas(u.defId) : monsterCanvas(u.defId, u.element as never));
    }
    return key;
  }

  private button(x: number, y: number, w: number, h: number, label: string, color: number, onClick: () => void) {
    const c = this.add.container(x, y).setDepth(4000);
    const g = this.add.graphics();
    g.fillStyle(0x000000, 0.35);
    g.fillRoundedRect(-w / 2, -h / 2 + 5, w, h, 16);
    g.fillStyle(color);
    g.fillRoundedRect(-w / 2, -h / 2, w, h, 16);
    g.fillStyle(0xffffff, 0.16);
    g.fillRoundedRect(-w / 2 + 6, -h / 2 + 5, w - 12, h * 0.38, 10);
    const label_ = this.text(0, 0, label, 30);
    c.add([g, label_]);
    c.setSize(w, h).setInteractive({ useHandCursor: true });
    c.on('pointerdown', () => c.setScale(0.95));
    c.on('pointerout', () => c.setScale(1));
    c.on('pointerup', () => {
      c.setScale(1);
      onClick();
    });
    return { c, label: label_ };
  }

  create() {
    const s = getState();
    this.battle = new Battle({ heroes: this.req.heroes, waves: this.req.waves, seed: this.req.seed, auto: s.auto });

    const g = this.add.graphics();
    g.fillGradientStyle(0x2b3a78, 0x2b3a78, 0x6b5ca8, 0x6b5ca8, 1);
    g.fillRect(0, 0, W, 420);
    g.fillGradientStyle(0x3d6b4a, 0x3d6b4a, 0x274a34, 0x274a34, 1);
    g.fillRect(0, 380, W, 400);
    g.fillStyle(0xffffff, 0.06);
    g.fillEllipse(W / 2, 560, 760, 330);
    g.fillStyle(0x14162b);
    g.fillRect(0, 780, W, H - 780);

    this.text(W / 2, 60, `${t(`mode.${this.req.kind}`)} ${this.titleSuffix()}`, 32, '#ffe27a');
    this.waveLabel = this.text(W / 2, 104, '', 24, '#a9b0d6');
    this.updateWaveLabel();
    if (this.req.damageMode) this.damageLabel = this.text(W / 2, 190, '0', 44, '#ffe27a');
    this.button(90, 60, 150, 60, t('battle.quit'), C.panelLight, () => this.finish());

    for (const u of this.battle.heroes) this.addView(u);
    for (const u of this.battle.enemies) this.addView(u);
    this.drawHud();
  }

  private titleSuffix(): string {
    if (this.req.kind === 'dailyBoss' || this.req.kind === 'guildBoss') return `· ${t(`monster.${this.req.title}`)}`;
    return this.req.title;
  }

  private updateWaveLabel() {
    this.waveLabel.setText(this.battle.waveCount > 1 ? `${t('battle.wave')} ${this.battle.wave + 1} / ${this.battle.waveCount}` : '');
  }

  private addView(unit: Unit, enter = false) {
    const hero = unit.side === 'hero';
    const x = hero ? HERO_X[unit.slot] : ENEMY_X[unit.slot];
    const y = ROW_Y[unit.slot];
    const scale = unit.boss ? (this.req.damageMode ? 2 : 1.45) : 0.95;
    const body = this.add.container(enter ? x + 320 : x, unit.boss && this.req.damageMode ? y - 30 : y).setDepth(y);
    const shadow = this.add.ellipse(0, 50 * scale, 90 * scale, 22, 0x000000, 0.3);
    const sprite = this.add.image(0, 0, this.texture(unit)).setScale(scale).setFlipX(!hero);
    const bars = this.add.graphics();
    body.add([shadow, sprite, bars]);
    if (hero && unit.slot === LEADER_SLOT) body.add(this.text(0, -66 * scale - 30, '♛', 26, '#ffe27a'));
    this.views.set(unit.id, { unit, body, sprite, bars, homeX: x });
    if (enter) this.tweens.add({ targets: body, x, duration: 450, ease: 'Back.easeOut' });
  }

  private drawHud() {
    const g = this.add.graphics();
    g.fillStyle(C.panel);
    g.fillRoundedRect(10, 900, 700, 220, 22);
    PORTRAIT_ORDER.forEach((slot, i) => {
      const unit = this.battle.heroes.find((h) => h.slot === slot);
      if (!unit) return;
      const x = 90 + i * 135;
      const y = 1000;
      const glow = this.add.circle(x, y, 66, C.energy, 0.35).setVisible(false);
      const frame = this.add.circle(x, y, 56, 0x14162b).setStrokeStyle(4, 0x3a4180);
      const img = this.add.image(x, y + 4, this.texture(unit)).setScale(0.78);
      const ring = this.add.graphics();
      this.tweens.add({ targets: glow, scale: 1.12, alpha: 0.6, yoyo: true, repeat: -1, duration: 380 });
      frame.setInteractive({ useHandCursor: true }).on('pointerdown', () => {
        if (this.battle.requestSkill(unit.id)) this.tweens.add({ targets: img, scale: 0.9, yoyo: true, duration: 90 });
      });
      this.portraits.push({ unit, x, ring, glow, img });
    });
    this.drawAuto();
    const speed = this.button(530, 1190, 260, 80, `×${getState().speed}`, C.blue, () => {
      const next = ((getState().speed % 3) + 1) as 1 | 2 | 3;
      setSpeed(next);
      speed.label.setText(`×${next}`);
    });
  }

  private drawAuto() {
    const on = getState().auto;
    const b = this.button(190, 1190, 260, 80, t('battle.auto'), on ? C.green : C.panelLight, () => {
      setAuto(!on);
      this.battle.setAuto(!on);
      b.c.destroy();
      this.drawAuto();
    });
  }

  update(_time: number, delta: number) {
    if (this.ended) return;
    this.acc += delta * getState().speed;
    while (this.acc >= TICK_MS && !this.battle.over) {
      this.acc -= TICK_MS;
      this.handle(this.battle.step());
    }
    this.syncBars();
    if (this.damageLabel) this.damageLabel.setText(this.damage().toLocaleString('fr-FR'));
  }

  private damage(): number {
    return this.battle.enemies.reduce((sum, e) => sum + (e.maxHp - e.hp), 0);
  }

  private syncBars() {
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
    for (const p of this.portraits) {
      const u = p.unit;
      const ready = u.hp > 0 && u.energy >= ENERGY_MAX;
      p.glow.setVisible(ready && !this.battle.auto);
      p.img.setAlpha(u.hp > 0 ? 1 : 0.3);
      p.ring.clear();
      if (u.hp <= 0) continue;
      p.ring.lineStyle(8, ready ? 0xffe27a : C.energy);
      p.ring.beginPath();
      p.ring.arc(p.x, 1000, 60, -Math.PI / 2, -Math.PI / 2 + Math.PI * 2 * (u.energy / ENERGY_MAX));
      p.ring.strokePath();
      p.ring.fillStyle(0x000000, 0.6);
      p.ring.fillRoundedRect(p.x - 52, 1068, 104, 12, 4);
      p.ring.fillStyle(C.green);
      p.ring.fillRoundedRect(p.x - 52, 1068, 104 * (u.hp / u.maxHp), 12, 4);
    }
  }

  private handle(events: BattleEvent[]) {
    const speed = getState().speed;
    for (const e of events) {
      switch (e.type) {
        case 'attack':
          this.animateAttack(e.source, e.hit, speed);
          break;
        case 'skill':
          this.animateSkill(e.source, e.skill.id, e.hits, speed);
          break;
        case 'death':
          this.animateDeath(e.unit);
          break;
        case 'wave':
          for (const [id, v] of this.views) {
            if (v.unit.side === 'enemy') {
              v.body.destroy();
              this.views.delete(id);
            }
          }
          for (const u of e.units) this.addView(u, true);
          this.updateWaveLabel();
          this.banner(`${t('battle.wave')} ${e.index + 1}`);
          break;
        case 'end':
          this.time.delayedCall(700, () => this.finish());
          break;
      }
    }
  }

  private finish() {
    if (this.ended) return;
    this.ended = true;
    this.done({ win: this.battle.over && this.battle.win, damage: this.damage(), inputs: this.battle.inputs });
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
    const x = v.body.x + Phaser.Math.Between(-18, 18);
    const y = v.body.y - 40;
    let color: string;
    let label = hit.amount.toLocaleString('fr-FR');
    if (hit.kind === 'heal') {
      color = '#5dff9a';
      label = `+${label}`;
    } else if (hit.kind === 'shield') {
      color = '#9fd8ff';
      const ring = this.add.circle(v.body.x, v.body.y, 70).setStrokeStyle(5, 0x9fd8ff).setDepth(998);
      this.tweens.add({ targets: ring, scale: 1.3, alpha: 0, duration: 500, onComplete: () => ring.destroy() });
    } else {
      color = hit.crit ? '#ffe27a' : hit.advantage ? '#ffb15c' : v.unit.side === 'hero' ? '#ff9b9b' : '#ffffff';
      v.sprite.setTintFill(0xffffff);
      this.time.delayedCall(70, () => v.sprite.clearTint());
      if (hit.stun) {
        const star = this.text(v.body.x + 30, v.body.y - 70, '✦', 28, '#ffe27a').setDepth(2000);
        this.tweens.add({ targets: star, angle: 360, alpha: 0, duration: 900, onComplete: () => star.destroy() });
      }
    }
    const n = this.text(x, y, hit.crit ? `${label}!` : label, (big ? 34 : 26) + (hit.crit ? 8 : 0), color).setDepth(2000);
    this.tweens.add({ targets: n, y: y - 60, alpha: 0, duration: 750, ease: 'Quad.easeOut', onComplete: () => n.destroy() });
  }

  private animateDeath(id: string) {
    const v = this.views.get(id);
    if (!v) return;
    this.tweens.add({ targets: v.body, alpha: 0, y: v.body.y + 20, angle: v.unit.side === 'hero' ? -20 : 20, duration: 450 });
  }

  private banner(label: string) {
    const b = this.text(W / 2, 300, label, 56).setDepth(3000).setScale(0.5);
    this.tweens.add({ targets: b, scale: 1, duration: 250, ease: 'Back.easeOut' });
    this.tweens.add({ targets: b, alpha: 0, delay: 800, duration: 300, onComplete: () => b.destroy() });
  }
}

/** Lance un combat dans le cadre donné ; `done` reçoit le résultat, puis le combat se ferme. */
export function runBattle(parent: HTMLElement, request: BattleRequest, done: (r: BattleResult) => void): () => void {
  const game = new Phaser.Game({
    type: Phaser.AUTO,
    parent,
    width: W,
    height: H,
    backgroundColor: '#14162b',
    scale: { mode: Phaser.Scale.FIT, autoCenter: Phaser.Scale.CENTER_BOTH },
    scene: [],
  });
  game.scene.add('battle', BattleScene, true, {
    request,
    done: (r: BattleResult) => {
      done(r);
      setTimeout(() => game.destroy(true), 0);
    },
  } satisfies BattleSceneData);
  return () => game.destroy(true);
}
