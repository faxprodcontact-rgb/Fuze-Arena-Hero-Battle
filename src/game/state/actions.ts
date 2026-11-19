// Toutes les actions du joueur. C'est LA porte d'entrée : à l'étape serveur, ces fonctions
// enverront la demande au serveur (qui utilisera les mêmes règles de src/core) au lieu de calculer ici.
import { LEADER_SLOT, type BattleInput, type Slot, type UnitInit } from '../../core/battle/types';
import { heroToUnit } from '../../core/battle/units';
import { stagePower } from '../../core/data/campaign';
import { incomePerHour, REWARDS, STAGE_REWARD_HOURS, STAGES_PER_CHAPTER } from '../../core/data/economy';
import { HEROES, heroDef } from '../../core/data/heroes';
import {
  FORGE_COUNT, GEAR_SLOTS, ITEM_RARITIES, SLOT_MAX_LEVEL, itemBonus, recycleDust, rollItemRarity, slotUpgradeCost,
  type GearSlot, type Item,
} from '../../core/data/items';
import {
  ACCOUNT_XP_PER_STAGE, ADS_PER_DAY, RENAME_COST, ARENA_FREE_TICKETS, ARENA_LOSS_POINTS, ARENA_SHOP, ARENA_TOKENS_PER_FIGHT,
  ARENA_WIN_POINTS, DAILY_BOSS_ATTEMPTS, DAILY_BOSS_TIERS, DAILY_CHESTS, DAILY_QUESTS, DUNGEON_ATTEMPTS_PER_DAY,
  DUNGEON_LEVELS, DUNGEON_REWARD_HOURS, DUNGEON_STAGE_PER_LEVEL, ESSENCE_RATIO, dungeonItems, FAST_LOOT_COSTS, FAST_LOOT_HOURS, GEMS_PER_10_SUMMONS,
  GEMS_PER_SUMMON, GUILD_BOSS_ATTEMPTS, GUILD_COINS_PER_ATTACK, GUILD_SHOP, IDLE_ITEM_HOURS, MISSION_TEMPLATES,
  MISSIONS_PER_DAY, MONTHLY_CARD, OFFERS, PASS_LEVELS, PASS_POINTS_PER_LEVEL, RESET_COST, STAGE_GEMS, TOWER_REWARD,
  TOWER_STAGE_PER_FLOOR, WEEKLY_CHESTS, WEEKLY_QUESTS, accountXpForLevel, type DungeonKind, type QuestEvent,
  type Reward,
} from '../../core/data/modes';
import { FRAGMENTS_PER_COPY, LADDER, RARITY_RULES } from '../../core/data/stars';
import type { DefenseSetup } from '../../core/defense/engine';
import {
  DEFENSE_HEROES, DEFENSE_LEVELS, DEFENSE_PADS, DEFENSE_REWARD, DEFENSE_STAGE_PER_LEVEL, defenseCrystals, defenseStars,
} from '../../core/data/defense';
import { applyFusion, canGainStar, isValidFusion, planFusion, type FusionPlan } from '../../core/fusion';
import { levelRefund } from '../../core/power';
import { createRng, pick, type Rng } from '../../core/rng';
import { BOSSES } from '../../core/data/monsters';
import { buildWaves, campaignWaves, chapterElement, chapterOf, slotsAt } from '../../core/stages';
import { summonBasic, summonOne } from '../../core/summon';
import type { Hero } from '../../core/types';
import { fresh, getState, now, replaceState, update } from './store';
import { CRYSTAL_HOURS, gearPct, heroByUid, heroPower, idlePreview, levelUpCost, slotLevel, teamPower, teamUnits } from './selectors';
import type { ArenaOpponent, Gain, MissionState, PlayerState, Wallet } from './types';

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
  for (const [k, v] of Object.entries(reward)) addCurrency(s, gain, k as keyof Wallet, v ?? 0);
}

/** Héros obtenus pour la première fois pendant cette session (étiquette « Nouveau ! » à la révélation). */
export const newlyFound = new Set<number>();

function addHero(s: PlayerState, defId: string): Hero {
  const hero: Hero = { uid: s.nextUid++, defId, stars: RARITY_RULES[heroDef(defId).rarity].bornStars, level: 1 };
  s.heroes.push(hero);
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
  s.items.push(item);
  return item;
}

function track(s: PlayerState, event: QuestEvent, n = 1) {
  for (const q of DAILY_QUESTS) if (q.event === event) s.daily.quests[q.id] = (s.daily.quests[q.id] ?? 0) + n;
  for (const q of WEEKLY_QUESTS) if (q.event === event) s.weekly.quests[q.id] = (s.weekly.quests[q.id] ?? 0) + n;
}

