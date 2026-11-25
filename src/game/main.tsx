// Point d'entrée du jeu.
import { render } from 'preact';
import { App } from './ui/app';
import './ui/style.css';
import { installPx } from './ui/px';
import { watchUpdates } from './updater';

// les pièces dessinées de l'interface (px.ts) : posées dans le CSS avant le premier dessin
installPx();
render(<App />, document.getElementById('game')!);
watchUpdates();

// L'écran de chargement s'efface dès que les menus peuvent s'afficher proprement : la planche de pictos est arrivée
// (ou 6 s ont passé). On n'attend pas que tout le reste soit téléchargé.
const splash = document.getElementById('splash');
if (splash) {
  const start = performance.now();
  let hidden = false;
  const hide = () => {
    if (hidden) return;
    hidden = true;
    setTimeout(() => {
      splash.classList.add('done');
      setTimeout(() => { splash.classList.add('gone'); setTimeout(() => splash.remove(), 600); }, 250);
    }, Math.max(0, 400 - (performance.now() - start)));
  };
  const icons = new Image();
  icons.onload = icons.onerror = hide;
  icons.src = 'art/icons.webp';
  setTimeout(hide, 6000);
}
