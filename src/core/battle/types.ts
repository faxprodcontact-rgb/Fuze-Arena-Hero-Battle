// Types du moteur de combat. Le moteur ne dessine rien : il calcule, et le jeu affiche ses événements.
import type { Element } from '../types';

export type Side = 'hero' | 'enemy';

/** Postes de la formation : 0-1 = défense (devant), 2 = centre (chef de section), 3-4 = attaque (derrière). */
export type Slot = 0 | 1 | 2 | 3 | 4;
export const LEADER_SLOT: Slot = 2;
export const ROWS: readonly (readonly Slot[])[] = [[0, 1], [2], [3, 4]];

// ---------- Bibliothèque d'effets ----------
// Une compétence (ou un passif) est une liste d'effets. Les héros sont construits en combinant ces effets.

/** Qui est visé. Les cibles ennemies tiennent compte de la provocation (`taunt`). */
export type Target =
  | 'front' // un ennemi de la première ligne
  | 'frontRow' // toute la première ligne ennemie
  | 'back' // un ennemi de la dernière ligne (sinon le plus proche)
  | 'backRow' // toute la dernière ligne ennemie
  | 'all' // tous les ennemis
  | 'random3' // 3 ennemis au hasard
  | 'lowestHp' // l'ennemi le plus affaibli
  | 'highestAtk' // l'ennemi le plus dangereux
  | 'attacker' // celui qui vient de frapper (contre-attaque) — ou, pour un passif « attaque », celui qu'on frappe
  | 'same' // les mêmes cibles que l'effet précédent
  | 'self'
  | 'allies' // toute son équipe
  | 'lowestAlly'; // l'allié le plus blessé

/** Effets qui restent un moment sur un combattant. */
export type StatusKind =
  | 'burn' // brûlure : dégâts chaque seconde (selon l'attaque du lanceur)
  | 'poison' // poison : dégâts chaque seconde (selon les PV max de la cible)
  | 'bleed' // saignement : dégâts chaque seconde, plus forts si la cible attaque
  | 'regen' // soin chaque seconde
  | 'stun' // étourdi : ne fait rien
  | 'silence' // ne peut pas lancer sa compétence
  | 'slow' // attaque plus lentement
  | 'taunt' // provocation : les ennemis le visent
  | 'atkUp' | 'atkDown' | 'defUp' | 'defDown' | 'speedUp' | 'critUp';

export const DEBUFFS: readonly StatusKind[] = ['burn', 'poison', 'bleed', 'stun', 'silence', 'slow', 'atkDown', 'defDown'];

export type Effect =
  /** Dégâts = attaque × power. `execute` : bonus contre une cible sous 50 % de PV. `lifesteal` : part rendue en soin. */
  | { type: 'damage'; target: Target; power: number; execute?: number; lifesteal?: number }
  /** Soin = attaque × power (ou PV max × pctMax). */
  | { type: 'heal'; target: Target; power?: number; pctMax?: number }
  /** Bouclier = PV max du lanceur × power. */
  | { type: 'shield'; target: Target; power: number }
  /** Pose un statut. `value` = force (ex. 0,3 = 30 %), `seconds` = durée, `chance` = probabilité (réduite par la Ténacité). */
  | { type: 'status'; target: Target; status: StatusKind; value?: number; seconds: number; chance?: number }
  /** Donne (ou retire si négatif) de l'énergie. */
  | { type: 'energy'; target: Target; amount: number }
  /** Retire les malus. */
  | { type: 'cleanse'; target: Target }
  /** Ramène un allié tombé avec une part de ses PV. */
  | { type: 'revive'; pctMax: number };

export interface SkillDef {
  id: string;
  effects: Effect[];
}

/** Bonus de statistiques en pourcentage (ou en points pour crit/esquive/ténacité, ex. 0,1 = +10 points). */
export interface StatMods {
  hp?: number;
  atk?: number;
  def?: number;
  speed?: number;
  crit?: number;
  critDmg?: number;
  dodge?: number;
  tenacity?: number;
  lifesteal?: number;
}

/** Un passif : un bonus permanent (pour soi ou l'équipe), ou des effets déclenchés par un événement. */
export type Passive =
  | { kind: 'stats'; stats: StatMods; team?: boolean }
  | { kind: 'trigger'; on: 'start' | 'attack' | 'hurt' | 'kill' | 'lowHp' | 'allyDeath'; chance?: number; effects: Effect[] };

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
  /** Temps entre deux attaques de base, en tours de 100 ms (la « Vitesse » affichée = 1000 / interval). */
  interval: number;
  /** Chance de coup critique (0,1 = 10 %), et force du coup critique (1,5 = +50 %). */
  crit?: number;
  critDmg?: number;
  /** Chance d'esquiver un coup, et résistance aux malus (réduit leur chance de réussir). */
  dodge?: number;
  tenacity?: number;
  lifesteal?: number;
  ranged: boolean;
  /** L'attaque normale vise l'arrière (assassins). */
  hitsBack?: boolean;
  skill: SkillDef;
  passives?: Passive[];
  talent?: Talent;
  boss?: boolean;
  /** Vrai pour les héros (le bonus d'équipe par élément ne vaut que pour eux). */
  hero?: boolean;
  /** Part de sa vie max avec laquelle il commence (mode Événement : la vie reste d'un niveau à l'autre). 1 par défaut. */
  hpFrac?: number;
}

export interface Status {
  kind: StatusKind;
  value: number;
  ticks: number;
  /** Attaque du lanceur au moment de la pose (pour les dégâts de brûlure et de saignement). */
  power: number;
  source: string;
}

export interface Unit extends UnitInit {
  hp: number;
  energy: number;
  shield: number;
  stun: number;
  cooldown: number;
  dead: boolean;
  statuses: Status[];
  /** Passif « sous 50 % de PV » déjà déclenché. */
  lowHpDone?: boolean;
}

export interface Hit {
  target: string;
  amount: number;
  kind: 'damage' | 'heal' | 'shield' | 'miss' | 'status' | 'revive';
  crit?: boolean;
  advantage?: boolean;
  stun?: boolean;
  status?: StatusKind;
  /** Dégâts dans le temps (brûlure, poison, saignement). */
  dot?: boolean;
}

export type BattleEvent =
  | { type: 'attack'; source: string; hit: Hit }
  | { type: 'skill'; source: string; skill: SkillDef; hits: Hit[] }
  | { type: 'passive'; source: string; hits: Hit[] }
  | { type: 'tick'; hits: Hit[] }
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
/** Valeurs par défaut quand un combattant n'en précise pas. */
export const CRIT_CHANCE = 0.05;
export const CRIT_MULT = 1.5;
/** Avantage d'élément : +30 % de dégâts (pas de malus dans l'autre sens). */
// (29/11 : 1.3 → 1.2 ; une région de l'élément « contraire » arrêtait des semaines une équipe plus puissante que demandé)
export const ADVANTAGE_MULT = 1.2;
/** Un statut dure un nombre de secondes ; les dégâts et soins dans le temps tombent chaque seconde. */
export const TICKS_PER_SECOND = 10;
/** Bonus d'équipe selon les éléments des héros (à partir de 3 du même élément, ou les 4 éléments réunis). */
export const ELEMENT_BONUS: Record<'same3' | 'same4' | 'same5' | 'rainbow', StatMods> = {
  same3: { atk: 0.1 },
  same4: { atk: 0.15, hp: 0.15 },
  same5: { atk: 0.2, hp: 0.2 },
  rainbow: { tenacity: 0.1, dodge: 0.1 },
};
