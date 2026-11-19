// Combat : le moteur (src/core/battle) calcule, cet écran anime ce qu'il raconte.
import Phaser from 'phaser';
import { Battle } from '../../core/battle/engine';
import { ENERGY_MAX, LEADER_SLOT, TICK_MS, type BattleEvent, type Hit, type Slot, type Unit } from '../../core/battle/types';
import {
  HERO_UNLOCKS,
  PROTO_STAGES,
  heroUnit,
  protoGold,
  protoSlots,
  stageWaves,
} from '../../core/data/prototype';
import { ELEMENT_COLOR, UI } from '../art';
import { t } from '../i18n';
import { loadSave, writeSave } from '../save';
import { H, W, button, panel, text } from '../ui';

const HERO_X: Record<Slot, number> = { 3: 110, 4: 110, 2: 215, 0: 315, 1: 315 };
const ENEMY_X: Record<Slot, number> = { 0: 405, 1: 405, 2: 505, 3: 610, 4: 610 };
const ROW_Y: Record<Slot, number> = { 0: 470, 3: 470, 2: 560, 1: 650, 4: 650 };
/** Ordre des portraits, de gauche à droite comme sur le terrain : l'arrière d'abord. */
const PORTRAIT_ORDER: Slot[] = [3, 4, 2, 0, 1];

interface UnitView {
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

export class BattleScene extends Phaser.Scene {
  private stage = 1;
  private battle!: Battle;
  private views = new Map<string, UnitView>();
  private portraits: Portrait[] = [];
  private acc = 0;
  private ended = false;
  private waveLabel!: Phaser.GameObjects.Text;

  constructor() {
    super('battle');
  }

  init(data: { stage: number }) {
    this.stage = data.stage;
    this.views.clear();
    this.portraits = [];
    this.acc = 0;
    this.ended = false;
  }

  create() {
    const save = loadSave();
    this.battle = new Battle({
      heroes: save.formation.map(([id, slot]) => heroUnit(id, save.levels[id] ?? 1, slot)),
      waves: stageWaves(this.stage),
      seed: (Date.now() ^ (this.stage * 7919)) >>> 0,
      auto: save.auto,
    });

    this.drawArena();
    for (const u of this.battle.heroes) this.addView(u);
    for (const u of this.battle.enemies) this.addView(u);
    this.drawHud();
  }

  // ---------- Décor et interface ----------

  private drawArena() {
    const g = this.add.graphics();
    g.fillGradientStyle(0x2b3a78, 0x2b3a78, 0x6b5ca8, 0x6b5ca8, 1);
    g.fillRect(0, 0, W, 420);
    g.fillGradientStyle(0x3d6b4a, 0x3d6b4a, 0x274a34, 0x274a34, 1);
    g.fillRect(0, 380, W, 400);
    g.fillStyle(0xffffff, 0.06);
    g.fillEllipse(W / 2, 560, 760, 330);
    g.fillStyle(UI.bg);
    g.fillRect(0, 780, W, H - 780);

    text(this, W / 2, 60, `${t('stage')} ${this.stage}`, 34, '#ffe27a');
    this.waveLabel = text(this, W / 2, 105, '', 26, UI.textDim);
    this.updateWaveLabel();
    button(this, 90, 60, 150, 60, t('quit'), UI.panelLight, () => this.scene.start('home'), 22);
  }

  private updateWaveLabel() {
    this.waveLabel.setText(`${t('wave')} ${this.battle.wave + 1} / ${this.battle.waveCount}`);
  }

