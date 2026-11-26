// Combat du Colisée (demande du 26/11/2026) : des duels en chaîne, tout automatique. Les deux combattants du duel sont
// face à face au milieu de l'arène ; ceux qui attendent leur tour sont plus petits, sur les côtés (chacun de son côté).
// Le gagnant d'un duel reste au milieu avec la vie qui lui reste ; le suivant de l'autre équipe s'avance.
// En haut : la pause, le titre, et les 3 visages de chaque équipe (éteints quand le héros est tombé). En bas : la vitesse.
// Les règles viennent de src/core/coliseum.ts (DuelChain) : l'écran ne fait que montrer le combat.
import Phaser from 'phaser';
import type { Battle } from '../core/battle/engine';
import type { Unit, UnitInit } from '../core/battle/types';
import { DuelChain, type ColiseumEvent, type ColiseumSetup, type DuelEvent } from '../core/coliseum';
import { heroImage } from './art';
import { FONT, FightScene, W, applyTheme, type View } from './fight-view';
import { HUD_RES, ROUND, ROUND_LIP, WIDE, hudText, loadHudArt, pillKey, type HudTone } from './hud-art';
import { t } from './i18n';
import { battleLook } from './look';
import { setSpeed } from './state/actions';
import { getState } from './state/store';
import { killGame } from './game-kill';

const H = 1280;
const H_MAX = 1640;
const FOND_ZOOM = 1.4;
/** Place des deux combattants du duel (écart au milieu) et des remplaçants (au bord, plus petits). */
const DUEL_DX = 138;
const DUEL_DY = 250;
const BENCH = [{ x: 72, dy: 130, k: 0.66 }, { x: 132, dy: 375, k: 0.66 }];
const FACE = 58;

export interface ColiseumSceneData {
  setup: ColiseumSetup;
  names: { me: string; foe: string };
  done: (win: boolean) => void;
  safe?: { top: number; bottom: number };
}

/** Un combattant hors du duel, pour l'affichage (le moteur ne le connaît pas encore). */
function benchUnit(init: UnitInit, side: 'hero' | 'enemy'): Unit {
  return { ...init, side, slot: 0, hp: init.maxHp, energy: 0, shield: 0, stun: 0, cooldown: 0, dead: false, statuses: [] };
}

export class ColiseumScene extends FightScene {
  private setup!: ColiseumSetup;
  private names!: { me: string; foe: string };
  private done!: (win: boolean) => void;
  private chain!: DuelChain;
  private safe = { top: 0, bottom: 0 };
  private ended = false;
  private paused = false;
  private pauseLayer?: Phaser.GameObjects.Container;
  private faces = new Map<string, Phaser.GameObjects.Image>();
  private duelLabel!: Phaser.GameObjects.Text;

  constructor() {
    super('coliseum');
  }

  init(data: ColiseumSceneData) {
    this.setup = data.setup;
    this.names = data.names;
    this.done = data.done;
    this.safe = data.safe ?? { top: 0, bottom: 0 };
    this.views.clear();
    this.faces.clear();
    this.ended = false;
    this.paused = false;
    this.pauseLayer = undefined;
    this.look = battleLook('coliseum', '');
    this.fondZoom = FOND_ZOOM;
  }

  protected preloadUnits() {
    return [...this.setup.heroes, ...this.setup.foes];
  }

  preload() {
    super.preload();
    loadHudArt(this);
    for (const u of [...this.setup.heroes, ...this.setup.foes]) {
      if (!this.textures.exists(`v-${u.defId}`)) this.load.image(`v-${u.defId}`, heroImage(u.defId));
    }
  }

  protected arenaBox() {
    const bottom = this.scale.height;
    return { groundTop: bottom - Math.round(430 * FOND_ZOOM), bottom };
  }

  /** Place du duel (au milieu) ou du banc (au bord : 0 = le prochain, 1 = celui d'après). */
  private spot(side: 'hero' | 'enemy', bench: number | null): { x: number; y: number; k: number } {
    const mirror = (x: number) => (side === 'hero' ? x : W - x);
    if (bench === null) return { x: mirror(W / 2 - DUEL_DX), y: this.groundTop + DUEL_DY, k: 1 };
    const b = BENCH[Math.min(bench, BENCH.length - 1)]!;
    return { x: mirror(b.x), y: this.groundTop + b.dy, k: b.k };
  }

  private place(v: View, p: { x: number; y: number; k: number }, ms = 0) {
    v.homeX = p.x;
    v.homeY = p.y;
    v.body.setDepth(p.y);
    v.bars.setVisible(p.k === 1);
    if (!ms) {
      v.body.setPosition(p.x, p.y).setScale(p.k);
      return;
    }
    this.tweens.add({ targets: v.body, x: p.x, y: p.y, scale: p.k, duration: ms, ease: 'Quad.easeInOut' });
  }

