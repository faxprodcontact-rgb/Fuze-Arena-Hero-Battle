// La TAILLE des héros dans les menus où on les voit en grand (fiche, estrade, tirage, préparation) : demande du
// 27/11 (« ils n'ont pas une taille cohérente entre eux : une taille standard, adaptée à chaque personnage ; le
// pirate est tout petit, le nain trop grand »). Chaque dessin a sa propre échelle (celle du combat, qui ne change
// pas) : on ramène sa hauteur de corps (des pieds au haut du crâne, sans armes levées, ailes ni plumes ; mesurée sur
// le dessin et la boîte de tête de refonte-graphique/ui-moderne/heros/tetes.json) à une taille standard, multipliée
// par son GABARIT (1 = un humain ; un nain, un singe, un corbeau plus petits ; un cyclope, un minotaure, un dragon
// plus grands).

/** Hauteur du corps, en pixels du dessin (art/vecto/<id>.webp, mesures de vecto.ts). */
const BODY: Record<string, number> = {
  'angels-1': 104.3, // celia
  'angels-10': 101.0, // aurelle
  'angels-11': 95.3, // dardane
  'angels-2': 107.1, // ilian
  'angels-6': 108.8, // elvyn
  'angels-7': 110.7, // solenn
  'assassins-11': 90.0, // zephyre
  'assassins-2': 96.4, // kael
  'assassins-3': 103.9, // sable
  'assassins-5': 106.6, // rook
  'assassins-7': 99.4, // corvin
  'assassins-9': 105.6, // jarek
  'demons-12': 108.3, // nerith
  'demons-3': 105.0, // barzul
  'demons-4': 94.7, // lilou
  'demons-5': 115.0, // kesha
  'demons-8': 97.4, // zaroth
  'demons-9': 99.7, // velith
  'dragon-feu': 113.7, // brasyr
  'dragon-terre': 98.1, // rocvar
  'dragon-vent': 94.6, // venthys
  'knights-1': 96.0, // berold
  'knights-3': 97.0, // aldric
  'knights-5': 86.5, // tybalt
  'knights-7': 96.2, // ysolde
  'knights-8': 102.0, // garvin
  'knights-9': 99.8, // lenore
  'mages-11': 97.4, // myrr
  'mages-2': 91.3, // mira
  'mages-3': 107.0, // orin
  'mages-4': 98.7, // tessa
  'mages-7': 108.2, // arcan
  'mages-8': 100.7, // eldra
  'mon-arachne-tisseuse': 90.9, // nyrra
  'mon-barzul-tireur': 97.2, // jessa
  'mon-eldra-rapide': 63.6, // gribou
  'mon-eldra-sorts': 83.0, // bao
  'mon-lenore-sorts': 88.6, // oboro
  'mon-meduse-rapide': 77.7, // sarvik
  'mon-orin-rapide': 84.5, // karu
  'mon-orin-sorts': 94.0, // sorai
  'myths-10': 107.3, // soyane
  'myths-3': 113.2, // taurok
  'myths-4': 117.9, // ophira
  'myths-6': 105.7, // nefira
  'myths-7': 116.3, // malgrave
  'myths-9': 105.1, // sylvar
};

/** Le gabarit de chacun (1 par défaut) : sa taille par rapport à un humain. */
const GABARIT: Record<string, number> = {
  'angels-10': 1.15, // aurelle
  'angels-2': 1.08, // ilian
  'angels-6': 1.05, // elvyn
  'angels-7': 0.8, // solenn
  'assassins-11': 0.95, // zephyre
  'assassins-3': 1.05, // sable
  'assassins-7': 0.95, // corvin
  'demons-3': 1.05, // barzul
  'demons-4': 0.8, // lilou
  'demons-5': 1.1, // kesha
  'demons-9': 1.12, // velith
  'dragon-feu': 1.12, // brasyr
  'dragon-terre': 1.1, // rocvar
  'dragon-vent': 1.05, // venthys
  'knights-5': 0.95, // tybalt
  'knights-8': 1.15, // garvin
  'knights-9': 1.05, // lenore
  'mages-2': 0.95, // mira
  'mages-3': 1.05, // orin
  'mages-7': 1.1, // arcan
  'mon-arachne-tisseuse': 0.9, // nyrra
  'mon-barzul-tireur': 0.9, // jessa
  'mon-eldra-rapide': 0.62, // gribou
  'mon-eldra-sorts': 0.8, // bao
  'mon-meduse-rapide': 0.85, // sarvik
  'mon-orin-rapide': 0.85, // karu
  'mon-orin-sorts': 0.95, // sorai
  'myths-3': 1.18, // taurok
  'myths-4': 1.05, // ophira
};

/** Le facteur d'échelle d'un dessin pour qu'un humain mesure 100 pixels du dessin (× son gabarit). */
export function sizeK(art: string): number {
  return (100 * (GABARIT[art] ?? 1)) / (BODY[art] ?? 100);
}
