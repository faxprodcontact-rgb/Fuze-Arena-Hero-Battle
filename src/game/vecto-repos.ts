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
  'angels-11': { n: 16, ms: 3000, taille: [542, 512], zones: [[37, 5, 358, 246], [293, 333, 14, 14]] },
  'angels-2': { n: 16, ms: 3000, taille: [445, 512], zones: [[5, 5, 366, 206]] },
  'angels-6': { n: 16, ms: 3000, taille: [446, 512], zones: [[309, 133, 137, 166], [29, 269, 94, 134]] },
  'assassins-2': { n: 16, ms: 3000, taille: [558, 512], zones: [[109, 0, 358, 227], [0, 365, 179, 110]] },
  'assassins-5': { n: 16, ms: 3000, taille: [435, 512], zones: [[0, 293, 131, 190]] },
  'assassins-7': { n: 16, ms: 3000, taille: [394, 512], zones: [[0, 189, 139, 286], [269, 229, 62, 118], [181, 429, 94, 54]] },
  'assassins-9': { n: 16, ms: 3000, taille: [411, 512], zones: [[5, 117, 134, 158], [165, 293, 94, 94]] },
  'demons-12': { n: 16, ms: 3000, taille: [512, 512], zones: [[349, 45, 158, 166]] },
  'demons-3': { n: 16, ms: 3000, taille: [558, 512], zones: [[101, 5, 134, 94]] },
  'demons-4': { n: 16, ms: 3000, taille: [542, 512], zones: [[85, 21, 142, 118]] },
  'demons-5': { n: 16, ms: 3000, taille: [538, 512], zones: [[405, 101, 78, 78], [333, 189, 126, 206], [0, 229, 227, 238]] },
  'dragon-feu': { n: 16, ms: 3000, taille: [564, 512], zones: [[101, 29, 230, 238], [453, 173, 110, 86]] },
  'dragon-terre': { n: 16, ms: 3000, taille: [418, 512], zones: [[341, 277, 22, 14], [309, 349, 86, 62]] },
  'knights-1': { n: 16, ms: 3000, taille: [408, 512], zones: [[53, 0, 230, 211], [261, 269, 70, 86]] },
  'knights-3': { n: 16, ms: 3000, taille: [456, 512], zones: [[5, 45, 86, 110], [301, 133, 155, 166]] },
  'knights-8': { n: 16, ms: 3000, taille: [578, 512], zones: [[77, 0, 118, 115]] },
  'knights-9': { n: 16, ms: 3000, taille: [436, 512], zones: [[0, 397, 123, 110]] },
  'mages-11': { n: 16, ms: 3000, taille: [551, 512], zones: [[213, 5, 150, 62]] },
  'mages-2': { n: 16, ms: 3000, taille: [431, 512], zones: [[29, 0, 262, 163]] },
  'mages-3': { n: 16, ms: 3000, taille: [580, 512], zones: [[77, 13, 150, 102]] },
  'mages-7': { n: 16, ms: 3000, taille: [500, 512], zones: [[53, 0, 358, 243]] },
  'mages-8': { n: 16, ms: 3000, taille: [558, 512], zones: [[69, 5, 254, 182], [69, 237, 150, 166]] },
  'mon-arachne-tisseuse': { n: 16, ms: 3000, taille: [626, 512], zones: [[173, 53, 78, 102], [405, 85, 38, 38], [357, 325, 94, 142]] },
  'mon-barzul-tireur': { n: 16, ms: 3000, taille: [410, 512], zones: [[0, 141, 83, 214]] },
  'mon-eldra-rapide': { n: 16, ms: 3000, taille: [655, 512], zones: [[0, 21, 227, 302]] },
  'mon-eldra-sorts': { n: 16, ms: 3000, taille: [481, 512], zones: [[325, 21, 156, 158]] },
  'mon-lenore-sorts': { n: 16, ms: 3000, taille: [448, 512], zones: [[357, 109, 70, 62], [157, 317, 70, 142]] },
  'mon-orin-rapide': { n: 16, ms: 3000, taille: [634, 512], zones: [[0, 21, 203, 206]] },
  'myths-4': { n: 16, ms: 3000, taille: [520, 512], zones: [[101, 0, 358, 243]] },
  'myths-6': { n: 16, ms: 3000, taille: [603, 512], zones: [[429, 37, 86, 110], [453, 173, 30, 30]] },
  'myths-7': { n: 16, ms: 3000, taille: [360, 512], zones: [[245, 141, 102, 126]] },
};
