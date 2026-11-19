// Point d'entrée du prototype.
import Phaser from 'phaser';
import { UI } from './art';
import { BattleScene } from './scenes/BattleScene';
import { BootScene } from './scenes/BootScene';
import { HomeScene } from './scenes/HomeScene';
import { TeamScene } from './scenes/TeamScene';
import { H, W } from './ui';

new Phaser.Game({
  type: Phaser.AUTO,
  parent: 'game',
  width: W,
  height: H,
  backgroundColor: UI.bg,
  scale: { mode: Phaser.Scale.FIT, autoCenter: Phaser.Scale.CENTER_BOTH },
  scene: [BootScene, HomeScene, TeamScene, BattleScene],
});
