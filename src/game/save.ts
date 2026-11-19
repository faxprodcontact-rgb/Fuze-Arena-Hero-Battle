// Sauvegarde du prototype, sur le téléphone seulement (le vrai jeu sauvegardera sur le serveur).
import type { Slot } from '../core/battle/types';
import { STARTING_HERO } from '../core/data/prototype';

export interface SaveData {
  cleared: number;
  gold: number;
  owned: string[];
  levels: Record<string, number>;
  formation: [string, Slot][];
  lang: 'fr' | 'en';
  speed: 1 | 2 | 3;
  auto: boolean;
  /** Ce que le joueur n'a pas encore vu (point rouge sur « Section »). */
  unseen: boolean;
}

const KEY = 'hero-battle-proto-v1';

function fresh(): SaveData {
  const lang = typeof navigator !== 'undefined' && !navigator.language.startsWith('fr') ? 'en' : 'fr';
  return {
    cleared: 0, gold: 0, owned: [STARTING_HERO], levels: { [STARTING_HERO]: 1 },
    formation: [[STARTING_HERO, 2]], lang, speed: 2, auto: true, unseen: false,
  };
}

let cache: SaveData | undefined;

export function loadSave(): SaveData {
  if (cache) return cache;
  try {
    const raw = localStorage.getItem(KEY);
    cache = raw ? { ...fresh(), ...(JSON.parse(raw) as Partial<SaveData>) } : fresh();
  } catch {
    cache = fresh();
  }
  return cache;
}

export function writeSave(change: Partial<SaveData> = {}): SaveData {
  cache = { ...loadSave(), ...change };
  try {
    localStorage.setItem(KEY, JSON.stringify(cache));
  } catch {
    // stockage indisponible (navigation privée) : la partie reste en mémoire
  }
  return cache;
}

export function resetSave(): void {
  cache = undefined;
  try {
    localStorage.removeItem(KEY);
  } catch {
    // rien à faire
  }
}
