import { describe, expect, it } from 'vitest';
import { Battle } from '../src/core/battle/engine';
import { heroToUnit } from '../src/core/battle/units';
import { ENERGY_MAX, type BattleSetup, type Slot } from '../src/core/battle/types';
import { hasAdvantage } from '../src/core/data/elements';
import { heroesOf } from '../src/core/data/heroes';
import { campaignWaves } from '../src/core/stages';
import type { Hero } from '../src/core/types';

const team: [string, Slot][] = [
  [heroesOf('knights', 'epic')[0]!.id, 0],
  [heroesOf('demons', 'epic')[1]!.id, 1],
  [heroesOf('mages', 'epic')[1]!.id, 2],
  [heroesOf('angels', 'epic')[3]!.id, 3],
  [heroesOf('myths', 'epic')[2]!.id, 4],
];

const setup = (seed: number, auto = true): BattleSetup => ({
  heroes: team.map(([defId, slot], i) => heroToUnit({ uid: i + 1, defId, stars: 4, level: 60 } as Hero, slot)),
  waves: campaignWaves(300),
  seed,
  auto,
});

function run(battle: Battle) {
  while (!battle.over) battle.step();
  return battle;
}

describe('moteur de combat', () => {
  it('même graine = même combat', () => {
    const a = run(new Battle(setup(42)));
    const b = run(new Battle(setup(42)));
    expect(a.tick).toBe(b.tick);
    expect(a.win).toBe(b.win);
    expect(a.heroes.map((h) => h.hp)).toEqual(b.heroes.map((h) => h.hp));
  });

  it('le serveur peut rejouer un combat manuel à partir des choix du joueur', () => {
    const live = new Battle(setup(7, false));
    while (!live.over) {
      for (const h of live.heroes) if (h.hp > 0 && h.energy >= ENERGY_MAX && live.tick % 3 === 0) live.requestSkill(h.id);
      if (live.tick === 150) live.setAuto(true);
      live.step();
    }
    const replayed = Battle.replay(setup(7, false), live.inputs);
    expect(replayed.tick).toBe(live.tick);
    expect(replayed.win).toBe(live.win);
    expect(replayed.heroes.map((h) => h.hp)).toEqual(live.heroes.map((h) => h.hp));
    expect(replayed.enemies.map((e) => e.hp)).toEqual(live.enemies.map((e) => e.hp));
  });

  it('une compétence ne part pas avant que la jauge soit pleine', () => {
    const battle = new Battle(setup(1, false));
    expect(battle.requestSkill(battle.heroes[0]!.id)).toBe(false);
  });

  it('les ennemis frappent d’abord la défense', () => {
    const battle = new Battle(setup(3));
    const back = battle.heroes.find((h) => h.slot === 3)!;
    for (let i = 0; i < 30; i++) battle.step();
    const front = battle.heroes.filter((h) => h.slot <= 1);
    expect(front.some((h) => h.hp < h.maxHp)).toBe(true);
    expect(back.hp).toBe(back.maxHp);
  });

  it('cycle des éléments', () => {
    expect(hasAdvantage('water', 'fire')).toBe(true);
    expect(hasAdvantage('fire', 'wind')).toBe(true);
    expect(hasAdvantage('wind', 'earth')).toBe(true);
    expect(hasAdvantage('earth', 'water')).toBe(true);
    expect(hasAdvantage('fire', 'water')).toBe(false);
  });

  it('les 1 200 niveaux de campagne se construisent', () => {
    for (let s = 1; s <= 1200; s++) expect(campaignWaves(s).length).toBeGreaterThan(0);
  });
});
