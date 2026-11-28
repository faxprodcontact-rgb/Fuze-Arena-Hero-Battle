// Toutes les actions du joueur. C'est LA porte d'entrée : à l'étape serveur, ces fonctions
// enverront la demande au serveur (qui utilisera les mêmes règles de src/core) au lieu de calculer ici.
import { LEADER_SLOT, type BattleInput, type Slot, type UnitInit } from '../../core/battle/types';
import { heroToUnit } from '../../core/battle/units';
import { stagePower } from '../../core/data/campaign';
import { incomePerHour, REWARDS, STAGE_REWARD_HOURS, STAGES_PER_CHAPTER } from '../../core/data/economy';
import { HEROES, heroDef } from '../../core/data/heroes';
import {
  FORGE_COUNT, GEAR_SETS, GEAR_SLOTS, ITEM_RARITIES, SLOT_MAX_LEVEL, itemBonus, recycleDust, rollItemRarity, slotUpgradeCost,
  type GearSlot, type Item,
} from '../../core/data/items';
import {
  ACCOUNT_XP_PER_STAGE, ADS_PER_DAY, FRIEND_GIFT, FRIENDS_MAX, GUILD_WAR, LOGIN_MONTH, LOGIN_WELCOME, type LoginReward, RENAME_COST, ARENA_FREE_TICKETS, ARENA_LOSS_POINTS, ARENA_SHOP, ARENA_TOKENS_PER_FIGHT,
  ARENA_WIN_POINTS, DAILY_CHESTS, DAILY_QUESTS, DUNGEON_ATTEMPTS_PER_DAY,
  DUNGEON_LEVELS, DUNGEON_REWARD_HOURS, DUNGEON_STAGE_PER_LEVEL, ESSENCE_RATIO, dungeonItems, FAST_LOOT_COSTS, FAST_LOOT_HOURS, GEMS_PER_10_SUMMONS,
  GEMS_PER_SUMMON, GUILD_BOSS_ATTEMPTS, GUILD_COINS_PER_ATTACK, GUILD_SHOP, IDLE_ITEM_HOURS, MISSION_TEMPLATES,
  MISSIONS_PER_DAY, MONTHLY_CARD, OFFERS, PASS_LEVELS, PASS_POINTS_PER_LEVEL, RED_SCROLLS, RESET_COST, STAGE_GEMS, TOWER_REWARD,
  TOWER_STAGE_PER_FLOOR, WEEKLY_CHESTS, WEEKLY_QUESTS, accountXpForLevel, type DungeonKind, type QuestEvent,
  type Reward,
  TUTORIAL_GIFT_SCROLLS,
  PASS_SEASON_DAYS,
} from '../../core/data/modes';
import { FRAGMENTS_PER_COPY, LADDER, RARITY_RULES } from '../../core/data/stars';
import { levelCap } from '../../core/data/stats';
import { FEATURED_BANNER } from '../../core/data/summon';
import {
  EVENT_BONUS_EVERY, EVENT_BONUS_VALUE, EVENT_BONUSES, EVENT_LEVELS, EVENT_TRIES_PER_DAY, eventScrolls, eventStage, eventXp, heroXpForLevel,
  type EventBonus,
} from '../../core/data/event';
import { applyFusion, canGainStar, isValidFusion, planFusion, type FusionPlan } from '../../core/fusion';
import { levelRefund } from '../../core/power';
import { createRng, pick, type Rng } from '../../core/rng';
import { MAIL_KEEP_DAYS, MAILS, type MailDef } from '../../core/data/mail';
import { BOSS_ELEMENT, BOSSES, GUILD_BOSSES } from '../../core/data/monsters';
import { buildWaves, campaignWaves, chapterElement, chapterOf, slotsAt } from '../../core/stages';
import { summonBasic, summonFeatured, summonOne } from '../../core/summon';
import type { SummonKind } from '../../core/data/summon';
import type { Hero } from '../../core/types';
import { fresh, getState, now, replaceState, update } from './store';
import { CRYSTAL_HOURS, formationOf, gearStatsOf, heroByUid, heroPower, idlePreview, isUnlocked, levelUpCost, resolveReward, slotLevel, teamPower, teamUnits } from './selectors';
import type { TeamKind } from './selectors';
import type { ArenaOpponent, AuthProvider, ColiseumFoe, ColiseumState, EventState, Friend, Gain, GuildWarState, MissionState, PlayerState, Wallet } from './types';
import {
  botTeam, foeUnits, leagueAfter, makeGroup, mixSeed, myRank, pointsChange, rankReward, runColiseum, standings, WEEK_HOURS,
  type ColiseumBot, type ColiseumSetup, type Standing,
} from '../../core/coliseum';
import { COLISEUM, COLISEUM_SHOP } from '../../core/data/coliseum';

// ---------- Outils ----------

export function dayKey(ms: number): string {
  const d = new Date(ms);
  return `${d.getFullYear()}-${d.getMonth() + 1}-${d.getDate()}`;
}

function weekKey(ms: number): string {
  const d = new Date(ms);
  d.setHours(0, 0, 0, 0);
  d.setDate(d.getDate() - ((d.getDay() + 6) % 7));
  return dayKey(d.getTime());
}

function nextRng(s: PlayerState): Rng {
  s.rng += 1;
  return createRng(Math.imul(s.rng, 2654435761) ^ s.createdAt);
}

function emptyGain(): Gain {
  return { currencies: {}, heroes: [], items: [] };
}

function addCurrency(s: PlayerState, gain: Gain, key: keyof Wallet, amount: number) {
  if (!amount) return;
  s.wallet[key] += Math.round(amount);
  gain.currencies[key] = (gain.currencies[key] ?? 0) + Math.round(amount);
}

function addReward(s: PlayerState, gain: Gain, reward: Reward) {
  for (const [k, v] of Object.entries(resolveReward(s, reward))) addCurrency(s, gain, k as keyof Wallet, v ?? 0);
}

/** Héros obtenus pour la première fois pendant cette session (étiquette « Nouveau ! » à la révélation). */
export const newlyFound = new Set<number>();

function addHero(s: PlayerState, defId: string): Hero {
  const hero: Hero = { uid: s.nextUid++, defId, stars: RARITY_RULES[heroDef(defId).rarity].bornStars, level: 1 };
  s.heroes.push(hero);
  // le tout premier héros (le tirage du tutoriel) entre tout de suite dans la section, au milieu
  if (!s.formation.length) s.formation = [[hero.uid, 2]];
  if (!s.discovered.includes(defId)) {
    s.discovered.push(defId);
    newlyFound.add(hero.uid);
  }
  return hero;
}

function makeItem(s: PlayerState, rng: Rng, rarity?: number, luck = 0): Item {
  const item: Item = {
    uid: s.nextUid++,
    slot: pick(rng, GEAR_SLOTS),
    rarity: rarity ?? rollItemRarity(rng, luck),
    tier: chapterOf(Math.max(1, s.campaign.cleared)) - 1,
  };
  // À partir des objets Bleus, une panoplie au hasard.
  if (item.rarity >= 2) item.set = pick(rng, GEAR_SETS);
  s.items.push(item);
  return item;
}

function track(s: PlayerState, event: QuestEvent, n = 1) {
  for (const q of DAILY_QUESTS) if (q.event === event) s.daily.quests[q.id] = (s.daily.quests[q.id] ?? 0) + n;
  for (const q of WEEKLY_QUESTS) if (q.event === event) s.weekly.quests[q.id] = (s.weekly.quests[q.id] ?? 0) + n;
}

/** Nouveau jour, nouvelle semaine : remises à zéro et livraisons quotidiennes. */
export function ensureDay(): void {
  checkMail();
  friendsDay();
  ensureWar();
  ensureColiseum();
  const s = getState();
  const today = dayKey(now());
  const week = weekKey(now());
  if (s.daily.day === today && s.weekly.week === week) return;
  update((st) => {
    if (st.weekly.week !== week) st.weekly = { week, quests: {}, claimed: [], chests: [] };
    if (st.daily.day !== today) {
      const keep = st.daily.missions.filter((m) => m.startedAt && !m.claimed);
      st.daily = {
        day: today, ads: 0, fastLoot: 0, entries: { gold: 0, essence: 0, gear: 0 }, bossAttempts: 0, bossBest: 0,
        arenaFights: 0, guildAttempts: 0, missions: [...keep, ...newMissions(st)], quests: {}, claimed: [], chests: [],
        cardClaimed: false,
      };
      if (st.shop.cardUntil > now()) {
        st.wallet.gems += MONTHLY_CARD.gemsPerDay;
        st.daily.cardClaimed = true;
      }
      track(st, 'login');
      if (!st.arena.opponents.length) st.arena.opponents = makeOpponents(st);
      // une nouvelle saison du passe (28 jours depuis la création du compte) : tout repart de zéro
      const season = Math.floor((now() - st.createdAt) / (PASS_SEASON_DAYS * 86_400_000));
      if ((st.pass.season ?? 0) !== season) {
        st.pass = { points: 0, claimedFree: [], claimedPremium: [], season };
        st.shop.passPremium = false;
      }
    }
  });
}

// ---------- Campagne et butin ----------

export function collectIdle(): Gain {
  return update((s) => {
    const p = idlePreview(s);
    const gain = emptyGain();
    addCurrency(s, gain, 'gold', p.gold);
    addCurrency(s, gain, 'essence', p.essence);
    const rng = nextRng(s);
    for (let i = 0; i < p.items; i++) gain.items.push(makeItem(s, rng));
    addCurrency(s, gain, 'basicScrolls', p.items);
    addCurrency(s, gain, 'crystals', p.crystals);
    s.campaign.itemHours = (s.campaign.itemHours + p.hours) % IDLE_ITEM_HOURS;
    if (s.campaign.cleared >= REWARDS.crystalsFromStage) s.campaign.crystalHours = ((s.campaign.crystalHours ?? 0) + p.hours) % CRYSTAL_HOURS;
    s.campaign.idleFrom = now();
    track(s, 'collectIdle');
    return gain;
  });
}

export function fastLootCost(s: PlayerState): number | null {
  return FAST_LOOT_COSTS[s.daily.fastLoot] ?? null;
}

export function fastLoot(): Gain | null {
  return update((s) => {
    const cost = fastLootCost(s);
    if (cost === null || s.wallet.gems < cost) return null;
    s.wallet.gems -= cost;
    s.daily.fastLoot += 1;
    const gain = emptyGain();
    const perHour = incomePerHour(s.campaign.cleared);
    addCurrency(s, gain, 'gold', perHour * FAST_LOOT_HOURS);
    addCurrency(s, gain, 'essence', perHour * FAST_LOOT_HOURS * ESSENCE_RATIO);
    gain.items.push(makeItem(s, nextRng(s)));
    addCurrency(s, gain, 'basicScrolls', 1);
    return gain;
  });
}

// ---------- Section ----------

const PREFERRED_SLOTS: Record<string, Slot[]> = {
  protector: [0, 1, 2, 3, 4], warrior: [1, 0, 2, 3, 4], marksman: [3, 4, 2, 1, 0], assassin: [4, 3, 2, 1, 0],
  healer: [3, 4, 2, 1, 0], support: [4, 3, 2, 1, 0],
};

/** Lit/écrit la section voulue (principale ou défense). La défense part d'une copie de la principale. */
function editTeam(s: PlayerState, team: TeamKind, change: (list: [number, Slot][]) => [number, Slot][]): void {
  if (team === 'main') s.formation = change(s.formation);
  else s.defenseTeam = change(formationOf(s, 'defense').map(([u, sl]) => [u, sl]));
}

