// Réglages des modes de jeu, des quêtes, de la boutique et des déblocages.
// Valeurs de départ, à affiner avec les simulations et les essais.

/** Niveau de campagne à finir pour débloquer chaque fonction. */
export const UNLOCKS = {
  tower: 20,
  missions: 30,
  dungeons: 40,
  dailyBoss: 60,
  arena: 80,
  guild: 100,
  defense: 400,
} as const;
export type Feature = keyof typeof UNLOCKS;

/**
 * OUTIL DE TEST (site de test) : tous les modes ouverts dès le début, pour que le propriétaire puisse les regarder.
 * À REMETTRE À false AVANT LA BÊTA. Le nombre de héros dans la section suit toujours la campagne.
 */
export const TEST_OPEN_ALL_MODES = true;

// ---------- Campagne et butin ----------

/** Butin hors ligne : l'or vaut le revenu horaire, l'essence la moitié. */
export const ESSENCE_RATIO = 0.5;
/** Un objet d'équipement et un parchemin simple toutes les 2 h de butin (≈ 12 parchemins par jour). */
export const IDLE_ITEM_HOURS = 2;
/** Changer de nom après le premier choix coûte des gemmes. */
export const RENAME_COST = 500;
/** Prix (en gemmes) de la Renaissance d'un héros (retour au niveau 1) : tout ce qui a été dépensé sur lui est rendu. */
export const RESET_COST = 50;
/** Butin rapide : 2 h de butin d'un coup. Le premier de la journée est gratuit, puis il coûte des gemmes. */
export const FAST_LOOT_HOURS = 2;
export const FAST_LOOT_COSTS = [0, 50, 100, 200];
/** Gemmes et XP de compte pour une victoire en campagne. */
export const STAGE_GEMS = 5;
export const ACCOUNT_XP_PER_STAGE = 20;
export function accountXpForLevel(level: number): number {
  return Math.round(100 * 1.08 ** (level - 1));
}

// ---------- Invocations ----------

export const GEMS_PER_SUMMON = 300;
export const GEMS_PER_10_SUMMONS = 2700;

// ---------- Tour des Épreuves ----------

/** Puissance demandée pour l'étage n : au niveau d'un niveau de campagne qui avance de 6 par étage. */
export const TOWER_STAGE_PER_FLOOR = 6;
export const TOWER_REWARD = { essencePerFloor: 40, scrollsEvery: 5, gemsEvery: 10, gems: 100 };

// ---------- Donjons du jour ----------

export type DungeonKind = 'gold' | 'essence' | 'gear';
/** Donjon ouvert selon le jour de la semaine (0 = dimanche : tous). */
// Trois donjons toujours ouverts (or, essence, armurerie), chacun avec ses niveaux à gravir.
// On combat le niveau suivant (obligatoire pour avancer) ou on « balaie » le dernier niveau gagné (instantané).
export const DUNGEON_ATTEMPTS_PER_DAY = 3;
export const DUNGEON_LEVELS = 150;
/** Force d'un niveau de donjon = celle du niveau de campagne (niveau × ce nombre). */
export const DUNGEON_STAGE_PER_LEVEL = 8;
/** Récompense : heures de butin hors ligne du niveau de campagne équivalent. */
export const DUNGEON_REWARD_HOURS = 6;
/** Armurerie : nombre d'objets et chance de rareté selon le niveau. */
export function dungeonItems(level: number): { count: number; luck: number } {
  return { count: Math.min(6, 2 + Math.floor(level / 30)), luck: 1 + Math.floor(level / 25) };
}

// ---------- Missions ----------

