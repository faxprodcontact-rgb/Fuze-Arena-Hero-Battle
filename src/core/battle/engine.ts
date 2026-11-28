// Moteur de combat déterministe : mêmes héros, même graine et mêmes choix = même combat.
// Le temps avance par tours de 100 ms. Le jeu appelle `step()` et anime les événements renvoyés.
// Les compétences et passifs sont des listes d'effets (voir `types.ts`) : le moteur sait jouer chaque effet.
import { hasAdvantage } from '../data/elements';
import { createRng, type Rng } from '../rng';
import {
  ADVANTAGE_MULT,
  CRIT_CHANCE,
  CRIT_MULT,
  DEBUFFS,
  ELEMENT_BONUS,
  ENERGY_MAX,
  ENERGY_PER_ATTACK,
  ENERGY_PER_HIT_TAKEN,
  LEADER_SLOT,
  MAX_TICKS,
  ROWS,
  TICKS_PER_SECOND,
  type BattleEvent,
  type BattleInput,
  type BattleSetup,
  type Effect,
  type Hit,
  type Passive,
  type Side,
  type StatMods,
  type StatusKind,
  type Talent,
  type Target,
  type Unit,
  type UnitInit,
} from './types';

/** Applique des bonus de statistiques (en %, ou en points pour crit/esquive/ténacité/vol de vie). */
export function applyStatMods<T extends UnitInit>(u: T, m: StatMods): T {
  return {
    ...u,
    maxHp: Math.round(u.maxHp * (1 + (m.hp ?? 0))),
    atk: Math.round(u.atk * (1 + (m.atk ?? 0))),
    def: Math.round(u.def * (1 + (m.def ?? 0))),
    interval: Math.max(4, Math.round(u.interval / (1 + (m.speed ?? 0)))),
    crit: (u.crit ?? CRIT_CHANCE) + (m.crit ?? 0),
    critDmg: (u.critDmg ?? CRIT_MULT) + (m.critDmg ?? 0),
    dodge: (u.dodge ?? 0) + (m.dodge ?? 0),
    tenacity: (u.tenacity ?? 0) + (m.tenacity ?? 0),
    lifesteal: (u.lifesteal ?? 0) + (m.lifesteal ?? 0),
  };
}

/** Bonus d'équipe selon les éléments des héros d'un camp. */
export function elementBonus(units: readonly UnitInit[]): StatMods | null {
  const heroes = units.filter((u) => u.hero);
  if (heroes.length < 3) return null;
  const counts = new Map<string, number>();
  for (const u of heroes) counts.set(u.element, (counts.get(u.element) ?? 0) + 1);
  const most = Math.max(...counts.values());
  if (most >= 5) return ELEMENT_BONUS.same5;
  if (most >= 4) return ELEMENT_BONUS.same4;
  if (most >= 3) return ELEMENT_BONUS.same3;
  if (counts.size >= 4) return ELEMENT_BONUS.rainbow;
  return null;
}

/** Prépare un camp : bonus d'élément, puis passifs permanents (pour soi ou toute l'équipe). */
function prepareSide(units: readonly UnitInit[]): UnitInit[] {
  const bonus = elementBonus(units);
  let list = units.map((u) => (bonus && u.hero ? applyStatMods(u, bonus) : u));
  for (const src of units) {
    for (const p of src.passives ?? []) {
      if (p.kind !== 'stats') continue;
      list = list.map((u) => (u.id === src.id || p.team ? applyStatMods(u, p.stats) : u));
    }
  }
  return list;
}

function spawn(init: UnitInit, startEnergy = 0): Unit {
  // Le décalage de départ dépend du poste : les attaques ne tombent pas toutes en même temps.
  const hp = init.hpFrac === undefined ? init.maxHp : Math.max(1, Math.round(init.maxHp * init.hpFrac));
  return { ...init, hp, energy: startEnergy, shield: 0, stun: 0, cooldown: 3 + init.slot * 2, dead: false, statuses: [] };
}

interface Ctx {
  /** Celui qui vient de frapper (pour une contre-attaque). */
  attacker?: Unit;
  /** Les effets déclenchés par un passif ne déclenchent pas d'autres passifs (pas de réactions en chaîne). */
  fromPassive?: boolean;
  /** Cibles de l'effet précédent (pour la cible `same`). */
  last?: Unit[];
}

export class Battle {
  tick = 0;
  heroes: Unit[];
  enemies: Unit[] = [];
  wave = 0;
  over = false;
  win = false;
  auto: boolean;
  /** Tous les choix du joueur, dans l'ordre (pour rejouer et vérifier le combat). */
  readonly inputs: BattleInput[] = [];

