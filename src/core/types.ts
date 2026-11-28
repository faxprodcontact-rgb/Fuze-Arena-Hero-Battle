// Types de base partagés par tout le jeu (téléphone, serveur, simulations).
import type { Passive, SkillDef, Talent } from './battle/types';


export const ELEMENTS = ['fire', 'wind', 'water', 'earth'] as const;
export type Element = (typeof ELEMENTS)[number];

/** Protecteur et Guerrier devant ; Tireur, Assassin, Soigneur et Soutien derrière (l'Assassin frappe l'arrière). */
export const ROLES = ['protector', 'warrior', 'marksman', 'assassin', 'healer', 'support'] as const;
export type Role = (typeof ROLES)[number];

/** Raretés obtenues à l'invocation. Mythique n'en fait pas partie : c'est un Légendaire éveillé. */
export const RARITIES = ['common', 'rare', 'epic', 'legendary'] as const;
export type Rarity = (typeof RARITIES)[number];

/** Fiche fixe d'un héros (la même pour tous les joueurs). Statistiques au niveau 1, ★1. */
export interface HeroDef {
  id: string;
  name: string;
  element: Element;
  role: Role;
  rarity: Rarity;
  ranged: boolean;
  hp: number;
  atk: number;
  def: number;
  /** Temps entre deux attaques, en tours de 100 ms. */
  interval: number;
  crit: number;
  critDmg: number;
  dodge: number;
  tenacity: number;
  /** L'attaque normale vise l'arrière ennemi (Assassins). */
  hitsBack?: boolean;
  skill: SkillDef;
  /** Passifs, chacun débloqué à partir d'un nombre d'étoiles. */
  passives: { stars: number; passive: Passive }[];
  /** Talent de chef de section : pour un héros sur trois. */
  talent?: Talent;
}

/**
 * Un héros possédé par un joueur.
 * `stars` va de 1 à 11 : 1-5 = étoiles jaunes, 6-10 = étoiles rouges (★1 à ★5 rouge), 11 = Mythique.
 */
export interface Hero {
  uid: number;
  defId: string;
  stars: number;
  level: number;
  /** Niveau d'équipement résumé (simulations). Le vrai jeu aura 4 objets par héros. */
  gear?: number;
  /** XP vers le niveau suivant (gagnée en mode Événement, core/data/event.ts). */
  xp?: number;
}
