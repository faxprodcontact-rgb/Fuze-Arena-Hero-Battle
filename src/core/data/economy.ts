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
/** Places de la section : la place n°i s'ouvre une fois ce niveau de campagne gagné. */
export const SLOT_UNLOCK_STAGES = [0, 4, 10, 20, 40];

/** Récompenses qui font avancer les étoiles (réglées par les simulations). */
export const REWARDS = {
  /** Parchemins d'invocation donnés à la fin de chaque chapitre. */
  chapterSummons: 5,
  /** Fragments du Légendaire choisi, gagnés chaque jour dans les boutiques, à partir de ce jour. */
  fragmentsFromDay: 7,
  fragmentsPerDay: 20,
  /** Héros jokers ★5 (tour, événements, guilde) : un tous les `jokerEveryDays` jours à partir du jour `jokerFromDay`. */
  jokerFromDay: 30,
  jokerEveryDays: 15,
  /** Cristaux d'éveil : gagnés chaque jour une fois ce niveau de campagne atteint. */
  crystalsFromStage: 900,
  crystalsPerDay: 5,
};