  private addView(unit: Unit, enterFromRight = false) {
    const hero = unit.side === 'hero';
    const x = hero ? HERO_X[unit.slot] : ENEMY_X[unit.slot];
    const y = ROW_Y[unit.slot];
    const scale = unit.boss ? 1.45 : 0.95;
    const body = this.add.container(enterFromRight ? x + 320 : x, y).setDepth(y);
    const shadow = this.add.ellipse(0, 52 * scale * 0.9, 90 * scale, 22, 0x000000, 0.3);
    const sprite = this.add.image(0, 0, `unit-${unit.defId}`).setScale(scale).setFlipX(!hero);
    const bars = this.add.graphics();
    body.add([shadow, sprite, bars]);
    if (hero && unit.slot === LEADER_SLOT) body.add(text(this, 0, -66 * scale - 30, '♛', 26, '#ffe27a'));
    const view: UnitView = { unit, body, sprite, bars, homeX: x };
    this.views.set(unit.id, view);
    if (enterFromRight) this.tweens.add({ targets: body, x, duration: 450, ease: 'Back.easeOut' });
  }

  private drawHud() {
    panel(this, W / 2, 1010, 700, 220, UI.panel, 1);
    PORTRAIT_ORDER.forEach((slot, i) => {
      const unit = this.battle.heroes.find((h) => h.slot === slot);
      if (!unit) return;
      const x = 90 + i * 135;
      const y = 1000;
      const glow = this.add.circle(x, y, 66, UI.energy, 0.35).setVisible(false);
      const frame = this.add.circle(x, y, 56, 0x14162b).setStrokeStyle(4, 0x3a4180);
      const img = this.add.image(x, y + 4, `unit-${unit.defId}`).setScale(0.78);
      const ring = this.add.graphics();
      this.tweens.add({ targets: glow, scale: 1.12, alpha: 0.6, yoyo: true, repeat: -1, duration: 380 });
      frame.setInteractive({ useHandCursor: true }).on('pointerdown', () => {
        if (this.battle.requestSkill(unit.id)) this.tweens.add({ targets: img, scale: 0.9, yoyo: true, duration: 90 });
      });
      this.portraits.push({ unit, x, ring, glow, img });
    });

    this.drawAutoButton();
    const speed = button(this, 530, 1190, 260, 80, `×${loadSave().speed}`, UI.blue, () => {
      const next = ((loadSave().speed % 3) + 1) as 1 | 2 | 3;
      writeSave({ speed: next });
      speed.label.setText(`×${next}`);
    }, 32);
  }

  /** Bouton AUTO : vert quand il est actif. */
  private drawAutoButton() {
    const on = loadSave().auto;
    const auto = button(this, 190, 1190, 260, 80, t('auto'), on ? UI.green : UI.panelLight, () => {
      writeSave({ auto: !on });
      this.battle.setAuto(!on);
      auto.destroy();
      this.drawAutoButton();
    }, 32);
  }

  // ---------- Boucle ----------

  update(_time: number, delta: number) {
    if (this.ended) return;
    this.acc += delta * loadSave().speed;
    while (this.acc >= TICK_MS && !this.battle.over) {
      this.acc -= TICK_MS;
      this.handle(this.battle.step());
    }
    this.syncBars();
  }

  private syncBars() {
    for (const view of this.views.values()) {
      const u = view.unit;
      const g = view.bars;
      g.clear();
      if (u.hp <= 0) continue;
      const w = u.boss ? 130 : 86;
      const y = (u.boss ? -100 : -72);
      g.fillStyle(0x000000, 0.6);
      g.fillRoundedRect(-w / 2 - 2, y - 2, w + 4, 16, 5);
      g.fillStyle(u.side === 'hero' ? UI.green : UI.red);
      g.fillRoundedRect(-w / 2, y, w * (u.hp / u.maxHp), 12, 4);
      if (u.shield > 0) {
        g.fillStyle(0x9fd8ff, 0.85);
        g.fillRoundedRect(-w / 2, y, Math.min(w, w * (u.shield / u.maxHp)), 6, 3);
      }
      g.fillStyle(UI.energy);
      g.fillRect(-w / 2, y + 15, w * (u.energy / ENERGY_MAX), 4);
      view.sprite.setAngle(u.stun > 0 ? Math.sin(this.time.now / 60) * 8 : 0);
    }
    for (const p of this.portraits) {
      const u = p.unit;
      const ready = u.hp > 0 && u.energy >= ENERGY_MAX;
      p.glow.setVisible(ready && !this.battle.auto);
      p.img.setAlpha(u.hp > 0 ? 1 : 0.3);
      p.ring.clear();
      if (u.hp <= 0) continue;
      p.ring.lineStyle(8, ready ? 0xffe27a : UI.energy);
      p.ring.beginPath();
      p.ring.arc(p.x, 1000, 60, -Math.PI / 2, -Math.PI / 2 + Math.PI * 2 * (u.energy / ENERGY_MAX));
      p.ring.strokePath();
      p.ring.fillStyle(0x000000, 0.6);
      p.ring.fillRoundedRect(p.x - 52, 1068, 104, 12, 4);
      p.ring.fillStyle(UI.green);
      p.ring.fillRoundedRect(p.x - 52, 1068, 104 * (u.hp / u.maxHp), 12, 4);
    }
  }