export function toggleInFormation(uid: number, team: TeamKind = 'main'): 'added' | 'removed' | 'full' | 'last' {
  return update((s) => {
    const list = formationOf(s, team);
    if (list.some(([u]) => u === uid)) {
      if (list.length <= 1) return 'last';
      editTeam(s, team, (l) => l.filter(([u]) => u !== uid));
      return 'removed';
    }
    if (list.length >= slotsAt(s.campaign.cleared)) return 'full';
    const hero = heroByUid(s, uid);
    if (!hero) return 'full';
    const taken = new Set(list.map(([, slot]) => slot));
    const slot = PREFERRED_SLOTS[heroDef(hero.defId).role]!.find((x) => !taken.has(x))!;
    editTeam(s, team, (l) => [...l, [uid, slot]]);
    return 'added';
  });
}

/**
 * Pose un héros sur une place choisie de la section (demande du 26/11 : choisir soi-même, sans « Meilleure section ») :
 * s'il y est déjà ailleurs, les deux places s'échangent ; sinon il prend la place (celui qui y était sort de la section).
 * Une place vide se remplit seulement s'il reste de la place.
 */
export function placeInSlot(uid: number, slot: Slot, team: TeamKind = 'main'): 'placed' | 'full' {
  return update((s) => {
    const list = formationOf(s, team);
    const here = list.find(([, sl]) => sl === slot)?.[0];
    const mine = list.find(([u]) => u === uid)?.[1];
    if (here === uid) return 'placed';
    if (mine !== undefined) {
      editTeam(s, team, (l) => l.map(([u, sl]): [number, Slot] => [u, sl === slot ? mine : sl === mine ? slot : sl]));
      return 'placed';
    }
    if (here === undefined && list.length >= slotsAt(s.campaign.cleared)) return 'full';
    editTeam(s, team, (l) => [...l.filter(([, sl]) => sl !== slot), [uid, slot]]);
    return 'placed';
  });
}

export function swapSlots(a: Slot, b: Slot, team: TeamKind = 'main'): void {
  update((s) => editTeam(s, team, (l) => l.map(([u, slot]): [number, Slot] => [u, slot === a ? b : slot === b ? a : slot])));
}

/** Remplit la section avec les héros les plus forts, chacun à son poste conseillé (un chef au centre si possible). */
export function autoFormation(exclude: readonly number[] = [], team: TeamKind = 'main'): void {
  update((s) => {
    const best = [...s.heroes].filter((h) => !exclude.includes(h.uid)).sort((a, b) => heroPower(s, b) - heroPower(s, a)).slice(0, slotsAt(s.campaign.cleared));
    const taken = new Set<Slot>();
    const list: [number, Slot][] = best.map((h) => {
      const slot = PREFERRED_SLOTS[heroDef(h.defId).role]!.find((x) => !taken.has(x))!;
      taken.add(slot);
      return [h.uid, slot];
    });
    const center = list.find(([, sl]) => sl === LEADER_SLOT);
    const chief = list.find(([u]) => !!heroDef(heroByUid(s, u)!.defId).talent);
    if (chief && center && !heroDef(heroByUid(s, center[0])!.defId).talent) {
      center[1] = chief[1];
      chief[1] = LEADER_SLOT;
    }
    editTeam(s, team, () => list);
  });
}

// ---------- Héros ----------

export function levelUp(uid: number, times = 1): number {
  return update((s) => {
    const hero = heroByUid(s, uid);
    let done = 0;
    while (hero && done < times) {
      const cost = levelUpCost(hero);
      if (!cost || s.wallet.gold < cost.gold || s.wallet.essence < cost.essence) break;
      s.wallet.gold -= cost.gold;
      s.wallet.essence -= cost.essence;
      hero.level += 1;
      done += 1;
    }
    if (done) track(s, 'levelUp', done);
    return done;
  });
}

/** Ce qu'on récupère en vidant un héros : niveaux, renforcement des emplacements, objets portés. */
export function heroRefund(s: PlayerState, hero: Hero): { gold: number; essence: number; dust: number; items: number } {
  const levelGold = levelRefund(hero.level);
  let gold = levelGold;
  let dust = 0;
  // Le renforcement des emplacements est rendu aussi (« rien n'est perdu »).
  const levels = s.slotLevels[hero.uid] ?? {};
  for (const slot of GEAR_SLOTS) {
    for (let l = 0; l < (levels[slot] ?? 0); l++) {
      const cost = slotUpgradeCost(l);
      gold += cost.gold;
      dust += cost.dust;
    }
  }
  const items = s.items.filter((it) => it.heroUid === hero.uid).length;
  return { gold, essence: Math.round(levelGold * ESSENCE_RATIO), dust, items };
}

function refundHero(s: PlayerState, hero: Hero, gain?: Gain) {
  const r = heroRefund(s, hero);
  s.wallet.gold += r.gold;
  s.wallet.essence += r.essence;
  s.wallet.dust += r.dust;
  if (gain) {
    gain.currencies.gold = (gain.currencies.gold ?? 0) + r.gold;
    gain.currencies.essence = (gain.currencies.essence ?? 0) + r.essence;
    gain.currencies.dust = (gain.currencies.dust ?? 0) + r.dust;
  }
  for (const it of s.items) if (it.heroUid === hero.uid) delete it.heroUid;
  delete s.slotLevels[hero.uid];
}

/** Un héros vaut la peine d'être réinitialisé s'il a des niveaux, des emplacements renforcés ou des objets. */
export function canReset(s: PlayerState, hero: Hero): boolean {
  const r = heroRefund(s, hero);
  return hero.level > 1 || r.dust > 0 || r.items > 0;
}

/** Réinitialise un héros (niveau 1, objets au sac) contre RESET_COST gemmes ; tout est rendu. */
export function resetHero(uid: number): Gain | null {
  const s0 = getState();
  const h0 = heroByUid(s0, uid);
  if (!h0 || !canReset(s0, h0) || s0.wallet.gems < RESET_COST) return null;
  return update((s) => {
    const gain = emptyGain();
    const hero = heroByUid(s, uid)!;
    s.wallet.gems -= RESET_COST;
    refundHero(s, hero, gain);
    hero.level = 1;
    return gain;
  });
}

export function equipBest(uid: number): void {
  update((s) => {
    for (const slot of GEAR_SLOTS) {
      const current = s.items.find((it) => it.heroUid === uid && it.slot === slot);
      const best = s.items
        .filter((it) => it.slot === slot && it.heroUid === undefined)
        .sort((a, b) => itemBonus(b) - itemBonus(a))[0];
      if (best && (!current || itemBonus(best) > itemBonus(current))) {
        if (current) delete current.heroUid;
        best.heroUid = uid;
      }
    }
  });
}

export function unequipAll(uid: number): void {
  update((s) => {
    for (const it of s.items) if (it.heroUid === uid) delete it.heroUid;
  });
}

/** Pose un objet sur un héros (l'objet déjà à cet emplacement retourne au sac ; un objet porté par un autre héros change de héros). */
export function equipItem(itemUid: number, heroUid: number): void {
  update((s) => {
    const item = s.items.find((it) => it.uid === itemUid);
    if (!item) return;
    for (const it of s.items) if (it.heroUid === heroUid && it.slot === item.slot) delete it.heroUid;
    item.heroUid = heroUid;
  });
}

export function unequipItem(itemUid: number): void {
  update((s) => {
    const item = s.items.find((it) => it.uid === itemUid);
    if (item) delete item.heroUid;
  });
}

/** Renforce un emplacement d'un héros (+1). Renvoie faux s'il manque de l'or ou de la poussière. */
export function upgradeSlot(heroUid: number, slot: GearSlot): boolean {
  return update((s) => {
    const level = slotLevel(s, heroUid, slot);
    if (level >= SLOT_MAX_LEVEL) return false;
    const cost = slotUpgradeCost(level);
    if (s.wallet.gold < cost.gold || s.wallet.dust < cost.dust) return false;
    s.wallet.gold -= cost.gold;
    s.wallet.dust -= cost.dust;
    s.slotLevels[heroUid] = { ...(s.slotLevels[heroUid] ?? {}), [slot]: level + 1 };
    return true;
  });
}

/** Les objets du sac (non portés) qui peuvent être forgés avec celui-ci. */
export function forgePartners(s: PlayerState, item: Item): Item[] {
  return s.items
    .filter((it) => it.uid !== item.uid && it.heroUid === undefined && it.slot === item.slot && it.rarity === item.rarity)
    .sort((a, b) => a.tier - b.tier);
}

function forgeWith(s: PlayerState, items: Item[]): Item {
  const used = new Set(items.map((it) => it.uid));
  const first = items[0]!;
  s.items = s.items.filter((it) => !used.has(it.uid));
  const result: Item = {
    uid: s.nextUid++,
    slot: first.slot,
    rarity: Math.min(ITEM_RARITIES - 1, first.rarity + 1),
    tier: Math.max(...items.map((it) => it.tier)),
  };
  // La panoplie : celle du premier objet ; un objet qui devient Bleu en reçoit une au hasard.
  const set = items.find((it) => it.set)?.set;
  if (set) result.set = set;
  else if (result.rarity >= 2) result.set = pick(nextRng(s), GEAR_SETS);
  s.items.push(result);
  return result;
}

/** Forge cet objet (non porté) avec 2 autres identiques du sac. */
export function forgeItem(itemUid: number): Item | null {
  return update((s) => {
    const item = s.items.find((it) => it.uid === itemUid);
    if (!item || item.heroUid !== undefined || item.rarity >= ITEM_RARITIES - 1) return null;
    const partners = forgePartners(s, item);
    if (partners.length < FORGE_COUNT - 1) return null;
    return forgeWith(s, [item, ...partners.slice(0, FORGE_COUNT - 1)]);
  });
}

/** « Tout forger » : forge les objets du sac, des plus faibles aux plus forts, jusqu'à la rareté `upTo` (incluse) comme résultat. */
export function forgeAll(upTo = 4): Item[] {
  return update((s) => {
    const made: Item[] = [];
    for (let rarity = 0; rarity < upTo; rarity++) {
      for (const slot of GEAR_SLOTS) {
        for (;;) {
          const pool = s.items.filter((it) => it.heroUid === undefined && it.slot === slot && it.rarity === rarity).sort((a, b) => a.tier - b.tier);
          if (pool.length < FORGE_COUNT) break;
          made.push(forgeWith(s, pool.slice(0, FORGE_COUNT)));
        }
      }
    }
    return made;
  });
}

/** Recycle des objets du sac (jamais ceux portés) en poussière de forge. */
export function recycleItems(itemUids: number[]): number {
  return update((s) => {
    const ids = new Set(itemUids);
    let dust = 0;
    s.items = s.items.filter((it) => {
      if (!ids.has(it.uid) || it.heroUid !== undefined) return true;
      dust += recycleDust(it);
      return false;
    });
    s.wallet.dust += dust;
    return dust;
  });
}

/** Ce qu'il manque pour la prochaine étoile, et le plan si tout est là. */
export function fusionPreview(uid: number): { plan: FusionPlan | null; maxed: boolean } {
  const s = getState();
  const hero = heroByUid(s, uid);
  if (!hero || !canGainStar(hero)) return { plan: null, maxed: true };
  const protect = new Set(s.formation.map(([u]) => u).filter((u) => u !== uid));
  return { plan: planFusion(s.heroes, uid, { protect, crystalsOwned: s.wallet.crystals }), maxed: false };
}

export type NeedKind = 'identical' | 'copy' | 'fodder';
export type FusionPicks = Record<NeedKind, number[]>;

export interface FusionNeed {
  kind: NeedKind;
  stars: number;
  element: string;
  defId?: string;
  /** Le héros choisi pour cette case, s'il y en a un. */
  hero?: Hero;
}

interface FusionSetup {
  hero: Hero;
  /** Nombre de cases de chaque sorte, et ce qu'elles demandent. */
  slots: { kind: NeedKind; count: number; stars: number; defId?: string }[];
  /** Héros qui peuvent remplir chaque sorte de case (hors section), les moins précieux d'abord. */
  pools: Record<NeedKind, Hero[]>;
  crystals: number;
  newStars: number;
}

const RANK = { common: 0, rare: 1, epic: 2, legendary: 3 } as const;

