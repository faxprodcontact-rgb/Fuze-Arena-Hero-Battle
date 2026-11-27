// GÉNÉRÉ par refonte-graphique/ui-moderne/heros/repos.py --assemble : ne pas modifier à la main.
// Le signe du repos des héros dans les menus : pour chaque zone qui bouge, une bande de n images côte à côte
// (art/vecto/repos/<id>-<v>-<k>.webp, chaque image entourée d’une gouttière de g px), posée sur l’image où ces
// zones sont vidées (<id>-<v>-base.webp ; v change avec le contenu). zones = [x, y, largeur, hauteur] en pixels
// de l’image des menus (art/vecto/<id>.webp, taille = [largeur, hauteur]), elles peuvent déborder du cadre ;
// ms = la durée de la boucle.
export interface VectoRepos {
  n: number; ms: number; taille: readonly [number, number]; v: string; g: number;
  zones: readonly (readonly [number, number, number, number])[];
}
export const VECTO_REPOS: Record<string, VectoRepos> = {
  'angels-1': { n: 16, ms: 3000, taille: [535, 512], v: '28db2dad', g: 2, zones: [[5, 48, 198, 374], [389, 56, 142, 62], [405, 160, 94, 46]] },
  'angels-10': { n: 16, ms: 3000, taille: [553, 512], v: 'd0ea9dd0', g: 2, zones: [[266, 128, 94, 78]] },
  'angels-11': { n: 16, ms: 3000, taille: [542, 512], v: '486bb5ef', g: 2, zones: [[36, 8, 358, 246]] },
  'angels-2': { n: 16, ms: 3000, taille: [445, 512], v: '02fd1153', g: 2, zones: [[10, 0, 366, 214]] },
  'angels-6': { n: 16, ms: 3000, taille: [446, 512], v: '87ac197f', g: 2, zones: [[306, 136, 158, 166], [26, 272, 94, 134]] },
  'angels-7': { n: 16, ms: 3000, taille: [416, 512], v: '77fa602d', g: 2, zones: [[87, 24, 222, 222], [311, 264, 62, 134]] },
  'assassins-11': { n: 16, ms: 3000, taille: [382, 512], v: 'deb7a48d', g: 2, zones: [[236, 32, 118, 86], [-12, 120, 142, 166]] },
  'assassins-2': { n: 16, ms: 3000, taille: [558, 512], v: 'dfe0f5b2', g: 2, zones: [[113, -16, 350, 246], [-23, 360, 198, 118]] },
  'assassins-3': { n: 16, ms: 3000, taille: [591, 512], v: 'ae3d981b', g: 2, zones: [[12, 184, 150, 230]] },
  'assassins-5': { n: 16, ms: 3000, taille: [435, 512], v: '5a73f1f3', g: 2, zones: [[-4, 288, 142, 198]] },
  'assassins-7': { n: 16, ms: 3000, taille: [394, 512], v: '367db68b', g: 2, zones: [[-22, 192, 158, 286], [266, 224, 62, 126], [178, 424, 94, 54]] },
  'assassins-9': { n: 16, ms: 3000, taille: [411, 512], v: '38900b29', g: 2, zones: [[7, 120, 134, 158], [167, 288, 94, 102]] },
  'demons-12': { n: 16, ms: 3000, taille: [512, 512], v: 'de958942', g: 2, zones: [[352, 48, 150, 166]] },
  'demons-3': { n: 16, ms: 3000, taille: [558, 512], v: '448cf46d', g: 2, zones: [[105, 8, 126, 86]] },
  'demons-4': { n: 16, ms: 3000, taille: [542, 512], v: 'f1e6e2b6', g: 2, zones: [[84, 16, 150, 126]] },
  'demons-5': { n: 16, ms: 3000, taille: [538, 512], v: '5c0cbc9d', g: 2, zones: [[340, 104, 142, 142], [-4, 232, 230, 238], [332, 248, 78, 150]] },
  'demons-8': { n: 16, ms: 3000, taille: [418, 512], v: '190b4fd6', g: 2, zones: [[270, 152, 134, 174]] },
  'demons-9': { n: 16, ms: 3000, taille: [538, 512], v: 'b1acdc16', g: 2, zones: [[92, 8, 158, 94]] },
  'dragon-feu': { n: 16, ms: 3000, taille: [564, 512], v: '64ffee1b', g: 2, zones: [[96, 32, 230, 238], [448, 176, 110, 86]] },
  'dragon-terre': { n: 16, ms: 3000, taille: [418, 512], v: '906b2dfa', g: 2, zones: [[342, 272, 22, 22], [310, 344, 86, 70]] },
  'dragon-vent': { n: 16, ms: 3000, taille: [550, 512], v: '5f6d30c5', g: 2, zones: [[27, 176, 270, 174], [331, 344, 62, 70]] },
  'knights-1': { n: 16, ms: 3000, taille: [408, 512], v: '345a9398', g: 2, zones: [[56, 0, 222, 214], [248, 248, 94, 118]] },
  'knights-3': { n: 16, ms: 3000, taille: [456, 512], v: '4cecba2c', g: 2, zones: [[9, 40, 86, 110], [305, 136, 158, 166]] },
  'knights-5': { n: 16, ms: 3000, taille: [648, 512], v: '7c7eb67b', g: 2, zones: [[-4, 208, 230, 198]] },
  'knights-7': { n: 16, ms: 3000, taille: [469, 512], v: '1e6e038b', g: 2, zones: [[343, 0, 94, 110]] },
  'knights-8': { n: 16, ms: 3000, taille: [578, 512], v: 'b93c7a4b', g: 2, zones: [[70, -8, 126, 118]] },
  'knights-9': { n: 16, ms: 3000, taille: [436, 512], v: '535e5745', g: 2, zones: [[-4, 400, 126, 110]] },
  'mages-11': { n: 16, ms: 3000, taille: [551, 512], v: 'b2a04a66', g: 2, zones: [[218, 8, 150, 62]] },
  'mages-2': { n: 16, ms: 3000, taille: [431, 512], v: '90533a77', g: 2, zones: [[28, -8, 262, 174]] },
  'mages-3': { n: 16, ms: 3000, taille: [580, 512], v: 'b496b001', g: 2, zones: [[78, 8, 150, 110]] },
  'mages-4': { n: 16, ms: 3000, taille: [549, 512], v: 'ae301652', g: 2, zones: [[187, 184, 198, 118]] },
  'mages-7': { n: 16, ms: 3000, taille: [500, 512], v: '90143a3f', g: 2, zones: [[50, -8, 358, 254]] },
  'mages-8': { n: 16, ms: 3000, taille: [558, 512], v: '6b220d24', g: 2, zones: [[65, 8, 254, 182], [65, 240, 150, 158]] },
  'mon-arachne-tisseuse': { n: 16, ms: 3000, taille: [626, 512], v: 'a6b60c36', g: 2, zones: [[175, 56, 78, 94], [375, 64, 86, 62], [359, 320, 94, 150]] },
  'mon-barzul-tireur': { n: 16, ms: 3000, taille: [410, 512], v: 'b57322b2', g: 2, zones: [[-1, 144, 86, 206]] },
  'mon-eldra-rapide': { n: 16, ms: 3000, taille: [655, 512], v: 'e47fb056', g: 2, zones: [[-5, 24, 230, 302]] },
  'mon-eldra-sorts': { n: 16, ms: 3000, taille: [481, 512], v: '080468a8', g: 2, zones: [[325, 24, 158, 158]] },
  'mon-lenore-sorts': { n: 16, ms: 3000, taille: [448, 512], v: 'c8ba3255', g: 2, zones: [[354, 112, 70, 62], [154, 320, 78, 142]] },
  'mon-meduse-rapide': { n: 16, ms: 3000, taille: [570, 512], v: '67993568', g: 2, zones: [[127, 24, 246, 158]] },
  'mon-orin-rapide': { n: 16, ms: 3000, taille: [634, 512], v: '5eaf2d40', g: 2, zones: [[-2, 24, 206, 198]] },
  'mon-orin-sorts': { n: 16, ms: 3000, taille: [616, 512], v: '8bedae79', g: 2, zones: [[145, 32, 174, 318]] },
  'myths-10': { n: 16, ms: 3000, taille: [532, 512], v: '38bf2447', g: 2, zones: [[61, 256, 230, 198]] },
  'myths-3': { n: 16, ms: 3000, taille: [500, 512], v: 'd8c944a4', g: 2, zones: [[330, 264, 134, 54], [354, 392, 126, 54]] },
  'myths-4': { n: 16, ms: 3000, taille: [520, 512], v: '40bfcbd2', g: 2, zones: [[103, -8, 358, 246]] },
  'myths-6': { n: 16, ms: 3000, taille: [603, 512], v: '80b6bb3a', g: 2, zones: [[427, 32, 86, 174]] },
  'myths-7': { n: 16, ms: 3000, taille: [360, 512], v: 'fa3d572d', g: 2, zones: [[247, 144, 102, 118]] },
  'myths-9': { n: 16, ms: 3000, taille: [471, 512], v: '3a1bb7d6', g: 2, zones: [[118, 32, 62, 86], [206, 104, 142, 78]] },
};
