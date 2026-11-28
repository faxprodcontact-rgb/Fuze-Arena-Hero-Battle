// Ce que le jeu sait d'un joueur. Aujourd'hui sur le téléphone ; demain, la même chose sur le serveur.
import type { Slot } from '../../core/battle/types';
import type { GearSlot, Item } from '../../core/data/items';
import type { DungeonKind, Reward } from '../../core/data/modes';
import type { EventBonus } from '../../core/data/event';
import type { FoeHero } from '../../core/coliseum';
import type { Hero } from '../../core/types';

export interface Wallet {
  gold: number;
  essence: number;
  gems: number;
  scrolls: number;
  basicScrolls: number;
  /** Parchemins rouges : la monnaie du portail spécial (27/11/2026), gagnés à quelques endroits (core/data/modes.ts). */
  redScrolls: number;
  arenaTokens: number;
  guildCoins: number;
  crystals: number;
  /** Poussière de forge : recyclage des objets, sert à renforcer les emplacements. */
  dust: number;
  /** Insignes du Colisée (boutique du Colisée). */
  badge: number;
}
export type Currency = keyof Wallet;

/** Fournisseur de connexion. */
export type AuthProvider = 'google' | 'apple';

/** Le compte en ligne lié à la partie (docs/connexion-comptes.md). */
export interface AuthLink {
  provider: AuthProvider;
  /** Identifiant du joueur côté serveur (Supabase : l'id de l'utilisateur). */
  id: string;
  email?: string;
  /** Date de la liaison. */
  at: number;
}

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

/** L'adversaire tiré au Colisée (gardé jusqu'au combat : partir et revenir ne le change pas). */
export interface ColiseumFoe {
  /** Sa place dans le groupe (core/coliseum.ts, makeGroup). */
  idx: number;
  name: string;
  points: number;
  team: FoeHero[];
  seed: number;
}

/** Le Colisée de la semaine (core/coliseum.ts). */
export interface ColiseumState {
  week: string;
  /** Ligue (0 = Bronze … 5 = Champion). */
  league: number;
  /** Graine du groupe de la semaine. */
  seed: number;
  points: number;
  fights: number;
  wins: number;
  /** Jour en cours : combats joués et combats achetés aujourd'hui. */
  day: string;
  today: number;
  bought: number;
  /** Les 3 héros, dans l'ordre de passage. */
  team: number[];
  foe?: ColiseumFoe;
  /** Résultat de la semaine passée, pas encore récupéré. */
  pending?: { week: string; league: number; rank: number; next: number; gems: number; badge: number };
}

export interface Friend {
  id: string;
  code: string;
  name: string;
  team: { defId: string; stars: number; level: number; slot: Slot }[];
}

export interface GuildWarState {
  week: string;
  foe: string;
  /** Puissance de la section en début de semaine (sert à la force des défenses adverses). */
  basePower: number;
  day: string;
  attacks: number;
  /** Héros ayant déjà attaqué aujourd'hui. */
  used: number[];
  myStars: number;
  claimed: boolean;
  /** Récompense de la guerre précédente, pas encore récupérée. */
  pending?: { result: 'win' | 'draw' | 'loss'; guildCoins: number; scrolls: number };
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
  /** Le portrait choisi (un héros découvert) ; absent : le visage du premier héros de la section. */
  avatar?: string;
  settings: { sound: boolean; music: boolean; notifications: boolean };
  createdAt: number;
  /** Décalage de l'horloge du jeu (simulations : le joueur automatique fait passer le temps). */
  timeShift: number;
  lang: 'fr' | 'en';
  speed: 1 | 2 | 3;
  auto: boolean;
  /** Compteur du hasard : chaque tirage utilise une nouvelle graine (le serveur fera la même chose). */
  rng: number;
  nextUid: number;
  account: { level: number; xp: number };
  /** Compte lié (Google ou Apple, src/game/auth.ts) ; absent = joueur invité (partie gardée seulement sur ce téléphone). */
  auth?: AuthLink;
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
  /** Amis : la liste, les cadeaux envoyés aujourd'hui et ceux reçus à ouvrir (par id d'ami). */
  friends: { list: Friend[]; day: string; sent: string[]; inbox: string[] };
  arena: { points: number; opponents: ArenaOpponent[] };
  /** Colisée (créé à son ouverture). */
  coliseum?: ColiseumState;
  /** Étape du tutoriel des premières minutes (-1 = fini ou passé). */
  tutorial?: number;
  /** Le cadeau de la fin du tutoriel (10 invocations) a été donné. */
  tutorialGift?: boolean;
  /** Courrier : messages reçus (id → date d'arrivée), lus, cadeaux récupérés, et cadeaux propres à ce joueur (id → cadeau). */
  mail?: { got: Record<string, number>; read: string[]; claimed: string[]; personal?: Record<string, Reward> };
  /** Calendrier de connexion : dernier jour coché et nombre de jours cochés. */
  login?: { day: string; count: number };
  /** Section de défense (attaquée par les autres en guerre de guildes) ; vide = la section principale. */
  defenseTeam?: [number, Slot][];
  /** Guerre de guildes de la semaine en cours (et récompense de la précédente si pas encore prise). */
  guildWar?: GuildWarState;
  guild: { joined: string | null; bossDamage: number; chat: ChatMessage[]; lastBotAt: number };
  worldChat: ChatMessage[];
  shop: { bought: Record<string, number>; cardUntil: number; passPremium: boolean; noAds: boolean };
  pass: { points: number; claimedFree: number[]; claimedPremium: number[]; /** n° de la saison (depuis la création du compte) */ season?: number };
  daily: {
    day: string;
    ads: number;
    /** L'invocation gratuite d'une pub a déjà servie aujourd'hui (une par jour, 28/11). */
    adSummon?: boolean;
    fastLoot: number;
    entries: Record<DungeonKind, number>;
    bossAttempts: number;
    bossBest: number;
    /** Parties du mode Événement commencées aujourd'hui. */
    eventTries?: number;
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
  /** Le mode Événement (core/data/event.ts) : l'événement en cours, sa difficulté, la partie commencée. */
  event?: EventState;
}

/** Une partie du mode Événement : l'équipe inscrite (ses places), le prochain niveau, la vie de chacun (part de sa vie
 * max, 0 = mort), les bonus d'attaque et de défense gagnés, et le choix de bonus en attente. */
export interface EventRun {
  team: [number, Slot][];
  level: number;
  hp: Record<number, number>;
  atk: number;
  def: number;
  offer?: EventBonus[];
}
export interface EventState {
  /** L'événement (l'id du portail d'événement) : un nouveau remet la difficulté à 1. */
  id: string;
  difficulty: number;
  run?: EventRun;
}

/** Récompense affichée après une action (coffre, combat, quête…). */
export interface Gain {
  currencies: Partial<Wallet>;
  heroes: Hero[];
  items: Item[];
  fragments?: { defId: string; amount: number };
  /** XP gagnée par chaque héros de l'équipe (mode Événement) et niveaux qu'elle leur a fait gagner. */
  xp?: number;
  levelsUp?: number;
}
