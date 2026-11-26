// Stockage de la partie et notification des écrans à chaque changement.
import { useEffect, useState } from 'preact/hooks';
import { HEROES, STARTER_HERO, heroDef } from '../../core/data/heroes';
import { levelCap } from '../../core/data/stats';
import { RARITY_RULES } from '../../core/data/stars';
import { retireHeroes } from './migrate';
import type { PlayerState } from './types';

const KEY = 'hero-battle-v2';
const HERO_IDS = new Set(HEROES.map((h) => h.id));

export function fresh(now = Date.now()): PlayerState {
  const starter = STARTER_HERO;
  const lang = typeof navigator !== 'undefined' && !navigator.language.startsWith('fr') ? 'en' : 'fr';
  return {
    v: 2,
    name: '',
    named: false,
    tutorial: 0,
    nameChanges: 0,
    settings: { sound: true, music: true, notifications: true },
    createdAt: now,
    timeShift: 0,
    lang,
    speed: 2,
    auto: true,
    rng: 1,
    nextUid: 2,
    account: { level: 1, xp: 0 },
    wallet: { gold: 300, essence: 150, gems: 0, scrolls: 0, basicScrolls: 0, arenaTokens: 0, guildCoins: 0, crystals: 0, dust: 0, badge: 0 },
    fragments: {},
    discovered: [starter],
    heroes: [{ uid: 1, defId: starter, stars: RARITY_RULES.epic.bornStars, level: 1 }],
    items: [],
    slotLevels: {},
    formation: [[1, 2]],
    campaign: { cleared: 0, idleFrom: now, itemHours: 0 },
    summon: { pity: 0, total: 0 },
    tower: { floor: 0 },
    dungeons: { gold: 0, essence: 0, gear: 0 },
    friends: { list: [], day: '', sent: [], inbox: [] },
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
      if (saved.v === 2) return restore(saved);
    }
  } catch {
    // stockage indisponible : nouvelle partie en mémoire
  }
  return fresh();
}

/** Une partie enregistrée, remise d'aplomb (champs ajoutés depuis, héros retirés du jeu, raretés refondues). */
export function restore(saved: PlayerState): PlayerState {
  const base = fresh();
  const discovered = saved.discovered ?? [...new Set((saved.heroes ?? []).map((h) => h.defId))];
  // Une ancienne partie déjà commencée ne refait pas le tutoriel.
  const tutorial = saved.tutorial ?? ((saved.campaign?.cleared ?? 0) > 0 ? -1 : 0);
  const s = retireHeroes({ ...base, ...saved, heroes: saved.heroes ?? [], discovered, tutorial, wallet: { ...base.wallet, ...saved.wallet } });
  // Les héros ont été refondus (raretés) : on ramène étoiles et niveaux dans les limites de leur rareté.
  s.heroes = s.heroes.filter((h) => HERO_IDS.has(h.defId)).map((h) => {
    const rule = RARITY_RULES[heroDef(h.defId).rarity];
    const stars = Math.min(rule.maxStars, Math.max(rule.bornStars, h.stars));
    return { ...h, stars, level: Math.min(h.level, levelCap(stars)) };
  });
  return s;
}

export function getState(): PlayerState {
  return state;
}

/** Heure du jeu (`timeShift` : décalage de l'horloge, utilisé par les simulations). */
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
