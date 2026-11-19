// Moteur du mode Défense : les monstres suivent le chemin, les héros posés autour frappent ceux à leur portée.
// Déterministe (graine + placement = même partie), pour que le serveur puisse rejouer et vérifier.
import { ADVANTAGE_MULT, CRIT_CHANCE, CRIT_MULT, ENERGY_MAX, ENERGY_PER_ATTACK, TICK_MS, type UnitInit } from '../battle/types';
import { monsterToUnit } from '../battle/units';
import { hasAdvantage } from '../data/elements';
import {
  DEFENSE_BOSS_HP, DEFENSE_HP_FACTOR, DEFENSE_LEAK, DEFENSE_WAVE_GROWTH, DEFENSE_LIVES, DEFENSE_MELEE_BONUS, DEFENSE_PADS, DEFENSE_PATH, DEFENSE_RANGE,
  DEFENSE_SPAWN_GAP, DEFENSE_SPEED, DEFENSE_WAVE_GAP, DEFENSE_WAVES, waveSize,
} from '../data/defense';
import { createRng, pick, type Rng } from '../rng';
import type { Element } from '../types';

export interface DefenseSetup {
  /** Les héros posés : leur fiche de combat et l'emplacement choisi. */
  towers: { unit: UnitInit; pad: number }[];
  /** Puissance de référence du niveau (sert à la résistance des monstres). */
  power: number;
  element: Element;
  seed: number;
}

export interface Tower {
  id: string;
  unit: UnitInit;
  x: number;
  y: number;
  range: number;
  cooldown: number;
  energy: number;
}

export interface Creep {
  id: string;
  defId: string;
  element: Element;
  boss: boolean;
  maxHp: number;
  hp: number;
  def: number;
  speed: number;
  /** Distance parcourue sur le chemin. */
  dist: number;
  x: number;
  y: number;
  stun: number;
  slow: number;
}

export type DefenseEvent =
  | { type: 'spawn'; creep: Creep }
  | { type: 'hit'; source: string; target: string; amount: number; crit: boolean; skill?: string }
  | { type: 'skill'; source: string; skill: string; targets: string[] }
  | { type: 'death'; creep: string }
  | { type: 'leak'; creep: string; lives: number }
  | { type: 'heal'; lives: number }
  | { type: 'wave'; index: number }
  | { type: 'end'; win: boolean; lives: number };

const TICKS_PER_SECOND = 1000 / TICK_MS;
const FRONT = ['goblin', 'wolf', 'golem'];
const BACK = ['wolf', 'goblin'];
const BOSS = ['ogre', 'lich', 'dragon'];

// Le chemin découpé en segments, pour placer un monstre à partir de la distance parcourue.
const SEGMENTS = DEFENSE_PATH.slice(1).map((p, i) => {
  const a = DEFENSE_PATH[i]!;
  return { a, b: p, len: Math.hypot(p[0] - a[0], p[1] - a[1]) };
});
export const PATH_LENGTH = SEGMENTS.reduce((s, x) => s + x.len, 0);

export function pointAt(dist: number): [number, number] {
  let d = dist;
  for (const s of SEGMENTS) {
    if (d <= s.len) return [s.a[0] + ((s.b[0] - s.a[0]) * d) / s.len, s.a[1] + ((s.b[1] - s.a[1]) * d) / s.len];
    d -= s.len;
  }
  const last = DEFENSE_PATH[DEFENSE_PATH.length - 1]!;
  return [last[0], last[1]];
}

interface Spawn {
  tick: number;
  wave: number;
  index: number;
  boss: boolean;
}

export class DefenseBattle {
  towers: Tower[];
  creeps: Creep[] = [];
  lives = DEFENSE_LIVES;
  tick = 0;
  wave = 0;
  over = false;
  win = false;
  private queue: Spawn[] = [];
  private rng: Rng;

