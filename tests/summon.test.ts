import { describe, expect, it } from 'vitest';
import { LEGENDARY_PITY, SUMMON_RATES } from '../src/core/data/summon';
import { createRng } from '../src/core/rng';
import { summonOne } from '../src/core/summon';

describe('invocations', () => {
  it('les chances affichées font 100 %', () => {
    const total = Object.values(SUMMON_RATES).reduce((a, b) => a + b, 0);
    expect(total).toBeCloseTo(1, 10);
  });

  it('un Légendaire au plus tard toutes les 40 invocations', () => {
    const rng = createRng(42);
    const state = { pity: 0 };
    let sinceLast = 0;
    for (let i = 0; i < 20000; i++) {
      sinceLast += 1;
      if (summonOne(state, rng).rarity === 'legendary') sinceLast = 0;
      expect(sinceLast).toBeLessThan(LEGENDARY_PITY);
    }
  });

  it('même graine, mêmes tirages', () => {
    const a = createRng(7);
    const b = createRng(7);
    const sa = { pity: 0 };
    const sb = { pity: 0 };
    for (let i = 0; i < 100; i++) expect(summonOne(sa, a).id).toBe(summonOne(sb, b).id);
  });
});
