// Règles du Colisée (sans aucun affichage : le même code servira au serveur).
// - Les duels en chaîne : le 1er héros de chaque équipe se battent (le moteur de combat habituel, en 1 contre 1) ; le
//   gagnant reste, avec la vie (et l'énergie) qui lui reste, contre le héros suivant de l'autre équipe. L'équipe qui n'a
//   plus personne a perdu. Tout est automatique et rejouable (graine).
// - Le classement de la semaine : un groupe de 30 joueurs par ligue, des points gagnés ou perdus à chaque combat, les 3
//   premiers montent, les 3 derniers descendent, une récompense selon la place.
// - Les autres joueurs du groupe sont fabriqués à partir d'une graine (prototype hors ligne) : leurs points avancent au fil
//   de la semaine, toujours de la même façon pour une même graine.
import { Battle } from './battle/engine';
import { heroPowerWithGear, heroToUnit } from './battle/units';
import { MAX_TICKS, type BattleEvent, type Unit, type UnitInit } from './battle/types';
import {
  COLISEUM, COLISEUM_LEAGUES, COLISEUM_RANK_REWARDS, LEAGUE_BOT_SKILL, LEAGUE_REWARD_MULT, NAME_HEADS, NAME_TAILS,
} from './data/coliseum';
import { HEROES, heroDef } from './data/heroes';
import { RARITY_RULES } from './data/stars';
import { LEVEL_GAIN, levelCap } from './data/stats';
import { createRng, pick } from './rng';

// ---------- Les duels en chaîne ----------

export interface ColiseumSetup {
  /** Les héros du joueur, dans l'ordre de passage. */
  heroes: UnitInit[];
  /** Ceux de l'adversaire, dans l'ordre de passage. */
  foes: UnitInit[];
  seed: number;
}

/** Un nouveau duel commence : les deux combattants du milieu (l'un des deux est souvent le gagnant du duel précédent). */
export interface DuelEvent {
  type: 'duel';
  index: number;
  hero: Unit;
  enemy: Unit;
  /** Ce combattant vient d'entrer (l'autre est resté). */
  heroNew: boolean;
  enemyNew: boolean;
}
export type ColiseumEvent = BattleEvent | DuelEvent;

export interface DuelRecord {
  hero: string;
  enemy: string;
  winner: 'hero' | 'enemy' | 'none';
}

/** Ce qui reste à un combattant d'un duel à l'autre. */
interface Carry {
  hp: number;
  energy: number;
}

/** Mélange une graine et un numéro (chaque duel a sa propre graine, tirée de celle du combat). */
export function mixSeed(seed: number, n: number): number {
  let h = (seed ^ Math.imul(n + 1, 0x9e3779b1)) >>> 0;
  h = Math.imul(h ^ (h >>> 16), 0x85ebca6b) >>> 0;
  return (h ^ (h >>> 13)) >>> 0;
}

/**
 * Le combat du Colisée : une suite de duels joués par le moteur habituel. S'utilise comme un `Battle` (le jeu appelle
 * `step()` et anime les événements) ; en plus des événements du moteur, un événement `duel` annonce chaque nouveau duel.
 */
export class DuelChain {
  over = false;
  win = false;
  /** Le joueur ne choisit rien : tout est automatique. */
  readonly auto = true;
  readonly inputs = [];
  readonly duels: DuelRecord[] = [];
  heroIndex = 0;
  foeIndex = 0;
  /** Le duel en cours (0 = le premier). */
  duel = 0;
  battle: Battle;
  private carryHero?: Carry;
  private carryFoe?: Carry;

  constructor(private setup: ColiseumSetup) {
    if (!setup.heroes.length || !setup.foes.length) throw new Error('Colisée : une équipe est vide');
    this.battle = this.open();
  }

  get hero(): Unit {
    return this.battle.heroes[0]!;
  }

  get enemy(): Unit {
    return this.battle.enemies[0]!;
  }

  /** Les combattants des deux équipes dans l'ordre de passage (pour l'affichage). */
  get lineup(): { heroes: UnitInit[]; foes: UnitInit[] } {
    return { heroes: this.setup.heroes, foes: this.setup.foes };
  }

  /** Le duel suivant : les deux combattants au poste 0 (aucun talent de chef, aucun bonus d'éléments en 1 contre 1). */
  private open(): Battle {
    const fierce = (u: UnitInit): UnitInit => ({ ...u, slot: 0, atk: Math.round(u.atk * COLISEUM.duelAtk) });
    const hero: UnitInit = { ...fierce(this.setup.heroes[this.heroIndex]!), side: 'hero' };
    const foe: UnitInit = { ...fierce(this.setup.foes[this.foeIndex]!), side: 'enemy' };
    const b = new Battle({ heroes: [hero], waves: [[foe]], seed: mixSeed(this.setup.seed, this.duel), auto: true });
    const restore = (u: Unit, c?: Carry) => {
      if (!c) return;
      u.hp = Math.max(1, Math.min(u.maxHp, c.hp));
      u.energy = COLISEUM.keepEnergy ? c.energy : 0;
    };
    restore(b.heroes[0]!, this.carryHero);
    restore(b.enemies[0]!, this.carryFoe);
    return b;
  }

