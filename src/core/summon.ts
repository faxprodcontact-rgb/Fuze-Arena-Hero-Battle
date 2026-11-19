// Invocations : tirage de la rareté, puis d'un héros de cette rareté.
import { HEROES } from './data/heroes';
import { BASIC_SUMMON_RATES, LEGENDARY_PITY, SUMMON_RATES } from './data/summon';
import { pick, type Rng } from './rng';
import { RARITIES, type HeroDef, type Rarity } from './types';

export interface SummonState {
  /** Invocations faites depuis le dernier Légendaire. */
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

export function summonOne(state: SummonState, rng: Rng): HeroDef {
  state.pity += 1;
  const rarity = state.pity >= LEGENDARY_PITY ? 'legendary' : rollRarity(rng);
  if (rarity === 'legendary') state.pity = 0;
  return pick(rng, BY_RARITY.get(rarity) ?? []);
}

/** Invocation simple : un Commun ou un Rare. */
export function summonBasic(rng: Rng): HeroDef {
  const rarity: Rarity = rng() < (BASIC_SUMMON_RATES.common ?? 0) ? 'common' : 'rare';
  return pick(rng, BY_RARITY.get(rarity) ?? []);
}
