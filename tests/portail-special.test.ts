// Le portail spécial (27/11/2026) : sa monnaie, le parchemin rouge ; mêmes chances par rareté et même Légendaire garanti que le portail
// normal ; un Légendaire est toujours un des héros mis en avant (aujourd'hui les 4 dragons). Le reste ne change pas.
import { beforeEach, describe, expect, it } from 'vitest';
import { HEROES, heroDef } from '../src/core/data/heroes';
import { FEATURED_BANNER, LEGENDARY_PITY, SUMMON_RATES } from '../src/core/data/summon';
import { createRng } from '../src/core/rng';
import { featuredLegends, summonFeatured, summonOne } from '../src/core/summon';
import { COLISEUM_SHOP } from '../src/core/data/coliseum';
import { MAILS } from '../src/core/data/mail';
import { DAILY_BOSS_TIERS, RED_SCROLLS, WEEKLY_CHESTS } from '../src/core/data/modes';
import { buyExchange, buyRedScroll, checkMail, claimMail, redScrollsBought, summon, summonCost } from '../src/game/state/actions';
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

  it('se paie en parchemins rouges (1 par invocation) et fait avancer le même compteur', () => {
    const st = getState();
    st.wallet.redScrolls = 10;
    st.wallet.scrolls = 50;
    st.wallet.gems = 99999;
    expect(summonCost('featured', 1)).toEqual({ currency: 'redScrolls', amount: 1 });
    expect(summonCost('featured', 10)).toEqual({ currency: 'redScrolls', amount: 10 });
    const out = summon('featured', 10);
    expect(out?.length).toBe(10);
    expect(getState().wallet.redScrolls).toBe(0);
    // ni parchemins ni gemmes : seulement des parchemins rouges
    expect(getState().wallet.scrolls).toBe(50);
    expect(getState().wallet.gems).toBe(99999);
    expect(getState().summon.total).toBe(10);
    expect(summon('featured', 1)).toBeNull();
  });

  it('une vieille sauvegarde démarre avec 0 parchemin rouge, et le courrier en offre 10', () => {
    const old = fresh() as unknown as { wallet: Record<string, number> };
    delete old.wallet.redScrolls;
    const s = restore(JSON.parse(JSON.stringify(old)));
    expect(s.wallet.redScrolls).toBe(0);
    replaceState(s);
    const mail = MAILS.find((m) => m.id === 'parchemins-rouges-2711')!;
    expect(mail.reward).toEqual({ redScrolls: 10 });
    expect(new Set(MAILS.map((m) => m.id)).size).toBe(MAILS.length);
    checkMail();
    expect(claimMail('parchemins-rouges-2711').currencies.redScrolls).toBe(10);
    expect(getState().wallet.redScrolls).toBe(10);
  });

  it('où gagner des parchemins rouges : boss du jour, coffre de la semaine, Colisée, boutique (limitée)', () => {
    expect(DAILY_BOSS_TIERS[DAILY_BOSS_TIERS.length - 1]!.redScrolls).toBe(1);
    expect(WEEKLY_CHESTS[WEEKLY_CHESTS.length - 1]!.reward.redScrolls).toBe(1);
    expect(RED_SCROLLS.perChapter).toBeGreaterThan(0);
    // Colisée : contre des insignes
    const st = getState();
    const red = COLISEUM_SHOP.find((x) => x.reward.redScrolls)!;
    st.wallet.badge = red.cost;
    expect(buyExchange('coliseum', red.id)?.currencies.redScrolls).toBe(1);
    // boutique : contre des gemmes, au plus RED_SCROLLS.gemsPerWeek par semaine
    st.wallet.gems = RED_SCROLLS.gems * (RED_SCROLLS.gemsPerWeek + 2);
    for (let i = 0; i < RED_SCROLLS.gemsPerWeek; i++) expect(buyRedScroll()?.currencies.redScrolls).toBe(1);
    expect(buyRedScroll()).toBeNull();
    expect(redScrollsBought()).toBe(RED_SCROLLS.gemsPerWeek);
    expect(getState().wallet.gems).toBe(RED_SCROLLS.gems * 2);
    expect(getState().wallet.redScrolls).toBe(1 + RED_SCROLLS.gemsPerWeek);
  });

  it('une vieille sauvegarde avec un dragon Épique (★3) reste valable : il passe à ★4, la naissance des Légendaires', () => {
    const old = fresh();
    old.heroes.push({ uid: 99, defId: 'dragon-feu', stars: 3, level: 20 });
    const s = restore(JSON.parse(JSON.stringify(old)));
    expect(s.heroes.find((h) => h.uid === 99)).toMatchObject({ defId: 'dragon-feu', stars: 4, level: 20 });
  });
});