  /** Avance d'un tour (100 ms). */
  step(): ColiseumEvent[] {
    if (this.over) return [];
    const events: ColiseumEvent[] = this.battle.step().filter((e) => e.type !== 'end');
    if (this.battle.over) this.close(events);
    return events;
  }

  /** Fin d'un duel : qui reste, qui entre, ou la fin du combat. */
  private close(events: ColiseumEvent[]) {
    const h = this.hero, e = this.enemy;
    // le temps est écoulé (90 s) : celui à qui il reste la plus grande part de sa vie gagne le duel
    if (h.hp > 0 && e.hp > 0) {
      const rh = h.hp / h.maxHp, re = e.hp / e.maxHp;
      const losers = rh > re ? [e] : re > rh ? [h] : [h, e];
      for (const u of losers) {
        u.hp = 0;
        u.dead = true;
        events.push({ type: 'death', unit: u.id });
      }
    }
    const heroDown = h.hp <= 0, foeDown = e.hp <= 0;
    this.duels.push({ hero: h.id, enemy: e.id, winner: heroDown && foeDown ? 'none' : heroDown ? 'enemy' : 'hero' });
    this.carryHero = heroDown ? undefined : { hp: h.hp, energy: h.energy };
    this.carryFoe = foeDown ? undefined : { hp: e.hp, energy: e.energy };
    if (heroDown) this.heroIndex += 1;
    if (foeDown) this.foeIndex += 1;
    const heroesOut = this.heroIndex >= this.setup.heroes.length;
    const foesOut = this.foeIndex >= this.setup.foes.length;
    if (heroesOut || foesOut) {
      this.over = true;
      // les deux derniers tombent ensemble : l'attaquant n'a pas gagné
      this.win = foesOut && !heroesOut;
      events.push({ type: 'end', win: this.win });
      return;
    }
    this.duel += 1;
    this.battle = this.open();
    events.push({ type: 'duel', index: this.duel, hero: this.hero, enemy: this.enemy, heroNew: heroDown, enemyNew: foeDown });
  }
}

export interface ColiseumOutcome {
  win: boolean;
  duels: DuelRecord[];
  /** Héros encore debout à la fin, de chaque côté. */
  heroesLeft: number;
  foesLeft: number;
}

/** Joue tout le combat d'un coup (le serveur, les tests, et le jeu pour décider du résultat). */
export function runColiseum(setup: ColiseumSetup): ColiseumOutcome {
  const chain = new DuelChain(setup);
  const limit = (setup.heroes.length + setup.foes.length) * (MAX_TICKS + 5);
  for (let i = 0; i < limit && !chain.over; i++) chain.step();
  return {
    win: chain.win,
    duels: chain.duels,
    heroesLeft: setup.heroes.length - chain.heroIndex,
    foesLeft: setup.foes.length - chain.foeIndex,
  };
}

// ---------- Points, ligues, récompenses ----------

const clamp = (x: number, lo: number, hi: number) => Math.max(lo, Math.min(hi, x));

/** Points gagnés (positif) ou perdus (négatif) après un combat, selon l'écart de classement avec l'adversaire. */
export function pointsChange(mine: number, foe: number, win: boolean): number {
  const gap = (foe - mine) / COLISEUM.pointsGap;
  if (win) return clamp(Math.round(COLISEUM.win.base + gap), COLISEUM.win.min, COLISEUM.win.max);
  return -clamp(Math.round(COLISEUM.loss.base - gap), COLISEUM.loss.min, COLISEUM.loss.max);
}

/** La ligue de la semaine suivante : +1 pour les premiers, −1 pour les derniers (jamais sous Bronze ni au-dessus de Champion). */
export function leagueAfter(league: number, rank: number, size = COLISEUM.groupSize): number {
  if (rank <= COLISEUM.promote && league < COLISEUM_LEAGUES.length - 1) return league + 1;
  if (rank > size - COLISEUM.relegate && league > 0) return league - 1;
  return league;
}

/** La zone d'une place : montée, descente ou rien (pour colorer le classement). */
export function rankZone(league: number, rank: number, size = COLISEUM.groupSize): 'up' | 'down' | null {
  const next = leagueAfter(league, rank, size);
  return next > league ? 'up' : next < league ? 'down' : null;
}

/** La récompense de fin de semaine d'une place dans une ligue. */
export function rankReward(league: number, rank: number): { gems: number; badge: number } {
  const tier = COLISEUM_RANK_REWARDS.find((r) => rank >= r.from && rank <= r.to) ?? COLISEUM_RANK_REWARDS[COLISEUM_RANK_REWARDS.length - 1]!;
  const k = LEAGUE_REWARD_MULT[league] ?? 1;
  return { gems: Math.round((tier.gems * k) / 5) * 5, badge: Math.round((tier.badge * k) / 5) * 5 };
}

// ---------- Les autres joueurs du groupe ----------

