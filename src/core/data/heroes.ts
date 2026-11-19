// Liste provisoire des 72 héros du lancement : 6 factions × 12 héros
// (2 Communs, 3 Rares, 4 Épiques, 3 Légendaires). Les vrais noms viendront avec l'univers.
import { ELEMENTS, FACTIONS, ROLES, type Faction, type HeroDef, type Rarity } from '../types';

export const HEROES_PER_FACTION: Rarity[] = [
  'common', 'common',
  'rare', 'rare', 'rare',
  'epic', 'epic', 'epic', 'epic',
  'legendary', 'legendary', 'legendary',
];

export const HEROES: HeroDef[] = FACTIONS.flatMap((faction, f) =>
  HEROES_PER_FACTION.map((rarity, i) => ({
    id: `${faction}-${i + 1}`,
    faction,
    rarity,
    element: ELEMENTS[(f + i) % ELEMENTS.length]!,
    role: ROLES[i % ROLES.length]!,
  })),
);

const BY_ID = new Map(HEROES.map((h) => [h.id, h]));

export function heroDef(id: string): HeroDef {
  const def = BY_ID.get(id);
  if (!def) throw new Error(`Héros inconnu : ${id}`);
  return def;
}

/** Les héros d'une faction et d'une rareté, dans l'ordre de la liste. */
export function heroesOf(faction: Faction, rarity: Rarity): HeroDef[] {
  return HEROES.filter((h) => h.faction === faction && h.rarity === rarity);
}
