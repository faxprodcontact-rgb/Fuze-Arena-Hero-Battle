// Arrêter un jeu Phaser en rendant vraiment sa mémoire graphique au téléphone (bug du 26/11 : le jeu plantait en
// changeant d'écran). Sur iPhone, un contexte WebGL abandonné n'est pas libéré tout de suite : après quelques combats ou
// retours à l'accueil, la page dépasse sa mémoire et Safari la recharge. On le perd donc exprès, juste après la fin.
import type Phaser from 'phaser';

export function killGame(game: Phaser.Game): void {
  const gl = (game.renderer as { gl?: WebGLRenderingContext } | null)?.gl;
  game.destroy(true);
  if (gl) setTimeout(() => gl.getExtension('WEBGL_lose_context')?.loseContext(), 300);
}
