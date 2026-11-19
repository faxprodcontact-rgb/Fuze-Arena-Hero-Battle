import { describe, expect, it } from 'vitest';
import { applyFusion, isValidFusion, planFusion } from '../src/core/fusion';
import { LADDER } from '../src/core/data/stars';
import type { Hero } from '../src/core/types';

let uid = 1;
const hero = (defId: string, stars: number, level = 1): Hero => ({ uid: uid++, defId, stars, level });

describe('fusion des Communs et des Rares', () => {
  it('3 héros identiques donnent +1 étoile', () => {
    const roster = [hero('knights-1', 1), hero('knights-1', 1), hero('knights-1', 1)];
    const plan = planFusion(roster, roster[0]!.uid);
    expect(plan?.newStars).toBe(2);
    expect(isValidFusion(roster, plan!, 0)).toBe(true);
    expect(applyFusion(roster, plan!).roster).toHaveLength(1);
  });

  it('refuse des étoiles différentes et le plafond de rareté', () => {
    const mixed = [hero('knights-1', 1), hero('knights-1', 1), hero('knights-1', 2)];
    expect(planFusion(mixed, mixed[0]!.uid)).toBeNull();
    const capped = [hero('knights-1', 3), hero('knights-1', 3), hero('knights-1', 3)];
    expect(planFusion(capped, capped[0]!.uid)).toBeNull();
  });
});

describe('fusion des Épiques et des Légendaires', () => {
  it('★3 → ★4 : 1 copie + 2 héros ★3 de la même faction', () => {
    const target = hero('mages-3', 3);
    const roster = [target, hero('mages-3', 3), hero('mages-1', 3), hero('mages-2', 3), hero('demons-2', 3)];
    const plan = planFusion(roster, target.uid);
    expect(plan).not.toBeNull();
    expect(plan!.consumed).toHaveLength(1 + LADDER[4]!.fodderCount);
    expect(isValidFusion(roster, plan!, 0)).toBe(true);
  });

  it('refuse un héros d’une autre faction', () => {
    const target = hero('mages-3', 3);
    const copy = hero('mages-3', 3);
    const roster = [target, copy, hero('demons-1', 3), hero('demons-2', 3)];
    expect(planFusion(roster, target.uid)).toBeNull();
    const cheat = { targetUid: target.uid, consumed: roster.slice(1).map((h) => h.uid), crystals: 0, newStars: 4 };
    expect(isValidFusion(roster, cheat, 0)).toBe(false);
  });

  it('ne sacrifie jamais un héros protégé ni un Légendaire', () => {
    const target = hero('angels-3', 3);
    const kept = hero('angels-1', 3);
    const roster = [target, hero('angels-3', 3), kept, hero('angels-2', 3), hero('angels-5', 3)];
    expect(planFusion(roster, target.uid, { protect: new Set([kept.uid]) })).toBeNull();
  });

  it('l’éveil Mythique demande des cristaux', () => {
    const target = hero('myths-5', 10);
    const roster = [target, hero('myths-5', 4), hero('myths-5', 4)];
    expect(planFusion(roster, target.uid, { crystalsOwned: 0 })).toBeNull();
    const plan = planFusion(roster, target.uid, { crystalsOwned: LADDER[11]!.crystals });
    expect(plan?.newStars).toBe(11);
  });

  it('rend les niveaux et l’équipement des héros sacrifiés', () => {
    const roster = [hero('knights-1', 1, 10), hero('knights-1', 1, 5), hero('knights-1', 1, 1)];
    const plan = planFusion(roster, roster[0]!.uid)!;
    expect(applyFusion(roster, plan).refund).toBeGreaterThan(0);
  });
});