  private rng: Rng;
  private pending: string[] = [];
  private started = false;

  constructor(private setup: BattleSetup) {
    this.rng = createRng(setup.seed);
    this.auto = setup.auto;
    const leader = setup.heroes.find((h) => h.slot === LEADER_SLOT);
    const startEnergy = leader?.talent?.startEnergy ?? 0;
    this.heroes = prepareSide(setup.heroes).map((h) => spawn(h, startEnergy));
    this.enemies = prepareSide(setup.waves[0] ?? []).map((u) => spawn(u));
  }

  get waveCount(): number {
    return this.setup.waves.length;
  }

  /** Le joueur touche le portrait d'un héros dont la jauge est pleine. */
  requestSkill(unitId: string): boolean {
    const hero = this.heroes.find((h) => h.id === unitId);
    if (this.over || !hero || hero.hp <= 0 || hero.energy < ENERGY_MAX || this.pending.includes(unitId)) return false;
    this.pending.push(unitId);
    this.inputs.push({ tick: this.tick, type: 'skill', unit: unitId });
    return true;
  }

  setAuto(on: boolean): void {
    if (this.auto === on) return;
    this.auto = on;
    this.inputs.push({ tick: this.tick, type: 'auto', on });
  }

  /** Avance d'un tour (100 ms) et renvoie ce qui s'est passé. */
  step(): BattleEvent[] {
    if (this.over) return [];
    const events: BattleEvent[] = [];
    if (!this.started) {
      this.started = true;
      for (const u of [...this.heroes, ...this.enemies]) this.trigger(u, 'start', events, {});
      this.afterHits(events);
      if (this.over) return events;
    }

    for (const id of this.pending.splice(0)) {
      const hero = this.heroes.find((h) => h.id === id);
      if (hero && hero.hp > 0 && hero.energy >= ENERGY_MAX && !this.has(hero, 'stun') && !this.has(hero, 'silence')) this.cast(hero, events);
      if (this.over) return events;
    }

    for (const unit of [...this.heroes, ...this.enemies]) {
      if (unit.hp <= 0) continue;
      if (this.has(unit, 'stun')) continue;
      unit.cooldown -= 1;
      if (unit.cooldown <= 0) {
        unit.cooldown = this.interval(unit);
        this.basicAttack(unit, events);
        if (this.over) break;
      }
      const autoCast = unit.side === 'enemy' || this.auto;
      if (autoCast && unit.hp > 0 && unit.energy >= ENERGY_MAX && !this.has(unit, 'silence') && !this.has(unit, 'stun')) this.cast(unit, events);
      if (this.over) break;
    }

    if (!this.over) this.tickStatuses(events);
    this.tick += 1;
    if (!this.over && this.tick >= MAX_TICKS) this.finish(false, events);
    return events;
  }

  /** Joue le combat jusqu'au bout avec une liste de choix (utilisé par le serveur et les tests). */
  static replay(setup: BattleSetup, inputs: readonly BattleInput[]): Battle {
    const battle = new Battle(setup);
    let next = 0;
    while (!battle.over) {
      while (next < inputs.length && inputs[next]!.tick === battle.tick) {
        const input = inputs[next++]!;
        if (input.type === 'skill') battle.requestSkill(input.unit);
        else battle.setAuto(input.on);
      }
      battle.step();
    }
    return battle;
  }

  // ---------- Statistiques du moment ----------

  /** Bonus du chef de section de ce camp, s'il est encore debout. */
  private talentOf(side: Side): Required<Omit<Talent, 'startEnergy'>> {
    const leader = side === 'hero' ? this.heroes.find((h) => h.slot === LEADER_SLOT && h.hp > 0) : undefined;
    const t = leader?.talent ?? {};
    return {
      atkMult: t.atkMult ?? 1,
      defMult: t.defMult ?? 1,
      intervalMult: t.intervalMult ?? 1,
      energyMult: t.energyMult ?? 1,
      healMult: t.healMult ?? 1,
    };
  }

  private has(u: Unit, kind: StatusKind): boolean {
    return u.statuses.some((x) => x.kind === kind);
  }

  private sum(u: Unit, kind: StatusKind): number {
    return u.statuses.filter((x) => x.kind === kind).reduce((a, x) => a + x.value, 0);
  }

