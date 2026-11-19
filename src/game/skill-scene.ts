// Aperçu d'une compétence (fiche d'un héros) : le héros seul lance sa compétence en boucle contre trois monstres.
import Phaser from 'phaser';
import { Battle } from '../core/battle/engine';
import { ENERGY_MAX, ENERGY_PER_ATTACK, TICK_MS, type UnitInit } from '../core/battle/types';
import { monsterToUnit } from '../core/battle/units';
import { FightScene, W } from './fight-view';

export const SKILL_H = 470;
const SPEED = 1;
/** Temps laissé pour voir l'effet de la compétence avant de recommencer. */
const AFTER_SKILL_MS = 2200;

interface SkillData {
  hero: UnitInit;
}

export class SkillScene extends FightScene {
  private hero!: UnitInit;
  private acc = 0;
  private wait = 0;
  private seed = 1;

  constructor() {
    super('skill');
  }

  init(data: SkillData) {
    // Pas de talent de chef dans l'aperçu : on ne montre que la compétence.
    this.hero = { ...data.hero, slot: 2, talent: undefined };
    this.groundTop = 130;
  }

  create() {
    this.drawArena(SKILL_H);
    // On zoome sur les combattants (le reste de l'arène est hors cadre).
    this.cameras.main.setZoom(1.45).centerOn(375, 300);
    this.start();
  }

  private start() {
    const h = this.hero;
    // Monstres solides mais peu dangereux : on voit les dégâts sans que le combat se termine.
    const enemies = ([0, 2, 1] as const).map((slot, i) => {
      const m = monsterToUnit(['goblin', 'wolf', 'golem'][i]!, slot, h.element, 1, `m${i}`);
      return { ...m, maxHp: h.atk * 40, atk: Math.max(1, Math.round(h.maxHp / 400)), def: 0 };
    });
    this.seed += 1;
    this.battle = new Battle({ heroes: [h], waves: [enemies], seed: this.seed, auto: true });
    // Une attaque normale d'abord, puis la jauge est pleine et la compétence part.
    this.battle.heroes[0]!.energy = ENERGY_MAX - ENERGY_PER_ATTACK;
    this.clearViews();
    for (const u of this.battle.heroes) this.addView(u);
    for (const u of this.battle.enemies) this.addView(u);
    this.wait = 0;
  }

  update(_time: number, delta: number) {
    if (this.wait > 0) {
      this.wait -= delta;
      if (this.wait <= 0) this.start();
    }
    this.acc = Math.min(this.acc + delta * SPEED, 1000);
    while (this.acc >= TICK_MS && !this.battle.over) {
      this.acc -= TICK_MS;
      const events = this.battle.step();
      if (this.wait <= 0 && events.some((e) => e.type === 'skill' && e.source === this.hero.id)) this.wait = AFTER_SKILL_MS;
      this.handle(events, SPEED);
    }
    this.syncUnits();
  }

  protected onEnd() {
    this.wait = 600;
  }
}

/** Lance l'aperçu dans le cadre donné. Renvoie la fonction qui l'arrête. */
export function runSkillPreview(parent: HTMLElement, hero: UnitInit): () => void {
  const game = new Phaser.Game({
    type: Phaser.AUTO,
    parent,
    width: W,
    height: SKILL_H,
    transparent: true,
    scale: { mode: Phaser.Scale.FIT, autoCenter: Phaser.Scale.CENTER_BOTH },
    scene: [],
    banner: false,
  });
  game.scene.add('skill', SkillScene, true, { hero } satisfies SkillData);
  return () => game.destroy(true);
}
