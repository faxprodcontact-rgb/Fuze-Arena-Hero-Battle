// Les scènes de combat (et Phaser avec elles : les deux tiers du code) ne sont téléchargées qu'au moment où la première
// scène démarre. Les menus s'affichent sans les attendre : au premier lancement, l'écran arrive plus vite.
import type { Slot } from '../core/battle/types';

type Stop = () => void;

/** La police des combats est-elle arrivée ? (Phaser écrit ses textes une fois pour toutes : il faut l'attendre, 1,5 s au plus.) */
let font: Promise<unknown> | undefined;
function fontReady(): Promise<unknown> {
  font ??= Promise.race([
    document.fonts?.load('20px "Lilita One"').catch(() => undefined) ?? Promise.resolve(),
    new Promise((ok) => setTimeout(ok, 1500)),
  ]);
  return font;
}

/** Lance une scène dès que son code est arrivé ; si on l'a arrêtée entre-temps, elle ne démarre pas. */
function defer(load: () => Promise<() => Stop>): Stop {
  let stop: Stop | undefined;
  let cancelled = false;
  void Promise.all([load(), fontReady()]).then(([run]) => { if (!cancelled) stop = run(); });
  return () => { cancelled = true; stop?.(); };
}

export const runIdle: typeof import('./idle-scene').runIdle = (...a) => defer(() => import('./idle-scene').then((m) => () => m.runIdle(...a)));
export const runBattle: typeof import('./battle-scene').runBattle = (...a) => defer(() => import('./battle-scene').then((m) => () => m.runBattle(...a)));
export const runSkillPreview: typeof import('./skill-scene').runSkillPreview = (...a) => defer(() => import('./skill-scene').then((m) => () => m.runSkillPreview(...a)));

/** Place des héros sur le terrain (en X, par emplacement) : sert au combat et à l'écran de préparation. */
export const HERO_X: Record<Slot, number> = { 3: 82, 4: 82, 2: 163, 0: 245, 1: 245 };
