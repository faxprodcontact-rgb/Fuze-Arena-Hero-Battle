// Fabrique les combattants du moteur à partir des héros d'un joueur et des monstres.
import { heroDef } from '../data/heroes';
import { monsterDef } from '../data/monsters';
import { BASE_POWER, LEVEL_GAIN, STAR_MULT } from '../data/stats';
import type { Element, Hero } from '../types';
import type { Slot, UnitInit } from './types';

/** Multiplicateur de force d'un héros : niveau × étoiles × équipement (bonus en %). */
export function heroMultiplier(hero: Hero, gearPct = 0): number {
  return (1 + LEVEL_GAIN * (hero.level - 1)) * (STAR_MULT[hero.stars] ?? 1) * (1 + gearPct / 100);
}

/** Force affichée d'un héros (même échelle que les simulations : 100 au niveau 1, ★1, sans équipement). */
export function heroPowerWithGear(hero: Hero, gearPct = 0): number {
  return Math.round(BASE_POWER * heroMultiplier(hero, gearPct));
}

/** La défense monte moins vite que les PV et l'attaque, sinon les gros niveaux deviendraient intouchables. */
function scaledDef(def: number, mult: number): number {
  return Math.round(def * Math.pow(mult, 0.25));
}

export function heroToUnit(hero: Hero, slot: Slot, gearPct = 0): UnitInit {
  const d = heroDef(hero.defId);
  const mult = heroMultiplier(hero, gearPct);
  return {
    id: `h-${hero.uid}`,
    defId: d.id,
    side: 'hero',
    slot,
    element: d.element,
    maxHp: Math.round(d.hp * mult),
    atk: Math.round(d.atk * mult),
    def: scaledDef(d.def, mult),
    interval: d.interval,
    ranged: d.ranged,
    skill: d.skill,
    talent: d.talent,
  };
}

export function monsterToUnit(monsterId: string, slot: Slot, element: Element, mult: number, id: string): UnitInit {
  const m = monsterDef(monsterId);
  return {
    id,
    defId: m.id,
    side: 'enemy',
    slot,
    element,
    maxHp: Math.round(m.hp * mult),
    atk: Math.round(m.atk * mult),
    def: scaledDef(m.def, mult),
    interval: m.interval,
    ranged: m.ranged,
    skill: m.skill,
    boss: m.boss,
  };
}
