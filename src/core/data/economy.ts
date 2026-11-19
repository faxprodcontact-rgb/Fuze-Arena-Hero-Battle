// Économie de progression : coût des niveaux, butin, campagne.
// Valeurs réglées par simulations/progression.ts (voir docs/simulations.md).

/** Coût en ressources pour passer du niveau L au niveau L+1. */
export function levelCost(level: number): number {
  return Math.round(10 * 1.07 ** level);
}

/**
 * Coût pour améliorer l'équipement d'un héros d'un cran (de `gear` à `gear + 1`).
 * Dans les simulations, l'équipement est résumé par un seul niveau par héros.
 */
export function gearCost(gear: number): number {
  return Math.round(25 * 1.06 ** gear);
}

/** Butin hors ligne par heure, selon le niveau de campagne atteint. */
export function incomePerHour(stage: number): number {
  return 100 * 1.0016 ** stage;
}

export const OFFLINE_CAP_HOURS = 12;
/** Une victoire en campagne rapporte l'équivalent de ce nombre d'heures de butin. */
export const STAGE_REWARD_HOURS = 0.25;

export const STAGES_PER_CHAPTER = 40;
export const CAMPAIGN_STAGES = 1200;
/** Parchemins d'invocation donnés à la fin de chaque chapitre. */
export const CHAPTER_SUMMONS = 5;

/** Places de la section : la place n°i s'ouvre une fois ce niveau de campagne gagné. */
export const SLOT_UNLOCK_STAGES = [0, 4, 10, 20, 40];

/** Cristaux d'éveil : gagnés chaque jour une fois ce niveau de campagne atteint. */
export const CRYSTALS_FROM_STAGE = 900;
export const CRYSTALS_PER_DAY = 3;

/** Fragments du héros choisi, gagnés chaque jour dans les boutiques, à partir de ce jour. */
export const FRAGMENTS_FROM_DAY = 7;
export const FRAGMENTS_PER_DAY = 5;

/**
 * Héros jokers ★5 (tour, événements, guilde) : un tous les `JOKER_EVERY_DAYS` jours à partir du jour `JOKER_FROM_DAY`.
 * Ils remplacent un héros ★5 de la même faction à sacrifier.
 */
export const JOKER_FROM_DAY = 90;
export const JOKER_EVERY_DAYS = 45;
