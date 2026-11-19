// Force des héros : niveau, étoiles et plafond de niveau.
import { MYTHIC_STARS } from './stars';

/** Multiplicateur de force par nombre d'étoiles (index = étoiles, 1 à 11). */
export const STAR_MULT = [0, 1, 1.2, 1.45, 1.75, 2.1, 2.6, 3.2, 3.9, 4.7, 5.6, 7.0];

/** Le niveau maximum dépend des étoiles : 20 par étoile (★5 = 100, ★5 rouge = 200, Mythique = 220). */
export function levelCap(stars: number): number {
  return 20 * Math.min(stars, MYTHIC_STARS);
}

/** Chaque niveau ajoute 12 % de la force de base. */
export const LEVEL_GAIN = 0.12;
export const BASE_POWER = 100;

/** Chaque cran d'équipement ajoute 2 % de force. */
export const GEAR_GAIN = 0.02;
