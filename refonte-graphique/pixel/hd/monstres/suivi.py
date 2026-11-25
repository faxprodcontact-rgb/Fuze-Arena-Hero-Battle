# Page de suivi des MONSTRES HD (pour le propriétaire) : 8 clans (chef = un héros HD) de 3 monstres.
# python3 refonte-graphique/pixel/hd/monstres/suivi.py → refonte-graphique/pixel/hd/sortie/suivi-monstres.html
# (+ sortie/anim-monstres/<nom>.gif quand le monstre est animé, à publier avec la page)
import os, sys, io, base64, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
HD = os.path.dirname(HERE)
sys.path.insert(0, HD)
import hd
from PIL import Image

# (clan = héros chef, élément, [(fichier, nom affiché, rôle, ce que c'est)])
ROSTER = [
    ('arachne', 'terre', [('araignee-bondissante', 'Araignée bondissante', 'rapide', 'petite araignée sauteuse'),
                          ('araignee-cuirassee', 'Araignée cuirassée', 'costaud', 'grosse araignée à carapace de pierre'),
                          ('araignee-tisseuse', 'Araignée tisseuse', 'tireur', 'crache de la toile')]),
    ('meduse', 'terre', [('serpent-guerrier', 'Serpent guerrier', 'rapide', 'homme-serpent à lames'),
                         ('naga-bouclier', 'Naga au bouclier', 'costaud', 'grand naga cuirassé'),
                         ('pretresse-serpent', 'Prêtresse serpent', 'sorts', 'pétrifie')]),
    ('kesha', 'eau', [('homme-poisson', 'Homme-poisson', 'rapide', 'guerrier des abysses à lance'),
                      ('crabe-geant', 'Crabe géant', 'costaud', 'énorme crabe cuirassé'),
                      ('meduse-eclair', 'Méduse éclair', 'sorts', 'lance des éclairs d\'eau')]),
    ('barzul', 'eau', [('matelot', 'Matelot', 'rapide', 'pirate au sabre'),
                       ('canonnier', 'Canonnier', 'costaud', 'gros pirate au canon'),
                       ('tireur-pirate', 'Tireur pirate', 'tireur', 'mousquet et perroquet')]),
    ('lenore', 'feu', [('diablotin', 'Diablotin', 'rapide', 'petit oni bondissant'),
                       ('oni-brute', 'Oni brute', 'costaud', 'grand oni à massue'),
                       ('sorcier-oni', 'Sorcier oni', 'sorts', 'feux follets')]),
    ('kael', 'feu', [('lutin-magma', 'Lutin de magma', 'rapide', 'petite créature de lave'),
                     ('golem-lave', 'Golem de lave', 'costaud', 'colosse de roche en fusion'),
                     ('salamandre', 'Salamandre', 'tireur', 'crache du feu')]),
    ('orin', 'vent', [('corbeau-tengu', 'Corbeau tengu', 'rapide', 'tengu corbeau agile'),
                      ('moine-tengu', 'Moine tengu', 'costaud', 'tengu massif au bâton'),
                      ('tengu-eventail', 'Tengu à l\'éventail', 'sorts', 'souffle des bourrasques')]),
    ('eldra', 'vent', [('singe-voleur', 'Singe voleur', 'rapide', 'petit singe agile'),
                       ('gorille-guerrier', 'Gorille guerrier', 'costaud', 'grand gorille cuirassé'),
                       ('singe-chaman', 'Singe chaman', 'sorts', 'bâton de nuages')]),
]
CHEFS = {'arachne': 'Arachné', 'meduse': 'Méduse', 'kesha': 'Kesha', 'barzul': 'Barzul', 'lenore': 'Lenore',
         'kael': 'Kael', 'orin': 'Orin', 'eldra': 'Eldra'}
VALIDES = set()
RETOUCHES = {}
FAITES = set()
# dessins finis par leur artiste (les autres fichiers sont encore en cours de dessin)
FINIS = {'araignee-bondissante', 'araignee-cuirassee', 'araignee-tisseuse'}
ELEMENTS = [('eau', 'Eau'), ('terre', 'Terre'), ('feu', 'Feu'), ('vent', 'Vent')]
LABEL = {'valide': 'Validé', 'retouche': 'Retouche en cours', 'aregarder': 'À regarder', 'encours': 'En cours', 'afaire': 'À faire'}
ANIMDIR = os.path.join(HD, 'sortie', 'anim-monstres')


