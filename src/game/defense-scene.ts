// Écran de jeu du mode Défense : la carte, le chemin, les héros posés, les monstres qui avancent.
// Le moteur (src/core/defense/engine.ts) décide de tout ; cette scène ne fait que montrer.
import Phaser from 'phaser';
import { TICK_MS } from '../core/battle/types';
import { DEFENSE_H, DEFENSE_LIVES, DEFENSE_PADS, DEFENSE_PATH, DEFENSE_W, defenseStars } from '../core/data/defense';
import { DefenseBattle, type Creep, type DefenseEvent, type DefenseSetup } from '../core/defense/engine';
import { ELEMENT_COLOR, cardUrl, hasArt, heroCanvas, monsterCanvas } from './art';
import { FONT } from './fight-view';
import { t } from './i18n';
import { DEFAULT_LOOK, monsterArtId } from './look';

/** Les monstres des règles qui peuvent venir (leur dessin dépend de l'élément du niveau). */
const CREEP_IDS = ['goblin', 'wolf', 'golem', 'archer', 'shaman', 'wraith', 'ogre', 'lich', 'dragon'];

const TOP = 96;
export const DEF_H = DEFENSE_H + TOP;
const SPEEDS = [1, 2, 3];

interface DefenseData {
  setup: DefenseSetup;
  done: (lives: number) => void;
}

interface CreepView {
  body: Phaser.GameObjects.Container;
  sprite: Phaser.GameObjects.Image;
  bar: Phaser.GameObjects.Graphics;
}

function hex(color: string): number {
  return Number.parseInt(color.slice(1), 16);
}

export class DefenseScene extends Phaser.Scene {
  private battle!: DefenseBattle;
  private setup!: DefenseSetup;
  private done!: (lives: number) => void;
  private creeps = new Map<string, CreepView>();
  private towers = new Map<string, Phaser.GameObjects.Container>();
  private acc = 0;
  private speed = 1;
  private finished = false;
  private waveText!: Phaser.GameObjects.Text;
  private livesText!: Phaser.GameObjects.Text;
  private speedText!: Phaser.GameObjects.Text;

  constructor() {
    super('defense');
  }

  init(data: DefenseData) {
    this.setup = data.setup;
    this.done = data.done;
  }

  private text(x: number, y: number, value: string, size = 28, color = '#ffffff') {
    return this.add.text(x, y, value, { fontFamily: FONT, fontSize: `${size}px`, color, align: 'center' })
      .setOrigin(0.5).setShadow(0, 2, '#000000', 3, false, true);
  }

  /** Vignettes des dessins Hailuo : héros posés et monstres possibles. */
  preload() {
    for (const { unit } of this.setup.towers) if (hasArt(unit.defId)) this.load.image(`c-${unit.defId}`, cardUrl(unit.defId));
    for (const id of CREEP_IDS) {
      const art = monsterArtId(id, this.setup.element, DEFAULT_LOOK);
      if (hasArt(art)) this.load.image(`c-${art}`, cardUrl(art));
    }
  }

  private tex(key: string, make: () => HTMLCanvasElement): string {
    if (!this.textures.exists(key)) this.textures.addCanvas(key, make());
    return key;
  }

  create() {
    this.battle = new DefenseBattle(this.setup);
    this.drawMap();
    this.battle.towers.forEach((tw) => {
      const c = this.add.container(tw.x, tw.y + TOP).setDepth(tw.y + TOP);
      const shadow = this.add.ellipse(0, 46, 84, 22, 0x000000, 0.35);
      const card = `c-${tw.unit.defId}`;
      const img = this.textures.exists(card)
        ? this.add.image(0, 46, card).setOrigin(0.5, 0.96).setDisplaySize(118, 118)
        : this.add.image(0, 0, this.tex(`h-${tw.unit.defId}`, () => heroCanvas(tw.unit.defId))).setScale(0.78);
      c.add([shadow, img]);
      this.towers.set(tw.id, c);
    });
    this.drawHud();
  }

