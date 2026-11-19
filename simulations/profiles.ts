// Les types de joueurs simulés.
import type { Profile } from './model';

/**
 * Joue 3 fois 5 minutes par jour et regarde la pub du jour. C'est lui qui sert de référence.
 * Invocations par jour : 7 (quêtes, gemmes d'arène et de succès, pub), plus 5 par chapitre terminé.
 */
export const REGULAR: Profile = {
  id: 'regulier',
  label: 'Régulier (3 × 5 min par jour)',
  sessions: (day) =>
    day === 0
      ? [
          { hour: 0, minutes: 10 },
          { hour: 0.2, minutes: 10 },
          { hour: 4, minutes: 15 },
          { hour: 10, minutes: 10 },
        ]
      : [
          { hour: 8, minutes: 5 },
          { hour: 13, minutes: 5 },
          { hour: 21, minutes: 5 },
        ],
  dailySummons: 7,
  dailyBasicSummons: 12,
  starterSummons: 0,
};

/** Une seule session de 5 minutes par jour, sans pub. */
export const CASUAL: Profile = {
  id: 'cinq-minutes',
  label: '5 minutes par jour',
  sessions: (day) =>
    day === 0
      ? [
          { hour: 0, minutes: 10 },
          { hour: 0.2, minutes: 10 },
        ]
      : [{ hour: 20, minutes: 5 }],
  dailySummons: 5.5,
  dailyBasicSummons: 9,
  starterSummons: 0,
};

/** Comme le régulier, avec l'offre de départ, la carte mensuelle et le passe de saison. */
export const SMALL_SPENDER: Profile = {
  ...REGULAR,
  id: 'petit-payeur',
  label: 'Petit payeur (offre de départ + carte mensuelle + passe)',
  dailySummons: 11,
  starterSummons: 30,
};

export const PROFILES = [REGULAR, CASUAL, SMALL_SPENDER];
