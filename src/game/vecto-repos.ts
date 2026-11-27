// GÉNÉRÉ par refonte-graphique/ui-moderne/heros/repos.py --assemble : ne pas modifier à la main.
// Le signe du repos des héros dans les menus : pour chaque zone qui bouge, une bande de n images côte à côte
// (art/vecto/repos/<id>-<k>.webp), posée sur l’image où ces zones sont vidées (<id>-base.webp).
// zones = [x, y, largeur, hauteur] en pixels de l’image des menus (art/vecto/<id>.webp, taille = [largeur,
// hauteur]) ; ms = la durée de la boucle.
export interface VectoRepos {
  n: number; ms: number; taille: readonly [number, number];
  zones: readonly (readonly [number, number, number, number])[];
}
export const VECTO_REPOS: Record<string, VectoRepos> = {
  'assassins-2': { n: 16, ms: 3000, taille: [558, 512], zones: [[109, 0, 358, 227], [0, 365, 179, 110]] },
};
