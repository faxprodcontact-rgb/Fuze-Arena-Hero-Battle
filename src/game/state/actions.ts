// Toutes les actions du joueur. C'est LA porte d'entrée : à l'étape serveur, ces fonctions
// enverront la demande au serveur (qui utilisera les mêmes règles de src/core) au lieu de calculer ici.
import type { BattleInput, Slot, UnitInit } from '../../core/battle/types';
import { heroToUnit } from '../../core/battle/units';
import { stagePower } from '../../core/data/campaign';
import { incomePerHour, REWARDS, STAGE_REWARD_HOURS, STAGES_PER_CHAPTER } from '../../core/data/economy';
import { HEROES, heroDef } from '../../core/data/heroes';
import { GEAR_SLOTS, itemBonus, rollItemRarity, type Item } from '../../core/data/items';
import {
  ACCOUNT_XP_PER_STAGE, ADS_PER_DAY, ARENA_FREE_TICKETS, ARENA_LOSS_POINTS, ARENA_SHOP, ARENA_TOKENS_PER_FIGHT,
  ARENA_WIN_POINTS, DAILY_BOSS_ATTEMPTS, DAILY_BOSS_TIERS, DAILY_CHESTS, DAILY_QUESTS, DUNGEON_ENTRIES_PER_DAY,
  DUNGEON_REWARD_HOURS, DUNGEON_TIERS, ESSENCE_RATIO, FAST_LOOT_COSTS, FAST_LOOT_HOURS, GEMS_PER_10_SUMMONS,
  GEMS_PER_SUMMON, GUILD_BOSS_ATTEMPTS, GUILD_COINS_PER_ATTACK, GUILD_SHOP, IDLE_ITEM_HOURS, MISSION_TEMPLATES,
  MISSIONS_PER_DAY, MONTHLY_CARD, OFFERS, PASS_LEVELS, PASS_POINTS_PER_LEVEL, STAGE_GEMS, TOWER_REWARD,
  TOWER_STAGE_PER_FLOOR, WEEKLY_CHESTS, WEEKLY_QUESTS, accountXpForLevel, type DungeonKind, type QuestEvent,
  type Reward,
} from '../../core/data/modes';
import { FRAGMENTS_PER_COPY, RARITY_RULES } from '../../core/data/stars';
import { applyFusion, canGainStar, planFusion, type FusionPlan } from '../../core/fusion';
import { levelRefund } from '../../core/power';
import { createRng, pick, type Rng } from '../../core/rng';
import { BOSSES } from '../../core/data/monsters';
import { buildWaves, campaignWaves, chapterElement, chapterOf, slotsAt } from '../../core/stages';
import { summonBasic, summonOne } from '../../core/summon';
import type { Hero } from '../../core/types';
import { fresh, getState, now, replaceState, update } from './store';
import { heroByUid, heroPower, idlePreview, levelUpCost, teamPower, teamUnits } from './selectors';
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

function addHero(s: PlayerState, defId: string): Hero {
  const hero: Hero = { uid: s.nextUid++, defId, stars: RARITY_RULES[heroDef(defId).rarity].bornStars, level: 1 };
  s.heroes.push(hero);
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
    s.campaign.itemHours = (s.campaign.itemHours + p.hours) % IDLE_ITEM_HOURS;
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

function refundHero(s: PlayerState, hero: Hero, gain?: Gain) {
  const gold = levelRefund(hero.level);
  s.wallet.gold += gold;
  s.wallet.essence += Math.round(gold * ESSENCE_RATIO);
  if (gain) {
    gain.currencies.gold = (gain.currencies.gold ?? 0) + gold;
    gain.currencies.essence = (gain.currencies.essence ?? 0) + Math.round(gold * ESSENCE_RATIO);
  }
  for (const it of s.items) if (it.heroUid === hero.uid) delete it.heroUid;
}

export function resetHero(uid: number): Gain {
  return update((s) => {
    const gain = emptyGain();
    const hero = heroByUid(s, uid);
    if (!hero) return gain;
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

/** Ce qu'il manque pour la prochaine étoile, et le plan si tout est là. */
export function fusionPreview(uid: number): { plan: FusionPlan | null; maxed: boolean } {
  const s = getState();
  const hero = heroByUid(s, uid);
  if (!hero || !canGainStar(hero)) return { plan: null, maxed: true };
  const protect = new Set(s.formation.map(([u]) => u).filter((u) => u !== uid));
  return { plan: planFusion(s.heroes, uid, { protect, crystalsOwned: s.wallet.crystals }), maxed: false };
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

export function fuse(uid: number): Gain | null {
  const { plan } = fusionPreview(uid);
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
  dungeon?: { kind: DungeonKind; tier: number };
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

export function dungeonBattle(kind: DungeonKind, tier: number): BattleRequest {
  return update((s) => ({
    kind: 'dungeon' as const,
    title: `${tier + 1}`,
    heroes: teamUnits(s),
    waves: dungeonPreview(s, kind, tier),
    seed: seedFor(s),
    dungeon: { kind, tier },
  }));
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

export function dungeonPlan(kind: DungeonKind, tier: number): BattlePlan {
  const s = getState();
  const req = dungeonPreview(s, kind, tier);
  return { kind: 'dungeon', title: `${tier + 1}`, waves: req, need: referencePower(s) * DUNGEON_TIERS[tier]!, build: () => dungeonBattle(kind, tier) };
}

function dungeonPreview(s: PlayerState, kind: DungeonKind, tier: number): UnitInit[][] {
  return buildWaves({
    power: referencePower(s) * DUNGEON_TIERS[tier]!, count: Math.min(5, Math.max(1, s.formation.length)), waves: 2,
    element: (['fire', 'water', 'earth'] as const)[['gold', 'essence', 'gear'].indexOf(kind)]!, seed: tier * 31 + kind.length,
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
        if (!res.win || !req.dungeon) break;
        const { kind, tier } = req.dungeon;
        s.daily.entries[kind] += 1;
        s.dungeons[kind] = Math.max(s.dungeons[kind], tier + 1);
        const hours = DUNGEON_REWARD_HOURS[tier]!;
        if (kind === 'gold') addCurrency(s, gain, 'gold', perHour * hours * 1.5);
        if (kind === 'essence') addCurrency(s, gain, 'essence', perHour * hours);
        if (kind === 'gear') for (let i = 0; i < tier + 2; i++) gain.items.push(makeItem(s, rng, undefined, 1 + tier));
        track(s, 'dungeon');
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
export function sendMission(id: string): boolean {
  return update((s) => {
    const m = s.daily.missions.find((x) => x.id === id);
    if (!m || m.startedAt) return false;
    const t = missionTemplate(m);
    const busy = new Set(s.daily.missions.filter((x) => x.startedAt && !x.claimed).flatMap((x) => x.heroUids));
    const inTeam = new Set(s.formation.map(([u]) => u));
    const pool = s.heroes
      .filter((h) => !busy.has(h.uid) && h.stars >= t.minStars)
      .sort((a, b) => Number(inTeam.has(a.uid)) - Number(inTeam.has(b.uid)) || a.stars - b.stars || a.level - b.level);
    if (pool.length < t.heroes) return false;
    m.heroUids = pool.slice(0, t.heroes).map((h) => h.uid);
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
      const target = s.fragmentTarget ?? HEROES.find((h) => h.rarity === 'legendary')!.id;
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

export function setName(name: string): void {
  const clean = name.trim().slice(0, 16);
  if (clean) update((s) => void (s.name = clean));
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
