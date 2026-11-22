# Adoucit un dessin de personnage pour qu'il se fonde dans le jeu (moins « dessin découpé et posé ») :
#   1. les petits détails et le grain sont lissés, sans toucher aux formes (filtre qui respecte les bords) ;
#   2. le trait noir prend la couleur de ce qu'il cerne, en plus sombre (trait brun autour de la peau, bordeaux autour
#      du rouge…) : c'est ce qui sépare un dessin de bande dessinée d'un personnage de jeu peint ;
#   3. un voile de lumière très léger arrondit les volumes ;
#   4. le bord de la silhouette est fondu sur un pixel.
# Appelé par decoupe-hailuo.py juste avant d'enregistrer chaque dessin. Essai sur des images déjà découpées :
#   python3 refonte-graphique/adoucir.py <entrée.webp> <sortie.png> [force]
import sys
import numpy as np
import cv2
from PIL import Image

def soften(img, k=1.0):
    """`img` : image PIL RGBA. `k` : force (1 = réglage du jeu, 0 = rien). Rend une image PIL RGBA de même taille."""
    a = np.array(img.convert('RGBA')).astype(np.float32)
    rgb, al = a[..., :3], a[..., 3] / 255.0
    solid = (al > 0.5)
    # Le liseré à demi transparent du bord (et le vide juste autour) prend la couleur du trait plein le plus proche :
    # les filtres ne ramènent ainsi ni noir ni clair par le bord. Les lueurs (loin du corps plein) gardent leur couleur.
    core = (al > 0.9).astype(np.uint8)
    hole = ((al <= 0.9) & (cv2.dilate(core, np.ones((9, 9), np.uint8)) > 0)).astype(np.uint8)
    work = cv2.inpaint(rgb.astype(np.uint8), hole, 3, cv2.INPAINT_TELEA) if hole.any() and core.any() else rgb.astype(np.uint8)
    # 1. le trait s'affine : une « fermeture » efface les traits fins (hachures, plis) et amincit les gros
    ker = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    # (le dehors est mis en noir pendant l'opération : le contour extérieur ne doit pas s'éclaircir par l'extérieur)
    thin = cv2.morphologyEx(work * solid[..., None].astype(np.uint8), cv2.MORPH_CLOSE, ker)
    work = np.where(solid[..., None], cv2.addWeighted(work, 1 - 0.75 * k, thin, 0.75 * k, 0), work)
    # 2. lissage qui respecte les bords : le grain et les petits détails se fondent, les formes restent nettes
    sm = work
    for _ in range(3):
        sm = cv2.bilateralFilter(sm, d=0, sigmaColor=30 * k + 1, sigmaSpace=3.6)
    sm = sm.astype(np.float32)
    # 3. le trait qui reste prend la couleur de ce qu'il cerne, en plus sombre (brun autour de la peau, bordeaux autour du rouge)
    mx, mn = sm.max(2), sm.min(2)
    line = np.clip((104 - mx) / 54, 0, 1) * np.clip(1 - (mx - mn) / 70, 0, 1)
    w = (1 - line) * solid                              # ce qui n'est pas du trait
    sig = 5.0
    num = cv2.GaussianBlur(sm * w[..., None], (0, 0), sig)
    den = cv2.GaussianBlur(w.astype(np.float32), (0, 0), sig)[..., None]
    near = num / np.maximum(den, 1e-3)                  # couleur du voisinage
    conf = np.clip(den[..., 0] * 3.0, 0, 1)             # au cœur d'une grande zone noire (cheveux, armure) : on ne touche pas
    lum = near.mean(2, keepdims=True)
    tint = np.clip(lum + (near - lum) * 1.45, 0, 255) * 0.44   # plus saturée, plus sombre
    mix = (line * conf * min(1.0, 0.95 * k))[..., None]
    out = sm * (1 - mix) + tint * mix
    # 4. les noirs ne sont plus tout à fait noirs (un noir pur fait « encre »), et un voile de lumière arrondit les volumes
    out = out + (np.array([26.0, 20.0, 30.0]) - out * 0.10) * 0.5 * k * np.clip(1 - out.max(2, keepdims=True) / 90, 0, 1)
    glow = cv2.GaussianBlur(out, (0, 0), 8)
    out = out + (255 - out) * (glow / 255.0) * 0.09 * k
    # 5. bord fondu : l'opacité est lissée sur un pixel, sans élargir la silhouette
    al2 = np.minimum(al, cv2.GaussianBlur(al, (0, 0), 1.1)) * k + al * (1 - k) if k <= 1 else np.minimum(al, cv2.GaussianBlur(al, (0, 0), 1.1))
    res = np.dstack([np.clip(out, 0, 255), np.clip(al2, 0, 1) * 255]).astype(np.uint8)
    return Image.fromarray(res, 'RGBA')

if __name__ == '__main__':
    k = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
    soften(Image.open(sys.argv[1]), k).save(sys.argv[2])
