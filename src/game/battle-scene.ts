// Écran de combat : sert à tous les modes (campagne, tour, donjons, boss, arène, guilde).
// Les récompenses sont affichées ensuite par les menus.
import Phaser from 'phaser';
import { Battle } from '../core/battle/engine';
import { ENERGY_MAX, TICK_MS, type Slot, type Unit } from '../core/battle/types';
import { C, FONT, FightScene, W, applyTheme } from './fight-view';
import { HUD_BUTTONS, PANEL_SHADOW, TILE, TILE_R, loadHudArt } from './hud-art';
import { t } from './i18n';
import { heroImage } from './art';
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
  glow: Phaser.GameObjects.Image;
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

  /** Un bouton dans le style des menus (hud-art.tsx) : arrondi, dégradé vif et lèvre ; les lettres blanches, une ombre franche. */
  private button(x: number, y: number, kind: HudButton, wide: boolean, label: string, onClick: () => void) {
    const c = this.add.container(x, y).setDepth(4000);
    const w = wide ? 290 : 160, h = wide ? 84 : 62;
    // (la toile a 8 unités de marge tout autour pour l'ombre)
    const bg = this.add.image(0, 0, `hud-btn-${kind}-${wide ? 290 : 160}`).setDisplaySize(w + 16, h + 16);
    const size = Math.round(h * 0.4);
    const label_ = this.add.text(0, -3, label, { fontFamily: FONT, fontSize: `${size}px`, color: '#ffffff' })
      .setOrigin(0.5).setStroke(HUD_BUTTONS[kind].ink, 3).setShadow(0, 3, HUD_BUTTONS[kind].ink, 0, true, true);
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
    for (const u of this.req.heroes) if (!this.textures.exists(`v-${u.defId}`)) this.load.image(`v-${u.defId}`, heroImage(u.defId));
  }

  /** Haut du panneau des héros (tout le bas de l'écran se place à partir de là). */
  private hudY = 908;

  /** Les boutons et le panneau des héros sont ancrés en bas (340 px), le terrain prend tout le reste. */
  protected arenaBox() {
    const bottom = this.scale.height - 340 - 26;
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
    // le bas de l'écran : une feuille raisin aux coins arrondis posée sur le terrain (hud-art.tsx), comme le bas de
    // l'accueil ; sous elle, le même raisin jusqu'en bas (grand téléphone)
    const top = arenaBottom - 30;
    this.add.rectangle(W / 2, top + 200 + (H - top - 200) / 2, W, H - top - 200, 0x150f36).setDepth(1349);
    this.add.image(0, top - PANEL_SHADOW, 'hud-panel').setOrigin(0, 0).setDisplaySize(W, 440 + PANEL_SHADOW).setDepth(1350);

    // le titre du combat, sur une pilule de verre sombre
    const title = this.text(W / 2, 60, `${t(`mode.${this.req.kind}`)} ${this.titleSuffix()}`, 30, '#ffe27a').setDepth(3000);
    this.add.image(W / 2, 60, 'hud-pill').setDisplaySize(Math.min(360, title.width + 56), 56).setDepth(2999);
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
    const speed = this.button(530, this.hudY + 258, 'blue', true, `×${getState().speed}`, () => {
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
    // les portraits : une tuile arrondie de la couleur de l'élément, le visage, un liseré blanc ; dessous, la vie et
    // l'énergie en pilules (hud-art.tsx). Prête, l'attaque spéciale fait luire la tuile d'or.
    PORTRAIT_ORDER.forEach((slot, i) => {
      const unit = this.battle.heroes.find((h) => h.slot === slot);
      if (!unit) return;
      const x = 90 + i * 135;
      const y = this.hudY + 70;
      const glow = keep(this.add.image(x, y, 'hud-glow').setDisplaySize(TILE + 44, TILE + 44).setDepth(1351).setVisible(false));
      const el = this.textures.exists(`hud-disc-${unit.element}`) ? unit.element : 'none';
      keep(this.add.image(x, y, `hud-disc-${el}`).setDisplaySize(TILE, TILE).setDepth(1351));
      // le visage, un peu plus grand que la tuile, coupé à sa forme
      const img = keep(this.add.image(x, y + 6, `v-${unit.defId}`).setDisplaySize(TILE + 14, TILE + 14).setDepth(1351));
      img.setMask(keep(this.make.graphics({}, false).fillRoundedRect(x - TILE / 2, y - TILE / 2, TILE, TILE, TILE_R)).createGeometryMask());
      const frame = keep(this.add.image(x, y, 'hud-frame').setDisplaySize(TILE + 12, TILE + 12).setDepth(1351));
      keep(this.add.image(x, this.hudY + 148, 'hud-hp').setDisplaySize(116, 18).setDepth(1351));
      keep(this.add.image(x, this.hudY + 170, 'hud-en').setDisplaySize(116, 10).setDepth(1351));
      const ring = keep(this.add.graphics().setDepth(1352));
      this.tweens.add({ targets: glow, alpha: 0.45, yoyo: true, repeat: -1, duration: 420 });
      frame.setInteractive(new Phaser.Geom.Rectangle(0, 0, frame.width, frame.height), Phaser.Geom.Rectangle.Contains).on('pointerdown', () => {
        if (this.battle.requestSkill(unit.id)) this.tweens.add({ targets: img, scale: img.scale * 0.9, yoyo: true, duration: 90 });
      });
      this.portraits.push({ unit, x, ring, glow, img });
    });
  }

  private drawAuto() {
    const on = getState().auto;
    const b = this.button(190, this.hudY + 258, on ? 'green' : 'navy', true, t('battle.auto'), () => {
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
      // la vie : une pilule verte (rouge sous 30 %), une lumière en haut
      const iw = 110;
      const wHp = iw * Math.max(0, Math.min(1, u.hp / u.maxHp));
      if (wHp > 0) {
        const hy = this.hudY + 148 - 6;
        p.ring.fillStyle(wHp < iw * 0.3 ? C.red : C.green);
        p.ring.fillRoundedRect(p.x - iw / 2, hy, Math.max(12, wHp), 12, 6);
        p.ring.fillStyle(0xffffff, 0.35);
        p.ring.fillRoundedRect(p.x - iw / 2 + 3, hy + 2, Math.max(6, wHp - 6), 3, 1.5);
      }
      // l'énergie : azur qui se remplit, or quand l'attaque spéciale est prête
      const wEn = (iw + 2) * Math.min(1, u.energy / ENERGY_MAX);
      if (wEn > 0) {
        p.ring.fillStyle(ready ? C.gold : C.energy);
        p.ring.fillRoundedRect(p.x - iw / 2 - 1, this.hudY + 170 - 3, Math.max(6, wEn), 6, 3);
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
