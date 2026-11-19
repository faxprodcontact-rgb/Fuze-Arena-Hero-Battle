// Règle la force des monstres : une section dont la force vaut la puissance demandée
// doit gagner environ 2 fois sur 3.   npx tsx simulations/combat.ts
import { Battle } from '../src/core/battle/engine';
import { heroPowerWithGear, heroToUnit } from '../src/core/battle/units';
import type { Slot } from '../src/core/battle/types';
import { stagePower } from '../src/core/data/campaign';
import { heroesOf } from '../src/core/data/heroes';
import { BALANCE, campaignWaves, slotsAt } from '../src/core/stages';
import type { Hero } from '../src/core/types';

/** Une section équilibrée : protecteur devant, attaquants, soigneur et soutien derrière. */
const LINEUP: [string, Slot][] = [
  [heroesOf('knights', 'epic')[0]!.id, 0], // protecteur
  [heroesOf('mages', 'epic')[1]!.id, 1], // attaquant
  [heroesOf('demons', 'epic')[2]!.id, 3], // soutien
  [heroesOf('angels', 'epic')[3]!.id, 4], // soigneur
  [heroesOf('assassins', 'legendary')[0]!.id, 2], // attaquant
];
const ORDER: Slot[][] = [[2], [0, 3], [0, 2, 3], [0, 1, 2, 3], [0, 1, 2, 3, 4]];

export function teamFor(stage: number, powerRatio = 1): { heroes: Hero[]; slots: Slot[] } {
  const count = slotsAt(stage - 1);
  const target = (stagePower(stage) * powerRatio) / count;
  const heroes: Hero[] = [];
  for (let i = 0; i < count; i++) {
    const h: Hero = { uid: i + 1, defId: LINEUP[i]!.at(0) as string, stars: 3, level: 1 };
    while (heroPowerWithGear(h) < target && h.level < 2000) h.level += 1;
    heroes.push(h);
  }
  return { heroes, slots: ORDER[count - 1]! };
}

export function winRate(stage: number, powerRatio = 1, seeds = 24): number {
  const { heroes, slots } = teamFor(stage, powerRatio);
  let wins = 0;
  for (let s = 0; s < seeds; s++) {
    const b = new Battle({ heroes: heroes.map((h, i) => heroToUnit(h, slots[i]!)), waves: campaignWaves(stage), seed: s + 1, auto: true });
    while (!b.over) b.step();
    if (b.win) wins += 1;
  }
  return wins / seeds;
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const [scale, exp, boss] = process.argv.slice(2).map(Number);
  if (scale) BALANCE.monsterScale = scale;
  if (exp !== undefined && !Number.isNaN(exp)) BALANCE.waveExponent = exp;
  if (boss) BALANCE.bossFactor = boss;
  const groups: Record<string, number[]> = {
    '1 vague': [5, 205, 405, 805, 1005],
    '2 vagues': [20, 220, 420, 820, 1020],
    '3 vagues': [35, 235, 435, 835, 1035],
    boss: [40, 240, 440, 840, 1040],
  };
  for (const [name, stages] of Object.entries(groups)) {
    const rates = stages.map((st) => winRate(st, 1, 12));
    const avg = rates.reduce((a, b) => a + b, 0) / rates.length;
    console.log(`${name.padEnd(9)} moyenne ${Math.round(avg * 100)}%  (${rates.map((r) => Math.round(r * 100)).join(' / ')})`);
  }
}
