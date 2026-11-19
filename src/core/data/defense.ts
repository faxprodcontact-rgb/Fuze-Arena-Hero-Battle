// Réglages du mode Défense : la carte (chemin + emplacements), les vagues, les vies et les récompenses.
// Valeurs de départ raisonnables, à revoir au grand réglage final avant la bêta.

/** Taille de la carte (mêmes unités que l'écran de combat). */
export const DEFENSE_W = 720;
export const DEFENSE_H = 1100;

/** Le chemin des monstres, de l'entrée (en haut) au camp (en bas). */
export const DEFENSE_PATH: [number, number][] = [
  [-40, 150], [570, 150], [570, 400], [160, 400], [160, 650], [570, 650], [570, 900], [360, 900], [360, 1140],
];

/** Les emplacements où l'on pose ses héros, autour du chemin. */
export const DEFENSE_PADS: [number, number][] = [
  [250, 275], [450, 275], [665, 400],
  [280, 525], [460, 525], [60, 525],
  [250, 775], [450, 775], [230, 975],
];

/** Nombre maximum de héros posés. */
export const DEFENSE_HEROES = 5;
/** Portée d'attaque (en points de carte) : les héros à distance tirent de plus loin, ceux au corps à corps frappent plus fort. */
export const DEFENSE_RANGE = { ranged: 290, melee: 175 };
export const DEFENSE_MELEE_BONUS = 1.6;

export const DEFENSE_LIVES = 20;
export const DEFENSE_WAVES = 8;
/** Secondes entre le début de deux vagues, et entre deux monstres d'une même vague. */
export const DEFENSE_WAVE_GAP = 10;
export const DEFENSE_SPAWN_GAP = 0.9;
/** Vitesse des monstres (points de carte par seconde). */
export const DEFENSE_SPEED: Record<string, number> = { wolf: 95, golem: 42, default: 62, boss: 36 };
/** Vies perdues quand un monstre atteint le camp. */
export const DEFENSE_LEAK = { normal: 1, boss: 5 };

/** Force d'un niveau : celle de la campagne au niveau (niveau × ce nombre). */
export const DEFENSE_STAGE_PER_LEVEL = 8;
/** Résistance des monstres (réglée pour qu'une section de la bonne puissance, bien placée, gagne). */
export const DEFENSE_HP_FACTOR = 0.5;
/** Le boss de la dernière vague vaut ce nombre de monstres. */
export const DEFENSE_BOSS_HP = 3;
/** Chaque vague est un peu plus résistante que la précédente. */
export const DEFENSE_WAVE_GROWTH = 0.12;

export const DEFENSE_LEVELS = 120;
/** Récompenses : à la première victoire (heures de butin hors ligne), puis des gemmes par nouvelle étoile. */
export const DEFENSE_REWARD = { goldHours: 3, gemsPerStar: 20 };

/** Étoiles selon les vies restantes. */
export function defenseStars(lives: number): number {
  if (lives <= 0) return 0;
  if (lives >= DEFENSE_LIVES) return 3;
  return lives >= DEFENSE_LIVES / 2 ? 2 : 1;
}

/** Nombre de monstres d'une vague (la dernière a un boss en plus). */
export function waveSize(wave: number): number {
  return 5 + Math.floor(wave / 2);
}
