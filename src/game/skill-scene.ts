// Aperçu d'une compétence (fiche d'un héros) : le héros seul lance sa compétence contre trois monstres,
// puis la relance toutes les 2 secondes. Pas d'attaque de base, les monstres ne ripostent pas.
import Phaser from 'phaser';
import { Battle } from '../core/battle/engine';
import { ENERGY_MAX, type UnitInit } from '../core/battle/types';
import { monsterToUnit } from '../core/battle/units';
import { FightScene, W } from './fight-view';
import { killGame } from './game-kill';

export const SKILL_H = 470;
/** Vitesse des animations (moins de 1 = ralenti). */
const SPEED = 0.7;
/** Temps entre deux lancers de la compétence (au moins : le temps de son animation). */
const EVERY_MS = 2000;
/** Personne n'attaque tout seul : seule la compétence demandée est jouée. */
const NEVER = 1e9;

interface SkillData {
  hero: UnitInit;
}

export class SkillScene extends FightScene {
  private hero!: UnitInit;
  private wait = 600;

  constructor() {
    super('skill');
  }

  init(data: SkillData) {
    // Pas de talent de chef dans l'aperçu : on ne montre que la compétence.
    this.hero = { ...data.hero, slot: 2, talent: undefined };
    this.groundTop = 130;
  }

  protected preloadUnits() {
    return [this.hero, ...['goblin', 'wolf', 'golem'].map((defId) => ({ defId, element: this.hero.element }))];
  }

  protected arenaBox() {
    return { groundTop: 130, bottom: SKILL_H };
  }

  create() {
    this.drawArena(SKILL_H);
    this.cameras.main.setZoom(1.15).centerOn(375, 290);
    this.setup();
  }

  private setup() {
    const h = this.hero;
    // Monstres très solides : on voit les dégâts sans qu'ils tombent.
    const enemies = ([0, 2, 1] as const).map((slot, i) => {
      const m = monsterToUnit(['goblin', 'wolf', 'golem'][i]!, slot, h.element, 1, `m${i}`);
      return { ...m, maxHp: h.atk * 60, def: 0 };
    });
    this.battle = new Battle({ heroes: [h], waves: [enemies], seed: 1, auto: false });
    this.clearViews();
    for (const u of this.battle.heroes) this.addView(u);
    for (const u of this.battle.enemies) this.addView(u);
  }

  /** Remet tout le monde d'aplomb et fait lancer la compétence au héros. */
  private cast() {
    if (this.battle.over) this.setup(); // au bout d'une demi-heure, le combat atteint sa durée maximale
    for (const u of [...this.battle.heroes, ...this.battle.enemies]) {
      u.cooldown = NEVER;
      u.stun = 0;
      if (u.side === 'enemy') u.energy = 0;
      if (u.hp < u.maxHp * 0.4) u.hp = u.maxHp;
    }
    const hero = this.battle.heroes[0]!;
    hero.hp = hero.maxHp;
    hero.shield = 0;
    hero.energy = ENERGY_MAX;
    this.battle.requestSkill(hero.id);
    const events = this.battle.step().filter((e) => e.type === 'skill');
    this.handle(events, SPEED);
  }

  update(_time: number, delta: number) {
    this.wait -= delta;
    if (this.wait <= 0) {
      this.turnMs = undefined;
      this.cast();
      // une spéciale HD peut durer plus de 2 s au ralenti : on attend qu'elle soit finie
      this.wait = Math.max(EVERY_MS, (this.turnMs ?? 0) + 500);
    }
    this.syncUnits();
  }

  protected onEnd() {
    // L'aperçu ne se termine jamais.
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
  return () => killGame(game);
}