  // ---------- Événements du moteur ----------

  private handle(events: BattleEvent[]) {
    const speed = loadSave().speed;
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
          for (const [id, v] of this.views) if (v.unit.side === 'enemy') {
            v.body.destroy();
            this.views.delete(id);
          }
          for (const u of e.units) this.addView(u, true);
          this.updateWaveLabel();
          this.banner(`${t('wave')} ${e.index + 1}`, '#ffffff');
          break;
        case 'end':
          this.ended = true;
          this.time.delayedCall(700, () => this.showResult(e.win));
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
      const shot = this.add.image(src.body.x + 30 * dir, src.body.y - 10, 'dot')
        .setTint(ELEMENT_COLOR[src.unit.element]).setScale(0.9).setDepth(1000);
      this.tweens.add({
        targets: shot, x: dst.body.x, y: dst.body.y - 10, duration: 220 / speed,
        onComplete: () => shot.destroy(),
      });
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
    const name = text(this, src.body.x, src.body.y - 130, t(`skill.${skillId}`), 30, hero ? '#ffe27a' : '#ff8a8a').setDepth(2000);
    this.tweens.add({ targets: name, y: name.y - 40, alpha: 0, delay: 500 / speed, duration: 500 / speed, onComplete: () => name.destroy() });
    const flash = this.add.circle(src.body.x, src.body.y, 30, hero ? 0xffe27a : 0xff6b6b, 0.6).setDepth(999);
    this.tweens.add({ targets: flash, scale: 4, alpha: 0, duration: 380 / speed, onComplete: () => flash.destroy() });
    if (hits.filter((h) => h.kind === 'damage').length > 1) this.cameras.main.shake(180, 0.006);
    this.time.delayedCall(200 / speed, () => hits.forEach((h) => this.showHit(h, true)));
  }

  private showHit(hit: Hit, big: boolean) {
    const view = this.views.get(hit.target);
    if (!view) return;
    const x = view.body.x + Phaser.Math.Between(-18, 18);
    const y = view.body.y - 40;
    let color = '#ffffff';
    let label = String(hit.amount);
    if (hit.kind === 'heal') {
      color = '#5dff9a';
      label = `+${hit.amount}`;
    } else if (hit.kind === 'shield') {
      color = '#9fd8ff';
      const ring = this.add.circle(view.body.x, view.body.y, 70).setStrokeStyle(5, 0x9fd8ff).setDepth(998);
      this.tweens.add({ targets: ring, scale: 1.3, alpha: 0, duration: 500, onComplete: () => ring.destroy() });
    } else {
      color = hit.crit ? '#ffe27a' : hit.advantage ? '#ffb15c' : view.unit.side === 'hero' ? '#ff9b9b' : '#ffffff';
      view.sprite.setTintFill(0xffffff);
      this.time.delayedCall(70, () => view.sprite.clearTint());
      if (hit.stun) {
        const zz = text(this, view.body.x + 30, view.body.y - 70, '✦', 28, '#ffe27a').setDepth(2000);
        this.tweens.add({ targets: zz, angle: 360, alpha: 0, duration: 900, onComplete: () => zz.destroy() });
      }
    }
    const size = (big ? 34 : 26) + (hit.crit ? 8 : 0);
    const n = text(this, x, y, hit.crit ? `${label}!` : label, size, color).setDepth(2000);
    this.tweens.add({ targets: n, y: y - 60, alpha: 0, duration: 750, ease: 'Quad.easeOut', onComplete: () => n.destroy() });
  }