function fusionSetup(s: PlayerState, uid: number): FusionSetup | null {
  const hero = heroByUid(s, uid);
  if (!hero || !canGainStar(hero)) return null;
  const d = heroDef(hero.defId);
  const rule = RARITY_RULES[d.rarity];
  const inTeam = new Set(s.formation.map(([u]) => u).filter((u) => u !== uid));
  const free = s.heroes
    .filter((h) => h.uid !== uid && !inTeam.has(h.uid))
    .sort((a, b) => RANK[heroDef(a.defId).rarity] - RANK[heroDef(b.defId).rarity] || a.level - b.level);
  const pools: Record<NeedKind, Hero[]> = { identical: [], copy: [], fodder: [] };
  if (rule.fusion === 'triple') {
    pools.identical = free.filter((h) => h.defId === hero.defId && h.stars === hero.stars);
    return { hero, slots: [{ kind: 'identical', count: 2, stars: hero.stars, defId: d.id }], pools, crystals: 0, newStars: hero.stars + 1 };
  }
  const step = LADDER[hero.stars + 1]!;
  pools.copy = free.filter((h) => h.defId === hero.defId && h.stars === rule.bornStars);
  pools.fodder = free.filter((h) => h.stars === step.fodderStars && heroDef(h.defId).element === d.element);
  const slots: FusionSetup['slots'] = [];
  if (step.copies) slots.push({ kind: 'copy', count: step.copies, stars: rule.bornStars, defId: d.id });
  if (step.fodderCount) slots.push({ kind: 'fodder', count: step.fodderCount, stars: step.fodderStars });
  return { hero, slots, pools, crystals: step.crystals, newStars: hero.stars + 1 };
}

/** Choix proposé d'office : les moins précieux, jamais un Légendaire en nourriture. */
export function autoPicks(uid: number): FusionPicks {
  const picks: FusionPicks = { identical: [], copy: [], fodder: [] };
  const setup = fusionSetup(getState(), uid);
  if (!setup) return picks;
  const used = new Set<number>();
  for (const slot of setup.slots) {
    const pool = setup.pools[slot.kind].filter((h) => !used.has(h.uid) && (slot.kind !== 'fodder' || heroDef(h.defId).rarity !== 'legendary'));
    picks[slot.kind] = pool.slice(0, slot.count).map((h) => h.uid);
    picks[slot.kind].forEach((u) => used.add(u));
  }
  return picks;
}

/** Les héros qui peuvent remplir une sorte de case. */
export function fusionPool(uid: number, kind: NeedKind): Hero[] {
  return fusionSetup(getState(), uid)?.pools[kind] ?? [];
}

/**
 * Ce que demande la prochaine étoile, case par case, rempli avec les héros choisis
 * (ou le choix proposé d'office) : ce qui manque reste vide (grisé à l'écran).
 */
export function fusionNeeds(uid: number, picks?: FusionPicks): { needs: FusionNeed[]; crystals: number; newStars: number; ready: boolean; consumed: number[] } | null {
  const s = getState();
  const setup = fusionSetup(s, uid);
  if (!setup) return null;
  const chosen = picks ?? autoPicks(uid);
  const d = heroDef(setup.hero.defId);
  const needs: FusionNeed[] = [];
  const used = new Set<number>();
  for (const slot of setup.slots) {
    const ok = new Set(setup.pools[slot.kind].map((h) => h.uid));
    const heroes = chosen[slot.kind].filter((u) => ok.has(u) && !used.has(u)).slice(0, slot.count).map((u) => heroByUid(s, u)!);
    heroes.forEach((h) => used.add(h.uid));
    for (let i = 0; i < slot.count; i++) needs.push({ kind: slot.kind, stars: slot.stars, element: d.element, defId: slot.defId, hero: heroes[i] });
  }
  const ready = needs.every((n) => n.hero) && s.wallet.crystals >= setup.crystals;
  return { needs, crystals: setup.crystals, newStars: setup.newStars, ready, consumed: [...used] };
}

function doFusion(s: PlayerState, plan: FusionPlan, gain: Gain) {
  for (const uid of plan.consumed) {
    const h = heroByUid(s, uid);
    if (h) refundHero(s, h, gain);
  }
  s.heroes = applyFusion(s.heroes, plan).roster;
  s.formation = s.formation.filter(([u]) => !plan.consumed.includes(u));
  s.wallet.crystals -= plan.crystals;
  track(s, 'fuse');
}

/** Fusionne. Sans liste, les héros sacrifiés sont choisis d'office ; avec une liste, ce sont ceux-là (vérifiés). */
export function fuse(uid: number, consumed?: number[]): Gain | null {
  let plan = fusionPreview(uid).plan;
  if (consumed) {
    const s = getState();
    const needs = fusionNeeds(uid, { identical: consumed, copy: consumed, fodder: consumed });
    const hero = heroByUid(s, uid);
    if (!hero || !needs?.ready || needs.consumed.length !== consumed.length) return null;
    plan = { targetUid: uid, consumed, crystals: needs.crystals, newStars: needs.newStars };
    if (!isValidFusion(s.heroes, plan, s.wallet.crystals)) return null;
  }
  if (!plan) return null;
  return update((s) => {
    const gain = emptyGain();
    doFusion(s, plan, gain);
    return gain;
  });
}

/** « Tout fusionner » : les fusions simples (Communs et Rares, 3 identiques), hors section. */
export function fuseAllSimple(): number {
  return update((s) => {
    let count = 0;
    for (let changed = true; changed; ) {
      changed = false;
      const inTeam = new Set(s.formation.map(([u]) => u));
      for (const h of s.heroes) {
        if (RARITY_RULES[heroDef(h.defId).rarity].fusion !== 'triple' || !canGainStar(h)) continue;
        const plan = planFusion(s.heroes, h.uid, { protect: inTeam });
        if (!plan) continue;
        doFusion(s, plan, emptyGain());
        count += 1;
        changed = true;
        break;
      }
    }
    return count;
  });
}

// ---------- Invocations ----------

/** Simple : parchemins simples ; spécial : parchemins rouges ; normal : parchemins, sinon gemmes. */
export function summonCost(kind: SummonKind, count: 1 | 10): { currency: keyof Wallet; amount: number } {
  const s = getState();
  if (kind === 'basic') return { currency: 'basicScrolls', amount: count };
  if (kind === 'featured') return { currency: 'redScrolls', amount: count };
  if (s.wallet.scrolls >= count) return { currency: 'scrolls', amount: count };
  return { currency: 'gems', amount: count === 10 ? GEMS_PER_10_SUMMONS : GEMS_PER_SUMMON };
}

export function summon(kind: SummonKind, count: 1 | 10, free = false): Hero[] | null {
  return update((s) => {
    const cost = summonCost(kind, count);
    if (!free) {
      if (s.wallet[cost.currency] < cost.amount) return null;
      s.wallet[cost.currency] -= cost.amount;
    }
    const rng = nextRng(s);
    const out: Hero[] = [];
    for (let i = 0; i < count; i++) {
      const def = kind === 'basic' ? summonBasic(rng) : kind === 'featured' ? summonFeatured(s.summon, rng) : summonOne(s.summon, rng);
      out.push(addHero(s, def.id));
    }
    // le portail spécial compte comme le normal (même compteur de Légendaire garanti, mêmes quêtes)
    if (kind !== 'basic') {
      s.summon.total += count;
      track(s, 'summon', count);
    }
    return out;
  });
}

export function setFragmentTarget(defId: string): void {
  update((s) => void (s.fragmentTarget = defId));
}

export function claimFragments(defId: string): Hero | null {
  return update((s) => {
    if ((s.fragments[defId] ?? 0) < FRAGMENTS_PER_COPY) return null;
    s.fragments[defId] = (s.fragments[defId] ?? 0) - FRAGMENTS_PER_COPY;
    return addHero(s, defId);
  });
}

// ---------- Combats ----------

export type BattleKind = 'campaign' | 'tower' | 'dungeon' | 'event' | 'arena' | 'guildBoss' | 'friend' | 'guildWar';

export interface BattleRequest {
  kind: BattleKind;
  title: string;
  heroes: UnitInit[];
  waves: UnitInit[][];
  seed: number;
  /** Combat de boss : on compte les dégâts, il n'y a pas de défaite. */
  damageMode?: boolean;
  dungeon?: { kind: DungeonKind; level: number };
  opponentId?: string;
}

export interface BattleResult {
  win: boolean;
  damage: number;
  /** Part des héros encore debout à la fin (0 à 1). */
  alive?: number;
  /** Vie de chaque héros à la fin (id de l'unité → part de sa vie max ; 0 = mort) : mode Événement. */
  heroHp?: Record<string, number>;
  inputs: BattleInput[];
}

function seedFor(s: PlayerState): number {
  s.rng += 1;
  return (Math.imul(s.rng, 2246822519) ^ s.createdAt) >>> 0;
}

export function campaignBattle(): BattleRequest {
  return update((s) => ({
    kind: 'campaign' as const,
    title: `${chapterOf(s.campaign.cleared + 1)}-${((s.campaign.cleared) % STAGES_PER_CHAPTER) + 1}`,
    heroes: teamUnits(s),
    waves: campaignWaves(s.campaign.cleared + 1),
    seed: seedFor(s),
  }));
}

export function towerBattle(): BattleRequest {
  return update((s) => {
    const floor = s.tower.floor + 1;
    return {
      kind: 'tower' as const,
      title: `${floor}`,
      heroes: teamUnits(s),
      waves: towerWaves(floor),
      seed: seedFor(s),
    };
  });
}

function referencePower(s: PlayerState): number {
  return stagePower(Math.max(1, s.campaign.cleared));
}

export function dungeonBattle(kind: DungeonKind): BattleRequest {
  return update((s) => {
    const level = s.dungeons[kind] + 1;
    return {
      kind: 'dungeon' as const,
      title: `${level}`,
      heroes: teamUnits(s),
      waves: dungeonWaves(kind, level),
      seed: seedFor(s),
      dungeon: { kind, level },
    };
  });
}

/** Les boss tournent selon le jour de la semaine. Ils sont très résistants : on vise le plus de dégâts. */
export function dailyBossId(at = now()): string {
  return BOSSES[new Date(at).getDay() % BOSSES.length]!;
}

/**
 * Le boss de guilde change lui aussi chaque jour, à minuit (quand les essais reviennent) : jamais le même que le boss du
 * jour. Son élément donne l'image de l'onglet Boss de la guilde (« Donjon de feu »…, ui/backdrop-dungeon.tsx).
 */
export function guildBossId(at = now()): string {
  // chaque jour (jour local), un des 4 boss de guilde, jamais celui du boss du jour : on tourne parmi les 3 autres
  const d = new Date(at);
  const day = Math.floor(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()) / 86400000);
  const others = GUILD_BOSSES.filter((b) => b !== dailyBossId(at));
  return others[day % others.length]!;
}

/** Le moment où le boss de guilde laisse sa place à un autre (le prochain minuit où il change). */
export function guildBossEndsAt(at = now()): number {
  const id = guildBossId(at);
  const d = new Date(at);
  d.setHours(24, 0, 0, 0);
  for (let i = 0; i < 7 && guildBossId(d.getTime()) === id; i++) d.setDate(d.getDate() + 1);
  return d.getTime();
}

function bossWave(s: PlayerState, bossId: string, hpFactor: number, seed: number): UnitInit[][] {
  const waves = buildWaves({ power: referencePower(s), count: 1, waves: 1, element: BOSS_ELEMENT[bossId] ?? 'fire', seed, boss: bossId });
  return waves.map((w) => w.map((u) => ({ ...u, maxHp: Math.round(u.maxHp * hpFactor) })));
}


export function guildBossBattle(): BattleRequest {
  return update((s) => ({
    kind: 'guildBoss' as const,
    title: guildBossId(),
    heroes: teamUnits(s),
    waves: bossWave(s, guildBossId(), 40, 11),
    seed: seedFor(s),
    damageMode: true,
  }));
}