  constructor(private setup: DefenseSetup) {
    this.rng = createRng(setup.seed);
    this.towers = setup.towers.map(({ unit, pad }, i) => {
      const [x, y] = DEFENSE_PADS[pad]!;
      return { id: `t${i}`, unit, x, y, range: unit.ranged ? DEFENSE_RANGE.ranged : DEFENSE_RANGE.melee, cooldown: 5 + i * 2, energy: 0 };
    });
    for (let w = 0; w < DEFENSE_WAVES; w++) {
      const start = Math.round(w * DEFENSE_WAVE_GAP * TICKS_PER_SECOND) + 20;
      const n = waveSize(w);
      for (let i = 0; i < n; i++) this.queue.push({ tick: start + Math.round(i * DEFENSE_SPAWN_GAP * TICKS_PER_SECOND), wave: w, index: i, boss: false });
      if (w === DEFENSE_WAVES - 1) this.queue.push({ tick: start + Math.round(n * DEFENSE_SPAWN_GAP * TICKS_PER_SECOND), wave: w, index: n, boss: true });
    }
  }

  get waveCount(): number {
    return DEFENSE_WAVES;
  }

  private makeCreep(s: Spawn): Creep {
    // Résistance d'un monstre : puissance du niveau répartie comme une vague de 5, un peu plus forte à chaque vague.
    const mult = (this.setup.power / 500) * DEFENSE_HP_FACTOR * (1 + s.wave * DEFENSE_WAVE_GROWTH) * (s.boss ? DEFENSE_BOSS_HP : 1);
    const id = s.boss ? pick(this.rng, BOSS) : pick(this.rng, s.index % 3 === 2 ? BACK : FRONT);
    const u = monsterToUnit(id, 0, this.setup.element, mult, `c-${s.wave}-${s.index}`);
    const speed = (s.boss ? DEFENSE_SPEED.boss : DEFENSE_SPEED[id] ?? DEFENSE_SPEED.default)! / TICKS_PER_SECOND;
    const [x, y] = pointAt(0);
    return { id: u.id, defId: id, element: this.setup.element, boss: s.boss, maxHp: u.maxHp, hp: u.maxHp, def: u.def, speed, dist: 0, x, y, stun: 0, slow: 0 };
  }

  /** Avance d'un tour (100 ms). */
  step(): DefenseEvent[] {
    if (this.over) return [];
    const events: DefenseEvent[] = [];

    while (this.queue.length && this.queue[0]!.tick <= this.tick) {
      const s = this.queue.shift()!;
      if (s.wave > this.wave || (s.wave === 0 && s.index === 0)) {
        this.wave = s.wave;
        events.push({ type: 'wave', index: s.wave });
      }
      const c = this.makeCreep(s);
      this.creeps.push(c);
      events.push({ type: 'spawn', creep: c });
    }

    // Les monstres avancent.
    for (const c of this.creeps) {
      if (c.stun > 0) {
        c.stun -= 1;
        continue;
      }
      c.dist += c.slow > 0 ? c.speed * 0.5 : c.speed;
      if (c.slow > 0) c.slow -= 1;
      [c.x, c.y] = pointAt(c.dist);
    }
    for (const c of [...this.creeps]) {
      if (c.dist < PATH_LENGTH) continue;
      this.creeps = this.creeps.filter((x) => x !== c);
      this.lives = Math.max(0, this.lives - (c.boss ? DEFENSE_LEAK.boss : DEFENSE_LEAK.normal));
      events.push({ type: 'leak', creep: c.id, lives: this.lives });
    }
    if (this.lives <= 0) return this.finish(false, events);

    // Les héros frappent.
    for (const t of this.towers) {
      t.cooldown -= 1;
      if (t.cooldown > 0) continue;
      const inRange = this.creeps.filter((c) => c.hp > 0 && Math.hypot(c.x - t.x, c.y - t.y) <= t.range);
      if (!inRange.length) {
        t.cooldown = 1;
        continue;
      }
      t.cooldown = t.unit.interval;
      // On vise le monstre le plus avancé (le plus proche du camp).
      const target = inRange.reduce((a, b) => (b.dist > a.dist ? b : a));
      if (t.energy >= ENERGY_MAX) this.cast(t, inRange, target, events);
      else {
        this.hit(t, target, 1, events);
        t.energy = Math.min(ENERGY_MAX, t.energy + ENERGY_PER_ATTACK);
      }
    }

    for (const c of [...this.creeps]) {
      if (c.hp > 0) continue;
      this.creeps = this.creeps.filter((x) => x !== c);
      events.push({ type: 'death', creep: c.id });
    }

    this.tick += 1;
    if (!this.queue.length && !this.creeps.length) return this.finish(true, events);
    return events;
  }

