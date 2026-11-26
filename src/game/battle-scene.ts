// Écran de combat : sert à tous les modes (campagne, tour, donjons, boss, arène, guilde).
// Les récompenses sont affichées ensuite par les menus.
// Disposition (demande du propriétaire, 26/11 : « on voit tout le terrain, sans bandeau ») : le décor et les combattants
// prennent tout l'écran ; l'interface flotte dessus, légère (hud-art.tsx) — en haut, le bouton pause rond et les pilules
// (le combat, la vague, le score) ; en bas, AUTO et la vitesse en boutons ronds, puis la rangée des cartes des héros
// (portrait, nom, vie, énergie ; toucher une carte qui luit = l'attaque spéciale) sur un fondu doux.
import Phaser from 'phaser';
import { Battle } from '../core/battle/engine';
import { ENERGY_MAX, TICK_MS, type Slot, type Unit } from '../core/battle/types';
import { heroDef, isHero } from '../core/data/heroes';
import { C, FONT, FightScene, W, applyTheme } from './fight-view';
import { CARD, HUD_RES, ROUND, ROUND_LIP, WIDE, hudText, loadHudArt, pillKey, type HudTone } from './hud-art';
import { t } from './i18n';
import { heroImage } from './art';
import { battleLook } from './look';
import { setAuto, setSpeed, type BattleRequest, type BattleResult } from './state/actions';
import { getState } from './state/store';

/** Hauteur de base de l'écran de combat ; sur un téléphone plus allongé, l'écran s'étire (jusqu'à `H_MAX`) et le décor en profite. */
export const H = 1280;
const H_MAX = 1640;
const PORTRAIT_ORDER: Slot[] = [3, 4, 2, 0, 1];
/** Le décor est agrandi (le sol est plus haut) : les combattants tiennent au-dessus des cartes, le sol va jusqu'en bas. */
const FOND_ZOOM = 1.4;
/** Marges du bas : sous les cartes, entre les cartes et les boutons ronds. */
const CARD_BOTTOM = 14, CARD_GAP = 10;

interface Portrait {
  unit: Unit;
  x: number;
  y: number;
  bars: Phaser.GameObjects.Graphics;
  glow: Phaser.GameObjects.Image;
  card: Phaser.GameObjects.Container;
  face: Phaser.GameObjects.Image;
}

export interface BattleSceneData {
  request: BattleRequest;
  done: (result: BattleResult) => void;
  /** La zone sûre (encoche en haut, barre de geste en bas), en unités du combat. */
  safe?: { top: number; bottom: number };
}