export function arenaBattle(opponentId: string): BattleRequest | null {
  return update((s) => {
    const o = s.arena.opponents.find((x) => x.id === opponentId);
    if (!o || s.daily.arenaFights >= ARENA_FREE_TICKETS) return null;
    return { kind: 'arena' as const, title: o.name, heroes: teamUnits(s), waves: [arenaEnemies(o)], seed: seedFor(s), opponentId };
  });
}

/**
 * Un combat avant son lancement : ce que montre l'écran de préparation (ennemis, force demandée),
 * puis `build` crée le vrai combat avec la section choisie.
 */
export interface BattlePlan {
  kind: BattleKind;
  title: string;
  waves: UnitInit[][];
  need?: number;
  /** Héros qui ne peuvent pas combattre ici (déjà utilisés aujourd'hui en guerre de guildes). */
  exclude?: number[];
  /** Donjon combattu (choisit le décor). */
  dungeon?: DungeonKind;
  build: () => BattleRequest | null;
}

export function campaignPlan(): BattlePlan {
  const s = getState();
  const stage = s.campaign.cleared + 1;
  return {
    kind: 'campaign', title: `${chapterOf(stage)}-${((stage - 1) % STAGES_PER_CHAPTER) + 1}`,
    waves: campaignWaves(stage), need: stagePower(stage), build: campaignBattle,
  };
}

export function towerPlan(): BattlePlan {
  const floor = getState().tower.floor + 1;
  return {
    kind: 'tower', title: `${floor}`, need: stagePower(floor * TOWER_STAGE_PER_FLOOR),
    waves: towerWaves(floor), build: towerBattle,
  };
}

function towerWaves(floor: number): UnitInit[][] {
  return buildWaves({
    power: stagePower(Math.max(1, floor * TOWER_STAGE_PER_FLOOR)), count: 5, waves: floor % 10 === 0 ? 2 : 1,
    element: chapterElement(floor), seed: floor * 104729, boss: floor % 10 === 0 ? BOSSES[(floor / 10) % BOSSES.length] : undefined,
  });
}

export function dungeonPower(level: number): number {
  return stagePower(Math.max(1, level * DUNGEON_STAGE_PER_LEVEL));
}

/** Le prochain niveau d'un donjon (à combattre). */
export function dungeonPlan(kind: DungeonKind): BattlePlan | null {
  const level = getState().dungeons[kind] + 1;
  if (level > DUNGEON_LEVELS) return null;
  return { kind: 'dungeon', title: `${level}`, waves: dungeonWaves(kind, level), need: dungeonPower(level), dungeon: kind, build: () => dungeonBattle(kind) };
}

function dungeonWaves(kind: DungeonKind, level: number): UnitInit[][] {
  return buildWaves({
    power: dungeonPower(level), count: 5, waves: 2,
    element: (['fire', 'water', 'earth'] as const)[['gold', 'essence', 'gear'].indexOf(kind)]!, seed: level * 7919 + kind.length,
  });
}

/** Ce que rapporte un niveau de donjon (même chose en combat ou en balayage). */
export function dungeonRewardPreview(kind: DungeonKind, level: number): { gold?: number; essence?: number; items?: number } {
  const perHour = incomePerHour(level * DUNGEON_STAGE_PER_LEVEL);
  if (kind === 'gold') return { gold: Math.round(perHour * DUNGEON_REWARD_HOURS) };
  if (kind === 'essence') return { essence: Math.round(perHour * DUNGEON_REWARD_HOURS * ESSENCE_RATIO * 2) };
  return { items: dungeonItems(level).count };
}

function giveDungeonReward(s: PlayerState, gain: Gain, kind: DungeonKind, level: number) {
  const r = dungeonRewardPreview(kind, level);
  if (r.gold) addCurrency(s, gain, 'gold', r.gold);
  if (r.essence) addCurrency(s, gain, 'essence', r.essence);
  if (r.items) {
    const rng = nextRng(s);
    for (let i = 0; i < r.items; i++) gain.items.push(makeItem(s, rng, undefined, dungeonItems(level).luck));
  }
  s.daily.entries[kind] += 1;
  track(s, 'dungeon');
}

export function dungeonAttemptsLeft(s: PlayerState, kind: DungeonKind): number {
  return Math.max(0, DUNGEON_ATTEMPTS_PER_DAY - s.daily.entries[kind]);
}

/** Balayage : on rejoue instantanément le dernier niveau gagné, sans combat, contre un essai. */
export function sweepDungeon(kind: DungeonKind): Gain | null {
  const s0 = getState();
  if (s0.dungeons[kind] < 1 || dungeonAttemptsLeft(s0, kind) <= 0) return null;
  return update((s) => {
    const gain = emptyGain();
    giveDungeonReward(s, gain, kind, s.dungeons[kind]);
    return gain;
  });
}


export function guildBossPlan(): BattlePlan {
  return { kind: 'guildBoss', title: guildBossId(), waves: bossWave(getState(), guildBossId(), 40, 11), build: guildBossBattle };
}

export function arenaPlan(opponentId: string): BattlePlan | null {
  const o = getState().arena.opponents.find((x) => x.id === opponentId);
  if (!o) return null;
  return { kind: 'arena', title: o.name, waves: [arenaEnemies(o)], need: opponentPower(o), build: () => arenaBattle(opponentId) };
}

function arenaEnemies(o: ArenaOpponent): UnitInit[] {
  return o.team.map((m, i) => ({
    ...heroToUnit({ uid: 9000 + i, defId: m.defId, stars: m.stars, level: m.level }, m.slot),
    id: `e-0-${i}`,
    side: 'enemy' as const,
  }));
}

/** Le combat permanent de l'accueil : la section contre les vagues du dernier niveau gagné. */
export function idleSetup(): { heroes: UnitInit[]; waves: UnitInit[][] } {
  const s = getState();
  const heroes = teamUnits(s);
  // pas encore de héros (avant le premier tirage du tutoriel) : un décor calme, sans monstres
  return { heroes, waves: heroes.length ? campaignWaves(Math.max(1, s.campaign.cleared)) : [] };
}

/** Le résultat d'un combat : récompenses selon le mode. */
export function finishBattle(req: BattleRequest, res: BattleResult): Gain {
  return update((s) => {
    const gain = emptyGain();
    const rng = nextRng(s);
    const perHour = incomePerHour(s.campaign.cleared);
    switch (req.kind) {
      case 'campaign': {
        if (!res.win) break;
        s.campaign.cleared += 1;
        const stage = s.campaign.cleared;
        addCurrency(s, gain, 'gold', incomePerHour(stage) * STAGE_REWARD_HOURS);
        addCurrency(s, gain, 'essence', incomePerHour(stage) * STAGE_REWARD_HOURS * ESSENCE_RATIO);
        addCurrency(s, gain, 'gems', STAGE_GEMS);
        if (stage % STAGES_PER_CHAPTER === 0) {
          addCurrency(s, gain, 'scrolls', REWARDS.chapterSummons);
          addCurrency(s, gain, 'redScrolls', RED_SCROLLS.perChapter);
          gain.items.push(makeItem(s, rng, undefined, 1));
        }
        s.account.xp += ACCOUNT_XP_PER_STAGE;
        while (s.account.xp >= accountXpForLevel(s.account.level)) {
          s.account.xp -= accountXpForLevel(s.account.level);
          s.account.level += 1;
          addCurrency(s, gain, 'gems', 50);
        }
        track(s, 'winStage');
        break;
      }
      case 'tower': {
        if (!res.win) break;
        s.tower.floor += 1;
        const f = s.tower.floor;
        addReward(s, gain, { essenceH: TOWER_REWARD.essenceHours });
        if (f % TOWER_REWARD.scrollsEvery === 0) addCurrency(s, gain, 'scrolls', 1);
        if (f % TOWER_REWARD.gemsEvery === 0) addCurrency(s, gain, 'gems', TOWER_REWARD.gems);
        track(s, 'tower');
        break;
      }
      case 'dungeon': {
        // Un essai n'est compté que si on gagne.
        if (!res.win || !req.dungeon) break;
        const { kind, level } = req.dungeon;
        if (dungeonAttemptsLeft(s, kind) <= 0 || level !== s.dungeons[kind] + 1) break;
        s.dungeons[kind] = level;
        giveDungeonReward(s, gain, kind, level);
        break;
      }
      case 'event': {
        eventAfterBattle(s, gain, res);
        break;
      }
      case 'arena': {
        s.daily.arenaFights += 1;
        s.arena.points = Math.max(0, s.arena.points + (res.win ? ARENA_WIN_POINTS : ARENA_LOSS_POINTS));
        addCurrency(s, gain, 'arenaTokens', res.win ? ARENA_TOKENS_PER_FIGHT.win : ARENA_TOKENS_PER_FIGHT.loss);
        s.arena.opponents = makeOpponents(s);
        track(s, 'arena');
        break;
      }
      case 'guildWar': {
        const war = s.guildWar;
        if (!war) break;
        war.attacks += 1;
        war.used.push(...req.heroes.map((u) => Number(u.id.slice(2))));
        const stars = warStars(res.win, res.alive ?? 0);
        war.myStars += stars;
        addCurrency(s, gain, 'guildCoins', stars * GUILD_WAR.coinsPerStar);
        break;
      }
      case 'guildBoss': {
        s.daily.guildAttempts += 1;
        s.guild.bossDamage += res.damage;
        addCurrency(s, gain, 'guildCoins', GUILD_COINS_PER_ATTACK);
        track(s, 'guildBoss');
        break;
      }
    }
    return gain;
  });
}

// ---------- Missions ----------

function newMissions(s: PlayerState): MissionState[] {
  const rng = nextRng(s);
  return Array.from({ length: MISSIONS_PER_DAY }, (_, i) => ({
    id: `${dayKey(now())}-${i}`,
    templateId: pick(rng, MISSION_TEMPLATES).id,
    heroUids: [],
    claimed: false,
  }));
}

export function missionTemplate(m: MissionState) {
  return MISSION_TEMPLATES.find((t) => t.id === m.templateId)!;
}

export function missionEnd(m: MissionState): number {
  return (m.startedAt ?? 0) + missionTemplate(m).hours * 3.6e6;
}

/** Envoie les héros disponibles les moins utiles (hors section) qui remplissent la condition. */
/** Héros qui peuvent partir en mission (assez d'étoiles, pas déjà partis), les moins utiles d'abord. */
export function missionCandidates(id: string): { eligible: Hero[]; need: number; minStars: number } | null {
  const s = getState();
  const m = s.daily.missions.find((x) => x.id === id);
  if (!m || m.startedAt) return null;
  const t = missionTemplate(m);
  const busy = new Set(s.daily.missions.filter((x) => x.startedAt && !x.claimed).flatMap((x) => x.heroUids));
  const inTeam = new Set(s.formation.map(([u]) => u));
  const eligible = s.heroes
    .filter((h) => !busy.has(h.uid) && h.stars >= t.minStars)
    .sort((a, b) => Number(inTeam.has(a.uid)) - Number(inTeam.has(b.uid)) || a.stars - b.stars || a.level - b.level);
  return { eligible, need: t.heroes, minStars: t.minStars };
}

/** Envoie une mission avec les héros choisis (ou, sans liste, ceux proposés d'office). */
export function sendMission(id: string, heroUids?: number[]): boolean {
  const c = missionCandidates(id);
  if (!c) return false;
  const ok = new Set(c.eligible.map((h) => h.uid));
  const team = heroUids ?? c.eligible.slice(0, c.need).map((h) => h.uid);
  if (team.length !== c.need || new Set(team).size !== team.length || team.some((u) => !ok.has(u))) return false;
  return update((s) => {
    const m = s.daily.missions.find((x) => x.id === id)!;
    m.heroUids = team;
    m.startedAt = now();
    return true;
  });
}

