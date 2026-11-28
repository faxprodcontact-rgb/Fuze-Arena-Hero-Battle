// Réglages des modes de jeu, des quêtes, de la boutique et des déblocages.
// Valeurs de départ, à affiner avec les simulations et les essais.

/** Niveau de campagne à finir pour débloquer chaque fonction. */
// Réglés le 28/11 sur le rythme visé (joueur de référence : 3 × 20 min par jour) : un mode de plus à chaque étape du
// premier jour (tour, missions, donjons, Événement), l'arène en fin de premier jour, la guilde le 2e ou 3e jour, le
// Colisée vers la fin de la première semaine.
export const UNLOCKS = {
  tower: 15,
  missions: 30,
  dungeons: 50,
  event: 90,   // le mode Événement (27/11, à la place du boss du jour : core/data/event.ts)
  arena: 140,
  guild: 220,
  defense: 360,
} as const;
export type Feature = keyof typeof UNLOCKS;

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

/**
 * Parchemins rouges (demande du propriétaire, 27/11/2026) : la monnaie du portail spécial, 1 par invocation (×10 = 10).
 * Rares, gagnés à quelques endroits seulement (valeurs raisonnables, à revoir au grand réglage avant la bêta) :
 * - fin de chaque chapitre de la campagne : RED_SCROLLS.perChapter ;
 * - mode Événement : aux niveaux 10 et 20 de chaque zone (core/data/event.ts, eventScrolls) ;
 * - coffre de la semaine à 100 points : 1 (WEEKLY_CHESTS) ;
 * - boutique du Colisée : 1 contre des insignes (COLISEUM_SHOP, core/data/coliseum.ts) ;
 * - boutique, onglet Échanges : 1 contre RED_SCROLLS.gems gemmes, au plus RED_SCROLLS.gemsPerWeek par semaine ;
 * - courrier de bienvenue du portail (core/data/mail.ts, `parchemins-rouges-2711`) : 10.
 */
export const RED_SCROLLS = { perChapter: 1, gems: 300, gemsPerWeek: 5 };
export const GEMS_PER_10_SUMMONS = 2700;

// ---------- Tour des Épreuves ----------

/** Puissance demandée pour l'étage n : au niveau d'un niveau de campagne qui avance de 6 par étage. */
export const TOWER_STAGE_PER_FLOOR = 6;
/** Chaque étage gagné : des heures d'essence (au revenu du joueur) ; un parchemin tous les 5 étages, des gemmes tous les 10. */
export const TOWER_REWARD = { essenceHours: 1, scrollsEvery: 5, gemsEvery: 10, gems: 100 };

// ---------- Donjons du jour ----------

export type DungeonKind = 'gold' | 'essence' | 'gear';
/** Donjon ouvert selon le jour de la semaine (0 = dimanche : tous). */
// Trois donjons toujours ouverts (or, essence, armurerie), chacun avec ses niveaux à gravir.
// On combat le niveau suivant (obligatoire pour avancer) ou on « balaie » le dernier niveau gagné (instantané).
export const DUNGEON_ATTEMPTS_PER_DAY = 3;
export const DUNGEON_LEVELS = 150;
/** Force d'un niveau de donjon = celle du niveau de campagne (niveau × ce nombre). */
export const DUNGEON_STAGE_PER_LEVEL = 8;
/** Récompense : heures de butin hors ligne du niveau de campagne équivalent (or : de l'or ; source d'essence : de l'essence). */
export const DUNGEON_REWARD_HOURS = 4;
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

