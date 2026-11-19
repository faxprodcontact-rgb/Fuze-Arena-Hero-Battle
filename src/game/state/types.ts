// Ce que le jeu sait d'un joueur. Aujourd'hui sur le téléphone ; demain, la même chose sur le serveur.
import type { Slot } from '../../core/battle/types';
import type { GearSlot, Item } from '../../core/data/items';
import type { DungeonKind } from '../../core/data/modes';
import type { Hero } from '../../core/types';

export interface Wallet {
  gold: number;
  essence: number;
  gems: number;
  scrolls: number;
  basicScrolls: number;
  arenaTokens: number;
  guildCoins: number;
  crystals: number;
  /** Poussière de forge : recyclage des objets, sert à renforcer les emplacements. */
  dust: number;
}
export type Currency = keyof Wallet;

export interface MissionState {
  id: string;
  templateId: string;
  heroUids: number[];
  startedAt?: number;
  claimed: boolean;
}

export interface ArenaOpponent {
  id: string;
  name: string;
  points: number;
  team: { defId: string; stars: number; level: number; slot: Slot }[];
}

export interface ChatMessage {
  from: string;
  text: string;
  at: number;
  me?: boolean;
}

export interface PlayerState {
  v: 2;
  name: string;
  /** Le joueur a choisi son nom (premier lancement). */
  named: boolean;
  /** Nombre de changements de nom payés. */
  nameChanges: number;
  settings: { sound: boolean; music: boolean; notifications: boolean };
  createdAt: number;
  /** Décalage du temps pour les tests (avancer de quelques heures). */
  timeShift: number;
  lang: 'fr' | 'en';
  speed: 1 | 2 | 3;
  auto: boolean;
  /** Compteur du hasard : chaque tirage utilise une nouvelle graine (le serveur fera la même chose). */
  rng: number;
  nextUid: number;
  account: { level: number; xp: number };
  wallet: Wallet;
  fragments: Record<string, number>;
  /** Le Légendaire que visent les fragments des boutiques. */
  fragmentTarget?: string;
  /** Héros déjà obtenus au moins une fois : on ne montre jamais un héros pas encore découvert. */
  discovered: string[];
  heroes: Hero[];
  items: Item[];
  /** Niveau de renforcement de chaque emplacement de chaque héros (uid → emplacement → +N). */
  slotLevels: Record<number, Partial<Record<GearSlot, number>>>;
  formation: [number, Slot][];
  /** crystalHours : heures de butin pas encore transformées en cristal (reste d'une collecte à l'autre). */
  campaign: { cleared: number; idleFrom: number; itemHours: number; crystalHours?: number };
  summon: { pity: number; total: number };
  tower: { floor: number };
  dungeons: Record<DungeonKind, number>;
  /** Mode Défense : dernier niveau gagné, étoiles par niveau, et les héros posés (uid → emplacement). */
  defense: { level: number; stars: Record<number, number>; placement: [number, number][]; chests?: number };
  arena: { points: number; opponents: ArenaOpponent[] };
  guild: { joined: string | null; bossDamage: number; chat: ChatMessage[]; lastBotAt: number };
  worldChat: ChatMessage[];
  shop: { bought: Record<string, number>; cardUntil: number; passPremium: boolean; noAds: boolean };
  pass: { points: number; claimedFree: number[]; claimedPremium: number[] };
  daily: {
    day: string;
    ads: number;
    fastLoot: number;
    entries: Record<DungeonKind, number>;
    bossAttempts: number;
    bossBest: number;
    arenaFights: number;
    guildAttempts: number;
    missions: MissionState[];
    quests: Record<string, number>;
    claimed: string[];
    chests: number[];
    cardClaimed: boolean;
  };
  weekly: { week: string; quests: Record<string, number>; claimed: string[]; chests: number[] };
  /** Fonctions déjà ouvertes au moins une fois (pour le point rouge « nouveau »). */
  seen: string[];
}

/** Récompense affichée après une action (coffre, combat, quête…). */
export interface Gain {
  currencies: Partial<Wallet>;
  heroes: Hero[];
  items: Item[];
  fragments?: { defId: string; amount: number };
}
