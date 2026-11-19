// Calcul de la force d'un héros et d'une section.
import { BASE_POWER, GEAR_GAIN, LEVEL_GAIN, STAR_MULT } from './data/stats';
import { gearCost, levelCost } from './data/economy';
import type { Hero } from './types';

export function heroPower(hero: Hero): number {
  const starMult = STAR_MULT[hero.stars] ?? 0;
  return BASE_POWER * (1 + LEVEL_GAIN * (hero.level - 1)) * starMult * (1 + GEAR_GAIN * (hero.gear ?? 0));
}

export function teamPower(heroes: readonly Hero[]): number {
  return heroes.reduce((sum, h) => sum + heroPower(h), 0);
}

/** Les `slots` héros les plus forts. */
export function bestTeam(roster: readonly Hero[], slots: number): Hero[] {
  return [...roster].sort((a, b) => heroPower(b) - heroPower(a)).slice(0, slots);
}

/** Ressources dépensées pour monter un héros du niveau 1 à `level` (rendues s'il est sacrifié). */
export function levelRefund(level: number): number {
  let total = 0;
  for (let l = 1; l < level; l++) total += levelCost(l);
  return total;
}

/** Ressources dépensées pour l'équipement d'un héros (rendues s'il est sacrifié ou réinitialisé). */
export function gearRefund(gear: number): number {
  let total = 0;
  for (let g = 0; g < gear; g++) total += gearCost(g);
  return total;
}
