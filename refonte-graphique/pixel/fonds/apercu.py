# L'aperçu d'un fond pour le propriétaire : le fond animé à la taille d'un écran de téléphone, avec des personnages HD
# en pose sur les places du combat (héros tournés vers la droite à gauche, ennemis retournés à droite), le bas de
# l'écran (le panneau bleu nuit et son rail d'or) pour situer le terrain.
#
# Les personnages viennent des planches du jeu (public/art/hd/<id>.webp et src/game/hd-meta.ts, en lecture seule) :
# l'animation « pose » de chacun, à sa vitesse. Un pixel du personnage = un pixel du fond (c'est la règle).
#
#   from apercu import apercu, zoom
#   apercu(fond, [('kael', 'heros', 2), ('golem-lave', 'ennemis', 1), …])
#     → refonte-graphique/pixel/sortie/fond-<clan>.gif (l'animation, une période complète) et fond-<clan>.png (fixe)
#   zoom(fond, (x0, y0, x1, y1), k, chemin)        → un morceau agrandi ×k (pour relire de près)
import os, json, math
import numpy as np
from PIL import Image, ImageDraw
import fondlib as F

HD_SCALE = None
_META = None
_SHEETS = {}
SORTIE = os.path.join(F.PIXEL, 'sortie')


def meta():
    global _META, HD_SCALE
    if _META is None:
        s = open(os.path.join(F.ROOT, 'src/game/hd-meta.ts')).read()
        i = s.find('export const HD_ANIM =') + len('export const HD_ANIM =')
        _META, _ = json.JSONDecoder().raw_decode(s[i:].lstrip())
        HD_SCALE = _META['scale']
    return _META


def id_of(name):
    """Le nom d'atelier (kael, golem-lave…) → l'identifiant du jeu (assassins-2, mon-kael-costaud…)."""
    for k, v in meta()['chars'].items():
        if v['name'] == name or k == name:
            return k
    raise KeyError(f'pas de personnage HD « {name} » dans hd-meta.ts')


def pose_frames(name):
    """Les images de la pose (PIL RGBA, taille réelle) avec leur décalage (ax, ay) depuis les pieds et leur durée."""
    m = meta()
    cid = id_of(name)
    if cid not in _SHEETS:
        _SHEETS[cid] = Image.open(os.path.join(F.ROOT, 'public/art/hd', cid + '.webp')).convert('RGBA')
    sh, c, up = _SHEETS[cid], m['chars'][cid], m['up']
    out = []
    a = c['anims']['pose']
    for fi, ms in zip(a['f'], a['ms']):
        r = c['frames'][fi]
        im = sh.crop((r[0] * up, r[1] * up, (r[0] + r[2]) * up, (r[1] + r[3]) * up)).resize((r[2], r[3]), Image.NEAREST)
        out.append((im, r[4], r[5], ms))
    return out, c


