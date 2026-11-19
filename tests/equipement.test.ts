// Équipement : chaque emplacement donne sa statistique, les objets Bleus et + ont des secondaires, panoplie à 4 pièces.
import { describe, expect, it } from 'vitest';
import { SET_BONUS, gearStats, itemMain, itemSubs, type Item } from '../src/core/data/items';

const it_ = (slot: Item['slot'], rarity: number, set?: Item['set']): Item => ({ uid: 1, slot, rarity, tier: 0, set });

describe('équipement', () => {
  it('statistique principale selon l’emplacement', () => {
    const g = gearStats([{ item: it_('weapon', 3), level: 0 }, { item: it_('armor', 3), level: 0 }]);
    expect(g.atk).toBeCloseTo(itemMain(it_('weapon', 3)) / 100);
    expect(g.hp).toBeCloseTo(itemMain(it_('armor', 3)) / 100);
    expect(g.speed).toBe(0);
  });

  it('secondaires à partir des objets Bleus', () => {
    expect(itemSubs(it_('weapon', 1))).toEqual({});
    expect(itemSubs(it_('weapon', 2)).crit).toBeGreaterThan(0);
    expect(itemSubs(it_('boots', 5)).dodge).toBeGreaterThan(0);
  });

  it('panoplie complète = bonus', () => {
    const four = (['weapon', 'armor', 'helmet', 'boots'] as const).map((slot) => ({ item: it_(slot, 2, 'vampire'), level: 0 }));
    expect(gearStats(four).lifesteal).toBeCloseTo(SET_BONUS.vampire.lifesteal!);
    expect(gearStats(four.slice(0, 3)).lifesteal).toBe(0);
  });
});