def uri(im):
    b = io.BytesIO()
    im.save(b, 'PNG', optimize=True)
    return 'data:image/png;base64,' + base64.b64encode(b.getvalue()).decode()


def path(nom):
    return os.path.join(HERE, nom + '.txt')


def state(nom):
    if nom in VALIDES:
        return 'valide'
    if nom in FAITES:
        return 'aregarder'
    if nom in RETOUCHES:
        return 'retouche'
    if nom in FINIS:
        return 'aregarder'
    return 'encours' if os.path.exists(path(nom)) else 'afaire'


def clip(nom):
    """L'enchaînement animé (sortie/anim-<nom>-jeu.gif, ×2) ramené à ×1 : sortie/anim-monstres/<nom>.gif."""
    src = os.path.join(HD, '..', 'sortie', f'anim-{nom}-jeu.gif')
    if not os.path.exists(src):
        return None
    os.makedirs(ANIMDIR, exist_ok=True)
    dst = os.path.join(ANIMDIR, nom + '.gif')
    if not os.path.exists(dst) or os.path.getmtime(dst) < os.path.getmtime(src):
        g = Image.open(src)
        frames, durs = [], []
        for i in range(g.n_frames):
            g.seek(i)
            f = g.convert('RGB')
            frames.append(f.resize((f.width // 2, f.height // 2), Image.NEAREST).quantize(256, dither=Image.Dither.NONE))
            durs.append(g.info.get('duration', 100))
        frames[0].save(dst, save_all=True, append_images=frames[1:], duration=durs, loop=0, optimize=True)
    return 'anim-monstres/' + nom + '.gif'


def card(m):
    nom, name, role, what = m
    st = state(nom)
    c = clip(nom) if st not in ('afaire', 'encours') else None
    if c:
        pic = f'<img src="{c}" loading="lazy" alt="{name} animé">'
        cls = 'card anim ' + st
    elif st in ('afaire', 'encours'):
        pic, cls = '<div class="empty">' + ('En cours de dessin' if st == 'encours' else 'À dessiner') + '</div>', 'card afaire'
    else:
        pic, cls = f'<img src="{uri(hd.frames(path(nom))[0])}" alt="{name}">', 'card ' + st
    note = f'<p class="note">{RETOUCHES[nom]}</p>' if nom in RETOUCHES and st == 'retouche' else ''
    return f'''<article class="{cls}">
  <div class="pic">{pic}</div>
  <div class="txt">
    <div class="row"><h3>{name}</h3><span class="pill {st}">{LABEL[st]}</span></div>
    <p class="meta">{role} · {what}</p>{note}
  </div>
</article>'''


def main():
    allm = [m for _, _, ms in ROSTER for m in ms]
    counts = {k: sum(1 for m in allm if state(m[0]) == k) for k in LABEL}
    done = len(allm) - counts['afaire'] - counts['encours']
    secs = []
    for key, title in ELEMENTS:
        clans = [r for r in ROSTER if r[1] == key]
        body = ''
        for chef, _, ms in clans:
            face = hd.frames(chef)[0]
            body += (f'<div class="clan"><h3><img src="{uri(face)}" alt="">Clan de {CHEFS[chef]} <small>chef : {CHEFS[chef]} (boss)</small></h3>'
                     f'<div class="trio">{"".join(card(m) for m in ms)}</div></div>')
        n = sum(1 for _, _, ms in clans for m in ms if state(m[0]) not in ('afaire', 'encours'))
        secs.append(f'<section class="el {key}"><header><h2>{title}</h2><span class="count">{n} / {3 * len(clans)} dessinés</span></header>'
                    f'<div class="clans">{body}</div></section>')
    html = open(os.path.join(HERE, 'suivi-modele.html'), encoding='utf-8').read()
    html = (html.replace('{{DATE}}', datetime.date.today().strftime('%d/%m/%Y')).replace('{{DONE}}', str(done))
            .replace('{{TOTAL}}', str(len(allm))).replace('{{VALIDE}}', str(counts['valide']))
            .replace('{{RETOUCHE}}', str(counts['retouche'])).replace('{{AREGARDER}}', str(counts['aregarder']))
            .replace('{{AFAIRE}}', str(counts['afaire'] + counts['encours'])).replace('{{PCT}}', str(round(100 * done / len(allm))))
            .replace('{{SECTIONS}}', '\n'.join(secs)))
    out = os.path.join(HD, 'sortie', 'suivi-monstres.html')
    open(out, 'w', encoding='utf-8').write(html)
    print(out, counts)


if __name__ == '__main__':
    main()