export function claimMission(id: string): Gain | null {
  return update((s) => {
    const m = s.daily.missions.find((x) => x.id === id);
    if (!m || !m.startedAt || m.claimed || now() < missionEnd(m)) return null;
    m.claimed = true;
    const gain = emptyGain();
    const r = missionTemplate(m).reward;
    const perHour = incomePerHour(s.campaign.cleared);
    if (r.kind === 'gold') addCurrency(s, gain, 'gold', perHour * (r.hours ?? 1));
    else if (r.kind === 'essence') addCurrency(s, gain, 'essence', perHour * (r.hours ?? 1) * ESSENCE_RATIO);
    else addCurrency(s, gain, r.kind, r.amount ?? 0);
    track(s, 'mission');
    return gain;
  });
}

// ---------- Arène ----------

const BOT_NAMES = ['Kaïro', 'Lunaria', 'Vaelis', 'Tormund', 'Ishara', 'Draven7', 'Mikaze', 'Orsolya', 'Bastien', 'Yuna', 'Ragnis', 'Selka', 'Noctis', 'Aïko', 'Feyd', 'Mirelle'];

function makeOpponents(s: PlayerState): ArenaOpponent[] {
  const rng = nextRng(s);
  const mine = Math.max(500, teamPower(s));
  const slots: Slot[] = [0, 1, 2, 3, 4];
  return [0.8, 1, 1.2].map((ratio, i) => {
    const target = (mine * ratio) / 5;
    const team = slots.map((slot) => {
      const def = pick(rng, HEROES.filter((h) => h.rarity !== 'common'));
      const stars = RARITY_RULES[def.rarity].bornStars;
      const hero: Hero = { uid: 0, defId: def.id, stars, level: 1 };
      while (heroPower(s, hero) < target && hero.level < 400) hero.level += 1;
      return { defId: def.id, stars, level: hero.level, slot };
    });
    return { id: `o-${s.rng}-${i}`, name: pick(rng, BOT_NAMES), points: Math.round(s.arena.points + (ratio - 1) * 200), team };
  });
}

export function refreshOpponents(): void {
  update((s) => void (s.arena.opponents = makeOpponents(s)));
}

export function opponentPower(o: ArenaOpponent): number {
  const s = getState();
  return o.team.reduce((sum, m) => sum + heroPower(s, { uid: 0, defId: m.defId, stars: m.stars, level: m.level }), 0);
}

// ---------- Guilde et tchat ----------

export const BOT_GUILDS = ['Les Lames d’Aube', 'Ordre du Corbeau', 'Les Vents Sauvages'];

export function joinGuild(name: string): void {
  update((s) => {
    s.guild = { joined: name, bossDamage: 0, chat: [], lastBotAt: 0 };
  });
}

export function leaveGuild(): void {
  update((s) => void (s.guild.joined = null));
}

/** Les autres membres « parlent » de temps en temps (messages préparés du prototype). */
export function botChatter(lines: string[], target: 'guild' | 'world'): void {
  update((s) => {
    const chat = target === 'guild' ? s.guild.chat : s.worldChat;
    const rng = nextRng(s);
    const last = chat[chat.length - 1]?.at ?? 0;
    if (now() - last < 60_000 && chat.length > 3) return;
    for (let i = chat.length ? 1 : 4; i > 0; i--) chat.push({ from: pick(rng, BOT_NAMES), text: pick(rng, lines), at: now() - i * 45_000 });
    if (chat.length > 60) chat.splice(0, chat.length - 60);
  });
}

export function sendChat(text: string, target: 'guild' | 'world'): void {
  const clean = text.trim().slice(0, 200);
  if (!clean) return;
  update((s) => {
    (target === 'guild' ? s.guild.chat : s.worldChat).push({ from: s.name, text: clean, at: now(), me: true });
  });
}

// ---------- Quêtes et passe ----------

export function questPoints(kind: 'daily' | 'weekly'): number {
  const s = getState();
  const defs = kind === 'daily' ? DAILY_QUESTS : WEEKLY_QUESTS;
  const claimed = kind === 'daily' ? s.daily.claimed : s.weekly.claimed;
  return defs.filter((q) => claimed.includes(q.id)).reduce((a, q) => a + q.points, 0);
}

export function claimQuest(id: string, kind: 'daily' | 'weekly'): boolean {
  return update((s) => {
    const defs = kind === 'daily' ? DAILY_QUESTS : WEEKLY_QUESTS;
    const box = kind === 'daily' ? s.daily : s.weekly;
    const q = defs.find((x) => x.id === id);
    if (!q || box.claimed.includes(id) || (box.quests[id] ?? 0) < q.goal) return false;
    box.claimed.push(id);
    s.pass.points += q.points;
    return true;
  });
}

export function claimChest(index: number, kind: 'daily' | 'weekly'): Gain | null {
  const chests = kind === 'daily' ? DAILY_CHESTS : WEEKLY_CHESTS;
  const chest = chests[index];
  if (!chest || questPoints(kind) < chest.points) return null;
  return update((s) => {
    const box = kind === 'daily' ? s.daily : s.weekly;
    if (box.chests.includes(index)) return null;
    box.chests.push(index);
    const gain = emptyGain();
    addReward(s, gain, chest.reward);
    return gain;
  });
}

export function passLevel(s: PlayerState): number {
  return Math.min(PASS_LEVELS.length, Math.floor(s.pass.points / PASS_POINTS_PER_LEVEL));
}

export function claimPass(level: number, premium: boolean): Gain | null {
  return update((s) => {
    const list = premium ? s.pass.claimedPremium : s.pass.claimedFree;
    if (level >= passLevel(s) || list.includes(level) || (premium && !s.shop.passPremium)) return null;
    list.push(level);
    const gain = emptyGain();
    addReward(s, gain, premium ? PASS_LEVELS[level]!.premium : PASS_LEVELS[level]!.free);
    return gain;
  });
}

// ---------- Pubs et boutique (simulées) ----------

export type AdReward = 'idle' | 'summon' | 'gems';

export function adsLeft(s: PlayerState): number {
  return Math.max(0, ADS_PER_DAY - s.daily.ads);
}

export function watchAd(kind: AdReward): Gain | null {
  const s0 = getState();
  if (adsLeft(s0) <= 0) return null;
  update((s) => {
    s.daily.ads += 1;
    track(s, 'watchAd');
  });
  if (kind === 'summon') {
    const heroes = summon('normal', 1, true) ?? [];
    return { currencies: {}, heroes, items: [] };
  }
  return update((s) => {
    const gain = emptyGain();
    if (kind === 'gems') addCurrency(s, gain, 'gems', 30);
    else {
      const perHour = incomePerHour(s.campaign.cleared);
      addCurrency(s, gain, 'gold', perHour * 2);
      addCurrency(s, gain, 'essence', perHour * 2 * ESSENCE_RATIO);
    }
    return gain;
  });
}

export function buyOffer(id: string): Gain | null {
  return update((s) => {
    const offer = OFFERS.find((o) => o.id === id);
    if (!offer) return null;
    const bought = s.shop.bought[id] ?? 0;
    if (offer.limit && bought >= offer.limit) return null;
    if (offer.kind === 'pass' && s.shop.passPremium) return null;
    s.shop.bought[id] = bought + 1;
    const gain = emptyGain();
    addReward(s, gain, offer.reward);
    if (offer.kind === 'card') s.shop.cardUntil = Math.max(now(), s.shop.cardUntil) + MONTHLY_CARD.days * 86_400_000;
    if (offer.kind === 'pass') s.shop.passPremium = true;
    if (offer.kind === 'noAds') s.shop.noAds = true;
    return gain;
  });
}

/** Parchemins rouges achetés en gemmes cette semaine (au plus RED_SCROLLS.gemsPerWeek). */
export function redScrollsBought(s: PlayerState = getState()): number {
  return s.shop.bought[`red-${weekKey(now())}`] ?? 0;
}

/** Un parchemin rouge contre des gemmes (boutique, onglet Échanges), limité chaque semaine. */
export function buyRedScroll(): Gain | null {
  return update((s) => {
    const key = `red-${weekKey(now())}`;
    if (redScrollsBought(s) >= RED_SCROLLS.gemsPerWeek || s.wallet.gems < RED_SCROLLS.gems) return null;
    // les compteurs des semaines passées ne servent plus
    for (const k of Object.keys(s.shop.bought)) if (k.startsWith('red-') && k !== key) delete s.shop.bought[k];
    s.wallet.gems -= RED_SCROLLS.gems;
    s.shop.bought[key] = (s.shop.bought[key] ?? 0) + 1;
    const gain = emptyGain();
    addCurrency(s, gain, 'redScrolls', 1);
    return gain;
  });
}

export function buyExchange(shop: 'arena' | 'guild' | 'coliseum', id: string): Gain | null {
  return update((s) => {
    const list = shop === 'arena' ? ARENA_SHOP : shop === 'coliseum' ? COLISEUM_SHOP : GUILD_SHOP;
    const currency = shop === 'arena' ? 'arenaTokens' : shop === 'coliseum' ? 'badge' : 'guildCoins';
    const entry = list.find((x) => x.id === id);
    if (!entry || s.wallet[currency] < entry.cost) return null;
    s.wallet[currency] -= entry.cost;
    const gain = emptyGain();
    const { fragments, item, ...rest } = entry.reward;
    addReward(s, gain, rest);
    if (fragments) {
      // Les fragments vont à un Légendaire déjà découvert (sinon à un Légendaire au hasard, qui se découvre ainsi).
      const known = HEROES.filter((h) => h.rarity === 'legendary' && s.discovered.includes(h.id));
      const target = known.length ? pick(nextRng(s), known).id : pick(nextRng(s), HEROES.filter((h) => h.rarity === 'legendary')).id;
      s.fragments[target] = (s.fragments[target] ?? 0) + fragments;
      gain.fragments = { defId: target, amount: fragments };
    }
    if (item !== undefined) gain.items.push(makeItem(s, nextRng(s), item));
    return gain;
  });
}

// ---------- Réglages ----------

export function setLang(lang: 'fr' | 'en'): void {
  update((s) => void (s.lang = lang));
}

const NAME_PATTERN = /^[\p{L}\p{N}][\p{L}\p{N} _-]{1,14}[\p{L}\p{N}]$/u;
const BANNED = ['admin', 'modo', 'moderat', 'support', 'claude', 'anthropic'];

/** Vérifie un nom : 3 à 16 caractères, lettres, chiffres, espaces, - et _. Renvoie la clé d'erreur ou null. */
export function nameError(name: string): string | null {
  const clean = name.trim();
  if (clean.length < 3 || clean.length > 16) return 'name.length';
  if (!NAME_PATTERN.test(clean)) return 'name.chars';
  if (BANNED.some((w) => clean.toLowerCase().includes(w))) return 'name.taken';
  return null;
}

/** Premier choix du nom (gratuit). */
export function chooseName(name: string): string | null {
  const err = nameError(name);
  if (err) return err;
  update((s) => {
    s.name = name.trim();
    s.named = true;
  });
  return null;
}

/** Changer de nom ensuite : payant, en gemmes. */
export function rename(name: string): string | null {
  const err = nameError(name);
  if (err) return err;
  if (getState().wallet.gems < RENAME_COST) return 'name.gems';
  update((s) => {
    s.wallet.gems -= RENAME_COST;
    s.name = name.trim();
    s.nameChanges += 1;
  });
  return null;
}

const NAME_PARTS = [
  ['Ardent', 'Sombre', 'Vif', 'Brave', 'Rusé', 'Fier', 'Lunaire', 'Sauvage'],
  ['Loup', 'Faucon', 'Lion', 'Corbeau', 'Dragon', 'Renard', 'Tigre', 'Ours'],
];

export function randomName(): string {
  const a = NAME_PARTS[0]![Math.floor(Math.random() * 8)]!;
  const b = NAME_PARTS[1]![Math.floor(Math.random() * 8)]!;
  return `${b}${a}${Math.floor(Math.random() * 90 + 10)}`;
}

