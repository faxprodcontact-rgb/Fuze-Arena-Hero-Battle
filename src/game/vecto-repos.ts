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
  'angels-1': { n: 16, ms: 3000, taille: [535, 512], zones: [[5, 53, 198, 374], [389, 61, 142, 54], [405, 157, 94, 46]] },
  'angels-10': { n: 16, ms: 3000, taille: [553, 512], zones: [[277, 133, 78, 62]] },
  'assassins-2': { n: 16, ms: 3000, taille: [558, 512], zones: [[109, 0, 358, 227], [0, 365, 179, 110]] },
  'demons-3': { n: 16, ms: 3000, taille: [558, 512], zones: [[101, 5, 134, 94]] },
  'dragon-feu': { n: 16, ms: 3000, taille: [564, 512], zones: [[101, 29, 230, 238], [453, 173, 110, 86]] },
  'knights-1': { n: 16, ms: 3000, taille: [408, 512], zones: [[53, 0, 230, 211], [261, 269, 70, 86]] },
  'knights-3': { n: 16, ms: 3000, taille: [456, 512], zones: [[5, 45, 86, 110], [301, 133, 155, 166]] },
  'mages-7': { n: 16, ms: 3000, taille: [500, 512], zones: [[53, 0, 358, 243]] },
  'mon-eldra-sorts': { n: 16, ms: 3000, taille: [481, 512], zones: [[325, 21, 156, 158]] },
};