// (le boss du jour est remplacé par le mode Événement le 27/11 : core/data/event.ts)

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
  | 'dungeon' | 'mission' | 'event' | 'arena' | 'guildBoss' | 'watchAd';

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
  { id: 'd-event', event: 'event', goal: 2, points: 10 },
];
export const WEEKLY_QUESTS: QuestDef[] = [
  { id: 'w-stage', event: 'winStage', goal: 30, points: 20 },
  { id: 'w-summon', event: 'summon', goal: 20, points: 20 },
  { id: 'w-tower', event: 'tower', goal: 5, points: 20 },
  { id: 'w-fuse', event: 'fuse', goal: 5, points: 20 },
  { id: 'w-guild', event: 'guildBoss', goal: 6, points: 20 },
];
/** Coffres d'activité : à 20, 40, 60, 80 et 100 points. */
/**
 * Une récompense. `goldH` / `essenceH` (28/11) : de l'or ou de l'essence comptés en HEURES DE BUTIN du joueur (le revenu
 * horaire de son niveau de campagne) : la récompense garde sa valeur du premier jour au dernier (un montant fixe valait
 * des centaines d'heures au début et presque rien à la fin). Changées en montants par resolveReward (state/selectors.ts).
 */
export type Reward = Partial<Record<'gold' | 'essence' | 'goldH' | 'essenceH' | 'gems' | 'scrolls' | 'basicScrolls' | 'redScrolls' | 'crystals' | 'dust', number>>;
// (28/11) un peu moins généreux : le joueur gratuit de référence reçoit environ 9 invocations par jour (il en avait 13)
export const DAILY_CHESTS: { points: number; reward: Reward }[] = [
  { points: 20, reward: { basicScrolls: 4 } },
  { points: 40, reward: { gems: 100, goldH: 2 } },
  { points: 60, reward: { basicScrolls: 4, essenceH: 2 } },
  { points: 80, reward: { gems: 150 } },
  { points: 100, reward: { scrolls: 1, basicScrolls: 6 } },
];
export const WEEKLY_CHESTS: { points: number; reward: Reward }[] = [
  { points: 40, reward: { scrolls: 3 } },
  { points: 100, reward: { gems: 1000, scrolls: 3, redScrolls: 1 } },
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
  { id: 'pass', price: '9,99 €', reward: {}, limit: 0, kind: 'pass' }, // une fois par saison (passPremium)
  { id: 'noads', price: '5,99 €', reward: {}, limit: 1, kind: 'noAds' },
  { id: 'gems-1', price: '1,99 €', reward: { gems: 300 }, limit: 0, kind: 'gems' },
  { id: 'gems-2', price: '9,99 €', reward: { gems: 1700 }, limit: 0, kind: 'gems' },
  { id: 'gems-3', price: '19,99 €', reward: { gems: 3600 }, limit: 0, kind: 'gems' },
  { id: 'gems-4', price: '49,99 €', reward: { gems: 9500 }, limit: 0, kind: 'gems' },
];
/** Carte mensuelle : 300 gemmes à l'achat, puis 300 par jour pendant 30 jours (26/11 : 200 ; 28/11 : 300, une invocation
 * par jour, pour qu'un petit payeur avance environ 2 fois plus vite). */
export const MONTHLY_CARD = { days: 30, gemsPerDay: 300 };

/** Passe de saison : on gagne des points avec les quêtes ; chaque palier a une récompense gratuite et une payante. */
export const PASS_POINTS_PER_LEVEL = 100;
/** Une saison du passe dure 28 jours (28/11) : ensuite points, paliers pris et voie premium repartent de zéro. */
export const PASS_SEASON_DAYS = 28;
// Plus de choses à chaque palier (demande du propriétaire, 26/11) : chaque palier mélange plusieurs gains, ceux qui
// tombent sur 5 sont de gros paliers, le 30e est le grand final. Valeurs raisonnables, à revoir au réglage final.
export const PASS_LEVELS: { free: Reward; premium: Reward }[] = Array.from({ length: 30 }, (_, i) => {
  const lv = i + 1;
  if (lv === 30) return {
    free: { scrolls: 3, gems: 300, goldH: 24 },
    premium: { scrolls: 15, crystals: 200, gems: 1500, dust: 500 },
  };
  if (lv % 5 === 0) return {
    free: { scrolls: 1, gems: 100, goldH: 8 },
    premium: { scrolls: 5, crystals: 50, gems: 500, essenceH: 8 },
  };
  // les autres paliers : un gain principal qui tourne, toujours avec un peu d'or et d'essence
  const turn = lv % 4;
  return {
    free: { goldH: 3, essenceH: 2, ...(turn === 1 ? { basicScrolls: 2 } : turn === 3 ? { gems: 30 } : {}) },
    premium: {
      gems: 200,
      ...(turn === 0 ? { scrolls: 2 } : turn === 1 ? { crystals: 20 } : turn === 2 ? { dust: 80 } : { basicScrolls: 5, essenceH: 4 }),
    },
  };
});

