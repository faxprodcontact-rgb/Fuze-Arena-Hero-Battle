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

/** Les trois portails : simple (Communs et Rares), normal, et spécial (le groupe mis en avant). */
export type SummonKind = 'basic' | 'normal' | 'featured';

/**
 * Le portail spécial (demande du propriétaire, 27/11/2026) : même prix, mêmes chances par rareté et même compteur de
 * Légendaire garanti que le portail normal ; seuls les Légendaires changent : on les tire parmi `heroes` (tous à parts
 * égales) au lieu de tous les Légendaires. Les Épiques, Rares et Communs sont ceux du portail normal.
 * À CHANGER À CHAQUE MISE À JOUR : un nouvel `id` (jamais réutilisé), le groupe (`heroes`, des Légendaires uniquement),
 * son nom (`summon.banner.<id>` dans src/game/i18n.ts) et ses couleurs au repos.
 */
export interface FeaturedBanner {
  id: string;
  /** Les héros mis en avant : tous Légendaires (vérifié par tests/portail-special.test.ts). */
  heroes: readonly string[];
  /** La lumière du portail au repos : [principale, claire, profonde], puis les éclats qui tournent autour. */
  tone: readonly [string, string, string];
  sparks: readonly string[];
}

export const FEATURED_BANNER: FeaturedBanner = {
  id: 'dragons-2711',
  // Elvyn (eau), Brasyr (feu), Rocvar (terre), Venthys (vent) : les 4 dragons
  heroes: ['angels-6', 'dragon-feu', 'dragon-terre', 'dragon-vent'],
  // braise et or, avec un éclat de chacun des 4 éléments
  tone: ['#ff6a1f', '#ffe08a', '#4a1204'],
  sparks: ['#5fc8ff', '#ff5a2a', '#9be05a', '#ffd34a'],
};
