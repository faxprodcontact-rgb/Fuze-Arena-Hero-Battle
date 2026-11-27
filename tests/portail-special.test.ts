// Le portail spécial (27/11/2026) : même prix, mêmes chances par rareté et même Légendaire garanti que le portail
// normal ; un Légendaire est toujours un des héros mis en avant (aujourd'hui les 4 dragons). Le reste ne change pas.
import { beforeEach, describe, expect, it } from 'vitest';
import { HEROES, heroDef } from '../src/core/data/heroes';
import { FEATURED_BANNER, LEGENDARY_PITY, SUMMON_RATES } from '../src/core/data/summon';
import { createRng } from '../src/core/rng';
import { featuredLegends, summonFeatured, summonOne } from '../src/core/summon';
import { summon, summonCost } from '../src/game/state/actions';
import { fresh, getState, replaceState, restore } from '../src/game/state/store';

describe('le portail spécial', () => {
  beforeEach(() => replaceState(fresh()));

  it('met en avant les 4 dragons, tous Légendaires', () => {
    expect([...FEATURED_BANNER.heroes].sort()).toEqual(['angels-6', 'dragon-feu', 'dragon-terre', 'dragon-vent']);
    for (const id of FEATURED_BANNER.heroes) expect(heroDef(id).rarity).toBe('legendary');
    expect(featuredLegends().length).toBe(FEATURED_BANNER.heroes.length);
    expect(new Set(FEATURED_BANNER.heroes).size).toBe(FEATURED_BANNER.heroes.length);
  });

  it('un Légendaire est toujours un dragon ; les autres raretés sont celles du portail normal', () => {
    const rng = createRng(3);
    const state = { pity: 0 };
    const counts: Record<string, number> = {};
    const seen = new Set<string>();
    const N = 40000;
    for (let i = 0; i < N; i++) {
      const h = summonFeatured(state, rng);
      counts[h.rarity] = (counts[h.rarity] ?? 0) + 1;
      seen.add(h.id);
      if (h.rarity === 'legendary') expect(FEATURED_BANNER.heroes).toContain(h.id);
    }
    // chaque dragon sort, et tous les Épiques, Rares et Communs du jeu restent possibles
    for (const id of FEATURED_BANNER.heroes) expect(seen.has(id)).toBe(true);
    for (const h of HEROES.filter((x) => x.rarity !== 'legendary')) expect(seen.has(h.id)).toBe(true);
    // aucun autre Légendaire
    for (const h of HEROES.filter((x) => x.rarity === 'legendary' && !FEATURED_BANNER.heroes.includes(x.id))) expect(seen.has(h.id)).toBe(false);
    // mêmes parts par rareté que le portail normal (à 1 point près ; le Légendaire garanti en ajoute un peu)
    for (const r of ['common', 'rare', 'epic'] as const) expect(Math.abs((counts[r] ?? 0) / N - SUMMON_RATES[r])).toBeLessThan(0.01);
  });

  it('même compteur et même tirage de rareté que le portail normal', () => {
    // même graine : la rareté de chaque tirage est la même dans les deux portails, seul le Légendaire change
    const a = createRng(9), b = createRng(9);
    const sa = { pity: 0 }, sb = { pity: 0 };
    for (let i = 0; i < 3000; i++) {
      const n = summonOne(sa, a), f = summonFeatured(sb, b);
      expect(f.rarity).toBe(n.rarity);
      expect(sb.pity).toBe(sa.pity);
    }
    // le Légendaire garanti : au plus tard à la 40e invocation
    const s = { pity: LEGENDARY_PITY - 1 };
    expect(summonFeatured(s, () => 0.01).rarity).toBe('legendary');
    expect(s.pity).toBe(0);
  });

  it('coûte comme le portail normal et fait avancer le même compteur', () => {
    const st = getState();
    st.wallet.scrolls = 10;
    st.wallet.gems = 0;
    expect(summonCost('featured', 10)).toEqual(summonCost('normal', 10));
    const out = summon('featured', 10);
    expect(out?.length).toBe(10);
    expect(getState().wallet.scrolls).toBe(0);
    expect(getState().summon.total).toBe(10);
    expect(getState().summon.pity).toBeGreaterThanOrEqual(0);
    // sans parchemin : en gemmes, comme le normal
    expect(summonCost('featured', 1)).toEqual(summonCost('normal', 1));
    expect(summon('featured', 1)).toBeNull();
  });

  it('une vieille sauvegarde avec un dragon Épique (★3) reste valable : il passe à ★4, la naissance des Légendaires', () => {
    const old = fresh();
    old.heroes.push({ uid: 99, defId: 'dragon-feu', stars: 3, level: 20 });
    const s = restore(JSON.parse(JSON.stringify(old)));
    expect(s.heroes.find((h) => h.uid === 99)).toMatchObject({ defId: 'dragon-feu', stars: 4, level: 20 });
  });
});
