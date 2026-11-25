// Écran de combat : sert à tous les modes (campagne, tour, donjons, boss, arène, guilde).
// Les récompenses sont affichées ensuite par les menus.
import Phaser from 'phaser';
import { Battle } from '../core/battle/engine';
import { ENERGY_MAX, TICK_MS, type Slot, type Unit } from '../core/battle/types';
import { C, FONT, FightScene, W, applyTheme } from './fight-view';
import { HUD_BUTTONS, loadHudArt } from './hud-art';
import { t } from './i18n';
import { faceUrl } from './art';
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

type HudButton = keyof typeof HUD_BUTTONS;

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
  /** Les pièces des portraits. */
  private portraitObjs: Phaser.GameObjects.GameObject[] = [];

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
    this.portraitObjs = [];
  }

  protected preloadUnits() {
    return [...this.req.heroes, ...this.req.waves.flat()];
  }

  /** Un bouton dans le style des menus (hud-art.tsx) : cadre d'or, émail bombé, lettres cernées de la couleur du bouton. */
  private button(x: number, y: number, kind: HudButton, wide: boolean, label: string, onClick: () => void) {
    const c = this.add.container(x, y).setDepth(4000);
    const w = wide ? 290 : 160, h = wide ? 84 : 62;
    const bg = this.add.image(0, 0, `hud-btn-${kind}-${wide ? 290 : 160}`).setDisplaySize(w, h);
    const size = Math.round(h * 0.4);
    const label_ = this.add.text(0, -4, label, { fontFamily: FONT, fontSize: `${size}px`, color: '#ffffff' })
      .setOrigin(0.5).setStroke(HUD_BUTTONS[kind].ink, Math.max(4, Math.round(size * 0.2))).setShadow(0, 3, HUD_BUTTONS[kind].ink, 0, true, true);
    c.add([bg, label_]);
    c.setSize(w, h).setInteractive({ useHandCursor: true });
    c.on('pointerdown', () => c.setScale(0.95));
    c.on('pointerout', () => c.setScale(1));
    c.on('pointerup', () => {
      c.setScale(1);
      onClick();
    });
    return { c, label: label_ };
  }

  preload() {
    super.preload();
    loadHudArt(this);
    // les visages des portraits du bas (refonte-graphique/pixel/hd/anim/vignettes.py)
    for (const u of this.req.heroes) if (!this.textures.exists(`v-${u.defId}`)) this.load.image(`v-${u.defId}`, faceUrl(u.defId));
  }

  /** Haut du panneau des héros (tout le bas de l'écran se place à partir de là). */
  private hudY = 908;

  /** Les boutons et le panneau des héros sont ancrés en bas (372 px), le terrain prend tout le reste. */
  protected arenaBox() {
    const bottom = this.scale.height - 372 - 26;
    return { groundTop: bottom - 430, bottom };
  }

  create() {
    applyTheme();
    this.battle = new Battle({ heroes: this.req.heroes, waves: this.req.waves, seed: this.req.seed, auto: getState().auto });
    // disposition : les boutons et le panneau des héros sont ancrés en bas, le décor prend tout le reste
    const H = this.scale.height;
    const { groundTop, bottom: arenaBottom } = this.arenaBox();
    this.hudY = arenaBottom + 26;
    this.groundTop = groundTop;
    this.drawArena(arenaBottom);
    // le bas de l'écran : un émail bleu nuit et son plateau cerclé d'or (hud-art.tsx) ; un rail d'or à cheval sur
    // le bas du terrain ; sous le panneau, le même émail jusqu'en bas (grand téléphone)
    this.add.rectangle(W / 2, arenaBottom + (H - arenaBottom) / 2, W, H - arenaBottom, 0x1c2457).setDepth(-6);
    this.add.image(0, arenaBottom, 'hud-panel').setOrigin(0, 0).setDepth(-5);
    this.add.image(0, arenaBottom - 8, 'hud-rail').setOrigin(0, 0).setDepth(1350);

    this.text(W / 2, 60, `${t(`mode.${this.req.kind}`)} ${this.titleSuffix()}`, 32, '#ffe27a').setDepth(3000);
    this.waveLabel = this.text(W / 2, 104, '', 24, '#ffffff').setDepth(3000);
    this.updateWaveLabel();
    if (this.req.damageMode) this.damageLabel = this.text(W / 2, 160, '0', 44, '#ffe27a').setDepth(3000);
    this.button(92, 60, 'navy', false, t('battle.quit'), () => this.finish());

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
    this.drawPortraits();
    this.drawAuto();
    const speed = this.button(530, this.hudY + 292, 'blue', true, `×${getState().speed}`, () => {
      const next = ((getState().speed % 3) + 1) as 1 | 2 | 3;
      setSpeed(next);
      speed.label.setText(`×${next}`);
    });
  }

  private drawPortraits() {
    this.tweens.killTweensOf(this.portraitObjs);
    this.portraitObjs.forEach((o) => o.destroy());
    this.portraitObjs = [];
    this.portraits = [];
    const keep = <T extends Phaser.GameObjects.GameObject>(o: T): T => {
      this.portraitObjs.push(o);
      return o;
    };
    // les portraits : un disque d'émail de la couleur de l'élément, le visage, l'anneau d'or (avec la rainure de l'énergie)
    PORTRAIT_ORDER.forEach((slot, i) => {
      const unit = this.battle.heroes.find((h) => h.slot === slot);
      if (!unit) return;
      const x = 90 + i * 135;
      const y = this.hudY + 104;
      const glow = keep(this.add.circle(x, y, 70, C.energy, 0.4).setVisible(false));
      const el = this.textures.exists(`hud-disc-${unit.element}`) ? unit.element : 'none';
      keep(this.add.image(x, y, `hud-disc-${el}`).setDisplaySize(100, 100));
      // le visage, un peu plus grand que le trou de l'anneau, coupé en rond juste sous l'or
      const img = keep(this.add.image(x, y + 4, `v-${unit.defId}`).setDisplaySize(112, 112));
      img.setMask(keep(this.make.graphics({}, false).fillCircle(x, y, 50)).createGeometryMask());
      const frame = keep(this.add.image(x, y, 'hud-ring'));
      keep(this.add.image(x, this.hudY + 190, 'hud-hp'));
      const ring = keep(this.add.graphics());
      this.tweens.add({ targets: glow, scale: 1.12, alpha: 0.7, yoyo: true, repeat: -1, duration: 380 });
      frame.setInteractive(new Phaser.Geom.Circle(72, 72, 70), Phaser.Geom.Circle.Contains).on('pointerdown', () => {
        if (this.battle.requestSkill(unit.id)) this.tweens.add({ targets: img, scale: img.scale * 0.9, yoyo: true, duration: 90 });
      });
      this.portraits.push({ unit, x, ring, glow, img });
    });
  }

  private drawAuto() {
    const on = getState().auto;
    const b = this.button(190, this.hudY + 292, on ? 'green' : 'navy', true, t('battle.auto'), () => {
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
      // l'énergie court dans la rainure de l'anneau : bleue qui se remplit, or quand l'attaque spéciale est prête
      const y = this.hudY + 104;
      const a1 = -Math.PI / 2 + Math.PI * 2 * Math.min(1, u.energy / ENERGY_MAX);
      if (u.energy > 0) {
        p.ring.lineStyle(7, ready ? C.gold : C.energy);
        p.ring.beginPath().arc(p.x, y, 55.3, -Math.PI / 2, a1).strokePath();
        p.ring.lineStyle(2, 0xffffff, ready ? 0.9 : 0.55);
        p.ring.beginPath().arc(p.x, y, 57, -Math.PI / 2, a1).strokePath();
      }
      // la vie, dans sa rainure (hud-art.tsx) : un aplat net, l'arête claire en haut (au pas des pixels du dessin : 4)
      const wHp = Math.round((112 * (u.hp / u.maxHp)) / 4) * 4;
      if (wHp > 0) {
        const hy = this.hudY + 190 - 8;
        p.ring.fillStyle(wHp < 112 * 0.3 ? C.red : C.green);
        p.ring.fillRect(p.x - 56, hy, wHp, 16);
        p.ring.fillStyle(0xffffff, 0.4);
        p.ring.fillRect(p.x - 56, hy, wHp, 4);
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
