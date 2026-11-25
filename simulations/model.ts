// Modèle d'un joueur pour les simulations de progression.
// Il joue ses sessions, récolte son butin, invoque, fusionne, monte ses héros et avance en campagne.
import {
  CAMPAIGN_STAGES,
  OFFLINE_CAP_HOURS,
  REWARDS,
  SLOT_UNLOCK_STAGES,
  STAGE_REWARD_HOURS,
  STAGES_PER_CHAPTER,
  gearCost,
  incomePerHour,
  levelCost,
} from '../src/core/data/economy';
import { STARTER_HERO as STARTER, heroDef, heroesOfElement } from '../src/core/data/heroes';
import { FRAGMENTS_PER_COPY, MAX_YELLOW, MYTHIC_STARS, RARITY_RULES } from '../src/core/data/stars';
import { GEAR_GAIN, LEVEL_GAIN, levelCap } from '../src/core/data/stats';
import { applyFusion, canGainStar, planFusion } from '../src/core/fusion';
import { gearRefund, levelRefund, teamPower } from '../src/core/power';
import { createRng, type Rng } from '../src/core/rng';
import { summonBasic, summonOne, type SummonState } from '../src/core/summon';
import type { Hero } from '../src/core/types';

export interface Session {
  hour: number;
  minutes: number;
}

export interface Profile {
  id: string;
  label: string;
  /** Sessions du jour `day` (0 = jour d'installation). */
  sessions(day: number): Session[];
  /** Invocations gagnées chaque jour (quêtes, gemmes, pubs, achats). */
  dailySummons: number;
  /** Invocations simples (Communs et Rares) gagnées chaque jour. */
  dailyBasicSummons: number;
  /** Invocations offertes au départ en plus du tutoriel (offre de départ…). */
  starterSummons: number;
}

/** Puissance demandée pour gagner un niveau de campagne. */
export type Curve = (stage: number) => number;

export const STARTER_HERO = STARTER;
export const TUTORIAL_SUMMONS = 10;
/** Un combat dure 20 à 40 s ; en vitesse ×2 avec l'écran de victoire, environ 20 s. */
const FIGHT_MINUTES = 1 / 3;

export type Milestone = 'legendary' | 'star5' | 'red1' | 'red5' | 'teamRed' | 'mythic' | 'campaignEnd' | 'teamMythic';

export interface DaySnapshot {
  day: number;
  stage: number;
  power: number;
  teamStars: number[];
  teamLevels: number[];
  teamGear: number[];
}

export class PlayerSim {
  roster: Hero[] = [];
  stage = 0;
  resources = 0;
  crystals = 0;
  fragments = 0;
  summonsPending = 0;
  summonsDone = 0;
  hours = 0;
  milestones: Partial<Record<Milestone, number>> = {};
  days: DaySnapshot[] = [];
  /** Niveau de campagne après la première session (≈ les 10 premières minutes). */
  stageAfterFirstSession = 0;

  private nextUid = 1;
  private lastCollect = -1;
  private summonState: SummonState = { pity: 0 };
  private rng: Rng;
  private tutorialDone = false;

  constructor(
    private profile: Profile,
    private curve: Curve,
    seed: number,
  ) {
    this.rng = createRng(seed);
    this.addHero(STARTER_HERO);
    this.summonsPending = profile.starterSummons;
  }

  get slots(): number {
    return SLOT_UNLOCK_STAGES.filter((s) => this.stage >= s).length;
  }

  /** La section : les héros aux plus d'étoiles, les Légendaires d'abord (ils iront plus loin), puis les plus hauts niveaux. */
  team(): Hero[] {
    const legendary = (h: Hero) => Number(heroDef(h.defId).rarity === 'legendary');
    return [...this.roster]
      .sort((a, b) => b.stars - a.stars || legendary(b) - legendary(a) || b.level - a.level)
      .slice(0, this.slots);
  }

  /** Joue toutes les sessions jusqu'à `untilHours` (inclus), jour par jour. */
  run(totalDays: number, untilHours = Infinity): this {
    for (let day = 0; day < totalDays; day++) {
      const sessions = this.profile.sessions(day);
      for (let i = 0; i < sessions.length; i++) {
        const s = sessions[i]!;
        const t = day * 24 + s.hour;
        if (t > untilHours) return this;
        this.hours = t;
        this.playSession(day, i === 0, s.minutes);
        if (day === 0 && i === 0) this.stageAfterFirstSession = this.stage;
      }
      this.snapshot(day);
    }
    return this;
  }

