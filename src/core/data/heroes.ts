// Liste provisoire des 30 héros du lancement : 6 factions × (1 Commun, 1 Rare, 2 Épiques, 1 Légendaire).
// Les vrais noms viendront avec l'univers ; ici seule la structure compte.
import { ELEMENTS, FACTIONS, ROLES, type HeroDef, type Rarity } from '../types';

const SLOTS: Rarity[] = ['common', 'rare', 'epic', 'epic', 'legendary'];

export const HEROES: HeroDef[] = FACTIONS.flatMap((faction, f) =>
  SLOTS.map((rarity, i) => ({
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