  private atkOf(u: Unit): number {
    return u.atk * this.talentOf(u.side).atkMult * Math.max(0.2, 1 + this.sum(u, 'atkUp') - this.sum(u, 'atkDown'));
  }

  private defOf(u: Unit): number {
    return u.def * this.talentOf(u.side).defMult * Math.max(0.2, 1 + this.sum(u, 'defUp') - this.sum(u, 'defDown'));
  }

  private interval(u: Unit): number {
    const slow = this.has(u, 'slow') ? 1 + this.sum(u, 'slow') : 1;
    const fast = 1 + this.sum(u, 'speedUp');
    return Math.max(3, Math.round((u.interval * this.talentOf(u.side).intervalMult * slow) / fast));
  }

  // ---------- Cibles ----------

  private allies(unit: Unit): Unit[] {
    return (unit.side === 'hero' ? this.heroes : this.enemies).filter((u) => u.hp > 0);
  }

  private foes(unit: Unit): Unit[] {
    return (unit.side === 'hero' ? this.enemies : this.heroes).filter((u) => u.hp > 0);
  }

  /** La première ligne encore debout : la défense, puis le centre, puis l'attaque. */
  private frontRow(units: Unit[]): Unit[] {
    for (const row of ROWS) {
      const alive = units.filter((u) => row.includes(u.slot));
      if (alive.length) return alive;
    }
    return [];
  }

  private backRow(units: Unit[]): Unit[] {
    for (const row of [...ROWS].reverse()) {
      const alive = units.filter((u) => row.includes(u.slot));
      if (alive.length) return alive;
    }
    return [];
  }

  private pick(list: Unit[]): Unit | undefined {
    return list.length ? list[Math.floor(this.rng() * list.length)] : undefined;
  }

  private targets(source: Unit, target: Target, ctx: Ctx): Unit[] {
    const foes = this.foes(source);
    const allies = this.allies(source);
    const taunt = foes.filter((f) => this.has(f, 'taunt'));
    const single = (u: Unit | undefined) => (u ? [u] : []);
    const one = (list: Unit[]) => (taunt.length ? [taunt[0]!] : single(this.pick(list)));
    switch (target) {
      case 'front': return one(this.frontRow(foes));
      case 'frontRow': return this.frontRow(foes);
      case 'back': return one(this.backRow(foes));
      case 'backRow': return this.backRow(foes);
      case 'all': return foes;
      case 'random3': {
        const pool = [...foes];
        const out: Unit[] = [];
        while (pool.length && out.length < 3) out.push(pool.splice(Math.floor(this.rng() * pool.length), 1)[0]!);
        return out;
      }
      case 'lowestHp': return taunt.length ? [taunt[0]!] : single(foes.reduce<Unit | undefined>((a, b) => (!a || b.hp / b.maxHp < a.hp / a.maxHp ? b : a), undefined));
      case 'highestAtk': return taunt.length ? [taunt[0]!] : single(foes.reduce<Unit | undefined>((a, b) => (!a || b.atk > a.atk ? b : a), undefined));
      case 'attacker': return ctx.attacker && ctx.attacker.hp > 0 ? [ctx.attacker] : [];
      case 'same': return (ctx.last ?? []).filter((u) => u.hp > 0);
      case 'self': return source.hp > 0 ? [source] : [];
      case 'allies': return allies;
      case 'lowestAlly': return single(allies.reduce<Unit | undefined>((a, b) => (!a || b.hp / b.maxHp < a.hp / a.maxHp ? b : a), undefined));
    }
  }

  // ---------- Actions ----------

  private gainEnergy(unit: Unit, amount: number): void {
    if (unit.hp <= 0) return;
    const mult = amount > 0 ? this.talentOf(unit.side).energyMult : 1;
    unit.energy = Math.max(0, Math.min(ENERGY_MAX, unit.energy + amount * mult));
  }

  private basicAttack(unit: Unit, events: BattleEvent[]): void {
    const [target] = this.targets(unit, unit.hitsBack ? 'back' : 'front', {});
    if (!target) return;
    const hit = this.damage(unit, target, 1, {}, {});
    events.push({ type: 'attack', source: unit.id, hit });
    this.gainEnergy(unit, ENERGY_PER_ATTACK);
    this.trigger(unit, 'attack', events, { attacker: target });
    this.afterHits(events);
  }

