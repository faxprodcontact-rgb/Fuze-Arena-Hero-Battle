// Échelle des étoiles, raretés et règles de fusion (validées dans le cahier de conception).
import type { Rarity } from '../types';

export const MAX_YELLOW = 5;
export const MAX_RED = 10;
export const MYTHIC_STARS = 11;

/** « ★3 », « ★2 rouge », « Mythique ». */
export function starLabel(stars: number): string {
  if (stars >= MYTHIC_STARS) return 'Mythique';
  if (stars > MAX_YELLOW) return `★${stars - MAX_YELLOW} rouge`;
  return `★${stars}`;
}

export interface RarityRule {
  /** Étoiles à la sortie de l'invocation. */
  bornStars: number;
  /** Étoiles maximum (11 = éveil Mythique). */
  maxStars: number;
  /** `triple` : 3 héros identiques = +1 étoile. `ladder` : copies + héros du même élément. */
  fusion: 'triple' | 'ladder';
}

export const RARITY_RULES: Record<Rarity, RarityRule> = {
  common: { bornStars: 1, maxStars: 3, fusion: 'triple' },
  rare: { bornStars: 2, maxStars: 4, fusion: 'triple' },
  epic: { bornStars: 3, maxStars: 5, fusion: 'ladder' },
  legendary: { bornStars: 4, maxStars: MYTHIC_STARS, fusion: 'ladder' },
};

export const TRIPLE_COUNT = 3;

export interface LadderStep {
  /** Copies du même héros, telles qu'elles sortent de l'invocation. */
  copies: number;
  /** Héros du même élément à sacrifier, et leur nombre d'étoiles exact. */
  fodderCount: number;
  fodderStars: number;
  /** Cristaux d'éveil (seulement pour Mythique). */
  crystals: number;
}

/** Coût pour ATTEINDRE ce nombre d'étoiles (Épique et Légendaire). */
export const LADDER: Record<number, LadderStep> = {
  4: { copies: 1, fodderCount: 2, fodderStars: 3, crystals: 0 },
  5: { copies: 1, fodderCount: 2, fodderStars: 4, crystals: 0 },
  // (28/11, grand réglage : les étoiles rouges étaient hors d'atteinte d'un joueur gratuit en 6 mois sur le vrai jeu)
  6: { copies: 1, fodderCount: 2, fodderStars: 5, crystals: 0 },
  7: { copies: 1, fodderCount: 2, fodderStars: 5, crystals: 0 },
  8: { copies: 2, fodderCount: 3, fodderStars: 5, crystals: 0 },
  9: { copies: 2, fodderCount: 4, fodderStars: 5, crystals: 0 },
  10: { copies: 3, fodderCount: 4, fodderStars: 5, crystals: 0 },
  11: { copies: 2, fodderCount: 0, fodderStars: 0, crystals: 500 },
};

/** Fragments nécessaires pour obtenir une copie d'un héros. */
export const FRAGMENTS_PER_COPY = 50;
