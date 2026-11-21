// Écran de combat : sert à tous les modes (campagne, tour, donjons, boss, arène, guilde).
// Les récompenses sont affichées ensuite par les menus.
import Phaser from 'phaser';
import { Battle } from '../core/battle/engine';
import { ENERGY_MAX, TICK_MS, type Slot, type Unit } from '../core/battle/types';
import { C, FightScene, W } from './fight-view';
import { t } from './i18n';
import { battleLook } from './look';
import { setAuto, setSpeed, type BattleRequest, type BattleResult } from './state/actions';
import { getState } from './state/store';

export const H = 1280;
const PORTRAIT_ORDER: Slot[] = [3, 4, 2, 0, 1];

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

export class BattleScene extends FightScene {
  private req!: BattleRequest;
  private done!: (r: BattleResult) => void;
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
    this.bigBoss = !!data.request.damageMode;
    this.look = battleLook(data.request.kind, data.request.title, data.request.dungeon?.kind);
  }

  protected preloadUnits() {
    return [...this.req.heroes, ...this.req.waves.flat()];
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
    this.battle = new Battle({ heroes: this.req.heroes, waves: this.req.waves, seed: this.req.seed, auto: getState().auto });
    this.drawArena(780);
    this.add.rectangle(W / 2, 780 + (H - 780) / 2, W, H - 780, 0x14162b).setDepth(-5);

    this.text(W / 2, 60, `${t(`mode.${this.req.kind}`)} ${this.titleSuffix()}`, 32, '#ffe27a').setDepth(3000);
    this.waveLabel = this.text(W / 2, 104, '', 24, '#a9b0d6').setDepth(3000);
    this.updateWaveLabel();
    if (this.req.damageMode) this.damageLabel = this.text(W / 2, 160, '0', 44, '#ffe27a').setDepth(3000);
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
      const card = `c-${this.charId(unit)}`;
      const img = this.textures.exists(card) ? this.add.image(x, y, card).setDisplaySize(108, 108) : this.add.image(x, y + 4, this.texture(unit)).setScale(0.78);
      const ring = this.add.graphics();
      this.tweens.add({ targets: glow, scale: 1.12, alpha: 0.6, yoyo: true, repeat: -1, duration: 380 });
      frame.setInteractive({ useHandCursor: true }).on('pointerdown', () => {
        if (this.battle.requestSkill(unit.id)) this.tweens.add({ targets: img, scale: img.scale * 0.9, yoyo: true, duration: 90 });
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
    this.advance(delta, getState().speed);
    this.syncUnits();
    this.syncPortraits();
    if (this.damageLabel) this.damageLabel.setText(this.damage().toLocaleString('fr-FR'));
  }

  private syncPortraits() {
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

  private damage(): number {
    return this.battle.enemies.reduce((sum, e) => sum + (e.maxHp - e.hp), 0);
  }

  protected onWave(index: number) {
    this.updateWaveLabel();
    this.banner(`${t('battle.wave')} ${index + 1}`, 165);
  }

  protected onEnd() {
    this.time.delayedCall(700, () => this.finish());
  }

  private finish() {
    if (this.ended) return;
    this.ended = true;
    this.done({
      win: this.battle.over && this.battle.win,
      damage: this.damage(),
      alive: this.battle.heroes.filter((h) => h.hp > 0).length / Math.max(1, this.battle.heroes.length),
      inputs: this.battle.inputs,
    });
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