  private damage(source: Unit, target: Unit, power: number, opts: { execute?: number; lifesteal?: number }, ctx: Ctx): Hit {
    if (this.rng() < (target.dodge ?? 0)) return { target: target.id, amount: 0, kind: 'miss' };
    const advantage = hasAdvantage(source.element, target.element);
    const crit = this.rng() < (source.crit ?? CRIT_CHANCE) + this.sum(source, 'critUp');
    const variance = 0.9 + this.rng() * 0.2;
    const execute = opts.execute && target.hp < target.maxHp / 2 ? 1 + opts.execute : 1;
    let amount = Math.round(
      this.atkOf(source) * power * (100 / (100 + this.defOf(target))) * (advantage ? ADVANTAGE_MULT : 1) *
        (crit ? (source.critDmg ?? CRIT_MULT) : 1) * execute * variance,
    );
    amount = Math.max(1, amount);
    const absorbed = Math.min(target.shield, amount);
    target.shield -= absorbed;
    const before = target.hp;
    target.hp = Math.max(0, target.hp - (amount - absorbed));
    const steal = (opts.lifesteal ?? 0) + (source.lifesteal ?? 0);
    if (steal > 0 && source.hp > 0) source.hp = Math.min(source.maxHp, source.hp + Math.round(amount * steal));
    this.gainEnergy(target, ENERGY_PER_HIT_TAKEN);
    if (!ctx.fromPassive) {
      // Réactions : riposte quand on est touché, passif « sous 50 % », passif « ennemi vaincu ».
      const sub: BattleEvent[] = [];
      if (target.hp > 0) this.trigger(target, 'hurt', sub, { attacker: source });
      if (target.hp > 0 && before >= target.maxHp / 2 && target.hp < target.maxHp / 2 && !target.lowHpDone) {
        target.lowHpDone = true;
        this.trigger(target, 'lowHp', sub, { attacker: source });
      }
      if (before > 0 && target.hp <= 0) this.trigger(source, 'kill', sub, {});
      this.queued.push(...sub);
    }
    return { target: target.id, amount, kind: 'damage', crit, advantage };
  }

  /** Événements de passifs déclenchés pendant un coup : ajoutés après l'événement du coup lui-même. */
  private queued: BattleEvent[] = [];

  private heal(source: Unit, target: Unit, amount: number): Hit {
    const value = Math.round(amount * this.talentOf(source.side).healMult);
    target.hp = Math.min(target.maxHp, target.hp + value);
    return { target: target.id, amount: value, kind: 'heal' };
  }

  private addStatus(source: Unit, target: Unit, kind: StatusKind, value: number, seconds: number, chance: number): Hit | null {
    const debuff = DEBUFFS.includes(kind);
    const odds = debuff && target.side !== source.side ? chance * (1 - Math.min(0.9, target.tenacity ?? 0)) : chance;
    if (this.rng() >= odds) return null;
    const ticks = Math.round(seconds * TICKS_PER_SECOND);
    const same = target.statuses.find((x) => x.kind === kind);
    if (same) {
      same.value = Math.max(same.value, value);
      same.ticks = Math.max(same.ticks, ticks);
      same.power = Math.max(same.power, this.atkOf(source));
    } else {
      target.statuses.push({ kind, value, ticks, power: this.atkOf(source), source: source.id });
    }
    if (kind === 'stun') target.stun = Math.max(target.stun, ticks);
    return { target: target.id, amount: 0, kind: 'status', status: kind, stun: kind === 'stun' };
  }

  /** Joue une liste d'effets lancée par `source`. */
  private apply(source: Unit, effects: readonly Effect[], ctx: Ctx): Hit[] {
    const hits: Hit[] = [];
    const local: Ctx = { ...ctx };
    for (const e of effects) {
      if (e.type === 'revive') {
        const side = source.side === 'hero' ? this.heroes : this.enemies;
        const fallen = side.find((u) => u.hp <= 0);
        if (fallen) {
          fallen.hp = Math.round(fallen.maxHp * e.pctMax);
          fallen.dead = false;
          fallen.statuses = [];
          fallen.stun = 0;
          fallen.energy = 0;
          hits.push({ target: fallen.id, amount: fallen.hp, kind: 'revive' });
        }
        continue;
      }
      const chosen = this.targets(source, e.target, local);
      local.last = chosen;
      for (const t of chosen) {
        switch (e.type) {
          case 'damage':
            if (t.hp > 0) hits.push(this.damage(source, t, e.power, e, local));
            break;
          case 'heal':
            hits.push(this.heal(source, t, (e.power ?? 0) * this.atkOf(source) + (e.pctMax ?? 0) * t.maxHp));
            break;
          case 'shield': {
            const value = Math.round(source.maxHp * e.power);
            t.shield += value;
            hits.push({ target: t.id, amount: value, kind: 'shield' });
            break;
          }
          case 'status': {
            if (t.hp <= 0) break;
            const h = this.addStatus(source, t, e.status, e.value ?? 0, e.seconds, e.chance ?? 1);
            if (h) hits.push(h);
            break;
          }
          case 'energy':
            this.gainEnergy(t, e.amount);
            break;
          case 'cleanse':
            t.statuses = t.statuses.filter((x) => !DEBUFFS.includes(x.kind));
            t.stun = 0;
            break;
        }
      }
    }
    return hits;
  }