  private drawMap() {
    const g = this.add.graphics().setDepth(-10);
    g.fillGradientStyle(0x3d6b4a, 0x3d6b4a, 0x274a34, 0x274a34, 1);
    g.fillRect(0, TOP, DEFENSE_W, DEFENSE_H);
    // Touffes d'herbe pour habiller le terrain.
    const rng = new Phaser.Math.RandomDataGenerator(['herbe']);
    g.fillStyle(0x4f8a5e, 0.5);
    for (let i = 0; i < 60; i++) g.fillEllipse(rng.between(0, DEFENSE_W), TOP + rng.between(0, DEFENSE_H), rng.between(18, 40), rng.between(8, 14));
    // Le chemin : un bord sombre, puis la terre.
    const pts = DEFENSE_PATH.map(([x, y]) => new Phaser.Math.Vector2(x, y + TOP));
    for (const [w, c] of [[86, 0x6b4a2a], [70, 0xc08a4a], [8, 0xd9a866]] as const) {
      g.lineStyle(w, c, 1);
      g.beginPath();
      g.moveTo(pts[0]!.x, pts[0]!.y);
      for (const p of pts.slice(1)) g.lineTo(p.x, p.y);
      g.strokePath();
      for (const p of pts) g.fillStyle(c, 1).fillCircle(p.x, p.y, w / 2);
    }
    // Les emplacements (pierres rondes).
    DEFENSE_PADS.forEach(([x, y]) => {
      g.fillStyle(0x000000, 0.25).fillEllipse(x, y + TOP + 40, 100, 34);
      g.fillStyle(0x8a8fa8, 1).fillEllipse(x, y + TOP + 34, 92, 30);
      g.fillStyle(0xa9aec4, 1).fillEllipse(x, y + TOP + 30, 80, 22);
    });
    // Le camp à protéger, au bout du chemin.
    const [cx, cy] = DEFENSE_PATH[DEFENSE_PATH.length - 1]!;
    const camp = this.add.graphics().setDepth(DEFENSE_H + TOP);
    camp.fillStyle(0x5a4a7a).fillRect(cx - 70, TOP + cy - 120, 140, 70);
    camp.fillStyle(0x7d6aa8).fillTriangle(cx - 84, TOP + cy - 120, cx, TOP + cy - 180, cx + 84, TOP + cy - 120);
    camp.fillStyle(0x2b2140).fillRoundedRect(cx - 20, TOP + cy - 92, 40, 42, { tl: 20, tr: 20, bl: 0, br: 0 });
    // L'entrée des monstres.
    this.text(30, TOP + DEFENSE_PATH[0]![1] - 70, '☠', 40, '#ff8a8a');
  }

  private drawHud() {
    const g = this.add.graphics().setDepth(5000);
    g.fillStyle(0x14162b, 0.92).fillRect(0, 0, DEFENSE_W, TOP);
    this.waveText = this.text(130, TOP / 2, '', 30).setDepth(5001);
    this.livesText = this.text(DEFENSE_W / 2, TOP / 2, '', 34, '#ff8a9a').setDepth(5001);
    const speedBtn = this.add.container(DEFENSE_W - 170, TOP / 2).setDepth(5001);
    const sg = this.add.graphics().fillStyle(0x2c3260).fillRoundedRect(-50, -28, 100, 56, 14);
    this.speedText = this.text(0, 0, '×1', 30);
    speedBtn.add([sg, this.speedText]).setSize(100, 56).setInteractive({ useHandCursor: true });
    speedBtn.on('pointerup', () => {
      this.speed = SPEEDS[(SPEEDS.indexOf(this.speed) + 1) % SPEEDS.length]!;
      this.speedText.setText(`×${this.speed}`);
    });
    const quit = this.add.container(DEFENSE_W - 56, TOP / 2).setDepth(5001);
    const qg = this.add.graphics().fillStyle(0xe5484d).fillRoundedRect(-36, -28, 72, 56, 14);
    quit.add([qg, this.text(0, 0, '✕', 30)]).setSize(72, 56).setInteractive({ useHandCursor: true });
    quit.on('pointerup', () => this.end(0));
    this.refreshHud();
  }