/** Identifiant de joueur affiché (pour l'assistance). */
export function playerId(s: PlayerState): string {
  return (s.createdAt % 2_176_782_336).toString(36).toUpperCase().padStart(6, '0');
}

/** Choisit le portrait du joueur parmi les héros découverts. Renvoie faux si le héros n'est pas connu. */
export function setAvatar(defId: string): boolean {
  if (!getState().discovered.includes(defId)) return false;
  update((s) => void (s.avatar = defId));
  return true;
}

export function setSetting(key: keyof PlayerState['settings'], on: boolean): void {
  update((s) => void (s.settings[key] = on));
}

/**
 * Lie la partie à un compte Google ou Apple (appelé par src/game/auth.ts une fois la connexion réussie).
 * La partie du téléphone est gardée telle quelle. Avec le serveur : elle sera envoyée au serveur à ce moment-là, et le
 * serveur deviendra le juge (docs/connexion-comptes.md). Renvoie faux si les informations ne vont pas.
 */
export function linkAuth(user: { provider: AuthProvider; id: string; email?: string }): boolean {
  if ((user.provider !== 'google' && user.provider !== 'apple') || !user.id) return false;
  update((s) => {
    s.auth = { provider: user.provider, id: user.id, at: now(), ...(user.email ? { email: user.email } : {}) };
  });
  return true;
}

/** Délie le compte : la partie redevient « invité » (elle reste sur le téléphone). */
export function unlinkAuth(): void {
  update((s) => void delete s.auth);
}

/** Supprime le compte. Aujourd'hui : efface la partie du téléphone. Avec le serveur : effacera aussi le compte en ligne. */
export function deleteAccount(): void {
  resetGame();
}

export function setSpeed(speed: 1 | 2 | 3): void {
  update((s) => void (s.speed = speed));
}

export function setAuto(auto: boolean): void {
  update((s) => void (s.auto = auto));
}

export function markSeen(feature: string): void {
  if (!getState().seen.includes(feature)) update((s) => void s.seen.push(feature));
}

export function resetGame(): void {
  replaceState(fresh());
  ensureDay();
}


/** Lance le combat préparé avec la section actuelle. */
export function startBattleFromPlan(plan: BattlePlan): BattleRequest | null {
  return plan.build();
}

// ---------- Amis ----------
// Hors ligne pour l'instant : un code ami fabrique un joueur fictif toujours identique (même code = même ami).
// Avec le serveur, le code désignera un vrai joueur.

function codeSeed(code: string): number {
  let h = 2166136261;
  for (const ch of code) h = Math.imul(h ^ ch.charCodeAt(0), 16777619);
  return h >>> 0;
}

function friendFromCode(s: PlayerState, code: string): Friend {
  const rng = createRng(codeSeed(code));
  const ratio = 0.7 + rng() * 0.6;
  const target = (Math.max(500, teamPower(s)) * ratio) / 5;
  const slots: Slot[] = [0, 1, 2, 3, 4];
  const team = slots.map((slot) => {
    const def = pick(rng, HEROES.filter((h) => h.rarity !== 'common'));
    const stars = RARITY_RULES[def.rarity].bornStars;
    const hero: Hero = { uid: 0, defId: def.id, stars, level: 1 };
    while (heroPower(s, hero) < target && hero.level < 400) hero.level += 1;
    return { defId: def.id, stars, level: hero.level, slot };
  });
  return { id: `f-${code}`, code, name: BOT_NAMES[codeSeed(code) % BOT_NAMES.length]!, team };
}

/** Des codes de joueurs à proposer quand on a peu d'amis. */
export function friendSuggestions(s: PlayerState = getState()): Friend[] {
  const have = new Set(s.friends.list.map((f) => f.code));
  // deux joueurs proposés n'ont jamais le même nom (contrôle du 26/11 : « Orsolya » deux fois), ni celui d'un ami
  const names = new Set(s.friends.list.map((f) => f.name));
  const rng = createRng(codeSeed(playerId(s)) + s.friends.list.length);
  const out: Friend[] = [];
  for (let i = 0; i < 20 && out.length < 3; i++) {
    const code = Math.floor(rng() * 2_176_782_336).toString(36).toUpperCase().padStart(6, '0');
    if (have.has(code)) continue;
    const f = friendFromCode(s, code);
    if (names.has(f.name)) continue;
    names.add(f.name);
    out.push(f);
  }
  return out;
}

export function addFriend(rawCode: string): 'added' | 'self' | 'already' | 'full' | 'invalid' {
  const code = rawCode.trim().toUpperCase();
  return update((s) => {
    if (!/^[0-9A-Z]{6}$/.test(code)) return 'invalid';
    if (code === playerId(s)) return 'self';
    if (s.friends.list.some((f) => f.code === code)) return 'already';
    if (s.friends.list.length >= FRIENDS_MAX) return 'full';
    s.friends.list.push(friendFromCode(s, code));
    return 'added';
  });
}

export function removeFriend(id: string): void {
  update((s) => {
    s.friends.list = s.friends.list.filter((f) => f.id !== id);
    s.friends.inbox = s.friends.inbox.filter((x) => x !== id);
  });
}

/** Chaque jour, les amis (fictifs) envoient leur cadeau, environ 2 sur 3. */
export function friendsDay(): void {
  const today = dayKey(now());
  if (getState().friends.day === today) return;
  update((s) => {
    const rng = createRng(codeSeed(today + playerId(s)));
    s.friends.day = today;
    s.friends.sent = [];
    s.friends.inbox = s.friends.list.filter(() => rng() < 0.67).map((f) => f.id);
  });
}

export function sendGift(id?: string): number {
  return update((s) => {
    const targets = s.friends.list.filter((f) => (id ? f.id === id : true) && !s.friends.sent.includes(f.id));
    s.friends.sent.push(...targets.map((f) => f.id));
    return targets.length;
  });
}

export function claimGifts(): Gain {
  return update((s) => {
    const gain = emptyGain();
    const n = s.friends.inbox.filter((id) => s.friends.list.some((f) => f.id === id)).length;
    addCurrency(s, gain, 'basicScrolls', n * FRIEND_GIFT.basicScrolls);
    s.friends.inbox = [];
    return gain;
  });
}

export function friendPower(f: Friend): number {
  return opponentPower({ id: f.id, name: f.name, points: 0, team: f.team });
}

/** Défier un ami : combat automatique contre sa section, pour le plaisir (pas de récompense). */
export function friendPlan(id: string): BattlePlan | null {
  const f = getState().friends.list.find((x) => x.id === id);
  if (!f) return null;
  const o = { id: f.id, name: f.name, points: 0, team: f.team };
  return {
    kind: 'friend', title: f.name, waves: [arenaEnemies(o)], need: friendPower(f),
    build: () => update((s) => ({ kind: 'friend' as const, title: f.name, heroes: teamUnits(s), waves: [arenaEnemies(o)], seed: seedFor(s) })),
  };
}

// ---------- Guerre de guildes ----------
// Hors ligne pour l'instant : l'adversaire et les autres membres sont simulés de façon fixe pour la semaine
// (même semaine = mêmes adversaires, mêmes scores). Avec le serveur, ce seront de vraies guildes.

const FOE_GUILDS = ['Les Crocs d’Ébène', 'La Garde Céleste', 'Les Fils du Tonnerre', 'Cercle d’Écume', 'Les Veilleurs', 'Flamme Noire'];
const WAR_NAMES = ['Kaïro', 'Lunaria', 'Vaelis', 'Tormund', 'Ishara', 'Mikaze', 'Orsolya', 'Bastien', 'Yuna', 'Ragnis', 'Selka', 'Noctis', 'Aïko', 'Feyd', 'Mirelle', 'Draven7'];

export type WarPhase = 'prep' | 'battle' | 'results';

export function warPhase(ms = now()): WarPhase {
  const d = new Date(ms).getDay();
  return d === 1 ? 'prep' : d === 0 ? 'results' : 'battle';
}

/** Jours de combat écoulés cette semaine (mardi = 0) et part de la journée en cours. */
function warDays(ms = now()): number {
  const d = new Date(ms);
  const idx = (d.getDay() + 6) % 7; // lundi = 0 … dimanche = 6
  if (idx === 0) return 0;
  if (idx === 6) return 5;
  return idx - 1 + (d.getHours() * 60 + d.getMinutes()) / 1440;
}

function freshWar(s: PlayerState, week: string): GuildWarState {
  const rng = createRng(codeSeed(week + (s.guild.joined ?? '')));
  return { week, foe: pick(rng, FOE_GUILDS), basePower: Math.max(500, teamPower(s)), day: dayKey(now()), attacks: 0, used: [], myStars: 0, claimed: false };
}

/** La guerre de la semaine (créée au besoin). La récompense d'une guerre finie et non prise est mise de côté. */
export function ensureWar(): GuildWarState | null {
  const s0 = getState();
  if (!s0.guild.joined) return null;
  const week = weekKey(now());
  const today = dayKey(now());
  const w0 = s0.guildWar;
  if (w0 && w0.week === week && w0.day === today) return w0;
  return update((s) => {
    const w = s.guildWar;
    if (!w || w.week !== week) {
      const pending = w && !w.claimed ? warReward(s, w, 5) : w?.pending;
      s.guildWar = { ...freshWar(s, week), pending };
    } else if (w.day !== today) {
      w.day = today;
      w.attacks = 0;
      w.used = [];
    }
    return s.guildWar!;
  });
}

/** Les défenses de la guilde adverse : fixes pour la semaine. */
export function warDefenses(s: PlayerState, w: GuildWarState): { name: string; team: ArenaOpponent['team']; power: number }[] {
  const rng = createRng(codeSeed(w.week + w.foe));
  const slots: Slot[] = [0, 1, 2, 3, 4];
  return Array.from({ length: GUILD_WAR.defenses }, (_, i) => {
    const ratio = 0.7 + (i / (GUILD_WAR.defenses - 1)) * 0.6; // du plus faible au plus fort
    const target = (w.basePower * ratio) / 5;
    const team = slots.map((slot) => {
      const def = pick(rng, HEROES.filter((h) => h.rarity !== 'common'));
      const stars = RARITY_RULES[def.rarity].bornStars;
      const hero: Hero = { uid: 0, defId: def.id, stars, level: 1 };
      while (heroPower(s, hero) < target && hero.level < 400) hero.level += 1;
      return { defId: def.id, stars, level: hero.level, slot };
    });
    const o = { id: `w${i}`, name: WAR_NAMES[(codeSeed(w.foe) + i) % WAR_NAMES.length]!, points: 0, team };
    return { name: o.name, team, power: opponentPower(o) };
  });
}

/** Scores : mes étoiles + celles des autres membres (simulées), contre celles de la guilde adverse. */
export function warScores(s: PlayerState, w: GuildWarState, days = warDays()): { mine: number; foe: number; members: { name: string; stars: number; me?: boolean }[] } {
  const rng = createRng(codeSeed(w.week + 'scores'));
  const full = Math.floor(days);
  const part = days - full;
  const members = WAR_NAMES.slice(0, 9).map((name) => {
    let stars = 0;
    for (let d = 0; d < 5; d++) {
      const daily = 2 + Math.floor(rng() * 4); // 2 à 5 étoiles par jour
      stars += d < full ? daily : d === full ? Math.floor(daily * part) : 0;
    }
    return { name, stars };
  });
  // Ma défense compte : plus elle est forte par rapport au début de semaine, moins l'adversaire marque.
  const defense = Math.max(0.85, Math.min(1.15, 1.15 - 0.3 * (teamPower(s, 'defense') / w.basePower - 1)));
  let foe = 0;
  for (let d = 0; d < 5; d++) {
    const daily = 10 * (2 + rng() * 3.4) * defense;
    foe += d < full ? daily : d === full ? daily * part : 0;
  }
  const all = [...members, { name: s.name, stars: w.myStars, me: true }].sort((a, b) => b.stars - a.stars);
  return { mine: all.reduce((a, m) => a + m.stars, 0), foe: Math.round(foe), members: all };
}