  private cast(unit: Unit, events: BattleEvent[]): void {
    if (!this.foes(unit).length) return;
    unit.energy = 0;
    const hits = this.apply(unit, unit.skill.effects, {});
    events.push({ type: 'skill', source: unit.id, skill: unit.skill, hits });
    events.push(...this.queued.splice(0));
    this.afterHits(events);
  }

  /** Déclenche les passifs d'un combattant pour un événement. */
  private trigger(unit: Unit, on: Extract<Passive, { kind: 'trigger' }>['on'], events: BattleEvent[], ctx: Ctx): void {
    for (const p of unit.passives ?? []) {
      if (p.kind !== 'trigger' || p.on !== on) continue;
      if (unit.hp <= 0 && on !== 'allyDeath') continue;
      if (this.rng() >= (p.chance ?? 1)) continue;
      const hits = this.apply(unit, p.effects, { ...ctx, fromPassive: true });
      if (hits.length) events.push({ type: 'passive', source: unit.id, hits });
    }
  }

  /** Chaque tour : les statuts s'usent ; chaque seconde, brûlure, poison, saignement et soins dans le temps. */
  private tickStatuses(events: BattleEvent[]): void {
    const second = this.tick % TICKS_PER_SECOND === 0;
    const hits: Hit[] = [];
    for (const u of [...this.heroes, ...this.enemies]) {
      if (u.hp <= 0) continue;
      if (second) {
        for (const st of u.statuses) {
          let dmg = 0;
          if (st.kind === 'burn' || st.kind === 'bleed') dmg = st.power * st.value * (st.kind === 'bleed' && u.cooldown <= 2 ? 1.5 : 1);
          if (st.kind === 'poison') dmg = u.maxHp * st.value;
          if (dmg > 0) {
            const amount = Math.max(1, Math.round(dmg));
            u.hp = Math.max(0, u.hp - amount);
            hits.push({ target: u.id, amount, kind: 'damage', dot: true, status: st.kind });
          }
          if (st.kind === 'regen') {
            const amount = Math.round(st.power * st.value);
            u.hp = Math.min(u.maxHp, u.hp + amount);
            hits.push({ target: u.id, amount, kind: 'heal', dot: true });
          }
        }
      }
      for (const st of u.statuses) st.ticks -= 1;
      u.statuses = u.statuses.filter((st) => st.ticks > 0);
      u.stun = u.statuses.find((x) => x.kind === 'stun')?.ticks ?? 0;
    }
    if (hits.length) {
      events.push({ type: 'tick', hits });
      this.afterHits(events);
    }
  }

  /** Morts, vague suivante, fin du combat. */
  private afterHits(events: BattleEvent[]): void {
    events.push(...this.queued.splice(0));
    for (const u of [...this.heroes, ...this.enemies]) {
      if (u.hp <= 0 && !u.dead) {
        u.dead = true;
        u.energy = 0;
        u.statuses = [];
        u.stun = 0;
        events.push({ type: 'death', unit: u.id });
        for (const ally of (u.side === 'hero' ? this.heroes : this.enemies).filter((a) => a.hp > 0)) this.trigger(ally, 'allyDeath', events, {});
      }
    }
    if (this.heroes.every((h) => h.hp <= 0)) return this.finish(false, events);
    if (this.enemies.every((e) => e.hp <= 0)) {
      if (this.wave + 1 >= this.setup.waves.length) return this.finish(true, events);
      this.wave += 1;
      this.enemies = prepareSide(this.setup.waves[this.wave] ?? []).map((u) => spawn(u));
      events.push({ type: 'wave', index: this.wave, units: this.enemies });
      for (const u of this.enemies) this.trigger(u, 'start', events, {});
    }
  }

  private finish(win: boolean, events: BattleEvent[]): void {
    if (this.over) return;
    this.over = true;
    this.win = win;
    events.push({ type: 'end', win });
  }
}