  create() {
    applyTheme();
    this.chain = new DuelChain(this.setup);
    // le Colisée se joue comme un combat ordinaire : le moteur (une suite de duels) avance, la scène anime
    this.battle = this.chain as unknown as Battle;
    const { groundTop, bottom } = this.arenaBox();
    this.groundTop = groundTop;
    this.drawArena(bottom);

    // les combattants : le duel au milieu, les autres sur le banc de leur côté
    this.addView(this.chain.hero);
    this.addView(this.chain.enemy);
    this.place(this.views.get(this.chain.hero.id)!, this.spot('hero', null));
    this.place(this.views.get(this.chain.enemy.id)!, this.spot('enemy', null));
    this.setup.heroes.slice(1).forEach((u, i) => {
      const unit = benchUnit(u, 'hero');
      this.addView(unit);
      this.place(this.views.get(unit.id)!, this.spot('hero', i));
    });
    this.setup.foes.slice(1).forEach((u, i) => {
      const unit = benchUnit(u, 'enemy');
      this.addView(unit);
      this.place(this.views.get(unit.id)!, this.spot('enemy', i));
    });

    // en haut : la pause, le titre, les deux équipes (visages) et le duel en cours
    const top = this.safe.top;
    this.round(52, top + 50, 'galet', null, () => this.pause());
    const title = this.text(W / 2, top + 48, t('adv.defense'), 27, '#ffe27a').setDepth(3000);
    this.pill(W / 2, top + 48, title);
    this.drawTeams(top + 128);
    this.duelLabel = this.text(W / 2, top + 128, '', 22, '#ffffff').setDepth(3000);
    this.add.image(W / 2, top + 128, pillKey(this, 118, 40)).setScale(1 / HUD_RES).setDepth(2999);
    this.setDuel(0);

    // en bas : la vitesse (le Colisée est tout automatique)
    const by = this.scale.height - this.safe.bottom - 24 - ROUND / 2;
    const speed = this.round(W - 52, by, 'galet', `×${getState().speed}`, () => {
      const next = ((getState().speed % 3) + 1) as 1 | 2 | 3;
      setSpeed(next);
      (speed.content as Phaser.GameObjects.Text).setText(`×${next}`);
    });
  }

  /** Les 3 visages de chaque équipe, dans l'ordre de passage, avec le nom du joueur au-dessus. */
  private drawTeams(y: number) {
    const row = (units: UnitInit[], side: 'hero' | 'enemy', name: string) => {
      const dir = side === 'hero' ? 1 : -1;
      const x0 = side === 'hero' ? 24 + FACE / 2 : W - 24 - FACE / 2;
      units.forEach((u, i) => {
        const x = x0 + dir * i * (FACE + 8);
        this.add.circle(x, y, FACE / 2 + 3, side === 'hero' ? 0x2fc457 : 0xff5468).setDepth(3000);
        const img = this.add.image(x, y, `v-${u.defId}`).setDisplaySize(FACE, FACE).setDepth(3001);
        const m = this.make.graphics({}, false).fillCircle(x, y, FACE / 2);
        img.setMask(m.createGeometryMask());
        this.faces.set(u.id, img);
      });
      const nx = side === 'hero' ? 24 : W - 24;
      const label = this.add.text(nx, y + FACE / 2 + 18, name, { fontFamily: FONT, fontSize: '20px', color: '#ffffff' })
        .setOrigin(side === 'hero' ? 0 : 1, 0.5).setDepth(3000).setStroke('#150f36', 4);
      if (label.width > 200) label.setScale(200 / label.width);
    };
    row(this.setup.heroes, 'hero', this.names.me);
    row(this.setup.foes, 'enemy', this.names.foe);
  }

  private setDuel(index: number) {
    this.duelLabel.setText(t('col.duel', { n: index + 1 }));
  }

  /** Les événements du moteur, plus l'arrivée d'un nouveau duel. */
  protected handle(events: ColiseumEvent[], speed: number) {
    const rest: ColiseumEvent[] = [];
    for (const e of events) {
      if (e.type === 'duel') this.nextDuel(e, speed);
      else rest.push(e);
    }
    if (rest.length) super.handle(rest as Parameters<FightScene['handle']>[0], speed);
  }

  protected onDeath(unit: Unit) {
    const face = this.faces.get(unit.id);
    face?.setTint(0x55526b).setAlpha(0.55);
  }

  /** Un nouveau duel : le gagnant reste (sa vie est celle qui lui reste), le suivant de l'autre équipe s'avance. */
  private nextDuel(e: DuelEvent, speed: number) {
    const walk = 650 / speed;
    for (const [unit, isNew] of [[e.hero, e.heroNew], [e.enemy, e.enemyNew]] as const) {
      const v = this.views.get(unit.id);
      if (!v) continue;
      v.unit = unit;
      v.hp = unit.hp;
      if (isNew) {
        this.place(v, this.spot(unit.side, null), walk);
        // les remplaçants restants avancent d'une place sur le banc
        const lineup = unit.side === 'hero' ? this.setup.heroes : this.setup.foes;
        const next = lineup.findIndex((u) => u.id === unit.id);
        lineup.slice(next + 1).forEach((u, i) => {
          const b = this.views.get(u.id);
          if (b) this.place(b, this.spot(unit.side, i), walk);
        });
      }
    }
    this.setDuel(e.index);
    this.banner(t('col.duel', { n: e.index + 1 }), this.groundTop - 60);
    this.turnMs = walk + 500 / speed;
  }

