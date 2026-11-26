// Point d'entrée du jeu.
import { render } from 'preact';
// le style commun d'abord : les fichiers des sections (ui/sections/*.css, importés par leurs écrans) passent après lui
import './ui/style.css';
import { App } from './ui/app';
// l'essai d'habillage « pierre » (?theme=pierre, ui/theme.ts) : après tous les CSS, pour gagner à priorité égale
import './ui/theme-pierre.css';
import './ui/theme-pierre-or.css';
import { installButtons } from './ui/buttons';
import { installSigns } from './ui/px';
import { installSkin } from './ui/skin';
import { installTheme } from './ui/theme';
import { watchUpdates } from './updater';
import { artUrl } from './art-url';
import { startDiag } from './diag';

// l'habillage de l'interface (style moderne, skin.ts), les petits signes (signs-art.ts) et les boutons de pierre
// (buttons.ts), posés avant le premier dessin
startDiag();
installSkin();
installTheme();
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
  icons.src = artUrl('art/icons.webp');
  setTimeout(hide, 6000);
}
