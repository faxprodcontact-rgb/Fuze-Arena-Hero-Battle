// Tutoriel des premières minutes : une main montre où toucher, sans texte. Toucher l'endroit montré passe à l'étape suivante.
// Les étapes : premier combat, coffre de butin, invocation, monter un héros, régler la section.
import { useEffect, useState } from 'preact/hooks';
import { setTutorial } from '../state/actions';
import { useGame } from '../state/store';
import { Art } from './kit';

/** Ce qu'il faut toucher à chaque étape (sélecteur CSS de l'élément). */
export const TUTORIAL_STEPS: string[] = [
  '.dock-fight', // combattre
  '.prep .btn-fight', // lancer le combat
  '.modal .btn-green', // fin du combat
  '.dock-chest', // coffre de butin
  '.modal .btn-green',
  '.tabbar-btn:nth-child(3)', // invoquer
  '.tuto-summon10',
  '.reveal-ok', // fin du tirage
  '.tabbar-btn:nth-child(2)', // héros
  '.grid .hcard',
  '.tuto-levelup',
  '.modal .x',
  '.team-strip', // section
  '.prep .prep-bar .btn',
  '.prep .prep-head .x',
];

function visible(el: Element | null): el is HTMLElement {
  if (!el) return false;
  const r = el.getBoundingClientRect();
  // (un bouton encore caché par son animation d'arrivée, comme OK à la fin du tirage, n'est pas encore montré)
  return r.width > 0 && r.height > 0 && getComputedStyle(el).visibility !== 'hidden';
}

export function TutorialHand() {
  const s = useGame();
  const step = s.tutorial ?? -1;
  const active = s.named && step >= 0 && step < TUTORIAL_STEPS.length;
  const [rect, setRect] = useState<DOMRect | null>(null);

  // Suit la position de l'élément à montrer (il peut apparaître plus tard, ou bouger).
  useEffect(() => {
    if (!active) return;
    const sel = TUTORIAL_STEPS[step]!;
    const tick = () => {
      const el = [...document.querySelectorAll(sel)].find(visible);
      setRect(el ? el.getBoundingClientRect() : null);
    };
    tick();
    const id = setInterval(tick, 250);
    // Toucher l'élément montré = étape suivante (après que le jeu a traité le toucher).
    const onClick = (e: Event) => {
      const target = e.target as Element | null;
      if (target?.closest(sel)) setTimeout(() => setTutorial(step + 1 >= TUTORIAL_STEPS.length ? -1 : step + 1), 0);
    };
    document.addEventListener('click', onClick, true);
    return () => {
      clearInterval(id);
      document.removeEventListener('click', onClick, true);
    };
  }, [active, step]);

  if (!active) return null;
  return (
    <>
      {rect && (
        <div class="tuto-ring" style={{ left: `${rect.left - 6}px`, top: `${rect.top - 6}px`, width: `${rect.width + 12}px`, height: `${rect.height + 12}px` }}>
          <span class="tuto-hand" style={{ left: `${rect.width / 2 + 6}px`, top: `${rect.height / 2 + 6}px` }}>👆</span>
        </div>
      )}
      {/* le hibou guide : il montre l'endroit à toucher (il lève l'aile au premier pas) */}
      <Art class={`tuto-owl${rect && rect.left + rect.width / 2 < innerWidth / 2 ? ' tuto-owl-right' : ''}`} name={`owl-${step === 0 ? 'explain' : rect ? 'point' : 'happy'}`} />
      <button class="tuto-skip" aria-label="skip" onClick={() => setTutorial(-1)}>»</button>
    </>
  );
}
