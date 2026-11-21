// Écran de combat : sert à tous les modes (campagne, tour, donjons, boss, arène, guilde).
// Les récompenses sont affichées ensuite par les menus.
import Phaser from 'phaser';
import { Battle } from '../core/battle/engine';
import { ENERGY_MAX, TICK_MS, type Slot, type Unit } from '../core/battle/types';
import { C, FONT, FightScene, W, applyTheme } from './fight-view';
import { t } from './i18n';
import { battleLook } from './look';
import { setAuto, setSpeed, type BattleRequest, type BattleResult } from './state/actions';
import { getState } from './state/store';

/** Hauteur de base de l'écran de combat ; sur un téléphone plus allongé, l'écran s'étire (jusqu'à `H_MAX`) et le décor en profite. */
export const H = 1280;
const H_MAX = 1640;
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

  /** Un bouton dans le style des menus : contour d'encre, reflet en haut, tranche plus sombre en bas. */
  private button(x: number, y: number, w: number, h: number, label: string, color: number, onClick: () => void, dark = color, ink = false) {
    const c = this.add.container(x, y).setDepth(4000);
    const g = this.add.graphics();
    const r = Math.min(20, h / 2.6);
    g.fillStyle(0x000000, 0.3);
    g.fillRoundedRect(-w / 2 - 3, -h / 2 + 3, w + 6, h + 8, r + 3);
    g.fillStyle(C.ink);
    g.fillRoundedRect(-w / 2 - 3, -h / 2 - 3, w + 6, h + 8, r + 3);
    g.fillStyle(dark);
    g.fillRoundedRect(-w / 2, -h / 2, w, h + 2, r);
    g.fillStyle(color);
    g.fillRoundedRect(-w / 2, -h / 2, w, h - 4, r);
    g.fillStyle(0xffffff, 0.2);
    g.fillRoundedRect(-w / 2 + 3, -h / 2 + 3, w - 6, (h - 6) * 0.45, { tl: r - 2, tr: r - 2, bl: 8, br: 8 });
    const label_ = ink
      ? this.add.text(0, -3, label, { fontFamily: FONT, fontSize: `${Math.round(h * 0.42)}px`, color: C.hudText, fontStyle: 'bold' }).setOrigin(0.5)
      : this.text(0, -3, label, Math.round(h * 0.42));
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

  /** Haut du panneau des héros (tout le bas de l'écran se place à partir de là). */
  private hudY = 908;

  create() {
    applyTheme();
    this.battle = new Battle({ heroes: this.req.heroes, waves: this.req.waves, seed: this.req.seed, auto: getState().auto });
    // disposition : les boutons et le panneau des héros sont ancrés en bas, le décor prend tout le reste
    const H = this.scale.height;
    this.hudY = H - 372;
    const arenaBottom = this.hudY - 26;
    this.groundTop = arenaBottom - 430;
    this.drawArena(arenaBottom);
    // le bas de l'écran : du papier crème (comme le bas de l'accueil), bordé d'encre et d'or sous le terrain
    this.add.rectangle(W / 2, arenaBottom + (H - arenaBottom) / 2, W, H - arenaBottom, C.paper).setDepth(-5);
    this.add.rectangle(W / 2, arenaBottom, W, 6, C.trim).setDepth(1350);
    this.add.rectangle(W / 2, arenaBottom - 4, W, 3, C.ink).setDepth(1351);
    this.add.rectangle(W / 2, arenaBottom + 4, W, 3, C.ink).setDepth(1351);
    this.add.rectangle(W / 2, arenaBottom + 16, W, 22, 0x000000, 0.18).setDepth(-4);

    this.text(W / 2, 60, `${t(`mode.${this.req.kind}`)} ${this.titleSuffix()}`, 32, '#ffe27a').setDepth(3000);
    this.waveLabel = this.text(W / 2, 104, '', 24, '#ffffff').setDepth(3000);
    this.updateWaveLabel();
    if (this.req.damageMode) this.damageLabel = this.text(W / 2, 160, '0', 44, '#ffe27a').setDepth(3000);
    this.button(92, 58, 150, 56, t('battle.quit'), C.panel, () => this.finish(), C.paper3, true);

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
    // le panneau des héros : papier crème, contour d'encre, tranche plus sombre
    const g = this.add.graphics();
    const top = this.hudY;
    g.fillStyle(0x000000, 0.3);
    g.fillRoundedRect(8, top + 6, 704, 236, 24);
    g.fillStyle(C.ink);
    g.fillRoundedRect(8, top, 704, 236, 24);
    g.fillStyle(C.trim);
    g.fillRoundedRect(11, top + 3, 698, 230, 21);
    g.fillStyle(C.ink);
    g.fillRoundedRect(14, top + 6, 692, 224, 18);
    g.fillStyle(C.paper3);
    g.fillRoundedRect(16, top + 8, 688, 220, 16);
    g.fillStyle(C.panel);
    g.fillRoundedRect(16, top + 8, 688, 212, 16);
    g.fillStyle(0xffffff, 0.14);
    g.fillRoundedRect(20, top + 12, 680, 60, { tl: 13, tr: 13, bl: 0, br: 0 });
    PORTRAIT_ORDER.forEach((slot, i) => {
      const unit = this.battle.heroes.find((h) => h.slot === slot);
      if (!unit) return;
      const x = 90 + i * 135;
      const y = this.hudY + 104;
      const glow = this.add.circle(x, y, 66, C.energy, 0.35).setVisible(false);
      this.add.circle(x, y, 63, C.ink);
      const frame = this.add.circle(x, y, 57, 0x3b6ea5).setStrokeStyle(3, C.trim);
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
    const speed = this.button(530, this.hudY + 290, 290, 78, `×${getState().speed}`, C.blue, () => {
      const next = ((getState().speed % 3) + 1) as 1 | 2 | 3;
      setSpeed(next);
      speed.label.setText(`×${next}`);
    }, C.blueDark);
  }

  private drawAuto() {
    const on = getState().auto;
    const b = this.button(190, this.hudY + 290, 290, 78, t('battle.auto'), on ? C.green : C.panel, () => {
      setAuto(!on);
      this.battle.setAuto(!on);
      b.c.destroy();
      this.drawAuto();
    }, on ? C.greenDark : C.paper3, !on);
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
      p.ring.lineStyle(9, ready ? C.gold : C.energy);
      p.ring.beginPath();
      p.ring.arc(p.x, this.hudY + 104, 59, -Math.PI / 2, -Math.PI / 2 + Math.PI * 2 * (u.energy / ENERGY_MAX));
      p.ring.strokePath();
      p.ring.fillStyle(C.ink);
      p.ring.fillRoundedRect(p.x - 54, this.hudY + 181, 108, 16, 7);
      p.ring.fillStyle(0x2a2230);
      p.ring.fillRoundedRect(p.x - 52, this.hudY + 183, 104, 12, 5);
      const wHp = 104 * (u.hp / u.maxHp);
      if (wHp > 1) {
        p.ring.fillStyle(C.green);
        p.ring.fillRoundedRect(p.x - 52, this.hudY + 183, wHp, 12, Math.min(5, wHp / 2));
        p.ring.fillStyle(0xffffff, 0.35);
        p.ring.fillRect(p.x - 50, this.hudY + 184.5, Math.max(0, wHp - 4), 3);
      }
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
    height: Math.max(H, Math.min(H_MAX, Math.round((W * (parent.clientHeight || H)) / (parent.clientWidth || W)))),
    backgroundColor: '#1a1420',
    scale: { mode: Phaser.Scale.FIT, autoCenter: Phaser.Scale.CENTER_HORIZONTALLY },
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