  private refreshHud() {
    this.waveText.setText(`${t('battle.wave')} ${this.battle.wave + 1}/${this.battle.waveCount}`);
    this.livesText.setText(`♥ ${this.battle.lives}`);
  }

  private addCreep(c: Creep) {
    const scale = c.boss ? 0.95 : 0.55;
    const body = this.add.container(c.x, c.y + TOP);
    const shadow = this.add.ellipse(0, 52 * scale, 80 * scale, 18, 0x000000, 0.3);
    const card = `c-${monsterArtId(c.defId, c.element, DEFAULT_LOOK)}`;
    const sprite = (this.textures.exists(card)
      ? this.add.image(0, 52 * scale, card).setOrigin(0.5, 0.96).setDisplaySize(150 * scale, 150 * scale)
      : this.add.image(0, 0, this.tex(`m-${c.defId}-${c.element}`, () => monsterCanvas(c.defId, c.element))).setScale(scale)).setFlipX(true);
    const bar = this.add.graphics();
    body.add([shadow, sprite, bar]);
    this.creeps.set(c.id, { body, sprite, bar });
  }

  private handle(events: DefenseEvent[]) {
    for (const e of events) {
      switch (e.type) {
        case 'spawn':
          this.addCreep(e.creep);
          break;
        case 'hit': {
          const tw = this.battle.towers.find((x) => x.id === e.source);
          const v = this.creeps.get(e.target);
          if (!tw || !v) break;
          if (tw.unit.ranged || e.skill) {
            const shot = this.add.circle(tw.x, tw.y + TOP - 20, e.skill ? 11 : 7, hex(ELEMENT_COLOR[tw.unit.element])).setDepth(3000);
            this.tweens.add({ targets: shot, x: v.body.x, y: v.body.y, duration: 160 / this.speed, onComplete: () => shot.destroy() });
          } else {
            const c = this.towers.get(tw.id)!;
            const dx = Math.sign(v.body.x - c.x) * 18;
            this.tweens.add({ targets: c, x: tw.x + dx, duration: 70 / this.speed, yoyo: true });
          }
          v.sprite.setTint(0xff9a9a);
          this.time.delayedCall(60, () => v.sprite.clearTint());
          if (e.crit || e.skill) {
            const n = this.text(v.body.x, v.body.y - 40, e.amount.toLocaleString('fr-FR'), e.skill ? 30 : 24, e.crit ? '#ffe27a' : '#ffffff').setDepth(4000);
            this.tweens.add({ targets: n, y: n.y - 40, alpha: 0, duration: 600, onComplete: () => n.destroy() });
          }
          break;
        }
        case 'skill': {
          const tw = this.battle.towers.find((x) => x.id === e.source);
          if (!tw) break;
          const flash = this.add.circle(tw.x, tw.y + TOP, tw.range, 0xffe27a, 0.18).setStrokeStyle(4, 0xffe27a, 0.8).setDepth(2000);
          this.tweens.add({ targets: flash, alpha: 0, duration: 500, onComplete: () => flash.destroy() });
          const name = this.text(tw.x, tw.y + TOP - 80, t(`skill.${e.skill}`), 26, '#ffe27a').setDepth(4000);
          this.tweens.add({ targets: name, y: name.y - 30, alpha: 0, delay: 400, duration: 400, onComplete: () => name.destroy() });
          break;
        }
        case 'death': {
          const v = this.creeps.get(e.creep);
          if (!v) break;
          this.creeps.delete(e.creep);
          this.tweens.add({ targets: v.body, alpha: 0, scale: 0.6, duration: 250, onComplete: () => v.body.destroy() });
          break;
        }
        case 'leak': {
          const v = this.creeps.get(e.creep);
          v?.body.destroy();
          this.creeps.delete(e.creep);
          this.cameras.main.shake(150, 0.006);
          this.livesText.setScale(1.3);
          this.tweens.add({ targets: this.livesText, scale: 1, duration: 250 });
          break;
        }
        case 'heal': {
          const [cx, cy] = DEFENSE_PATH[DEFENSE_PATH.length - 1]!;
          const n = this.text(cx, TOP + cy - 200, '+1 ♥', 30, '#5dff9a').setDepth(6000);
          this.tweens.add({ targets: n, y: n.y - 40, alpha: 0, duration: 700, onComplete: () => n.destroy() });
          break;
        }
        case 'wave': {
          const b = this.text(DEFENSE_W / 2, TOP + 300, `${t('battle.wave')} ${e.index + 1}`, 56).setDepth(6000).setScale(0.5);
          this.tweens.add({ targets: b, scale: 1, duration: 250, ease: 'Back.easeOut' });
          this.tweens.add({ targets: b, alpha: 0, delay: 700, duration: 300, onComplete: () => b.destroy() });
          break;
        }
        case 'end':
          this.end(e.lives);
          break;
      }
    }
  }

