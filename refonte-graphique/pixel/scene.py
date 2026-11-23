# Une scène de combat fixe (pour l'aperçu) : le fond, 5 héros à gauche (tournés vers la droite), 5 monstres à droite
# (retournés pour regarder les héros). Les places reprennent celles du combat du jeu (fight-view.ts), divisées par 3.
# python3 scene.py sortie.png [image]
import sys, os, importlib
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, 'persos'))
from PIL import Image
from pix import Canvas
import fond

HEROES = [('kael', 0), ('sable', 1), ('eldra', 2), ('rook', 3), ('ilian', 4)]
MONSTERS = [('renard', 0), ('dino', 1), ('follet', 2), ('petard', 3), ('chouette', 4)]
# les places : x du milieu, y des pieds (le jeu : HERO_X, ENEMY_X, ROW_DY sous le haut du sol, pieds 47 plus bas, ÷ 3)
HERO_X = {3: 27, 4: 27, 2: 54, 0: 82, 1: 82}
ENEMY_X = {0: 158, 1: 158, 2: 186, 3: 213, 4: 213}
FEET = {0: 290, 3: 290, 2: 320, 1: 350, 4: 350}


def sprite(pid, t):
    c = Canvas()
    importlib.import_module(pid).draw(c, t)
    c.outline()
    return c.image()


def compose(t=0):
    bg = fond.draw().convert('RGBA')
    units = [(FEET[s], HERO_X[s], pid, False) for pid, s in HEROES] + [(FEET[s], ENEMY_X[s], pid, True) for pid, s in MONSTERS]
    for feet, x, pid, flip in sorted(units):
        im = sprite(pid, t)
        if flip:
            im = im.transpose(Image.FLIP_LEFT_RIGHT)
        # l'ombre douce au sol
        sh = Image.new('RGBA', (40, 8), (0, 0, 0, 0))
        from PIL import ImageDraw
        ImageDraw.Draw(sh).ellipse((0, 0, 39, 7), fill=(20, 40, 16, 110))
        bg.alpha_composite(sh, (x - 20, feet - 5))
        bg.alpha_composite(im, (x - 48, feet - 94))
    return bg


if __name__ == '__main__':
    out = sys.argv[1]
    t = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    im = compose(t)
    im.resize((im.width * 2, im.height * 2), Image.NEAREST).save(out)
    print(out, im.size)