export interface MissionTemplate {
  id: string;
  hours: number;
  heroes: number;
  /** Étoiles minimum de chaque héros envoyé. */
  minStars: number;
  reward: { kind: 'gold' | 'essence' | 'gems' | 'scrolls' | 'basicScrolls'; hours?: number; amount?: number };
}
export const MISSIONS_PER_DAY = 5;
export const MISSION_TEMPLATES: MissionTemplate[] = [
  { id: 'patrol', hours: 1, heroes: 1, minStars: 1, reward: { kind: 'gold', hours: 2 } },
  { id: 'escort', hours: 2, heroes: 2, minStars: 2, reward: { kind: 'essence', hours: 3 } },
  { id: 'ruins', hours: 4, heroes: 2, minStars: 3, reward: { kind: 'basicScrolls', amount: 5 } },
  { id: 'hunt', hours: 4, heroes: 3, minStars: 3, reward: { kind: 'gems', amount: 80 } },
  { id: 'relic', hours: 8, heroes: 3, minStars: 4, reward: { kind: 'scrolls', amount: 1 } },
  { id: 'siege', hours: 8, heroes: 4, minStars: 4, reward: { kind: 'gems', amount: 150 } },
];

// ---------- Boss du jour ----------

export const DAILY_BOSS_ATTEMPTS = 2;
/** Paliers de dégâts, exprimés en part des PV du boss, et leur récompense en gemmes. */
export const DAILY_BOSS_TIERS = [
  { share: 0.05, gems: 30 }, { share: 0.15, gems: 60 }, { share: 0.3, gems: 100 },
  { share: 0.5, gems: 150 }, { share: 0.75, gems: 220 }, { share: 1, gems: 300 },
];

// ---------- Arène ----------

export const ARENA_FREE_TICKETS = 5;
export const ARENA_WIN_POINTS = 25;
export const ARENA_LOSS_POINTS = -10;
export const ARENA_TOKENS_PER_FIGHT = { win: 30, loss: 10 };
export const ARENA_LEAGUES = [
  { id: 'bronze', from: 0 }, { id: 'silver', from: 1200 }, { id: 'gold', from: 1500 },
  { id: 'platinum', from: 1800 }, { id: 'diamond', from: 2200 },
];
export const ARENA_START_POINTS = 1000;

// ---------- Guilde ----------

export const GUILD_BOSS_ATTEMPTS = 2;
export const GUILD_COINS_PER_ATTACK = 60;

// ---------- Quêtes ----------

export type QuestEvent =
  | 'login' | 'collectIdle' | 'winStage' | 'summon' | 'levelUp' | 'fuse' | 'tower'
  | 'dungeon' | 'mission' | 'dailyBoss' | 'arena' | 'guildBoss' | 'watchAd';

export interface QuestDef {
  id: string;
  event: QuestEvent;
  goal: number;
  points: number;
}
export const DAILY_QUESTS: QuestDef[] = [
  { id: 'd-login', event: 'login', goal: 1, points: 10 },
  { id: 'd-idle', event: 'collectIdle', goal: 2, points: 10 },
  { id: 'd-stage', event: 'winStage', goal: 3, points: 20 },
  { id: 'd-summon', event: 'summon', goal: 1, points: 10 },
  { id: 'd-level', event: 'levelUp', goal: 3, points: 10 },
  { id: 'd-dungeon', event: 'dungeon', goal: 1, points: 10 },
  { id: 'd-mission', event: 'mission', goal: 2, points: 10 },
  { id: 'd-arena', event: 'arena', goal: 2, points: 10 },
  { id: 'd-boss', event: 'dailyBoss', goal: 1, points: 10 },
];
export const WEEKLY_QUESTS: QuestDef[] = [
  { id: 'w-stage', event: 'winStage', goal: 30, points: 20 },
  { id: 'w-summon', event: 'summon', goal: 20, points: 20 },
  { id: 'w-tower', event: 'tower', goal: 5, points: 20 },
  { id: 'w-fuse', event: 'fuse', goal: 5, points: 20 },
  { id: 'w-guild', event: 'guildBoss', goal: 6, points: 20 },
];
/** Coffres d'activité : à 20, 40, 60, 80 et 100 points. */
export type Reward = Partial<Record<'gold' | 'essence' | 'gems' | 'scrolls' | 'basicScrolls' | 'crystals', number>>;
export const DAILY_CHESTS: { points: number; reward: Reward }[] = [
  { points: 20, reward: { basicScrolls: 4 } },
  { points: 40, reward: { gems: 150 } },
  { points: 60, reward: { scrolls: 1 } },
  { points: 80, reward: { gems: 250 } },
  { points: 100, reward: { scrolls: 2, basicScrolls: 8 } },
];
export const WEEKLY_CHESTS: { points: number; reward: Reward }[] = [
  { points: 40, reward: { scrolls: 5 } },
  { points: 100, reward: { gems: 1500, scrolls: 5 } },
];