/** Boutiques d'échange : arène (jetons) et guilde (pièces). */
export interface ShopItem {
  id: string;
  cost: number;
  reward: Reward & { fragments?: number; item?: number };
}
export const ARENA_SHOP: ShopItem[] = [
  { id: 'a-scroll', cost: 300, reward: { scrolls: 1 } },
  { id: 'a-frag', cost: 300, reward: { fragments: 20 } }, // (28/11 : 200 → 300, les fragments vont au Légendaire visé)
  { id: 'a-gold', cost: 100, reward: { goldH: 8 } },
  { id: 'a-item', cost: 400, reward: { item: 4 } },
];
export const GUILD_SHOP: ShopItem[] = [
  { id: 'g-frag', cost: 250, reward: { fragments: 20 } },
  { id: 'g-basic', cost: 100, reward: { basicScrolls: 10 } },
  { id: 'g-crystal', cost: 300, reward: { crystals: 50 } },
  { id: 'g-item', cost: 350, reward: { item: 4 } },
];

// ---------- Amis ----------

export const FRIENDS_MAX = 20;
/** Un cadeau d'ami reçu vaut ceci (envoyer ne coûte rien, une fois par jour et par ami). */
export const FRIEND_GIFT = { basicScrolls: 1 };

// ---------- Guerre de guildes ----------
// Une guerre par semaine : lundi préparation (adversaire connu, défense à régler), mardi → samedi combats,
// dimanche résultats. Chaque membre attaque 2 fois par jour ; un héros n'attaque qu'une fois par jour.
// Les étoiles de chaque attaque s'additionnent : la guilde qui en a le plus gagne.

export const GUILD_WAR = {
  attacksPerDay: 2,
  defenses: 9,
  /** Pièces de guilde par étoile gagnée en attaque (tout de suite). */
  coinsPerStar: 10,
  reward: {
    win: { guildCoins: 600, scrolls: 5 },
    draw: { guildCoins: 450, scrolls: 3 },
    loss: { guildCoins: 300, scrolls: 2 },
  },
  /** Bonus pour le meilleur attaquant de la guilde. */
  bestAttacker: { scrolls: 3 },
};

// ---------- Calendrier de connexion ----------
// Un jour coché par jour de connexion (un jour manqué ne fait rien perdre). D'abord 7 jours de bienvenue,
// puis un calendrier de 28 jours qui recommence. Le 7e jour de bienvenue donne un héros Légendaire.

export type LoginReward = Reward & { legendary?: number };

/** Le cadeau de la fin du tutoriel : des parchemins pour une invocation ×10 (28/11). */
export const TUTORIAL_GIFT_SCROLLS = 10;

export const LOGIN_WELCOME: LoginReward[] = [
  { goldH: 12 }, { scrolls: 5 }, { essenceH: 12 }, { gems: 300 }, { scrolls: 5 }, { basicScrolls: 10 }, { legendary: 1 },
];

export const LOGIN_MONTH: LoginReward[] = Array.from({ length: 28 }, (_, i): LoginReward => {
  if (i % 7 === 6) return { scrolls: 3, crystals: 30 };
  return [{ goldH: 8 }, { essenceH: 8 }, { gems: 100 }, { basicScrolls: 5 }, { scrolls: 1 }, { gems: 150 }][i % 7]!;
});