function warReward(s: PlayerState, w: GuildWarState, days: number): NonNullable<GuildWarState['pending']> {
  const sc = warScores(s, w, days);
  const result = sc.mine > sc.foe ? 'win' : sc.mine === sc.foe ? 'draw' : 'loss';
  const r = GUILD_WAR.reward[result];
  const best = sc.members[0]?.me ? GUILD_WAR.bestAttacker.scrolls : 0;
  return { result, guildCoins: r.guildCoins, scrolls: r.scrolls + best };
}

/** Le dimanche, ou pour une guerre précédente : récupérer la récompense. */
export function claimWar(): Gain | null {
  const w0 = ensureWar();
  if (!w0) return null;
  return update((s) => {
    const w = s.guildWar!;
    const gain = emptyGain();
    let r = w.pending;
    if (r) w.pending = undefined;
    else if (warPhase() === 'results' && !w.claimed) {
      r = warReward(s, w, 5);
      w.claimed = true;
    }
    if (!r) return null;
    addCurrency(s, gain, 'guildCoins', r.guildCoins);
    addCurrency(s, gain, 'scrolls', r.scrolls);
    return gain;
  });
}

export function warAttacksLeft(w: GuildWarState): number {
  return warPhase() === 'battle' ? Math.max(0, GUILD_WAR.attacksPerDay - w.attacks) : 0;
}

/** Attaquer une défense adverse. Les héros qui ont déjà attaqué aujourd'hui restent sur le côté. */
export function warPlan(index: number): BattlePlan | null {
  const w = ensureWar();
  const s = getState();
  if (!w) return null;
  const d = warDefenses(s, w)[index];
  if (!d) return null;
  const o = { id: `w${index}`, name: d.name, points: 0, team: d.team };
  return {
    kind: 'guildWar', title: d.name, waves: [arenaEnemies(o)], need: d.power, exclude: [...w.used],
    build: () => update((st) => {
      const war = st.guildWar;
      if (!war || warAttacksLeft(war) <= 0) return null;
      const heroes = teamUnits(st).filter((u) => !war.used.includes(Number(u.id.slice(2))));
      if (!heroes.length) return null;
      return { kind: 'guildWar' as const, title: d.name, heroes, waves: [arenaEnemies(o)], seed: seedFor(st) };
    }),
  };
}

/** Étoiles d'une attaque gagnée : selon la part de héros encore debout. */
export function warStars(win: boolean, alive: number): number {
  if (!win) return 0;
  return alive >= 0.99 ? 3 : alive >= 0.5 ? 2 : 1;
}

// ---------- Calendrier de connexion ----------

/** Le calendrier affiché (bienvenue, puis mois) et la case du jour. */
export function loginCalendar(s: PlayerState = getState()): { kind: 'welcome' | 'month'; rewards: LoginReward[]; index: number; claimed: boolean } {
  const count = s.login?.count ?? 0;
  const claimed = s.login?.day === dayKey(now());
  // La case du jour : déjà cochée aujourd'hui = la dernière cochée ; sinon la suivante.
  const n = claimed ? count - 1 : count;
  if (n < LOGIN_WELCOME.length) return { kind: 'welcome', rewards: LOGIN_WELCOME, index: n, claimed };
  return { kind: 'month', rewards: LOGIN_MONTH, index: (n - LOGIN_WELCOME.length) % LOGIN_MONTH.length, claimed };
}

/** Le jour de connexion du jour donne-t-il un Légendaire à choisir ? */
export function loginNeedsChoice(): boolean {
  const cal = loginCalendar();
  return !cal.claimed && !!cal.rewards[cal.index]?.legendary;
}

/** Les Légendaires qu'on peut choisir au 7e jour de bienvenue : tous, ceux qu'on n'a pas encore d'abord. */
export function loginLegendChoices(s: PlayerState = getState()): string[] {
  const owned = new Set(s.heroes.map((h) => h.defId));
  return HEROES.filter((h) => h.rarity === 'legendary').map((h) => h.id).sort((a, b) => Number(owned.has(a)) - Number(owned.has(b)));
}

/** Prend la case du jour ; le 7e jour de bienvenue, `choice` = le Légendaire choisi par le joueur (28/11 : au choix). */
export function claimLogin(choice?: string): Gain | null {
  const cal = loginCalendar();
  if (cal.claimed) return null;
  return update((s) => {
    const gain = emptyGain();
    const { legendary, ...rest } = cal.rewards[cal.index]!;
    addReward(s, gain, rest);
    const choices = loginLegendChoices(s);
    for (let i = 0; i < (legendary ?? 0); i++) {
      const id = choice && choices.includes(choice) ? choice : pick(nextRng(s), choices.slice(0, Math.max(1, choices.length)));
      gain.heroes.push(addHero(s, id));
    }
    s.login = { day: dayKey(now()), count: (s.login?.count ?? 0) + 1 };
    return gain;
  });
}

// ---------- Courrier ----------

/** Fait arriver les messages dont la date est passée (et oublie ceux de plus de 30 jours). */
export function checkMail(): void {
  const s0 = getState();
  const t = now();
  const fresh = MAILS.filter((m) => !(s0.mail?.got ?? {})[m.id] && (m.at === null || Date.parse(m.at) <= t) && (!m.personal || s0.mail?.personal?.[m.id]));
  if (!fresh.length) return;
  update((s) => {
    const box = (s.mail ??= { got: {}, read: [], claimed: [] });
    // un cadeau personnel arrive maintenant (une vieille partie l'aurait sinon déjà « oublié »)
    for (const m of fresh) box.got[m.id] = m.personal ? t : m.at === null ? s.createdAt : Math.max(Date.parse(m.at), s.createdAt);
  });
}

export interface MailItem {
  def: MailDef;
  at: number;
  read: boolean;
  claimed: boolean;
}

/** Les messages de la boîte, du plus récent au plus ancien. */
export function mailbox(s: PlayerState = getState()): MailItem[] {
  const box = s.mail;
  if (!box) return [];
  const limit = now() - MAIL_KEEP_DAYS * 864e5;
  return MAILS.filter((m) => box.got[m.id] !== undefined && box.got[m.id]! >= limit)
    // un cadeau personnel est rangé dans la sauvegarde
    .map((m) => ({ ...m, reward: m.personal ? box.personal?.[m.id] : m.reward }))
    .map((def) => ({ def, at: box.got[def.id]!, read: box.read.includes(def.id), claimed: box.claimed.includes(def.id) }))
    .sort((a, b) => b.at - a.at);
}

export function readMail(id: string): void {
  if (getState().mail?.read.includes(id)) return;
  update((s) => void s.mail?.read.push(id));
}

/** Récupère le cadeau d'un message (ou de tous). */
export function claimMail(id?: string): Gain {
  return update((s) => {
    const gain = emptyGain();
    for (const m of mailbox(s)) {
      if ((id && m.def.id !== id) || m.claimed || !m.def.reward) continue;
      addReward(s, gain, m.def.reward);
      s.mail!.claimed.push(m.def.id);
      if (!s.mail!.read.includes(m.def.id)) s.mail!.read.push(m.def.id);
    }
    return gain;
  });
}

/** Point rouge : un message non lu ou un cadeau à prendre. */
export function mailWaiting(s: PlayerState = getState()): number {
  return mailbox(s).filter((m) => !m.read || (m.def.reward && !m.claimed)).length;
}

// ---------- Tutoriel ----------

/** Le cadeau de la fin du tutoriel : 10 invocations (une seule fois). */
export function tutorialGift(): Gain | null {
  return update((s) => {
    if (s.tutorialGift) return null;
    s.tutorialGift = true;
    const gain = emptyGain();
    addCurrency(s, gain, 'scrolls', TUTORIAL_GIFT_SCROLLS);
    return gain;
  });
}

export function setTutorial(step: number): void {
  update((s) => void (s.tutorial = step));
}

// ---------- Colisée ----------
// Duels en chaîne, équipes de 3, classement de la semaine par groupe de 30 et par ligue (règles : src/core/coliseum.ts).
// Le résultat d'un combat est rejoué ici à partir de la graine (l'écran ne fait que le montrer) : demain, le serveur.

function weekStartMs(ms: number): number {
  const d = new Date(ms);
  d.setHours(0, 0, 0, 0);
  d.setDate(d.getDate() - ((d.getDay() + 6) % 7));
  return d.getTime();
}

/** Heures écoulées depuis le début de la semaine (lundi 0 h). */
export function coliseumHours(): number {
  return (now() - weekStartMs(now())) / 3.6e6;
}

/** Fin de la semaine du Colisée (lundi prochain, 0 h). */
export function coliseumWeekEnd(): number {
  const d = new Date(weekStartMs(now()));
  d.setDate(d.getDate() + 7);
  return d.getTime();
}

function hashText(text: string): number {
  let h = 2166136261;
  for (const ch of text) h = Math.imul(h ^ ch.charCodeAt(0), 16777619) >>> 0;
  return h;
}

function newColiseumWeek(s: PlayerState, week: string, league: number, team: number[] = []): ColiseumState {
  return {
    week, league, seed: mixSeed(s.createdAt >>> 0, hashText(week)), points: COLISEUM.startPoints, fights: 0, wins: 0,
    day: dayKey(now()), today: 0, bought: 0, team,
  };
}

/** Le groupe de la semaine en cours. */
export function coliseumGroup(c: ColiseumState): ColiseumBot[] {
  return makeGroup(c.seed, c.league);
}

/** Le classement du groupe, maintenant (ou à la fin de la semaine). */
export function coliseumStandings(s: PlayerState = getState(), hours = coliseumHours()): Standing[] {
  const c = s.coliseum;
  if (!c) return [];
  return standings(coliseumGroup(c), hours, { name: s.name, points: c.points });
}

/**
 * Nouvelle semaine : la place de la semaine passée donne sa récompense (à récupérer) et la ligue monte ou descend.
 * Une semaine sans combat ne rapporte rien et ne change pas de ligue. Nouveau jour : les combats du jour reviennent.
 */
export function ensureColiseum(): void {
  const s0 = getState();
  if (!isUnlocked(s0, 'defense')) return;
  const week = weekKey(now());
  const today = dayKey(now());
  const c0 = s0.coliseum;
  if (c0 && c0.week === week && c0.day === today) return;
  update((s) => {
    const c = s.coliseum;
    if (!c) {
      s.coliseum = newColiseumWeek(s, week, 0);
      return;
    }
    if (c.week !== week) {
      let league = c.league;
      if (c.fights > 0) {
        const rank = myRank(coliseumGroup(c), WEEK_HOURS, { name: s.name, points: c.points });
        league = leagueAfter(c.league, rank);
        const r = rankReward(c.league, rank);
        // une récompense pas encore prise s'ajoute à la nouvelle (rien ne se perd)
        const prev = c.pending;
        c.pending = { week: c.week, league: c.league, rank, next: league, gems: r.gems + (prev?.gems ?? 0), badge: r.badge + (prev?.badge ?? 0) };
      }
      s.coliseum = { ...newColiseumWeek(s, week, league, c.team), pending: c.pending };
      return;
    }
    c.day = today;
    c.today = 0;
    c.bought = 0;
  });
}

/** Combats encore possibles aujourd'hui (offerts + achetés − joués). */
export function coliseumFightsLeft(s: PlayerState = getState()): number {
  const c = s.coliseum;
  if (!c) return 0;
  return Math.max(0, COLISEUM.freeFights + c.bought - c.today);
}

/** Prix du prochain combat en plus (null : plus d'achat possible aujourd'hui). */
export function coliseumExtraCost(s: PlayerState = getState()): number | null {
  const c = s.coliseum;
  if (!c) return null;
  return COLISEUM.extraCosts[c.bought] ?? null;
}

/** Achète un combat de plus (seulement quand ceux du jour sont joués). */
export function buyColiseumFight(): boolean {
  return update((s) => {
    const cost = coliseumExtraCost(s);
    if (!s.coliseum || cost === null || s.wallet.gems < cost || coliseumFightsLeft(s) > 0) return false;
    s.wallet.gems -= cost;
    s.coliseum.bought += 1;
    return true;
  });
}

