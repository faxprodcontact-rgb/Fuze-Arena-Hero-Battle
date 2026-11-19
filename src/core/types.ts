// Types de base partagés par tout le jeu (téléphone, serveur, simulations).

export const FACTIONS = ['knights', 'assassins', 'mages', 'demons', 'angels', 'myths'] as const;
export type Faction = (typeof FACTIONS)[number];

export const ELEMENTS = ['fire', 'wind', 'water', 'earth'] as const;
export type Element = (typeof ELEMENTS)[number];

export const ROLES = ['protector', 'attacker', 'healer', 'support'] as const;
export type Role = (typeof ROLES)[number];

/** Raretés obtenues à l'invocation. Mythique n'en fait pas partie : c'est un Légendaire éveillé. */
export const RARITIES = ['common', 'rare', 'epic', 'legendary'] as const;
export type Rarity = (typeof RARITIES)[number];

/** Fiche fixe d'un héros (la même pour tous les joueurs). */
export interface HeroDef {
  id: string;
  faction: Faction;
  element: Element;
  role: Role;
  rarity: Rarity;
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
}
