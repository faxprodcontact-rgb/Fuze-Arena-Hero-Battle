// Navigation : onglet ouvert, sous-écran, fenêtres empilées, combat en cours, petit message.
import { useEffect, useState } from 'preact/hooks';
import type { Feature } from '../../core/data/modes';
import type { BattlePlan, BattleRequest } from '../state/actions';
import type { Gain } from '../state/types';
import type { Hero } from '../../core/types';

export type Tab = 'campaign' | 'heroes' | 'summon' | 'adventure' | 'guild';
export type Sub = Exclude<Feature, 'guild'> | null;

export type Modal =
  | { type: 'hero'; uid: number }
  | { type: 'gain'; title: string; gain: Gain; damage?: number; win?: boolean }
  | { type: 'summon'; heroes: Hero[] }
  | { type: 'quests' }
  | { type: 'shop'; tab?: 'offers' | 'pass' | 'exchange' }
  | { type: 'ranking' }
  | { type: 'chat' }
  | { type: 'settings' }
  | { type: 'odds' }
  | { type: 'confirm'; text: string; onYes: () => void }
  | { type: 'ad'; onDone: () => void }
  | { type: 'prep'; plan: BattlePlan | null }
  | { type: 'fastLoot' }
  | { type: 'rename' }
  | { type: 'fusion'; uid?: number }
  | { type: 'forge' }
  | { type: 'reset'; uid?: number }
  | { type: 'item'; uid: number }
  | { type: 'slot'; heroUid: number; slot: 'weapon' | 'armor' | 'helmet' | 'boots' }
  | { type: 'legal'; doc: 'privacy' | 'terms' | 'notice' | 'credits' | 'support' };

interface NavState {
  tab: Tab;
  sub: Sub;
  modals: Modal[];
  battle: BattleRequest | null;
  toast: string | null;
}

const nav: NavState = { tab: 'campaign', sub: null, modals: [], battle: null, toast: null };
const listeners = new Set<() => void>();
let version = 0;
let toastTimer: ReturnType<typeof setTimeout> | undefined;

function changed() {
  version += 1;
  for (const l of listeners) l();
}

export function useNav(): NavState {
  const [, setV] = useState(version);
  useEffect(() => {
    const l = () => setV(version);
    listeners.add(l);
    return () => void listeners.delete(l);
  }, []);
  return nav;
}

export function go(tab: Tab): void {
  nav.tab = tab;
  nav.sub = null;
  changed();
}

export function openSub(sub: Sub): void {
  nav.sub = sub;
  changed();
}

export function open(modal: Modal): void {
  nav.modals.push(modal);
  changed();
}

export function close(): void {
  nav.modals.pop();
  changed();
}

export function startBattle(req: BattleRequest | null): void {
  nav.battle = req;
  changed();
}

export function toast(text: string): void {
  nav.toast = text;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    nav.toast = null;
    changed();
  }, 1800);
  changed();
}

/** Ouvre l'écran de préparation d'un combat (ou de la section seule si `plan` est null). */
export function prepare(plan: BattlePlan | null): void {
  open({ type: 'prep', plan });
}