export interface ColiseumBot {
  /** Place dans le groupe (0 … 28). */
  idx: number;
  name: string;
  /** Ses 3 héros, toujours les mêmes de la semaine. */
  heroes: string[];
  /** Chance de gagner un combat, combats par jour, heure du premier combat. */
  skill: number;
  perDay: number;
  offset: number;
  seed: number;
}

/** Le groupe de la semaine : les 29 autres joueurs (graine de la semaine + ligue). */
export function makeGroup(seed: number, league: number): ColiseumBot[] {
  const rng = createRng(mixSeed(seed, 1000 + league));
  const pool = HEROES.filter((h) => h.rarity !== 'common');
  const used = new Set<string>();
  return Array.from({ length: COLISEUM.groupSize - 1 }, (_, idx) => {
    let name = '';
    for (let k = 0; k < 20 && (!name || used.has(name)); k++) name = pick(rng, NAME_HEADS) + pick(rng, NAME_TAILS);
    if (used.has(name)) name += String(idx);
    used.add(name);
    const heroes: string[] = [];
    while (heroes.length < COLISEUM.team) {
      const h = pick(rng, pool).id;
      if (!heroes.includes(h)) heroes.push(h);
    }
    const perDay = 2 + Math.floor(rng() * 6);
    return {
      idx, name, heroes, perDay,
      skill: 0.3 + rng() * 0.42 + (LEAGUE_BOT_SKILL[league] ?? 0),
      offset: rng() * (24 / perDay),
      seed: Math.floor(rng() * 2 ** 31),
    };
  });
}

/** Heures dans une semaine. */
export const WEEK_HOURS = 168;

/** Les points d'un joueur du groupe au bout de `hours` heures de la semaine (ses combats tombent à heures fixes). */
export function botPoints(bot: ColiseumBot, hours: number): number {
  const rng = createRng(bot.seed);
  const h = Math.min(WEEK_HOURS, Math.max(0, hours));
  let points: number = COLISEUM.startPoints;
  for (let k = 0; ; k++) {
    const at = bot.offset + (k * 24) / bot.perDay;
    if (at > h) break;
    const win = rng() < bot.skill;
    // il affronte quelqu'un de son niveau : l'écart de points ne compte pas
    points = Math.max(0, points + pointsChange(points, points, win));
  }
  return points;
}

export interface Standing {
  /** -1 = le joueur. */
  idx: number;
  name: string;
  points: number;
  rank: number;
}

/** Le classement du groupe à un moment de la semaine (à égalité, le joueur passe devant). */
export function standings(bots: readonly ColiseumBot[], hours: number, me: { name: string; points: number }): Standing[] {
  const rows = [
    { idx: -1, name: me.name, points: me.points },
    ...bots.map((b) => ({ idx: b.idx, name: b.name, points: botPoints(b, hours) })),
  ];
  rows.sort((a, b) => b.points - a.points || (a.idx === -1 ? -1 : b.idx === -1 ? 1 : a.idx - b.idx));
  return rows.map((r, i) => ({ ...r, rank: i + 1 }));
}

/** La place du joueur dans le classement. */
export function myRank(bots: readonly ColiseumBot[], hours: number, me: { name: string; points: number }): number {
  return standings(bots, hours, me).find((r) => r.idx === -1)!.rank;
}

export interface FoeHero {
  defId: string;
  stars: number;
  level: number;
}

/** Les héros d'un adversaire, montés pour que leur puissance totale soit proche de `power`. */
export function botTeam(heroes: readonly string[], power: number): FoeHero[] {
  const each = power / heroes.length;
  return heroes.map((defId) => {
    const rule = RARITY_RULES[heroDef(defId).rarity];
    const levelFor = (stars: number) => Math.round(1 + (each / heroPowerWithGear({ uid: 0, defId, stars, level: 1 }) - 1) / LEVEL_GAIN);
    // le moins d'étoiles possible, au niveau qu'il faut (dans la limite de ses étoiles)
    for (let stars = rule.bornStars; stars <= rule.maxStars; stars++) {
      const level = clamp(levelFor(stars), 1, levelCap(stars));
      if (heroPowerWithGear({ uid: 0, defId, stars, level }) >= each * 0.97) return { defId, stars, level };
    }
    // un héros qui plafonne : il dépasse son niveau maximum (seule sa puissance compte pour l'adversaire)
    return { defId, stars: rule.maxStars, level: clamp(levelFor(rule.maxStars), 1, 999) };
  });
}

/** Les combattants d'un adversaire pour le moteur (ids `e-0-<n>`). */
export function foeUnits(team: readonly FoeHero[]): UnitInit[] {
  return team.map((m, i) => ({ ...heroToUnit({ uid: 9000 + i, defId: m.defId, stars: m.stars, level: m.level }, 0), id: `e-0-${i}`, side: 'enemy' as const }));
}

/** Puissance d'une équipe d'adversaire. */
export function foePower(team: readonly FoeHero[]): number {
  return team.reduce((a, m) => a + heroPowerWithGear({ uid: 0, defId: m.defId, stars: m.stars, level: m.level }), 0);
}