  private hit(t: Tower, c: Creep, power: number, events: DefenseEvent[], skill?: string) {
    const crit = this.rng() < (t.unit.crit ?? CRIT_CHANCE);
    const adv = hasAdvantage(t.unit.element, c.element);
    const melee = t.unit.ranged ? 1 : DEFENSE_MELEE_BONUS;
    const variance = 0.9 + this.rng() * 0.2;
    const amount = Math.max(1, Math.round(t.unit.atk * power * melee * (100 / (100 + c.def)) * (adv ? ADVANTAGE_MULT : 1) * (crit ? (t.unit.critDmg ?? CRIT_MULT) : 1) * variance));
    c.hp = Math.max(0, c.hp - amount);
    events.push({ type: 'hit', source: t.id, target: c.id, amount, crit, skill });
  }

  /**
   * Compétences adaptées à la Défense, lues dans la liste d'effets du héros :
   * dégâts de zone si la compétence touche plusieurs ennemis, sinon un gros coup ; un étourdissement arrête les monstres ;
   * un bouclier ou une provocation ralentit ceux qui passent ; un soin répare le camp (une vie).
   */
  private cast(t: Tower, inRange: Creep[], target: Creep, events: DefenseEvent[]) {
    t.energy = 0;
    const { skill } = t.unit;
    const fx = skill.effects;
    const targets: Creep[] = [];
    const damages = fx.filter((e): e is Extract<typeof e, { type: 'damage' }> => e.type === 'damage');
    const stun = fx.find((e) => e.type === 'status' && e.status === 'stun');
    const wide = damages.some((e) => ['all', 'frontRow', 'backRow', 'random3'].includes(e.target));
    if (fx.some((e) => e.type === 'heal' || e.type === 'revive')) {
      this.lives = Math.min(DEFENSE_LIVES, this.lives + 1);
      events.push({ type: 'heal', lives: this.lives });
    }
    if (fx.some((e) => e.type === 'shield' || (e.type === 'status' && (e.status === 'taunt' || e.status === 'slow' || e.status === 'defDown')))) {
      for (const c of inRange) {
        c.slow = Math.max(c.slow, 40);
        targets.push(c);
      }
    }
    if (damages.length) {
      const power = damages.reduce((a, e) => a + e.power, 0);
      const hitList = wide ? inRange : [damages.some((e) => e.target === 'highestAtk' || e.target === 'lowestHp' || e.target === 'back') ? inRange.reduce((a, b) => (b.hp > a.hp ? b : a)) : target];
      for (const c of hitList) {
        this.hit(t, c, power, events, skill.id);
        if (stun && 'seconds' in stun) c.stun = Math.max(c.stun, Math.round(stun.seconds * 10));
        targets.push(c);
      }
    } else if (!targets.length) {
      this.hit(t, target, 1, events);
    }
    events.push({ type: 'skill', source: t.id, skill: skill.id, targets: targets.map((c) => c.id) });
  }

  private finish(win: boolean, events: DefenseEvent[]): DefenseEvent[] {
    this.over = true;
    this.win = win;
    events.push({ type: 'end', win, lives: this.lives });
    return events;
  }

  /** Joue la partie jusqu'au bout (serveur, tests). */
  static run(setup: DefenseSetup): DefenseBattle {
    const b = new DefenseBattle(setup);
    let guard = 0;
    while (!b.over && guard++ < 20000) b.step();
    return b;
  }
}