/** Nouveau jour, nouvelle semaine : remises à zéro et livraisons quotidiennes. */
export function ensureDay(): void {
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
  protector: [0, 1, 2, 3, 4], attacker: [1, 2, 0, 3, 4], healer: [3, 4, 2, 1, 0], support: [4, 3, 2, 1, 0],
};

export function toggleInFormation(uid: number): 'added' | 'removed' | 'full' | 'last' {
  return update((s) => {
    if (s.formation.some(([u]) => u === uid)) {
      if (s.formation.length <= 1) return 'last';
      s.formation = s.formation.filter(([u]) => u !== uid);
      return 'removed';
    }
    if (s.formation.length >= slotsAt(s.campaign.cleared)) return 'full';
    const hero = heroByUid(s, uid);
    if (!hero) return 'full';
    const taken = new Set(s.formation.map(([, slot]) => slot));
    const slot = PREFERRED_SLOTS[heroDef(hero.defId).role]!.find((x) => !taken.has(x))!;
    s.formation.push([uid, slot]);
    return 'added';
  });
}

export function swapSlots(a: Slot, b: Slot): void {
  update((s) => {
    s.formation = s.formation.map(([u, slot]): [number, Slot] => [u, slot === a ? b : slot === b ? a : slot]);
  });
}

/** Remplit la section avec les héros les plus forts, chacun à son poste conseillé. */
export function autoFormation(): void {
  update((s) => {
    const best = [...s.heroes].sort((a, b) => heroPower(s, b) - heroPower(s, a)).slice(0, slotsAt(s.campaign.cleared));
    const taken = new Set<Slot>();
    s.formation = best.map((h) => {
      const slot = PREFERRED_SLOTS[heroDef(h.defId).role]!.find((x) => !taken.has(x))!;
      taken.add(slot);
      return [h.uid, slot];
    });
    // Le centre revient au chef de section le plus fort de la section, s'il y en a un.
    const center = s.formation.find(([, sl]) => sl === LEADER_SLOT);
    const chief = s.formation.find(([u]) => !!heroDef(heroByUid(s, u)!.defId).talent);
    if (chief && center && !heroDef(heroByUid(s, center[0])!.defId).talent) {
      center[1] = chief[1];
      chief[1] = LEADER_SLOT;
    }
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
  faction: string;
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
  pools.fodder = free.filter((h) => h.stars === step.fodderStars && heroDef(h.defId).faction === d.faction);
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
    for (let i = 0; i < slot.count; i++) needs.push({ kind: slot.kind, stars: slot.stars, faction: d.faction, defId: slot.defId, hero: heroes[i] });
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

export function summonCost(kind: 'normal' | 'basic', count: 1 | 10): { currency: keyof Wallet; amount: number } {
  const s = getState();
  if (kind === 'basic') return { currency: 'basicScrolls', amount: count };
  if (s.wallet.scrolls >= count) return { currency: 'scrolls', amount: count };
  return { currency: 'gems', amount: count === 10 ? GEMS_PER_10_SUMMONS : GEMS_PER_SUMMON };
}

export function summon(kind: 'normal' | 'basic', count: 1 | 10, free = false): Hero[] | null {
  return update((s) => {
    const cost = summonCost(kind, count);
    if (!free) {
      if (s.wallet[cost.currency] < cost.amount) return null;
      s.wallet[cost.currency] -= cost.amount;
    }
    const rng = nextRng(s);
    const out: Hero[] = [];
    for (let i = 0; i < count; i++) {
      const def = kind === 'basic' ? summonBasic(rng) : summonOne(s.summon, rng);
      out.push(addHero(s, def.id));
    }
    if (kind === 'normal') {
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

export type BattleKind = 'campaign' | 'tower' | 'dungeon' | 'dailyBoss' | 'arena' | 'guildBoss';

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
export function dailyBossId(): string {
  return BOSSES[new Date(now()).getDay() % BOSSES.length]!;
}

function bossWave(s: PlayerState, bossId: string, hpFactor: number, seed: number): UnitInit[][] {
  const waves = buildWaves({ power: referencePower(s), count: 1, waves: 1, element: 'fire', seed, boss: bossId });
  return waves.map((w) => w.map((u) => ({ ...u, maxHp: Math.round(u.maxHp * hpFactor) })));
}

export function dailyBossBattle(): BattleRequest {
  return update((s) => ({
    kind: 'dailyBoss' as const,
    title: dailyBossId(),
    heroes: teamUnits(s),
    waves: bossWave(s, dailyBossId(), 12, 7),
    seed: seedFor(s),
    damageMode: true,
  }));
}

export function guildBossBattle(): BattleRequest {
  return update((s) => ({
    kind: 'guildBoss' as const,
    title: 'dragon',
    heroes: teamUnits(s),
    waves: bossWave(s, 'dragon', 40, 11),
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
  return { kind: 'dungeon', title: `${level}`, waves: dungeonWaves(kind, level), need: dungeonPower(level), build: () => dungeonBattle(kind) };
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
  if (kind === 'gold') return { gold: Math.round(perHour * DUNGEON_REWARD_HOURS * 1.5) };
  if (kind === 'essence') return { essence: Math.round(perHour * DUNGEON_REWARD_HOURS) };
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

export function dailyBossPlan(): BattlePlan {
  return { kind: 'dailyBoss', title: dailyBossId(), waves: bossWave(getState(), dailyBossId(), 12, 7), build: dailyBossBattle };
}

export function guildBossPlan(): BattlePlan {
  return { kind: 'guildBoss', title: 'dragon', waves: bossWave(getState(), 'dragon', 40, 11), build: guildBossBattle };
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
  return { heroes: teamUnits(s), waves: campaignWaves(Math.max(1, s.campaign.cleared)) };
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
        // Première victoire : de quoi faire l'invocation guidée du tutoriel.
        if (stage === 1) addCurrency(s, gain, 'scrolls', 10);
        if (stage % STAGES_PER_CHAPTER === 0) {
          addCurrency(s, gain, 'scrolls', REWARDS.chapterSummons);
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
        addCurrency(s, gain, 'essence', TOWER_REWARD.essencePerFloor * f);
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
      case 'dailyBoss': {
        s.daily.bossAttempts += 1;
        const total = req.waves[0]!.reduce((a, u) => a + u.maxHp, 0);
        const share = res.damage / total;
        s.daily.bossBest = Math.max(s.daily.bossBest, res.damage);
        const tier = [...DAILY_BOSS_TIERS].reverse().find((t) => share >= t.share);
        addCurrency(s, gain, 'gems', tier?.gems ?? 15);
        addCurrency(s, gain, 'gold', perHour);
        track(s, 'dailyBoss');
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
    s.shop.bought[id] = bought + 1;
    const gain = emptyGain();
    addReward(s, gain, offer.reward);
    if (offer.kind === 'card') s.shop.cardUntil = Math.max(now(), s.shop.cardUntil) + MONTHLY_CARD.days * 86_400_000;
    if (offer.kind === 'pass') s.shop.passPremium = true;
    if (offer.kind === 'noAds') s.shop.noAds = true;
    return gain;
  });
}

export function buyExchange(shop: 'arena' | 'guild', id: string): Gain | null {
  return update((s) => {
    const list = shop === 'arena' ? ARENA_SHOP : GUILD_SHOP;
    const currency = shop === 'arena' ? 'arenaTokens' : 'guildCoins';
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

// ---------- Réglages et outils de test ----------

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

export function setSetting(key: keyof PlayerState['settings'], on: boolean): void {
  update((s) => void (s.settings[key] = on));
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

export function timeTravel(hours: number): void {
  update((s) => void (s.timeShift += hours * 3.6e6));
  ensureDay();
}

export function giveTestResources(): void {
  update((s) => {
    s.wallet.gems += 20000;
    s.wallet.scrolls += 50;
    s.wallet.basicScrolls += 100;
    s.wallet.gold += 5_000_000;
    s.wallet.essence += 2_500_000;
    s.wallet.crystals += 1000;
    s.wallet.arenaTokens += 2000;
    s.wallet.guildCoins += 2000;
    s.wallet.dust += 3000;
  });
}

/** Démonstration : saute au chapitre 11 avec une section solide, pour voir tout le jeu débloqué. */
export function demoUnlockAll(): void {
  update((s) => {
    s.campaign.cleared = Math.max(s.campaign.cleared, 410);
    const picks = ['knights-11', 'mages-10', 'angels-9', 'myths-12', 'assassins-10'];
    const slots: Slot[] = [0, 1, 3, 4, 2];
    s.formation = picks.map((defId, i) => {
      const h = addHero(s, defId);
      h.stars = defId.endsWith('-9') ? 5 : 7;
      h.level = 135;
      return [h.uid, slots[i]!];
    });
    const rng = nextRng(s);
    for (const [uid] of s.formation) {
      for (const slot of GEAR_SLOTS) s.items.push({ uid: s.nextUid++, slot, rarity: 4, tier: 9, heroUid: uid });
    }
    for (let i = 0; i < 25; i++) addHero(s, pick(rng, HEROES).id);
    s.arena.opponents = makeOpponents(s);
  });
  giveTestResources();
}

export function resetGame(): void {
  replaceState(fresh());
  ensureDay();
}


/** Lance le combat préparé avec la section actuelle. */
export function startBattleFromPlan(plan: BattlePlan): BattleRequest | null {
  return plan.build();
}

// ---------- Défense ----------

/** Puissance demandée par un niveau de Défense. */
export function defensePower(level: number): number {
  return stagePower(Math.max(1, level * DEFENSE_STAGE_PER_LEVEL));
}

/** Les héros posés encore présents dans la collection (un héros sacrifié en fusion disparaît du plan). */
export function defensePlacement(s: PlayerState = getState()): [number, number][] {
  const owned = new Set(s.heroes.map((h) => h.uid));
  return s.defense.placement.filter(([u, pad]) => owned.has(u) && pad < DEFENSE_PADS.length);
}

/** Poser un héros sur un emplacement (ou l'enlever s'il y est déjà). Un emplacement ne garde qu'un héros. */
export function placeDefender(uid: number, pad: number): 'placed' | 'removed' | 'full' {
  return update((s) => {
    const list = defensePlacement(s);
    const here = list.find(([u]) => u === uid);
    if (here && here[1] === pad) {
      s.defense.placement = list.filter(([u]) => u !== uid);
      return 'removed';
    }
    const others = list.filter(([u, p]) => u !== uid && p !== pad);
    if (!here && others.length >= DEFENSE_HEROES) return 'full';
    s.defense.placement = [...others, [uid, pad]];
    return 'placed';
  });
}

export function removeDefender(uid: number): void {
  update((s) => {
    s.defense.placement = defensePlacement(s).filter(([u]) => u !== uid);
  });
}

/** Échange deux emplacements (ou déplace un héros vers un emplacement vide). */
export function swapPads(a: number, b: number): void {
  update((s) => {
    s.defense.placement = defensePlacement(s).map(([u, p]) => [u, p === a ? b : p === b ? a : p]);
  });
}

/** Placement automatique : les 5 plus forts ; ceux à distance au milieu de la carte, ceux au corps à corps près des virages. */
export function autoDefense(): void {
  update((s) => {
    const best = [...s.heroes].sort((a, b) => heroPower(s, b) - heroPower(s, a)).slice(0, DEFENSE_HEROES);
    const rangedPads = [4, 1, 3, 7, 0, 6, 2, 5, 8];
    const meleePads = [2, 5, 0, 7, 6, 4, 1, 3, 8];
    const used = new Set<number>();
    s.defense.placement = best.map((h) => {
      const pads = heroDef(h.defId).ranged ? rangedPads : meleePads;
      const pad = pads.find((p) => !used.has(p))!;
      used.add(pad);
      return [h.uid, pad];
    });
  });
}

export interface DefenseRequest {
  level: number;
  setup: DefenseSetup;
}

/** Prépare la partie du prochain niveau (ou d'un niveau déjà gagné, pour faire mieux). */
export function defenseRequest(level: number): DefenseRequest | null {
  return update((s) => {
    const placement = defensePlacement(s);
    if (!placement.length || level < 1 || level > Math.min(DEFENSE_LEVELS, s.defense.level + 1)) return null;
    const towers = placement.map(([uid, pad]) => ({ unit: heroToUnit(heroByUid(s, uid)!, 0, gearPct(s, uid)), pad }));
    return { level, setup: { towers, power: defensePower(level), element: chapterElement(level), seed: seedFor(s) } };
  });
}

/** Total des étoiles gagnées au Siège. */
export function defenseStarTotal(s: PlayerState = getState()): number {
  return Object.values(s.defense.stars).reduce((a, n) => a + n, 0);
}

/** Fin de partie : première victoire = or + cristaux ; les étoiles remplissent les coffres d'étoiles. */
export function finishDefense(req: DefenseRequest, lives: number): Gain {
  return update((s) => {
    const gain = emptyGain();
    const stars = defenseStars(lives);
    if (stars <= 0) return gain;
    if (req.level === s.defense.level + 1) {
      s.defense.level = req.level;
      addCurrency(s, gain, 'gold', incomePerHour(req.level * DEFENSE_STAGE_PER_LEVEL) * DEFENSE_REWARD.goldHours);
      addCurrency(s, gain, 'crystals', defenseCrystals(req.level));
    }
    if (stars > (s.defense.stars[req.level] ?? 0)) s.defense.stars[req.level] = stars;
    // Coffres d'étoiles : donnés d'office dès qu'un palier est franchi.
    const earned = Math.floor(defenseStarTotal(s) / DEFENSE_REWARD.chestEvery);
    for (let c = s.defense.chests ?? 0; c < earned; c++) {
      addCurrency(s, gain, 'crystals', DEFENSE_REWARD.chest.crystals);
      addCurrency(s, gain, 'scrolls', DEFENSE_REWARD.chest.scrolls);
    }
    s.defense.chests = Math.max(s.defense.chests ?? 0, earned);
    return gain;
  });
}