  private end(lives: number) {
    if (this.finished) return;
    this.finished = true;
    const stars = defenseStars(lives);
    const panel = this.add.graphics().setDepth(7000);
    panel.fillStyle(0x000000, 0.55).fillRect(0, 0, DEFENSE_W, DEF_H);
    this.text(DEFENSE_W / 2, DEF_H / 2 - 60, stars ? t('result.victory') : t('result.defeat'), 72, stars ? '#ffe27a' : '#ff8a8a').setDepth(7001);
    this.text(DEFENSE_W / 2, DEF_H / 2 + 30, '★'.repeat(stars) + '☆'.repeat(3 - stars), 64, '#ffe27a').setDepth(7001);
    this.time.delayedCall(1600, () => this.done(lives));
  }

  update(_time: number, delta: number) {
    if (this.finished) return;
    this.acc = Math.min(this.acc + delta * this.speed, 1500);
    while (this.acc >= TICK_MS && !this.battle.over) {
      this.acc -= TICK_MS;
      this.handle(this.battle.step());
    }
    // Les monstres glissent vers leur position (mouvement fluide entre deux tours).
    for (const c of this.battle.creeps) {
      const v = this.creeps.get(c.id);
      if (!v) continue;
      v.body.x += (c.x - v.body.x) * 0.35;
      v.body.y += (c.y + TOP - v.body.y) * 0.35;
      v.body.setDepth(v.body.y);
      const w = c.boss ? 90 : 56;
      const y = c.boss ? -78 : -48;
      v.bar.clear();
      v.bar.fillStyle(0x000000, 0.6).fillRect(-w / 2 - 2, y - 2, w + 4, 11);
      v.bar.fillStyle(0xe5484d).fillRect(-w / 2, y, w * (c.hp / c.maxHp), 7);
      v.sprite.setAngle(c.stun > 0 ? Math.sin(this.time.now / 60) * 10 : 0);
      v.sprite.setTint(c.slow > 0 ? 0x9fd8ff : 0xffffff);
    }
    this.refreshHud();
    if (this.battle.lives < DEFENSE_LIVES / 2) this.livesText.setColor('#ff4d5e');
  }
}

/** Lance une partie de Défense dans le cadre donné. Renvoie la fonction qui l'arrête. */
export function runDefense(parent: HTMLElement, setup: DefenseSetup, done: (lives: number) => void): () => void {
  const game = new Phaser.Game({
    type: Phaser.AUTO,
    parent,
    width: DEFENSE_W,
    height: DEF_H,
    backgroundColor: '#14162b',
    scale: { mode: Phaser.Scale.FIT, autoCenter: Phaser.Scale.CENTER_BOTH },
    scene: [],
    banner: false,
  });
  game.scene.add('defense', DefenseScene, true, {
    setup,
    done: (lives: number) => {
      done(lives);
      setTimeout(() => game.destroy(true), 0);
    },
  } satisfies DefenseData);
  return () => game.destroy(true);
}