/** Les 3 héros du Colisée (ordre de passage) : ceux choisis, complétés par les plus forts. */
export function coliseumTeam(s: PlayerState = getState()): Hero[] {
  const chosen = (s.coliseum?.team ?? []).map((u) => heroByUid(s, u)).filter((h): h is Hero => !!h);
  const want = Math.min(COLISEUM.team, s.heroes.length);
  if (chosen.length >= want) return chosen.slice(0, want);
  const rest = s.heroes.filter((h) => !chosen.includes(h)).sort((a, b) => heroPower(s, b) - heroPower(s, a));
  return [...chosen, ...rest].slice(0, want);
}

export function coliseumTeamPower(s: PlayerState = getState()): number {
  return coliseumTeam(s).reduce((a, h) => a + heroPower(s, h), 0);
}

/** Choisit les héros (dans l'ordre de passage). */
export function setColiseumTeam(uids: number[]): boolean {
  const s0 = getState();
  const ok = uids.length >= 1 && uids.length <= COLISEUM.team && new Set(uids).size === uids.length && uids.every((u) => heroByUid(s0, u));
  if (!ok || !s0.coliseum) return false;
  return update((s) => {
    s.coliseum!.team = [...uids];
    return true;
  });
}

/**
 * Cherche un adversaire : au hasard parmi les joueurs du groupe les plus proches au classement, avec une équipe de la
 * même puissance que la nôtre. Il reste le même jusqu'au combat.
 */
export function findColiseumFoe(): ColiseumFoe | null {
  const s0 = getState();
  if (!s0.coliseum || coliseumFightsLeft(s0) <= 0) return null;
  if (s0.coliseum.foe) return s0.coliseum.foe;
  return update((s) => {
    const c = s.coliseum!;
    const rng = nextRng(s);
    const rows = coliseumStandings(s).filter((r) => r.idx >= 0).sort((a, b) => Math.abs(a.points - c.points) - Math.abs(b.points - c.points));
    const row = pick(rng, rows.slice(0, COLISEUM.foeChoice));
    const bot = coliseumGroup(c)[row.idx]!;
    const [lo, hi] = COLISEUM.foePower;
    const power = Math.max(300, coliseumTeamPower(s)) * (lo + rng() * (hi - lo));
    c.foe = { idx: bot.idx, name: bot.name, points: row.points, team: botTeam(bot.heroes, power), seed: seedFor(s) };
    return c.foe;
  });
}

/** Le combat contre l'adversaire tiré : les deux équipes et la graine (le même combat partout). */
export function coliseumSetup(s: PlayerState = getState()): ColiseumSetup | null {
  const foe = s.coliseum?.foe;
  if (!foe) return null;
  const heroes = coliseumTeam(s).map((h) => heroToUnit(h, 0, gearStatsOf(s, h.uid)));
  if (!heroes.length) return null;
  return { heroes, foes: foeUnits(foe.team), seed: foe.seed };
}

export interface ColiseumFightResult {
  win: boolean;
  delta: number;
  points: number;
  rankBefore: number;
  rankAfter: number;
  foe: string;
  gain: Gain;
}

/** Fin du combat : le résultat est rejoué à partir de la graine, puis les points et les insignes sont donnés. */
export function finishColiseum(): ColiseumFightResult | null {
  const setup = coliseumSetup();
  if (!setup || coliseumFightsLeft() <= 0) return null;
  const outcome = runColiseum(setup);
  return update((s) => {
    const c = s.coliseum!;
    const foe = c.foe!;
    const rankBefore = myRank(coliseumGroup(c), coliseumHours(), { name: s.name, points: c.points });
    const delta = pointsChange(c.points, foe.points, outcome.win);
    c.points = Math.max(0, c.points + delta);
    c.fights += 1;
    c.today += 1;
    if (outcome.win) c.wins += 1;
    delete c.foe;
    const gain = emptyGain();
    addCurrency(s, gain, 'badge', outcome.win ? COLISEUM.fightBadges.win : COLISEUM.fightBadges.loss);
    const rankAfter = myRank(coliseumGroup(c), coliseumHours(), { name: s.name, points: c.points });
    return { win: outcome.win, delta, points: c.points, rankBefore, rankAfter, foe: foe.name, gain };
  });
}

/** Récupère la récompense de la semaine passée. */
export function claimColiseumWeek(): Gain | null {
  return update((s) => {
    const p = s.coliseum?.pending;
    if (!p) return null;
    const gain = emptyGain();
    addCurrency(s, gain, 'gems', p.gems);
    addCurrency(s, gain, 'badge', p.badge);
    delete s.coliseum!.pending;
    return gain;
  });
}

// ---------- Le mode Événement (core/data/event.ts) ----------

/** L'état du mode pour l'événement en cours : un nouvel événement (portail d'événement changé) remet la difficulté à 1. */
export function eventOf(s: PlayerState): EventState {
  return s.event && s.event.id === FEATURED_BANNER.id ? s.event : { id: FEATURED_BANNER.id, difficulty: 1 };
}

export function eventTriesLeft(s: PlayerState): number {
  return Math.max(0, EVENT_TRIES_PER_DAY - (s.daily.eventTries ?? 0));
}

/** Les ennemis d'un niveau : une vague de 5 ; tous les 5 niveaux, un boss (le dernier de la zone en a deux vagues). */
export function eventWaves(difficulty: number, level: number): UnitInit[][] {
  const bossy = level % 5 === 0;
  return buildWaves({
    power: stagePower(eventStage(difficulty, level)), count: 5, waves: level === EVENT_LEVELS ? 2 : 1,
    element: chapterElement(difficulty * EVENT_LEVELS + level), seed: difficulty * 7919 + level * 104729,
    boss: bossy ? BOSSES[(difficulty + level / 5) % BOSSES.length] : undefined,
  });
}

/** Les héros de la partie en cours : seulement les vivants, avec leur vie gardée et les bonus d'attaque et de défense. */
function eventUnits(s: PlayerState): UnitInit[] {
  const run = eventOf(s).run;
  if (!run) return [];
  return run.team
    .map(([uid, slot]) => ({ hero: heroByUid(s, uid), slot, hp: run.hp[uid] ?? 1 }))
    .filter((x) => x.hero && x.hp > 0)
    .map(({ hero, slot, hp }) => {
      const u = heroToUnit(hero!, slot, gearStatsOf(s, hero!.uid));
      return { ...u, atk: Math.round(u.atk * (1 + run.atk)), def: Math.round(u.def * (1 + run.def)), hpFrac: hp };
    });
}

/** Le combat du prochain niveau de la partie en cours (sans écran de préparation : l'équipe est inscrite). */
export function eventBattle(): BattleRequest | null {
  return update((s) => {
    const ev = eventOf(s);
    if (!ev.run || ev.run.offer) return null;
    const heroes = eventUnits(s);
    if (!heroes.length) return null;
    return { kind: 'event' as const, title: `${ev.difficulty}-${ev.run.level}`, heroes, waves: eventWaves(ev.difficulty, ev.run.level), seed: seedFor(s) };
  });
}

/** L'inscription (écran de préparation, section principale) : elle commence une partie, prend un essai du jour, puis
 * lance le niveau 1. */
export function eventPlan(): BattlePlan {
  const ev = eventOf(getState());
  return {
    kind: 'event', title: `${ev.difficulty}-1`, waves: eventWaves(ev.difficulty, 1), need: stagePower(eventStage(ev.difficulty, 1)),
    build: () => {
      const ok = update((s) => {
        const e = eventOf(s);
        if (e.run || eventTriesLeft(s) <= 0) return false;
        const team = formationOf(s).filter(([u]) => heroByUid(s, u));
        if (!team.length) return false;
        s.daily.eventTries = (s.daily.eventTries ?? 0) + 1;
        s.event = { ...e, run: { team: team.map(([u, sl]) => [u, sl]), level: 1, hp: Object.fromEntries(team.map(([u]) => [u, 1])), atk: 0, def: 0 } };
        return true;
      });
      return ok ? eventBattle() : null;
    },
  };
}

/** Après un combat d'Événement : la vie gardée ; gagné : récompense, niveau suivant, choix de bonus tous les 2 niveaux,
 * zone finie → difficulté suivante ; perdu : la partie s'arrête. */
function eventAfterBattle(s: PlayerState, gain: Gain, res: BattleResult) {
  const ev = eventOf(s);
  const run = ev.run;
  if (!run) return;
  for (const [uid] of run.team) {
    const v = res.heroHp?.[`h-${uid}`];
    if (v !== undefined) run.hp[uid] = v;
  }
  if (!res.win) {
    s.event = { id: ev.id, difficulty: ev.difficulty };
    return;
  }
  const level = run.level;
  addCurrency(s, gain, 'redScrolls', eventScrolls(ev.difficulty, level));
  const xp = eventXp(ev.difficulty, level);
  let ups = 0;
  for (const [uid] of run.team) {
    const h = heroByUid(s, uid);
    if (!h || !(run.hp[uid]! > 0)) continue;
    h.xp = (h.xp ?? 0) + xp;
    while (h.level < levelCap(h.stars) && h.xp >= heroXpForLevel(h.level)) {
      h.xp -= heroXpForLevel(h.level);
      h.level += 1;
      ups += 1;
    }
    if (h.level >= levelCap(h.stars)) h.xp = 0;
  }
  gain.xp = xp;
  gain.levelsUp = ups;
  track(s, 'event');
  if (level >= EVENT_LEVELS) {
    // la zone est finie : la difficulté suivante, une nouvelle partie à commencer
    s.event = { id: ev.id, difficulty: ev.difficulty + 1 };
    return;
  }
  run.level = level + 1;
  if (level % EVENT_BONUS_EVERY === 0) run.offer = eventOffer(s, run, nextRng(s));
  s.event = { ...ev, run };
}

/** Deux bonus différents au hasard (le retour d'un héros seulement s'il y a un mort, le soin seulement s'il y a un
 * blessé). */
function eventOffer(s: PlayerState, run: NonNullable<EventState['run']>, rng: Rng): EventBonus[] {
  const dead = run.team.some(([u]) => (run.hp[u] ?? 1) <= 0 && heroByUid(s, u));
  const hurt = run.team.some(([u]) => { const v = run.hp[u] ?? 1; return v > 0 && v < 1; });
  const pool = EVENT_BONUSES.filter((b) => (b !== 'revive' || dead) && (b !== 'heal' || hurt));
  const a = pick(rng, pool);
  const b = pick(rng, pool.filter((x) => x !== a));
  return [a, b];
}

/** Le joueur choisit un des deux bonus proposés. */
export function eventChooseBonus(bonus: EventBonus): boolean {
  return update((s) => {
    const ev = eventOf(s);
    const run = ev.run;
    if (!run?.offer?.includes(bonus)) return false;
    const v = EVENT_BONUS_VALUE[bonus];
    if (bonus === 'atk') run.atk += v;
    if (bonus === 'def') run.def += v;
    if (bonus === 'heal') for (const [u] of run.team) { const h = run.hp[u] ?? 1; if (h > 0) run.hp[u] = Math.min(1, h + v); }
    if (bonus === 'revive') {
      // le plus fort des héros morts revient
      const dead = run.team.map(([u]) => heroByUid(s, u)).filter((h): h is Hero => !!h && (run.hp[h.uid] ?? 1) <= 0)
        .sort((x, y) => heroPower(s, y) - heroPower(s, x));
      if (dead[0]) run.hp[dead[0].uid] = v;
    }
    run.offer = undefined;
    s.event = { ...ev, run };
    return true;
  });
}

/** Abandonner la partie en cours (l'essai du jour est déjà pris). */
export function eventAbandon(): void {
  update((s) => {
    const ev = eventOf(s);
    s.event = { id: ev.id, difficulty: ev.difficulty };
  });
}
