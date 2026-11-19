// Les 4 éléments : Eau bat Feu, Feu bat Vent, Vent bat Terre, Terre bat Eau.
import type { Element } from '../types';

const BEATS: Record<Element, Element> = { water: 'fire', fire: 'wind', wind: 'earth', earth: 'water' };

export function hasAdvantage(attacker: Element, defender: Element): boolean {
  return BEATS[attacker] === defender;
}