  protected onEnd(win: boolean) {
    const label = this.text(W / 2, this.groundTop - 60, win ? t('col.win') : t('col.loss'), 64, win ? '#ffe27a' : '#ff9b9b').setDepth(3000).setScale(0.4);
    this.tweens.add({ targets: label, scale: 1, duration: 300, ease: 'Back.easeOut' });
    this.time.delayedCall(Math.max(1300, this.deathsEnd - this.time.now + 600), () => this.finish());
  }

  update(_time: number, delta: number) {
    if (this.ended || this.paused) return;
    this.advance(delta, getState().speed);
    this.syncUnits();
  }

  private finish() {
    if (this.ended) return;
    this.ended = true;
    this.done(this.chain.win);
  }

  // ---------- Boutons (les mêmes pierres que l'écran de combat) ----------

  private stoneText(label: string, size: number, tone: HudTone) {
    const { color, glow, ink } = hudText(tone);
    const txt = this.add.text(0, 0, label, { fontFamily: FONT, fontSize: `${size}px`, color }).setOrigin(0.5);
    return glow ? txt.setShadow(0, 0, glow, 10, true, true).setStroke(ink, 2) : txt.setStroke(ink, 3).setShadow(0, 2, ink, 0, true, true);
  }

  private press(c: Phaser.GameObjects.Container, bg: Phaser.GameObjects.Image, key: string, content: Phaser.GameObjects.Components.Transform, y0: number, lip: number, onClick: () => void) {
    const up = () => { bg.setTexture(key); content.y = y0; };
    c.on('pointerdown', () => { bg.setTexture(`${key}-down`); content.y = y0 + lip - 1; });
    c.on('pointerout', up);
    c.on('pointerup', () => { up(); onClick(); });
  }

  private round(x: number, y: number, tone: HudTone, label: string | null, onClick: () => void) {
    const c = this.add.container(x, y).setDepth(4000);
    const key = `hud-round-${tone}`;
    const bg = this.add.image(0, 0, key).setDisplaySize(ROUND, ROUND + ROUND_LIP);
    const y0 = -ROUND_LIP / 2 - 1;
    const content = label === null ? this.add.image(0, y0, 'hud-pause').setDisplaySize(28, 28) : this.stoneText(label, 25, tone).setY(y0);
    c.add([bg, content]);
    c.setSize(ROUND, ROUND).setInteractive({ useHandCursor: true });
    this.press(c, bg, key, content, y0, ROUND_LIP, onClick);
    return { c, bg, content };
  }

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

  private pill(x: number, y: number, text: Phaser.GameObjects.Text, h = 48) {
    return this.add.image(x, y, pillKey(this, Math.min(W - 180, Math.max(h * 2, text.width + 44)), h)).setScale(1 / HUD_RES).setDepth(2999);
  }

  /** La pause : reprendre, ou passer à la fin (le résultat est déjà décidé par les règles : quitter ne change rien). */
  private pause() {
    if (this.paused || this.ended) return;
    this.paused = true;
    this.tweens.pauseAll();
    this.time.paused = true;
    const H = this.scale.height;
    const veil = this.add.rectangle(0, 0, W, H, 0x0a0620, 0.6).setOrigin(0).setInteractive();
    const icon = this.add.image(W / 2, H / 2 - 150, 'hud-pause').setDisplaySize(64, 64).setAlpha(0.9);
    const resume = this.wideButton(W / 2, H / 2 - 30, 'basalte', t('battle.resume'), () => {
      this.pauseLayer?.destroy();
      this.pauseLayer = undefined;
      this.paused = false;
      this.tweens.resumeAll();
      this.time.paused = false;
    });
    const skip = this.wideButton(W / 2, H / 2 + 80, 'galet', t('col.skip'), () => {
      this.pauseLayer?.destroy();
      while (!this.chain.over) this.chain.step();
      this.finish();
    });
    this.pauseLayer = this.add.container(0, 0, [veil, icon, resume, skip]).setDepth(6000);
  }
}

/** Lance un combat du Colisée dans le cadre donné ; `done` reçoit le résultat montré, puis le combat se ferme. */
export function runColiseumFight(parent: HTMLElement, data: Omit<ColiseumSceneData, 'safe'>): () => void {
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
  game.scene.add('coliseum', ColiseumScene, true, {
    ...data,
    done: (win: boolean) => {
      data.done(win);
      setTimeout(() => killGame(game), 0);
    },
    safe,
  } satisfies ColiseumSceneData);
  return () => killGame(game);
}
