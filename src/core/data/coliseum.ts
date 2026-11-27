// Réglages du Colisée (PvP en duels, demande du propriétaire du 26/11/2026).
// On choisit 3 héros ; on tombe au hasard sur un joueur de son groupe, de la même puissance. Le combat est automatique :
// le 1er héros de chaque équipe se battent, le gagnant reste (avec la vie qui lui reste) et affronte le suivant ; l'équipe
// qui n'a plus de héros a perdu. Le gagnant prend des points de classement. Chaque semaine, un groupe de 30 joueurs par
// ligue : les 3 premiers montent, les 3 derniers descendent, et chacun reçoit une récompense selon sa place.
// Valeurs raisonnables : le grand réglage se fera avant la bêta.
import type { ShopItem } from './modes';

export const COLISEUM = {
  /** Héros par équipe (ils combattent dans l'ordre choisi). */
  team: 3,
  /** Combats offerts chaque jour, puis quelques-uns de plus contre des gemmes (prix du 1er, du 2e, du 3e). */
  freeFights: 5,
  extraCosts: [50, 100, 150] as readonly number[],
  /** Joueurs par groupe (le joueur compris), montées et descentes en fin de semaine. */
  groupSize: 30,
  promote: 3,
  relegate: 3,
  /** Points de chacun au début de la semaine. */
  startPoints: 1000,
  /**
   * Points gagnés ou perdus (à la façon d'Elo) : à points égaux, +20 en cas de victoire, −14 en cas de défaite ; battre
   * quelqu'un de mieux classé rapporte plus, perdre contre lui coûte moins (1 point d'écart par 25 points de classement).
   */
  win: { base: 20, min: 10, max: 32 },
  loss: { base: 14, min: 5, max: 24 },
  pointsGap: 25,
  /** Puissance de l'adversaire : entre ces deux parts de celle de l'équipe du joueur. */
  foePower: [0.9, 1.08] as const,
  /** Adversaire tiré parmi les N joueurs du groupe les plus proches au classement. */
  foeChoice: 10,
  /** Insignes gagnés à chaque combat (le gros vient des récompenses de la semaine). */
  fightBadges: { win: 12, loss: 4 },
  /**
   * Duels plus vifs : l'attaque des deux combattants est multipliée (dégâts, brûlures et soins suivent l'attaque), sinon un
   * duel de deux héros de même force traîne (≈ 30 coups ; ≈ 12 avec ×2,5).
   */
  duelAtk: 2.5,
  /** La vie se garde d'un duel à l'autre ; l'énergie aussi (choix du 26/11 : un héros chargé enchaîne sur son attaque spéciale). */
  keepEnergy: true,
} as const;

/** Les 6 ligues, de la plus basse à la plus haute (Bronze → Champion). */
export const COLISEUM_LEAGUES = ['bronze', 'silver', 'gold', 'platinum', 'diamond', 'champion'] as const;
export type ColiseumLeague = (typeof COLISEUM_LEAGUES)[number];
/** Les récompenses montent avec la ligue. */
export const LEAGUE_REWARD_MULT: readonly number[] = [1, 1.25, 1.5, 1.8, 2.2, 2.6];
/** Les adversaires des ligues hautes gagnent un peu plus souvent (ils montent plus vite au classement). */
export const LEAGUE_BOT_SKILL: readonly number[] = [0, 0.02, 0.04, 0.06, 0.08, 0.1];

/** Récompenses de fin de semaine selon la place (en Bronze ; multipliées par LEAGUE_REWARD_MULT). */
export const COLISEUM_RANK_REWARDS: readonly { from: number; to: number; gems: number; badge: number }[] = [
  { from: 1, to: 1, gems: 300, badge: 600 },
  { from: 2, to: 2, gems: 250, badge: 500 },
  { from: 3, to: 3, gems: 200, badge: 420 },
  { from: 4, to: 10, gems: 150, badge: 320 },
  { from: 11, to: 20, gems: 100, badge: 220 },
  { from: 21, to: 30, gems: 50, badge: 120 },
];

/** La boutique du Colisée (prix en insignes). */
export const COLISEUM_SHOP: ShopItem[] = [
  { id: 'c-frag', cost: 300, reward: { fragments: 30 } },
  { id: 'c-scroll', cost: 250, reward: { scrolls: 1 } },
  { id: 'c-crystal', cost: 400, reward: { crystals: 60 } },
  { id: 'c-item', cost: 450, reward: { item: 4 } },
  { id: 'c-basic', cost: 120, reward: { basicScrolls: 10 } },
  { id: 'c-dust', cost: 150, reward: { dust: 300 } },
  { id: 'c-red', cost: 400, reward: { redScrolls: 1 } },
];

/** Les noms des autres joueurs du groupe : deux morceaux tirés au hasard (graine de la semaine). */
export const NAME_HEADS = ['Kaï', 'Lun', 'Vae', 'Tor', 'Ish', 'Dra', 'Mik', 'Ors', 'Bas', 'Yun', 'Rag', 'Sel', 'Noc', 'Aï', 'Fey', 'Mir', 'Zar', 'Ely', 'Gor', 'Thal'];
export const NAME_TAILS = ['ro', 'aria', 'lis', 'mund', 'ara', 'ven', 'aze', 'olya', 'tien', 'na', 'nis', 'ka', 'tis', 'ko', 'dra', 'elle', 'ion', 'wyn', 'rok', 'ith'];
