// Types du moteur de combat. Le moteur ne dessine rien : il calcule, et le jeu affiche ses événements.
import type { Element } from '../types';

export type Side = 'hero' | 'enemy';

/** Postes de la formation : 0-1 = défense (devant), 2 = centre (chef de section), 3-4 = attaque (derrière). */
export type Slot = 0 | 1 | 2 | 3 | 4;
export const LEADER_SLOT: Slot = 2;
export const ROWS: readonly (readonly Slot[])[] = [[0, 1], [2], [3, 4]];

export type SkillKind =
  | 'shieldAll' // bouclier sur tous les alliés
  | 'strikeBack' // gros coup sur l'arrière la plus fragile
  | 'aoe' // dégâts sur tous les ennemis
  | 'healAll' // soin de tous les alliés
  | 'drain' // coup sur l'avant + soin de soi
  | 'stunFront' // dégâts + étourdissement de la première ligne
  | 'strike' // gros coup sur l'avant
  | 'smash'; // dégâts sur toute la première ligne

export interface SkillDef {
  id: string;
  kind: SkillKind;
  /** Multiplicateur de l'attaque (ou des PV max pour le bouclier). */
  power: number;
  /** Durée d'étourdissement, en tours de 100 ms. */
  stunTicks?: number;
}

/** Bonus de chef de section, actif tant que le chef est debout (sauf `startEnergy`, donné au début). */
export interface Talent {
  atkMult?: number;
  defMult?: number;
  /** Multiplie le temps entre deux attaques (0,85 = 15 % plus rapide). */
  intervalMult?: number;
  energyMult?: number;
  healMult?: number;
  startEnergy?: number;
}

export interface UnitInit {
  id: string;
  defId: string;
  side: Side;
  slot: Slot;
  element: Element;
  maxHp: number;
  atk: number;
  def: number;
  /** Temps entre deux attaques de base, en tours de 100 ms. */
  interval: number;
  ranged: boolean;
  skill: SkillDef;
  talent?: Talent;
  boss?: boolean;
}

export interface Unit extends UnitInit {
  hp: number;
  energy: number;
  shield: number;
  stun: number;
  cooldown: number;
  dead: boolean;
}

export interface Hit {
  target: string;
  amount: number;
  kind: 'damage' | 'heal' | 'shield';
  crit?: boolean;
  advantage?: boolean;
  stun?: boolean;
}

export type BattleEvent =
  | { type: 'attack'; source: string; hit: Hit }
  | { type: 'skill'; source: string; skill: SkillDef; hits: Hit[] }
  | { type: 'death'; unit: string }
  | { type: 'wave'; index: number; units: Unit[] }
  | { type: 'end'; win: boolean };

/** Choix du joueur pendant un combat, enregistrés pour que le serveur puisse rejouer le combat. */
export type BattleInput = { tick: number; type: 'skill'; unit: string } | { tick: number; type: 'auto'; on: boolean };

export interface BattleSetup {
  heroes: UnitInit[];
  waves: UnitInit[][];
  seed: number;
  auto: boolean;
}

/** Énergie : un combattant lance sa compétence à 100. */
export const ENERGY_MAX = 100;
export const ENERGY_PER_ATTACK = 20;
export const ENERGY_PER_HIT_TAKEN = 8;
/** Au-delà de ce nombre de tours (90 s), le combat est perdu. */
export const MAX_TICKS = 900;
export const TICK_MS = 100;
export const CRIT_CHANCE = 0.1;
export const CRIT_MULT = 1.5;
export const ADVANTAGE_MULT = 1.3;
