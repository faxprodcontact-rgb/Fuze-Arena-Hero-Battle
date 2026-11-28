// La force de chaque héros (28/11/2026, grand réglage) : des milliers de combats 5 contre 5 entre équipes tirées au
// hasard, tous au même niveau et aux mêmes étoiles ; pour chaque héros, la part des combats gagnés par les équipes où il
// est. Un héros « normal » est à 50 % ; visé : les Légendaires au-dessus, les Communs en dessous, et, dans une même
// rareté, des héros proches les uns des autres (aucun indispensable, aucun inutile).
//   npx tsx simulations/heros.ts [combats] [niveau] [étoiles]
import { Battle } from '../src/core/battle/engine';
import { heroToUnit } from '../src/core/battle/units';
import type { Slot, UnitInit } from '../src/core/battle/types';
import { HEROES } from '../src/core/data/heroes';
import { createRng, pick, type Rng } from '../src/core/rng';
import type { HeroDef } from '../src/core/types';

/** Où se place chaque rôle (comme la meilleure section du jeu) : devant les protecteurs et guerriers, derrière les autres. */
const FRONT = new Set(['protector', 'warrior']);

function team(rng: Rng, forced?: HeroDef): HeroDef[] {
  const out: HeroDef[] = forced ? [forced] : [];
  while (out.length < 5) {
    const h = pick(rng, HEROES);
    if (!out.includes(h)) out.push(h);
  }
  return out;
}

function units(defs: HeroDef[], side: 'hero' | 'enemy', level: number, stars: number): UnitInit[] {
  // devant (cases 0 à 2) les protecteurs et guerriers d'abord, puis le reste ; derrière (3, 4) les autres
  const sorted = [...defs].sort((a, b) => Number(FRONT.has(b.role)) - Number(FRONT.has(a.role)));
  return sorted.map((d, i) => {
    const u = heroToUnit({ uid: i + (side === 'hero' ? 1 : 100), defId: d.id, stars, level }, i as Slot);
    return side === 'hero' ? u : { ...u, id: `e-0-${i}`, side: 'enemy' as const };
  });
}

export function heroWinRates(fights: number, level: number, stars: number, seed = 1): Map<string, { win: number; n: number }> {
  const rng = createRng(seed);
  const stats = new Map(HEROES.map((h) => [h.id, { win: 0, n: 0 }]));
  for (let k = 0; k < fights; k++) {
    const a = team(rng);
    const b = team(rng);
    const battle = new Battle({ heroes: units(a, 'hero', level, stars), waves: [units(b, 'enemy', level, stars)], seed: k + 1, auto: true });
    while (!battle.over) battle.step();
    for (const h of a) { const st = stats.get(h.id)!; st.n += 1; if (battle.win) st.win += 1; }
    for (const h of b) { const st = stats.get(h.id)!; st.n += 1; if (!battle.win) st.win += 1; }
  }
  return stats;
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const fights = Number(process.argv[2] ?? 6000);
  const level = Number(process.argv[3] ?? 60);
  const stars = Number(process.argv[4] ?? 5);
  const stats = heroWinRates(fights, level, stars);
  const order = ['legendary', 'epic', 'rare', 'common'];
  const rows = HEROES.map((h) => ({ h, rate: stats.get(h.id)!.win / Math.max(1, stats.get(h.id)!.n) }))
    .sort((a, b) => order.indexOf(a.h.rarity) - order.indexOf(b.h.rarity) || b.rate - a.rate);
  let last = '';
  for (const { h, rate } of rows) {
    if (h.rarity !== last) {
      const group = rows.filter((r) => r.h.rarity === h.rarity);
      console.log(`\n${h.rarity} (moyenne ${Math.round((group.reduce((s, r) => s + r.rate, 0) / group.length) * 100)} %)`);
      last = h.rarity;
    }
    console.log(`  ${String(Math.round(rate * 100)).padStart(3)} %  ${h.name.padEnd(10)} ${h.id.padEnd(13)} ${h.element.padEnd(6)} ${h.role}`);
  }
}
