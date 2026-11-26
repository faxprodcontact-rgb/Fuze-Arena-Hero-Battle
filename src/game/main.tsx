// Point d'entrée du jeu.
import { render } from 'preact';
// le style commun d'abord : les fichiers des sections (ui/sections/*.css, importés par leurs écrans) passent après lui
import './ui/style.css';
import { App } from './ui/app';
import { installButtons } from './ui/buttons';
import { installSigns } from './ui/px';
import { installSkin } from './ui/skin';
import { watchUpdates } from './updater';

// l'habillage de l'interface (style moderne, skin.ts), les petits signes (signs-art.ts) et les boutons de pierre
// (buttons.ts), posés avant le premier dessin
installSkin();
installSigns();
installButtons();
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
