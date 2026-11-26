// Calculs dérivés de l'état du joueur (rien n'est modifié ici).
import { heroPowerWithGear, heroToUnit } from '../../core/battle/units';
import type { Slot, UnitInit } from '../../core/battle/types';
import { incomePerHour, OFFLINE_CAP_HOURS, REWARDS, levelCost } from '../../core/data/economy';
import { heroDef } from '../../core/data/heroes';
import { equippedBonus, gearStats, type GearSlot, type Item } from '../../core/data/items';
import type { StatMods } from '../../core/battle/types';
import { ESSENCE_RATIO, IDLE_ITEM_HOURS, UNLOCKS, type Feature } from '../../core/data/modes';
import { levelCap } from '../../core/data/stats';
import { slotsAt } from '../../core/stages';
import type { Hero } from '../../core/types';
import { now } from './store';
import type { PlayerState } from './types';

export function heroByUid(s: PlayerState, uid: number): Hero | undefined {
  return s.heroes.find((h) => h.uid === uid);
}

export function heroItems(s: PlayerState, uid: number): Partial<Record<GearSlot, Item>> {
  const out: Partial<Record<GearSlot, Item>> = {};
  for (const it of s.items) if (it.heroUid === uid) out[it.slot] = it;
  return out;
}

export function slotLevel(s: PlayerState, uid: number, slot: GearSlot): number {
  return s.slotLevels[uid]?.[slot] ?? 0;
}

/** Bonus total de l'équipement d'un héros, en % (objets × renforcement de leurs emplacements). */
/** Les vraies statistiques apportées par l'équipement d'un héros (objets, renforcements, panoplie). */
export function gearStatsOf(s: PlayerState, uid: number): StatMods {
  return gearStats(s.items.filter((it) => it.heroUid === uid).map((item) => ({ item, level: slotLevel(s, uid, item.slot) })));
}

/** Bonus d'équipement en % (pour la puissance affichée). */
export function gearPct(s: PlayerState, uid: number): number {
  return s.items.filter((it) => it.heroUid === uid).reduce((sum, it) => sum + equippedBonus(it, slotLevel(s, uid, it.slot)), 0);
}

export function heroPower(s: PlayerState, hero: Hero): number {
  return heroPowerWithGear(hero, gearPct(s, hero.uid));
}

export type TeamKind = 'main' | 'defense';

/** La section principale, ou la section de défense (par défaut, la même que la principale). */
export function formationOf(s: PlayerState, team: TeamKind = 'main'): [number, Slot][] {
  if (team === 'main') return s.formation;
  const owned = new Set(s.heroes.map((h) => h.uid));
  const def = (s.defenseTeam ?? []).filter(([u]) => owned.has(u));
  return def.length ? def : s.formation;
}

export function teamHeroes(s: PlayerState, team: TeamKind = 'main'): { hero: Hero; slot: Slot }[] {
  return formationOf(s, team)
    .map(([uid, slot]) => ({ hero: heroByUid(s, uid)!, slot }))
    .filter((x) => x.hero);
}

export function teamPower(s: PlayerState, team: TeamKind = 'main'): number {
  return teamHeroes(s, team).reduce((sum, { hero }) => sum + heroPower(s, hero), 0);
}

export function teamUnits(s: PlayerState): UnitInit[] {
  return teamHeroes(s).map(({ hero, slot }) => heroToUnit(hero, slot, gearStatsOf(s, hero.uid)));
}

export function slotCount(s: PlayerState): number {
  return slotsAt(s.campaign.cleared);
}

/**
 * Essai du propriétaire (26/11) : tout ouvrir pour vérifier les zones bloquées par niveau. L'adresse `?tout=1` l'allume
 * (gardé sur le téléphone), `?tout=0` l'éteint. À retirer avant la bêta.
 */
const OPEN_ALL = (() => {
  try {
    const q = new URLSearchParams(location.search).get('tout');
    if (q === '1') localStorage.setItem('fuze-tout', '1');
    if (q === '0') localStorage.removeItem('fuze-tout');
    return localStorage.getItem('fuze-tout') === '1';
  } catch { return false; }
})();

export function isUnlocked(s: PlayerState, feature: Feature): boolean {
  return OPEN_ALL || s.campaign.cleared >= UNLOCKS[feature];
}

/** Butin hors ligne accumulé depuis la dernière récolte. */
/** Heures de butin pour un cristal (crystalsPerDay par jour). */
export const CRYSTAL_HOURS = 24 / REWARDS.crystalsPerDay;

export function idlePreview(s: PlayerState) {
  const hours = Math.min(OFFLINE_CAP_HOURS, Math.max(0, (now() - s.campaign.idleFrom) / 3.6e6));
  const perHour = incomePerHour(s.campaign.cleared);
  return {
    hours,
    full: hours >= OFFLINE_CAP_HOURS,
    gold: Math.floor(hours * perHour),
    essence: Math.floor(hours * perHour * ESSENCE_RATIO),
    items: Math.floor((s.campaign.itemHours + hours) / IDLE_ITEM_HOURS),
    // Cristaux d'éveil : à partir d'un niveau de campagne avancé, quelques-uns par jour dans le butin.
    crystals: s.campaign.cleared >= REWARDS.crystalsFromStage ? Math.floor(((s.campaign.crystalHours ?? 0) + hours) / CRYSTAL_HOURS) : 0,
    perHour,
  };
}

export function levelUpCost(hero: Hero): { gold: number; essence: number } | null {
  if (hero.level >= levelCap(hero.stars)) return null;
  const gold = levelCost(hero.level);
  return { gold, essence: Math.round(gold * ESSENCE_RATIO) };
}

export function canLevelUp(s: PlayerState, hero: Hero): boolean {
  const cost = levelUpCost(hero);
  return !!cost && s.wallet.gold >= cost.gold && s.wallet.essence >= cost.essence;
}

export function sortedHeroes(s: PlayerState): Hero[] {
  return [...s.heroes].sort((a, b) => heroPower(s, b) - heroPower(s, a));
}

export function heroName(hero: Hero): string {
  return heroDef(hero.defId).name;
}

/** Le portrait du joueur : le héros choisi dans les réglages, sinon le visage du premier héros de la section. */
export function avatarOf(s: PlayerState): string | undefined {
  if (s.avatar && s.discovered.includes(s.avatar)) return s.avatar;
  return (s.heroes.find((h) => h.uid === s.formation[0]?.[0]) ?? s.heroes[0])?.defId;
}