// ---------- Pubs volontaires ----------

export const ADS_PER_DAY = 6;
export const AD_SECONDS = 3;

// ---------- Boutique (achats SIMULÉS dans le prototype) ----------

export interface Offer {
  id: string;
  price: string;
  reward: Reward;
  /** Nombre d'achats possibles (0 = illimité). */
  limit: number;
  kind: 'starter' | 'gems' | 'card' | 'pass' | 'noAds' | 'growth';
}
export const OFFERS: Offer[] = [
  { id: 'starter', price: '0,99 €', reward: { gems: 1000, scrolls: 10 }, limit: 1, kind: 'starter' },
  { id: 'growth', price: '4,99 €', reward: { gems: 3000, scrolls: 15, crystals: 100 }, limit: 1, kind: 'growth' },
  { id: 'card', price: '4,99 €', reward: { gems: 300 }, limit: 0, kind: 'card' },
  { id: 'pass', price: '9,99 €', reward: {}, limit: 1, kind: 'pass' },
  { id: 'noads', price: '5,99 €', reward: {}, limit: 1, kind: 'noAds' },
  { id: 'gems-1', price: '1,99 €', reward: { gems: 300 }, limit: 0, kind: 'gems' },
  { id: 'gems-2', price: '9,99 €', reward: { gems: 1700 }, limit: 0, kind: 'gems' },
  { id: 'gems-3', price: '19,99 €', reward: { gems: 3600 }, limit: 0, kind: 'gems' },
  { id: 'gems-4', price: '49,99 €', reward: { gems: 9500 }, limit: 0, kind: 'gems' },
];
/** Carte mensuelle : 300 gemmes à l'achat, puis 100 par jour pendant 30 jours. */
export const MONTHLY_CARD = { days: 30, gemsPerDay: 100 };

/** Passe de saison : on gagne des points avec les quêtes ; chaque palier a une récompense gratuite et une payante. */
export const PASS_POINTS_PER_LEVEL = 100;
export const PASS_LEVELS: { free: Reward; premium: Reward }[] = Array.from({ length: 30 }, (_, i) => ({
  free: i % 5 === 4 ? { scrolls: 1 } : { gold: 2000 * (i + 1) },
  premium: i % 5 === 4 ? { scrolls: 3, crystals: 30 } : { gems: 100 },
}));

/** Boutiques d'échange : arène (jetons) et guilde (pièces). */
export interface ShopItem {
  id: string;
  cost: number;
  reward: Reward & { fragments?: number; item?: number };
}
export const ARENA_SHOP: ShopItem[] = [
  { id: 'a-scroll', cost: 300, reward: { scrolls: 1 } },
  { id: 'a-frag', cost: 200, reward: { fragments: 20 } },
  { id: 'a-gold', cost: 100, reward: { gold: 20000 } },
  { id: 'a-item', cost: 400, reward: { item: 4 } },
];
export const GUILD_SHOP: ShopItem[] = [
  { id: 'g-frag', cost: 150, reward: { fragments: 20 } },
  { id: 'g-basic', cost: 100, reward: { basicScrolls: 10 } },
  { id: 'g-crystal', cost: 300, reward: { crystals: 50 } },
  { id: 'g-item', cost: 350, reward: { item: 4 } },
];