  private playSession(day: number, firstOfDay: boolean, minutes: number): void {
    if (this.lastCollect >= 0) {
      const away = Math.min(this.hours - this.lastCollect, OFFLINE_CAP_HOURS);
      this.resources += away * incomePerHour(this.stage);
    }
    this.lastCollect = this.hours;
    if (firstOfDay) {
      if (day > 0) {
        this.summonsPending += this.profile.dailySummons;
        for (let i = 0; i < this.profile.dailyBasicSummons; i++) this.addHero(summonBasic(this.rng).id);
      }
      if (day >= REWARDS.fragmentsFromDay) this.fragments += REWARDS.fragmentsPerDay;
      if (this.stage >= REWARDS.crystalsFromStage) this.crystals += REWARDS.crystalsPerDay;
      if (day >= REWARDS.jokerFromDay && (day - REWARDS.jokerFromDay) % REWARDS.jokerEveryDays === 0) this.addJoker();
    }
    this.manage();
    this.campaign(minutes, day);
  }

  private campaign(minutes: number, day: number): void {
    let left = minutes;
    while (left >= FIGHT_MINUTES && this.stage < CAMPAIGN_STAGES) {
      left -= FIGHT_MINUTES;
      if (teamPower(this.team()) < this.curve(this.stage + 1)) break;
      this.stage += 1;
      this.resources += incomePerHour(this.stage) * STAGE_REWARD_HOURS;
      if (!this.tutorialDone) {
        this.tutorialDone = true;
        this.tutorialSummons();
      }
      if (this.stage % STAGES_PER_CHAPTER === 0) this.summonsPending += REWARDS.chapterSummons;
      this.manage();
      this.checkMilestones(day);
    }
    this.checkMilestones(day);
  }

  /** Après la première victoire : 10 invocations guidées, dont un Épique garanti. */
  private tutorialSummons(): void {
    const before = this.roster.length;
    this.summon(TUTORIAL_SUMMONS);
    const fresh = this.roster.slice(before);
    if (!fresh.some((h) => heroDef(h.defId).rarity === 'epic')) {
      const last = fresh[fresh.length - 1]!;
      this.roster = this.roster.filter((h) => h.uid !== last.uid);
      this.addHero('mages-2');
    }
  }

  private manage(): void {
    this.summon(Math.floor(this.summonsPending));
    this.useFragments();
    this.fuseAll();
    this.resetBench();
    this.levelTeam();
  }

  private addHero(defId: string): Hero {
    const hero: Hero = { uid: this.nextUid++, defId, stars: RARITY_RULES[heroDef(defId).rarity].bornStars, level: 1 };
    this.roster.push(hero);
    return hero;
  }

  private summon(count: number): void {
    for (let i = 0; i < count; i++) this.addHero(summonOne(this.summonState, this.rng).id);
    this.summonsPending -= count;
    this.summonsDone += count;
  }

  /**
   * Un joker ★5 de l'élément du Légendaire le plus avancé. Pour la simulation, c'est un Épique ★5
   * de cet élément : il compte exactement comme un héros ★5 à sacrifier.
   */
  private addJoker(): void {
    const best = this.roster
      .filter((h) => heroDef(h.defId).rarity === 'legendary')
      .sort((a, b) => b.stars - a.stars)[0];
    if (!best) return;
    const element = heroDef(best.defId).element;
    const joker = this.addHero(heroesOfElement(element, 'epic')[0]!.id);
    joker.stars = MAX_YELLOW;
  }

  /** Les fragments servent à faire monter le Légendaire le plus avancé. */
  private useFragments(): void {
    const best = this.roster
      .filter((h) => heroDef(h.defId).rarity === 'legendary')
      .sort((a, b) => b.stars - a.stars)[0];
    while (best && this.fragments >= FRAGMENTS_PER_COPY) {
      this.fragments -= FRAGMENTS_PER_COPY;
      this.addHero(best.defId);
    }
  }