  private animateDeath(id: string) {
    const view = this.views.get(id);
    if (!view) return;
    this.tweens.add({ targets: view.body, alpha: 0, y: view.body.y + 20, angle: view.unit.side === 'hero' ? -20 : 20, duration: 450 });
  }

  private banner(label: string, color: string) {
    const b = text(this, W / 2, 300, label, 56, color).setDepth(3000).setScale(0.5);
    this.tweens.add({ targets: b, scale: 1, duration: 250, ease: 'Back.easeOut' });
    this.tweens.add({ targets: b, alpha: 0, delay: 800, duration: 300, onComplete: () => b.destroy() });
  }

  // ---------- Résultat ----------

  private showResult(win: boolean) {
    const save = loadSave();
    const first = win && this.stage === save.cleared + 1;
    const gold = protoGold(this.stage, first ? 'first' : win ? 'replay' : 'loss');
    const unlocks: { label: string; image?: string }[] = [];
    const change: Parameters<typeof writeSave>[0] = { gold: save.gold + gold };
    if (first) {
      change.cleared = this.stage;
      const heroId = HERO_UNLOCKS[this.stage];
      if (heroId && !save.owned.includes(heroId)) {
        const lowest = Math.min(...Object.values(save.levels));
        change.owned = [...save.owned, heroId];
        change.levels = { ...save.levels, [heroId]: Math.max(1, lowest - 2) };
        unlocks.push({ label: `${t('newHero')} : ${t(`hero.${heroId}`)}`, image: `unit-${heroId}` });
      }
      if (protoSlots(this.stage) > protoSlots(save.cleared)) unlocks.push({ label: `${t('newSlot')} : ${protoSlots(this.stage)} / 5` });
      if (unlocks.length) change.unseen = true;
    }
    writeSave(change);

    const layer = this.add.container(0, 0).setDepth(5000);
    layer.add(this.add.rectangle(W / 2, H / 2, W, H, 0x000000, 0.65).setInteractive());
    layer.add(panel(this, W / 2, 620, 600, 640, UI.panel));
    const title = text(this, W / 2, 380, win ? t('victory') : t('defeat'), 64, win ? '#ffe27a' : '#ff8a8a');
    layer.add(title);
    this.tweens.add({ targets: title, scale: { from: 0.4, to: 1 }, duration: 350, ease: 'Back.easeOut' });
    layer.add(this.add.circle(W / 2 - 70, 480, 22, UI.gold).setStrokeStyle(3, 0xb8860b));
    layer.add(text(this, W / 2 + 20, 480, `+${gold}`, 40, '#ffe27a'));
    unlocks.forEach((u, i) => {
      const y = 580 + i * 110;
      if (u.image) layer.add(this.add.image(W / 2 - 200, y, u.image).setScale(0.7));
      layer.add(text(this, W / 2 + 30, y, u.label, 28));
    });

    const last = PROTO_STAGES.length;
    if (win) {
      if (this.stage < last) layer.add(button(this, W / 2, 800, 380, 96, t('next'), UI.green, () => this.scene.restart({ stage: this.stage + 1 }), 36));
      layer.add(button(this, W / 2, 900, 300, 70, t('home'), UI.panelLight, () => this.scene.start('home'), 28));
    } else {
      layer.add(button(this, W / 2, 680, 380, 90, t('retry'), UI.green, () => this.scene.restart({ stage: this.stage }), 34));
      layer.add(button(this, W / 2, 790, 380, 90, t('team'), UI.blue, () => this.scene.start('team'), 34));
      layer.add(button(this, W / 2, 890, 300, 70, t('home'), UI.panelLight, () => this.scene.start('home'), 28));
    }
  }
}
