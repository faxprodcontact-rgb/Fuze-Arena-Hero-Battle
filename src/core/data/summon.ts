// Chances d'invocation (affichées aux joueurs, obligation Apple / Google).
import type { Rarity } from '../types';

export const SUMMON_RATES: Record<Rarity, number> = {
  common: 0.45,
  rare: 0.35,
  epic: 0.165,
  legendary: 0.035,
};

/** Un Légendaire est garanti au plus tard à cette invocation (le compteur repart à zéro à chaque Légendaire). */
export const LEGENDARY_PITY = 40;

/**
 * Invocation simple : seulement des Communs et des Rares, pour nourrir les fusions.
 * Gagnée en jouant (butin, quêtes), jamais vendue.
 */
export const BASIC_SUMMON_RATES: Partial<Record<Rarity, number>> = {
  common: 0.6,
  rare: 0.4,
};