def poseur(persos):
    """Une fonction qui pose les combattants sur une image du fond à l'instant t (triés par rang : le fond d'abord)."""
    k = meta()['scale'] / F.UNIT                       # un pixel du dessin HD = k pixels du fond (≈ 1)
    actors = []
    for (name, side, slot) in persos:
        frames, c = pose_frames(name)
        fx, fy = F.place(side, slot)
        actors.append((fy, fx, side, frames, c))
    actors.sort(key=lambda a: a[0])

    def poser(im, t_ms):
        sh = Image.new('RGBA', im.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(sh)
        for (fy, fx, side, frames, c) in actors:
            # l'ombre du jeu : un ovale noir à 30 %, de la largeur des pieds
            w = min(160, (c['sol'][1] - c['sol'][0]) * meta()['scale'] * 1.1) / F.UNIT
            d.ellipse((fx - w / 2, fy - 8, fx + w / 2, fy + 8), fill=(0, 0, 0, 77))
        im.alpha_composite(sh)
        for (fy, fx, side, frames, c) in actors:
            total = sum(f[3] for f in frames)
            tt = t_ms % total
            for (fr, ax, ay, ms) in frames:
                if tt < ms:
                    break
                tt -= ms
            if abs(k - 1) > 0.01:
                fr = fr.resize((round(fr.width * k), round(fr.height * k)), Image.NEAREST)
            if side == 'heros':
                x, y = fx + ax, fy + ay
            else:
                fr = fr.transpose(Image.FLIP_LEFT_RIGHT)
                x, y = fx - ax - fr.width, fy + ay
            im.alpha_composite(fr, (int(x), int(y))) if x >= 0 and y >= 0 else im.paste(fr, (int(x), int(y)), fr)
    return poser


def ecran(im, telephone='moyen'):
    """Coupe l'image comme sur l'écran d'un téléphone et ajoute le haut du panneau du bas (bleu nuit, rail d'or)."""
    top = F.VISIBLE[telephone]
    body = im.crop((0, top, F.W, F.H))
    hud = 44
    out = Image.new('RGBA', (F.W, body.height + hud), (15, 21, 51, 255))
    out.alpha_composite(body, (0, 0))
    d = ImageDraw.Draw(out)
    y = body.height
    d.rectangle((0, y - 5, F.W, y + 3), fill=(217, 166, 62, 255))       # le rail d'or à cheval sur le bas du terrain
    d.rectangle((0, y - 5, F.W, y - 4), fill=(255, 226, 140, 255))
    d.rectangle((0, y + 2, F.W, y + 3), fill=(120, 80, 30, 255))
    return out


def apercu(fond, persos, telephone='moyen', pas_ms=100, nom=None, dossier=SORTIE):
    """Écrit sortie/fond-<clan>.gif (une période entière, sans couture) et sortie/fond-<clan>.png (l'instant 0).
    telephone = 'court' (16:9), 'moyen' (19,5:9) ou 'long' (21:9) : ce qu'on voit du haut de l'image."""
    nom = nom or f'fond-{fond.clan}'
    SORTIE_ = dossier
    poser = poseur(persos)
    n = fond.periode // pas_ms
    frames = [ecran(fond.instant(i * pas_ms, poser), telephone) for i in range(n)]
    frames[0].convert('RGB').save(os.path.join(SORTIE_, nom + '.png'))
    # une seule palette pour toutes les images (sinon les couleurs sautent d'une image à l'autre)
    sample = Image.new('RGB', (F.W, frames[0].height * 4))
    for k in range(4):
        sample.paste(frames[k * n // 4].convert('RGB'), (0, k * frames[0].height))
    pal = sample.quantize(255, method=Image.Quantize.MEDIANCUT)
    gif = [f.convert('RGB').quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
    path = os.path.join(SORTIE_, nom + '.gif')
    gif[0].save(path, save_all=True, append_images=gif[1:], duration=pas_ms, loop=0, optimize=False, disposal=1)
    print(f'  aperçu : {os.path.relpath(path, F.ROOT)} ({n} images, {os.path.getsize(path) // 1024} Ko) et .png')
    return frames


def zoom(fond, box, k, chemin, t_ms=0, persos=None):
    """Un morceau de l'image (à l'instant t) agrandi ×k, pour relire de près."""
    im = fond.instant(t_ms, poseur(persos) if persos else None)
    im.crop(box).resize(((box[2] - box[0]) * k, (box[3] - box[1]) * k), Image.NEAREST).save(chemin)
    return chemin


def bande(fond, id, chemin, k=3):
    """Toutes les images d'un calque « boucle » côte à côte (×k), pour vérifier la boucle image par image."""
    c = next(c for c in fond.calques if c['id'] == id)
    ims = [f.image() for f in c['frames']]
    w, h = ims[0].size
    out = Image.new('RGBA', ((w + 2) * len(ims), h), (40, 40, 48, 255))
    for i, im in enumerate(ims):
        out.alpha_composite(im, (i * (w + 2), 0))
    out.resize((out.width * k, out.height * k), Image.NEAREST).save(chemin)
    return chemin
