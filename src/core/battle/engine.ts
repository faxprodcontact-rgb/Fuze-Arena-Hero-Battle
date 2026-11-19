// Moteur de combat déterministe : mêmes héros, même graine et mêmes choix = même combat.
// Le temps avance par tours de 100 ms. Le jeu appelle `step()` et anime les événements renvoyés.
import { hasAdvantage } from '../data/elements';
import { createRng, type Rng } from '../rng';
import {
  ADVANTAGE_MULT,
  CRIT_CHANCE,
  CRIT_MULT,
  ENERGY_MAX,
  ENERGY_PER_ATTACK,
  ENERGY_PER_HIT_TAKEN,
  LEADER_SLOT,
  MAX_TICKS,
  ROWS,
  type BattleEvent,
  type BattleInput,
  type BattleSetup,
  type Hit,
  type Side,
  type Talent,
  type Unit,
  type UnitInit,
} from './types';

function spawn(init: UnitInit, startEnergy = 0): Unit {
  // Le décalage de départ dépend du poste : les attaques ne tombent pas toutes en même temps.
  return { ...init, hp: init.maxHp, energy: startEnergy, shield: 0, stun: 0, cooldown: 3 + init.slot * 2, dead: false };
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

  constructor(private setup: BattleSetup) {
    this.rng = createRng(setup.seed);
    this.auto = setup.auto;
    const leader = setup.heroes.find((h) => h.slot === LEADER_SLOT);
    const startEnergy = leader?.talent?.startEnergy ?? 0;
    this.heroes = setup.heroes.map((h) => spawn(h, startEnergy));
    this.enemies = (setup.waves[0] ?? []).map((u) => spawn(u));
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

    for (const id of this.pending.splice(0)) {
      const hero = this.heroes.find((h) => h.id === id);
      if (hero && hero.hp > 0 && hero.energy >= ENERGY_MAX) this.cast(hero, events);
    }

    for (const unit of [...this.heroes, ...this.enemies]) {
      if (unit.hp <= 0) continue;
      if (unit.stun > 0) {
        unit.stun -= 1;
        continue;
      }
      unit.cooldown -= 1;
      if (unit.cooldown <= 0) {
        unit.cooldown = Math.max(1, Math.round(unit.interval * this.talentOf(unit.side).intervalMult));
        this.basicAttack(unit, events);
        if (this.over) break;
      }
      const autoCast = unit.side === 'enemy' || this.auto;
      if (autoCast && unit.hp > 0 && unit.energy >= ENERGY_MAX) this.cast(unit, events);
      if (this.over) break;
    }

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

  private gainEnergy(unit: Unit, amount: number): void {
    if (unit.hp <= 0) return;
    unit.energy = Math.min(ENERGY_MAX, unit.energy + amount * this.talentOf(unit.side).energyMult);
  }

  private basicAttack(unit: Unit, events: BattleEvent[]): void {
    const front = this.frontRow(this.foes(unit));
    if (!front.length) return;
    const target = front[Math.floor(this.rng() * front.length)]!;
    const hit = this.damage(unit, target, 1);
    events.push({ type: 'attack', source: unit.id, hit });
    this.gainEnergy(unit, ENERGY_PER_ATTACK);
    this.afterHits(events);
  }

  private damage(source: Unit, target: Unit, power: number): Hit {
    const advantage = hasAdvantage(source.element, target.element);
    const crit = this.rng() < CRIT_CHANCE;
    const atk = source.atk * this.talentOf(source.side).atkMult;
    const def = target.def * this.talentOf(target.side).defMult;
    const variance = 0.9 + this.rng() * 0.2;
    let amount = Math.round(
      atk * power * (100 / (100 + def)) * (advantage ? ADVANTAGE_MULT : 1) * (crit ? CRIT_MULT : 1) * variance,
    );
    amount = Math.max(1, amount);
    const absorbed = Math.min(target.shield, amount);
    target.shield -= absorbed;
    target.hp = Math.max(0, target.hp - (amount - absorbed));
    this.gainEnergy(target, ENERGY_PER_HIT_TAKEN);
    return { target: target.id, amount, kind: 'damage', crit, advantage };
  }

  private heal(source: Unit, target: Unit, amount: number): Hit {
    const value = Math.round(amount * this.talentOf(source.side).healMult);
    target.hp = Math.min(target.maxHp, target.hp + value);
    return { target: target.id, amount: value, kind: 'heal' };
  }

  private cast(unit: Unit, events: BattleEvent[]): void {
    const foes = this.foes(unit);
    const allies = this.allies(unit);
    if (!foes.length) return;
    unit.energy = 0;
    const { skill } = unit;
    const hits: Hit[] = [];
    switch (skill.kind) {
      case 'shieldAll':
        for (const ally of allies) {
          const value = Math.round(unit.maxHp * skill.power);
          ally.shield += value;
          hits.push({ target: ally.id, amount: value, kind: 'shield' });
        }
        break;
      case 'strikeBack': {
        const back = foes.filter((f) => f.slot >= 3);
        const pool = back.length ? back : foes;
        const target = pool.reduce((a, b) => (b.hp < a.hp ? b : a));
        hits.push(this.damage(unit, target, skill.power));
        break;
      }
      case 'aoe':
        for (const foe of foes) hits.push(this.damage(unit, foe, skill.power));
        break;
      case 'healAll':
        for (const ally of allies) hits.push(this.heal(unit, ally, unit.atk * skill.power));
        break;
      case 'drain': {
        const front = this.frontRow(foes);
        const target = front[Math.floor(this.rng() * front.length)]!;
        const hit = this.damage(unit, target, skill.power);
        hits.push(hit, this.heal(unit, unit, hit.amount * 0.5));
        break;
      }
      case 'stunFront':
        for (const foe of this.frontRow(foes)) {
          const hit = this.damage(unit, foe, skill.power);
          if (foe.hp > 0) foe.stun = Math.max(foe.stun, skill.stunTicks ?? 0);
          hits.push({ ...hit, stun: true });
        }
        break;
      case 'strike': {
        const front = this.frontRow(foes);
        hits.push(this.damage(unit, front[Math.floor(this.rng() * front.length)]!, skill.power));
        break;
      }
      case 'smash':
        for (const foe of this.frontRow(foes)) hits.push(this.damage(unit, foe, skill.power));
        break;
    }
    events.push({ type: 'skill', source: unit.id, skill, hits });
    this.afterHits(events);
  }

  /** Morts, vague suivante, fin du combat. */
  private afterHits(events: BattleEvent[]): void {
    for (const u of [...this.heroes, ...this.enemies]) {
      if (u.hp <= 0 && !u.dead) {
        u.dead = true;
        u.energy = 0;
        events.push({ type: 'death', unit: u.id });
      }
    }
    if (this.heroes.every((h) => h.hp <= 0)) return this.finish(false, events);
    if (this.enemies.every((e) => e.hp <= 0)) {
      if (this.wave + 1 >= this.setup.waves.length) return this.finish(true, events);
      this.wave += 1;
      this.enemies = (this.setup.waves[this.wave] ?? []).map((u) => spawn(u));
      events.push({ type: 'wave', index: this.wave, units: this.enemies });
    }
  }

  private finish(win: boolean, events: BattleEvent[]): void {
    this.over = true;
    this.win = win;
    events.push({ type: 'end', win });
  }
}
