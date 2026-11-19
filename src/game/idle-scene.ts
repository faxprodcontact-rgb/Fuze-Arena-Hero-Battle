// Le combat permanent de l'accueil : la section se bat seule contre des vagues sans fin.
// C'est l'image du butin hors ligne : chaque monstre vaincu lâche des pièces vers le coffre.
import Phaser from 'phaser';
import { Battle } from '../core/battle/engine';
import { TICK_MS, type UnitInit, type Unit } from '../core/battle/types';
import { FightScene, W } from './fight-view';

export const IDLE_H = 980;
const IDLE_SPEED = 1.2;

export interface IdleSetup {
  heroes: UnitInit[];
  waves: UnitInit[][];
}

interface IdleData {
  setup: () => IdleSetup;
}

export class IdleScene extends FightScene {
  private getSetup!: () => IdleSetup;
  private acc = 0;
  private pause = 0;
  private seed = 1;

  constructor() {
    super('idle');
  }

  init(data: IdleData) {
    this.getSetup = data.setup;
    this.groundTop = 560;
    this.xSquash = 0.8;
  }

  create() {
    this.drawArena(IDLE_H);
    this.startFight();
  }

  /** Nouveau combat : mêmes héros, nouvelles vagues. Les héros reviennent en pleine forme. */
  private startFight() {
    const { heroes, waves } = this.getSetup();
    this.seed += 1;
    this.battle = new Battle({ heroes, waves, seed: this.seed, auto: true });
    this.clearViews();
    for (const u of this.battle.heroes) this.addView(u);
    for (const u of this.battle.enemies) this.addView(u, true);
  }

  update(_time: number, delta: number) {
    if (this.pause > 0) {
      this.pause -= delta;
      if (this.pause <= 0) this.startFight();
      return;
    }
    this.acc = Math.min(this.acc + delta * IDLE_SPEED, 1000);
    while (this.acc >= TICK_MS && !this.battle.over) {
      this.acc -= TICK_MS;
      this.handle(this.battle.step(), IDLE_SPEED);
    }
    this.syncUnits();
  }

  protected onDeath(unit: Unit) {
    if (unit.side !== 'enemy') return;
    const v = this.views.get(unit.id);
    if (!v) return;
    // Des pièces jaillissent et filent vers le coffre (en bas à gauche).
    for (let i = 0; i < 4; i++) {
      const coin = this.add.circle(v.body.x, v.body.y - 20, 9, 0xffc94a).setStrokeStyle(3, 0xb8860b).setDepth(2500);
      this.tweens.add({
        targets: coin,
        x: { from: v.body.x + Phaser.Math.Between(-40, 40), to: 40 },
        y: { from: v.body.y - 60 - Phaser.Math.Between(0, 40), to: IDLE_H - 20 },
        scale: { from: 1.2, to: 0.5 },
        delay: i * 70,
        duration: 650,
        ease: 'Cubic.easeIn',
        onComplete: () => coin.destroy(),
      });
    }
  }

  protected onEnd() {
    this.pause = 900;
  }
}

/** Lance le combat permanent dans le cadre donné. Renvoie la fonction qui l'arrête. */
export function runIdle(parent: HTMLElement, setup: () => IdleSetup): () => void {
  const game = new Phaser.Game({
    type: Phaser.AUTO,
    parent,
    width: W,
    height: IDLE_H,
    transparent: true,
    scale: { mode: Phaser.Scale.ENVELOP, autoCenter: Phaser.Scale.CENTER_BOTH },
    scene: [],
    banner: false,
  });
  game.scene.add('idle', IdleScene, true, { setup } satisfies IdleData);
  return () => game.destroy(true);
}
