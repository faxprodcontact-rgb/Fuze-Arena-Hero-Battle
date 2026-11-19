// Génère les vagues de monstres de n'importe quel niveau à partir d'une puissance visée.
// Même niveau = mêmes monstres pour tout le monde (le hasard part du numéro du niveau).
import { monsterToUnit } from './battle/units';
import type { Slot, UnitInit } from './battle/types';
import { stagePower } from './data/campaign';
import { SLOT_UNLOCK_STAGES, STAGES_PER_CHAPTER } from './data/economy';
import { BACK_MONSTERS, BOSSES, FRONT_MONSTERS } from './data/monsters';
import { createRng, pick } from './rng';
import { ELEMENTS, type Element } from './types';

/**
 * Réglage de la force des monstres : une section dont la force vaut exactement la puissance demandée
 * gagne environ 2 fois sur 3 (réglé par simulations/combat.ts).
 */
export const BALANCE = {
  monsterScale: 1.1,
  /** Plus il y a de vagues, plus chacune est légère : les héros doivent tenir jusqu'au bout. */
  waveExponent: 0.35,
  /** Force du boss par rapport à un monstre normal, multipliée par le nombre de héros. */
  bossFactor: 0.2,
};

export function slotsAt(cleared: number): number {
  return SLOT_UNLOCK_STAGES.filter((s) => cleared >= s).length;
}

export function chapterOf(stage: number): number {
  return Math.ceil(stage / STAGES_PER_CHAPTER);
}

export function stageInChapter(stage: number): number {
  return ((stage - 1) % STAGES_PER_CHAPTER) + 1;
}

export function chapterElement(chapter: number): Element {
  return ELEMENTS[(chapter - 1) % ELEMENTS.length]!;
}

export function isBossStage(stage: number): boolean {
  return stageInChapter(stage) === STAGES_PER_CHAPTER;
}

export interface WaveOptions {
  /** Puissance totale de section que ce combat demande. */
  power: number;
  /** Nombre de monstres par vague (comme le nombre de héros du joueur à ce moment-là). */
  count: number;
  waves: number;
  element: Element;
  seed: number;
  boss?: string;
}

const FRONT_SLOTS: Slot[] = [0, 1, 2];
const BACK_SLOTS: Slot[] = [3, 4];

export function buildWaves(o: WaveOptions): UnitInit[][] {
  const rng = createRng(o.seed);
  const perMonster = ((o.power / (100 * o.count)) * BALANCE.monsterScale) / Math.pow(o.waves, BALANCE.waveExponent);
  const waves: UnitInit[][] = [];
  for (let w = 0; w < o.waves; w++) {
    const last = w === o.waves - 1;
    const units: UnitInit[] = [];
    if (last && o.boss) {
      units.push(monsterToUnit(o.boss, 2, o.element, perMonster * Math.max(1, o.count * BALANCE.bossFactor), `e-${w}-boss`));
      const adds = Math.min(2, o.count - 1);
      for (let i = 0; i < adds; i++) units.push(monsterToUnit(pick(rng, FRONT_MONSTERS), i as Slot, o.element, perMonster * 0.6, `e-${w}-${i}`));
    } else {
      const front = Math.min(3, Math.max(1, Math.ceil(o.count * 0.6)));
      for (let i = 0; i < o.count; i++) {
        const isFront = i < front;
        const slot = isFront ? FRONT_SLOTS[i]! : BACK_SLOTS[i - front]!;
        units.push(monsterToUnit(pick(rng, isFront ? FRONT_MONSTERS : BACK_MONSTERS), o.count === 1 ? 2 : slot, o.element, perMonster, `e-${w}-${i}`));
      }
    }
    waves.push(units);
  }
  return waves;
}

/** Les vagues d'un niveau de campagne. */
export function campaignWaves(stage: number): UnitInit[][] {
  const pos = stageInChapter(stage);
  const chapter = chapterOf(stage);
  return buildWaves({
    power: stagePower(stage),
    count: slotsAt(stage - 1),
    waves: pos <= 10 ? 1 : pos <= 30 ? 2 : 3,
    element: chapterElement(chapter),
    seed: stage * 7919,
    boss: isBossStage(stage) ? BOSSES[(chapter - 1) % BOSSES.length] : undefined,
  });
}
