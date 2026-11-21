// Point d'entrée du jeu.
import { render } from 'preact';
import { App } from './ui/app';
import './ui/style.css';
import { watchUpdates } from './updater';

render(<App />, document.getElementById('game')!);
watchUpdates();

// l'écran de chargement s'efface une fois tout chargé (au moins un court instant, pour qu'on le voie)
const splash = document.getElementById('splash');
if (splash) {
  const start = performance.now();
  const hide = () => setTimeout(() => {
    splash.classList.add('done');
    setTimeout(() => { splash.classList.add('gone'); setTimeout(() => splash.remove(), 600); }, 300);
  }, Math.max(0, 1200 - (performance.now() - start)));
  if (document.readyState === 'complete') hide();
  else addEventListener('load', hide, { once: true });
}