export class BattleScene extends FightScene {
  private req!: BattleRequest;
  private done!: (r: BattleResult) => void;
  private portraits: Portrait[] = [];
  private acc = 0;
  private ended = false;
  private paused = false;
  private pauseLayer?: Phaser.GameObjects.Container;
  private waveLabel!: Phaser.GameObjects.Text;
  private wavePill!: Phaser.GameObjects.Image;
  private damageLabel?: Phaser.GameObjects.Text;
  private safe = { top: 0, bottom: 0 };

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
    this.paused = false;
    this.pauseLayer = undefined;
    this.bigBoss = !!data.request.damageMode;
    this.look = battleLook(data.request.kind, data.request.title, data.request.dungeon?.kind);
    this.fondZoom = FOND_ZOOM;
    this.safe = data.safe ?? { top: 0, bottom: 0 };
  }

  protected preloadUnits() {
    return [...this.req.heroes, ...this.req.waves.flat()];
  }

  /** Des lettres posées sur une pierre : elles luisent sur une pierre allumée, ont une ombre franche sur une pierre éteinte. */
  private stoneText(label: string, size: number, tone: HudTone) {
    const { color, glow, ink } = hudText(tone);
    const txt = this.add.text(0, 0, label, { fontFamily: FONT, fontSize: `${size}px`, color }).setOrigin(0.5);
    return glow ? txt.setShadow(0, 0, glow, 10, true, true).setStroke(ink, 2) : txt.setStroke(ink, 3).setShadow(0, 2, ink, 0, true, true);
  }

  /** Appuyer sur une pierre : elle descend de son épaisseur (dessin enfoncé), son contenu avec elle. */
  private press(c: Phaser.GameObjects.Container, bg: Phaser.GameObjects.Image, key: string, content: Phaser.GameObjects.Components.Transform, y0: number, lip: number, onClick: () => void) {
    const up = () => { bg.setTexture(key); content.y = y0; };
    c.on('pointerdown', () => { bg.setTexture(`${key}-down`); content.y = y0 + lip - 1; });
    c.on('pointerout', up);
    c.on('pointerup', () => { up(); onClick(); });
  }

  /** Un galet rond (ui/buttons.ts) avec un texte ou le signe pause ; il s'enfonce sous le doigt. */
  private round(x: number, y: number, tone: HudTone, label: string | null, onClick: () => void) {
    const c = this.add.container(x, y).setDepth(4000);
    const key = `hud-round-${tone}`;
    const bg = this.add.image(0, 0, key).setDisplaySize(ROUND, ROUND + ROUND_LIP);
    const y0 = -ROUND_LIP / 2 - 1;
    const content = label === null
      ? this.add.image(0, y0, 'hud-pause').setDisplaySize(28, 28)
      : this.stoneText(label, label.length > 3 ? 19 : 25, tone).setY(y0);
    c.add([bg, content]);
    c.setSize(ROUND, ROUND).setInteractive({ useHandCursor: true });
    this.press(c, bg, key, content, y0, ROUND_LIP, onClick);
    return { c, bg, content };
  }

  /** Une dalle de pierre large (fenêtre de pause). */
  private wideButton(x: number, y: number, tone: HudTone, label: string, onClick: () => void) {
    const c = this.add.container(x, y);
    const key = `hud-btn-${tone}`;
    const bg = this.add.image(0, 0, key).setDisplaySize(WIDE.w, WIDE.h);
    const y0 = -WIDE.lip / 2 - 1;
    const txt = this.stoneText(label, 34, tone).setY(y0);
    c.add([bg, txt]);
    c.setSize(WIDE.w, WIDE.h).setInteractive({ useHandCursor: true });
    this.press(c, bg, key, txt, y0, WIDE.lip, onClick);
    return c;
  }

  /** Une pilule de verre sombre derrière un texte, à sa largeur. */
  private pill(x: number, y: number, text: Phaser.GameObjects.Text, h = 48) {
    return this.add.image(x, y, pillKey(this, Math.min(W - 180, Math.max(h * 2, text.width + 44)), h)).setScale(1 / HUD_RES).setDepth(2999);
  }

  preload() {
    super.preload();
    loadHudArt(this);
    // les visages des cartes du bas (refonte-graphique/pixel/hd/anim/vignettes.py)
    for (const u of this.req.heroes) if (!this.textures.exists(`v-${u.defId}`)) this.load.image(`v-${u.defId}`, heroImage(u.defId));
  }

  /** Le haut des cartes des héros. */
  private get cardsTop() {
    return this.scale.height - this.safe.bottom - CARD_BOTTOM - CARD.h;
  }

  /**
   * Le terrain prend tout l'écran : le décor (agrandi de FOND_ZOOM) touche le bas ; ses rangées sont placées pour que les
   * pieds du dernier rang restent au-dessus des boutons ronds.
   */
  protected arenaBox() {
    const bottom = this.scale.height;
    return { groundTop: bottom - Math.round(430 * FOND_ZOOM), bottom };
  }

  create() {
    applyTheme();
    this.battle = new Battle({ heroes: this.req.heroes, waves: this.req.waves, seed: this.req.seed, auto: getState().auto });
    const H = this.scale.height;
    const { groundTop, bottom } = this.arenaBox();
    this.groundTop = groundTop;
    this.drawArena(bottom);

    // en haut : la pause (bouton rond), le combat et la vague dans des pilules
    const top = this.safe.top;
    this.round(52, top + 50, 'galet', null, () => this.pause());
    const title = this.text(W / 2, top + 48, `${t(`mode.${this.req.kind}`)} ${this.titleSuffix()}`, 27, '#ffe27a').setDepth(3000);
    this.pill(W / 2, top + 48, title);
    this.waveLabel = this.text(W / 2, top + 98, '', 20, '#ffffff').setDepth(3000);
    this.wavePill = this.add.image(W / 2, top + 98, pillKey(this, 150, 38)).setScale(1 / HUD_RES).setDepth(2999);
    this.updateWaveLabel();
    if (this.req.damageMode) {
      this.damageLabel = this.text(W / 2, top + 150, '0', 34, '#ffe27a').setDepth(3000);
      this.add.image(W / 2, top + 150, pillKey(this, 240, 52)).setScale(1 / HUD_RES).setDepth(2999);
    }

    for (const u of this.battle.heroes) this.addView(u);
    for (const u of this.battle.enemies) this.addView(u);

    // en bas : le fondu sous les cartes, les cartes, AUTO et la vitesse
    this.add.image(0, H - 300, 'hud-fade').setOrigin(0).setDisplaySize(W, 300).setDepth(3500);
    this.drawCards();
    const by = this.cardsTop - CARD_GAP - ROUND / 2 - 4;
    this.drawAuto(by);
    const speed = this.round(W - 48, by, 'galet', `×${getState().speed}`, () => {
      const next = ((getState().speed % 3) + 1) as 1 | 2 | 3;
      setSpeed(next);
      (speed.content as Phaser.GameObjects.Text).setText(`×${next}`);
    });
  }

  private titleSuffix(): string {
    if (this.req.kind === 'dailyBoss' || this.req.kind === 'guildBoss') return `· ${t(`monster.${this.req.title}`)}`;
    return this.req.title;
  }

  private updateWaveLabel() {
    const many = this.battle.waveCount > 1;
    this.waveLabel.setText(many ? `${t('battle.wave')} ${this.battle.wave + 1} / ${this.battle.waveCount}` : '');
    this.wavePill?.setVisible(many);
  }

  /** Les cartes des héros, le long du bas de l'écran (l'ordre des postes, de l'arrière vers l'avant). */
  private drawCards() {
    const units = PORTRAIT_ORDER.map((slot) => this.battle.heroes.find((h) => h.slot === slot)).filter((u): u is Unit => !!u);
    const gap = 10, w = CARD.w, total = units.length * w + (units.length - 1) * gap;
    const y = this.cardsTop + CARD.h / 2;
    units.forEach((unit, i) => {
      const x = W / 2 - total / 2 + w / 2 + i * (w + gap);
      const card = this.add.container(x, y).setDepth(3600);
      const glow = this.add.image(0, 0, 'hud-card-glow').setDisplaySize(CARD.w + 44, CARD.h + 44).setVisible(false);
      const el = this.textures.exists(`hud-card-${unit.element}`) ? unit.element : 'none';
      const bg = this.add.image(0, 0, `hud-card-${el}`).setDisplaySize(CARD.w + 16, CARD.h + 16);
      // le visage, au haut de la carte, coupé à sa forme (coins du haut arrondis)
      const top = -CARD.h / 2;
      const face = this.add.image(0, top + CARD.face / 2 + 4, `v-${unit.defId}`).setDisplaySize(CARD.w + 4, CARD.w + 4);
      const mask = this.make.graphics({}, false).fillRoundedRect(x - CARD.w / 2, y + top, CARD.w, CARD.face, { tl: CARD.r, tr: CARD.r, bl: 0, br: 0 });
      face.setMask(mask.createGeometryMask());
      const frame = this.add.image(0, 0, 'hud-card-frame').setDisplaySize(CARD.w + 16, CARD.h + 16);
      const name = this.add.text(0, top + CARD.face - 12, isHero(unit.defId) ? heroDef(unit.defId).name : '', { fontFamily: FONT, fontSize: '20px', color: '#ffffff' })
        .setOrigin(0.5).setShadow(0, 2, '#0c0822', 0, true, true);
      if (name.width > CARD.w - 12) name.setScale((CARD.w - 12) / name.width);
      const hp = this.add.image(0, CARD.h / 2 - 34, 'hud-hp').setDisplaySize(108, 14);
      const en = this.add.image(0, CARD.h / 2 - 16, 'hud-en').setDisplaySize(108, 8);
      const bars = this.add.graphics();
      card.add([glow, bg, face, frame, name, hp, en, bars]);
      this.tweens.add({ targets: glow, alpha: 0.4, yoyo: true, repeat: -1, duration: 420 });
      card.setSize(CARD.w, CARD.h).setInteractive({ useHandCursor: true }).on('pointerdown', () => {
        if (this.paused) return;
        if (this.battle.requestSkill(unit.id)) this.tweens.add({ targets: card, scale: 0.93, yoyo: true, duration: 90 });
      });
      this.portraits.push({ unit, x, y, bars, glow, card, face });
    });
  }

  private drawAuto(y: number) {
    const on = getState().auto;
    const b = this.round(W - 48 - ROUND - 14, y, on ? 'basalte' : 'galet', t('battle.auto'), () => {
      setAuto(!on);
      this.battle.setAuto(!on);
      b.c.destroy();
      this.drawAuto(y);
    });
  }

  /** La pause : tout s'arrête, une fenêtre propose de reprendre ou de quitter. */
  private pause() {
    if (this.paused || this.ended) return;
    this.paused = true;
    this.tweens.pauseAll();
    const H = this.scale.height;
    const veil = this.add.rectangle(0, 0, W, H, 0x0a0620, 0.6).setOrigin(0).setInteractive();
    const icon = this.add.image(W / 2, H / 2 - 150, 'hud-pause').setDisplaySize(64, 64).setAlpha(0.9);
    const resume = this.wideButton(W / 2, H / 2 - 30, 'basalte', t('battle.resume'), () => {
      this.pauseLayer?.destroy();
      this.pauseLayer = undefined;
      this.paused = false;
      this.tweens.resumeAll();
    });
    const quit = this.wideButton(W / 2, H / 2 + 80, 'feu', t('battle.quit'), () => {
      this.pauseLayer?.destroy();
      this.finish();
    });
    this.pauseLayer = this.add.container(0, 0, [veil, icon, resume, quit]).setDepth(6000);
  }

  update(_time: number, delta: number) {
    if (this.ended || this.paused) return;
    this.advance(delta, getState().speed);
    this.syncUnits();
    this.syncCards();
    if (this.damageLabel) this.damageLabel.setText(this.damage().toLocaleString('fr-FR'));
  }

  private syncCards() {
    for (const p of this.portraits) {
      const u = p.unit;
      const ready = u.hp > 0 && u.energy >= ENERGY_MAX;
      p.glow.setVisible(ready && !this.battle.auto);
      p.card.setAlpha(u.hp > 0 ? 1 : 0.45);
      p.face.setTint(u.hp > 0 ? 0xffffff : 0x8a87a3);
      p.bars.clear();
      if (u.hp <= 0) continue;
      // la vie : une pilule verte (rouge sous 30 %), une lumière en haut
      const iw = 104, x0 = -iw / 2;
      const wHp = iw * Math.max(0, Math.min(1, u.hp / u.maxHp));
      if (wHp > 0) {
        const hy = CARD.h / 2 - 34 - 5;
        p.bars.fillStyle(wHp < iw * 0.3 ? C.red : C.green);
        p.bars.fillRoundedRect(x0, hy, Math.max(10, wHp), 10, 5);
        p.bars.fillStyle(0xffffff, 0.35);
        p.bars.fillRoundedRect(x0 + 3, hy + 2, Math.max(4, wHp - 6), 2.5, 1.2);
      }
      // l'énergie : azur qui se remplit, or quand l'attaque spéciale est prête
      const wEn = iw * Math.min(1, u.energy / ENERGY_MAX);
      if (wEn > 0) {
        p.bars.fillStyle(ready ? C.gold : C.energy);
        p.bars.fillRoundedRect(x0, CARD.h / 2 - 16 - 2, Math.max(4, wEn), 4, 2);
      }
    }
  }

  private damage(): number {
    return this.battle.enemies.reduce((sum, e) => sum + (e.maxHp - e.hp), 0);
  }

  protected onWave(index: number) {
    this.updateWaveLabel();
    this.banner(`${t('battle.wave')} ${index + 1}`, 220);
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
  // la zone sûre (encoche, barre de geste), lue sur une sonde du CSS, en unités du combat
  const probe = document.createElement('div');
  probe.className = 'safe-probe';
  parent.appendChild(probe);
  const cs = getComputedStyle(probe), k = W / (parent.clientWidth || W);
  const safe = { top: (Number.parseFloat(cs.paddingTop) || 0) * k, bottom: (Number.parseFloat(cs.paddingBottom) || 0) * k };
  probe.remove();
  const game = new Phaser.Game({
    type: Phaser.AUTO,
    parent,
    width: W,
    height: Math.max(H, Math.min(H_MAX, Math.round((W * (parent.clientHeight || H)) / (parent.clientWidth || W)))),
    backgroundColor: '#150f36',
    scale: { mode: Phaser.Scale.FIT, autoCenter: Phaser.Scale.CENTER_HORIZONTALLY },
    scene: [],
  });
  game.scene.add('battle', BattleScene, true, {
    request,
    done: (r: BattleResult) => {
      done(r);
      setTimeout(() => game.destroy(true), 0);
    },
    safe,
  } satisfies BattleSceneData);
  return () => game.destroy(true);
}