  /** Comme le bouton « Tout fusionner », puis les fusions d'Épiques et de Légendaires, les plus forts d'abord. */
  private fuseAll(): void {
    for (let changed = true; changed; ) {
      changed = false;
      const team = new Set(this.team().map((h) => h.uid));
      const teamDefs = new Set(this.team().map((h) => h.defId));
      // Hors section, on ne fait monter que jusqu'à ★5 (pour fabriquer de quoi nourrir les fusions),
      // et jamais un doublon d'un héros de la section : c'est une copie mise de côté pour lui.
      const candidates = this.roster
        .filter((h) => canGainStar(h))
        .filter((h) => team.has(h.uid) || (h.stars < MAX_YELLOW && !teamDefs.has(h.defId)))
        .sort((a, b) => Number(team.has(b.uid)) - Number(team.has(a.uid)) || b.stars - a.stars || b.level - a.level);
      for (const target of candidates) {
        const protect = new Set([...team].filter((uid) => uid !== target.uid));
        const plan = planFusion(this.roster, target.uid, { protect, crystalsOwned: this.crystals });
        if (!plan) continue;
        const result = applyFusion(this.roster, plan);
        this.roster = result.roster;
        this.resources += result.refund;
        this.crystals -= plan.crystals;
        changed = true;
        break;
      }
    }
  }

  /** Les héros hors section sont réinitialisés : leurs ressources reviennent (règle « rien n'est perdu »). */
  private resetBench(): void {
    const team = new Set(this.team().map((h) => h.uid));
    for (const h of this.roster) {
      if (!team.has(h.uid) && (h.level > 1 || (h.gear ?? 0) > 0)) {
        this.resources += levelRefund(h.level) + gearRefund(h.gear ?? 0);
        h.level = 1;
        h.gear = 0;
      }
    }
  }

  /**
   * Dépense les ressources dans la section : à chaque fois l'amélioration qui rapporte le plus
   * de force par ressource (un niveau, ou un cran d'équipement).
   */
  private levelTeam(): void {
    const team = this.team();
    for (;;) {
      let best: { hero: Hero; kind: 'level' | 'gear'; cost: number; ratio: number } | undefined;
      for (const h of team) {
        const gear = h.gear ?? 0;
        if (h.level < levelCap(h.stars)) {
          const cost = levelCost(h.level);
          const ratio = LEVEL_GAIN / (1 + LEVEL_GAIN * (h.level - 1)) / cost;
          if (!best || ratio > best.ratio) best = { hero: h, kind: 'level', cost, ratio };
        }
        const cost = gearCost(gear);
        const ratio = GEAR_GAIN / (1 + GEAR_GAIN * gear) / cost;
        if (!best || ratio > best.ratio) best = { hero: h, kind: 'gear', cost, ratio };
      }
      if (!best || this.resources < best.cost) return;
      this.resources -= best.cost;
      if (best.kind === 'level') best.hero.level += 1;
      else best.hero.gear = (best.hero.gear ?? 0) + 1;
    }
  }

  private checkMilestones(day: number): void {
    const mark = (m: Milestone, ok: boolean) => {
      if (ok && this.milestones[m] === undefined) this.milestones[m] = day + (this.hours % 24) / 24;
    };
    const stars = this.roster.map((h) => h.stars);
    const team = this.team();
    mark('legendary', this.roster.some((h) => heroDef(h.defId).rarity === 'legendary'));
    mark('star5', stars.some((s) => s >= MAX_YELLOW));
    mark('red1', stars.some((s) => s > MAX_YELLOW));
    mark('red5', stars.some((s) => s >= 2 * MAX_YELLOW));
    mark('teamRed', team.length === 5 && team.every((h) => h.stars > MAX_YELLOW));
    mark('mythic', stars.some((s) => s >= MYTHIC_STARS));
    mark('teamMythic', team.length === 5 && team.every((h) => h.stars >= MYTHIC_STARS));
    mark('campaignEnd', this.stage >= CAMPAIGN_STAGES);
  }

  private snapshot(day: number): void {
    const team = this.team();
    this.days.push({
      day,
      stage: this.stage,
      power: Math.round(teamPower(team)),
      teamStars: team.map((h) => h.stars),
      teamLevels: team.map((h) => h.level),
      teamGear: team.map((h) => h.gear ?? 0),
    });
  }
}
