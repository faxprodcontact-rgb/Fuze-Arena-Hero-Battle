// Fabrique les combattants du moteur à partir des héros d'un joueur et des monstres.
import { AWAKEN_SKILL, AWAKEN_STARS, heroDef } from '../data/heroes';
import { monsterDef } from '../data/monsters';
import { BASE_POWER, LEVEL_GAIN, STAR_MULT } from '../data/stats';
import type { Element, Hero } from '../types';
import { applyStatMods } from './engine';
import type { Effect, SkillDef, Slot, StatMods, UnitInit } from './types';

/** Éveil (★10) : la compétence gagne en force. */
function awaken(skill: SkillDef): SkillDef {
  const up = (e: Effect): Effect =>
    e.type === 'damage' || e.type === 'shield' ? { ...e, power: Math.round(e.power * AWAKEN_SKILL * 100) / 100 }
      : e.type === 'heal' ? { ...e, power: e.power && Math.round(e.power * AWAKEN_SKILL * 100) / 100, pctMax: e.pctMax && e.pctMax * AWAKEN_SKILL }
        : e;
  return { id: skill.id, effects: skill.effects.map(up) };
}

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

/**
 * Le combattant d'un héros. `gear` = ce que donne son équipement : soit un pourcentage global (ancien calcul,
 * gardé pour les simulations), soit les vraies statistiques de ses objets (atq, PV, déf, vitesse, critique…).
 */
export function heroToUnit(hero: Hero, slot: Slot, gear: number | StatMods = 0): UnitInit {
  const d = heroDef(hero.defId);
  const mult = heroMultiplier(hero, typeof gear === 'number' ? gear : 0);
  const unit: UnitInit = {
    id: `h-${hero.uid}`,
    defId: d.id,
    side: 'hero',
    slot,
    element: d.element,
    maxHp: Math.round(d.hp * mult),
    atk: Math.round(d.atk * mult),
    def: scaledDef(d.def, mult),
    interval: d.interval,
    crit: d.crit,
    critDmg: d.critDmg,
    dodge: d.dodge,
    tenacity: d.tenacity,
    ranged: d.ranged,
    hitsBack: d.hitsBack,
    skill: hero.stars >= AWAKEN_STARS ? awaken(d.skill) : d.skill,
    // Les passifs se débloquent avec les étoiles.
    passives: d.passives.filter((p) => hero.stars >= p.stars).map((p) => p.passive),
    talent: d.talent,
    hero: true,
  };
  return typeof gear === 'number' ? unit : applyStatMods(unit, gear);
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
