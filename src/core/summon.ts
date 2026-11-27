// Invocations : tirage de la rareté, puis d'un héros de cette rareté.
import { HEROES, heroDef } from './data/heroes';
import { BASIC_SUMMON_RATES, FEATURED_BANNER, LEGENDARY_PITY, SUMMON_RATES, type FeaturedBanner } from './data/summon';
import { pick, type Rng } from './rng';
import { RARITIES, type HeroDef, type Rarity } from './types';

export interface SummonState {
  /** Invocations faites depuis le dernier Légendaire (le même compteur pour le portail normal et le spécial). */
  pity: number;
}

const BY_RARITY = new Map<Rarity, HeroDef[]>(
  RARITIES.map((r) => [r, HEROES.filter((h) => h.rarity === r)]),
);

export function rollRarity(rng: Rng): Rarity {
  let roll = rng();
  for (const rarity of RARITIES) {
    roll -= SUMMON_RATES[rarity];
    if (roll < 0) return rarity;
  }
  return 'common';
}

/** La rareté d'une invocation normale ou spéciale (avec le Légendaire garanti). */
function rollWithPity(state: SummonState, rng: Rng): Rarity {
  state.pity += 1;
  const rarity = state.pity >= LEGENDARY_PITY ? 'legendary' : rollRarity(rng);
  if (rarity === 'legendary') state.pity = 0;
  return rarity;
}

export function summonOne(state: SummonState, rng: Rng): HeroDef {
  return pick(rng, BY_RARITY.get(rollWithPity(state, rng)) ?? []);
}

/** Les Légendaires du portail spécial (ceux de la liste qui existent et sont bien Légendaires). */
export function featuredLegends(banner: FeaturedBanner = FEATURED_BANNER): HeroDef[] {
  return banner.heroes.map(heroDef).filter((h) => h.rarity === 'legendary');
}

/** Invocation spéciale : comme la normale, mais un Légendaire est toujours un des héros mis en avant. */
export function summonFeatured(state: SummonState, rng: Rng, banner: FeaturedBanner = FEATURED_BANNER): HeroDef {
  const rarity = rollWithPity(state, rng);
  return pick(rng, rarity === 'legendary' ? featuredLegends(banner) : BY_RARITY.get(rarity) ?? []);
}

/** Invocation simple : un Commun ou un Rare. */
export function summonBasic(rng: Rng): HeroDef {
  const rarity: Rarity = rng() < (BASIC_SUMMON_RATES.common ?? 0) ? 'common' : 'rare';
  return pick(rng, BY_RARITY.get(rarity) ?? []);
}
