// Stockage de la partie et notification des écrans à chaque changement.
import { useEffect, useState } from 'preact/hooks';
import { heroesOf } from '../../core/data/heroes';
import { RARITY_RULES } from '../../core/data/stars';
import type { PlayerState } from './types';

const KEY = 'hero-battle-v2';

export function fresh(now = Date.now()): PlayerState {
  const starter = heroesOf('knights', 'epic')[0]!.id;
  const lang = typeof navigator !== 'undefined' && !navigator.language.startsWith('fr') ? 'en' : 'fr';
  return {
    v: 2,
    name: 'Capitaine',
    createdAt: now,
    timeShift: 0,
    lang,
    speed: 2,
    auto: true,
    rng: 1,
    nextUid: 2,
    account: { level: 1, xp: 0 },
    wallet: { gold: 300, essence: 150, gems: 0, scrolls: 0, basicScrolls: 0, arenaTokens: 0, guildCoins: 0, crystals: 0 },
    fragments: {},
    heroes: [{ uid: 1, defId: starter, stars: RARITY_RULES.epic.bornStars, level: 1 }],
    items: [],
    formation: [[1, 2]],
    campaign: { cleared: 0, idleFrom: now, itemHours: 0 },
    summon: { pity: 0, total: 0 },
    tower: { floor: 0 },
    dungeons: { gold: 0, essence: 0, gear: 0 },
    arena: { points: 1000, opponents: [] },
    guild: { joined: null, bossDamage: 0, chat: [], lastBotAt: now },
    worldChat: [],
    shop: { bought: {}, cardUntil: 0, passPremium: false, noAds: false },
    pass: { points: 0, claimedFree: [], claimedPremium: [] },
    daily: {
      day: '', ads: 0, fastLoot: 0, entries: { gold: 0, essence: 0, gear: 0 }, bossAttempts: 0, bossBest: 0,
      arenaFights: 0, guildAttempts: 0, missions: [], quests: {}, claimed: [], chests: [], cardClaimed: false,
    },
    weekly: { week: '', quests: {}, claimed: [], chests: [] },
    seen: [],
  };
}

let state: PlayerState = load();
let version = 0;
const listeners = new Set<() => void>();

function load(): PlayerState {
  try {
    const raw = localStorage.getItem(KEY);
    if (raw) {
      const saved = JSON.parse(raw) as PlayerState;
      if (saved.v === 2) return { ...fresh(), ...saved };
    }
  } catch {
    // stockage indisponible : nouvelle partie en mémoire
  }
  return fresh();
}

export function getState(): PlayerState {
  return state;
}

/** Heure du jeu (avec le décalage des outils de test). */
export function now(): number {
  return Date.now() + state.timeShift;
}

/** Toute modification passe par ici : elle est enregistrée puis les écrans se mettent à jour. */
export function update<T>(change: (s: PlayerState) => T): T {
  const result = change(state);
  version += 1;
  try {
    localStorage.setItem(KEY, JSON.stringify(state));
  } catch {
    // stockage indisponible
  }
  for (const l of listeners) l();
  return result;
}

export function replaceState(next: PlayerState): void {
  state = next;
  update(() => undefined);
}

/** Les écrans appellent ce crochet : ils sont redessinés à chaque changement. */
export function useGame(): PlayerState {
  const [, setV] = useState(version);
  useEffect(() => {
    const l = () => setV(version);
    listeners.add(l);
    return () => void listeners.delete(l);
  }, []);
  return state;
}
