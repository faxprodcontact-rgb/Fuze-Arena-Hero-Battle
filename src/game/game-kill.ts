// Arrêter un jeu Phaser en rendant vraiment sa mémoire graphique au téléphone (bug du 26/11 : le jeu plantait en
// changeant d'écran). Sur iPhone, un contexte WebGL abandonné n'est pas libéré tout de suite : après quelques combats ou
// retours à l'accueil, la page dépasse sa mémoire et Safari la recharge. On le perd donc exprès, juste après la fin.
import type Phaser from 'phaser';

export function killGame(game: Phaser.Game): void {
  const gl = (game.renderer as { gl?: WebGLRenderingContext } | null)?.gl;
  game.destroy(true);
  if (gl) setTimeout(() => gl.getExtension('WEBGL_lose_context')?.loseContext(), 300);
}

/**
 * Le combat de l'accueil dort quand on quitte l'accueil (idle-scene.ts) ; mais un autre combat qui démarre (campagne,
 * Colisée, aperçu d'une compétence) charge ses propres dessins : on libère alors vraiment celui de l'accueil, pour ne
 * jamais garder deux jeux en mémoire en même temps (plantage « Un problème récurrent est survenu » sur iPhone, 26/11).
 */
let idleRelease: (() => void) | undefined;
export function onIdleRelease(fn: (() => void) | undefined): void {
  idleRelease = fn;
}
export function releaseIdle(): void {
  idleRelease?.();
}
