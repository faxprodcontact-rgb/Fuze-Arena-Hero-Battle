import { describe, expect, it } from 'vitest';
import { applyFusion, isValidFusion, planFusion } from '../src/core/fusion';
import { LADDER } from '../src/core/data/stars';
import { heroesOf, heroesOfElement } from '../src/core/data/heroes';
import type { Hero } from '../src/core/types';

let uid = 1;
const id = (faction: Parameters<typeof heroesOf>[0], rarity: Parameters<typeof heroesOf>[1], n = 0) =>
  heroesOf(faction, rarity)[n]!.id;
const hero = (defId: string, stars: number, level = 1): Hero => ({ uid: uid++, defId, stars, level });
const el = (element: Parameters<typeof heroesOfElement>[0], rarity: Parameters<typeof heroesOfElement>[1], n = 0) =>
  heroesOfElement(element, rarity)[n]!.id;

describe('fusion des Communs et des Rares', () => {
  it('3 héros identiques donnent +1 étoile', () => {
    const roster = [hero(id('knights', 'common'), 1), hero(id('knights', 'common'), 1), hero(id('knights', 'common'), 1)];
    const plan = planFusion(roster, roster[0]!.uid);
    expect(plan?.newStars).toBe(2);
    expect(isValidFusion(roster, plan!, 0)).toBe(true);
    expect(applyFusion(roster, plan!).roster).toHaveLength(1);
  });

  it('refuse des étoiles différentes et le plafond de rareté', () => {
    const mixed = [hero(id('knights', 'common'), 1), hero(id('knights', 'common'), 1), hero(id('knights', 'common'), 2)];
    expect(planFusion(mixed, mixed[0]!.uid)).toBeNull();
    const capped = [hero(id('knights', 'common'), 3), hero(id('knights', 'common'), 3), hero(id('knights', 'common'), 3)];
    expect(planFusion(capped, capped[0]!.uid)).toBeNull();
  });
});

describe('fusion des Épiques et des Légendaires', () => {
  it('★3 → ★4 : 1 copie + 2 héros ★3 du même élément', () => {
    const target = hero(el('fire', 'epic'), 3);
    const roster = [target, hero(el('fire', 'epic'), 3), hero(el('fire', 'common'), 3), hero(el('fire', 'rare'), 3), hero(el('water', 'rare'), 3)];
    const plan = planFusion(roster, target.uid);
    expect(plan).not.toBeNull();
    expect(plan!.consumed).toHaveLength(1 + LADDER[4]!.fodderCount);
    expect(isValidFusion(roster, plan!, 0)).toBe(true);
  });

  it('refuse un héros d’un autre élément', () => {
    const target = hero(el('fire', 'epic'), 3);
    const copy = hero(el('fire', 'epic'), 3);
    const roster = [target, copy, hero(el('water', 'common'), 3), hero(el('earth', 'rare'), 3)];
    expect(planFusion(roster, target.uid)).toBeNull();
    const cheat = { targetUid: target.uid, consumed: roster.slice(1).map((h) => h.uid), crystals: 0, newStars: 4 };
    expect(isValidFusion(roster, cheat, 0)).toBe(false);
  });

  it('ne sacrifie jamais un héros protégé ni un Légendaire', () => {
    const target = hero(el('wind', 'epic'), 3);
    const kept = hero(el('wind', 'common'), 3);
    const roster = [target, hero(el('wind', 'epic'), 3), kept, hero(el('wind', 'rare'), 3), hero(el('wind', 'legendary'), 3)];
    expect(planFusion(roster, target.uid, { protect: new Set([kept.uid]) })).toBeNull();
  });

  it('l’éveil Mythique demande des cristaux', () => {
    const target = hero(id('myths', 'legendary'), 10);
    const roster = [target, hero(id('myths', 'legendary'), 4), hero(id('myths', 'legendary'), 4)];
    expect(planFusion(roster, target.uid, { crystalsOwned: 0 })).toBeNull();
    const plan = planFusion(roster, target.uid, { crystalsOwned: LADDER[11]!.crystals });
    expect(plan?.newStars).toBe(11);
  });

  it('rend les niveaux et l’équipement des héros sacrifiés', () => {
    const roster = [hero(id('knights', 'common'), 1, 10), hero(id('knights', 'common'), 1, 5), hero(id('knights', 'common'), 1, 1)];
    const plan = planFusion(roster, roster[0]!.uid)!;
    expect(applyFusion(roster, plan).refund).toBeGreaterThan(0);
  });
});
