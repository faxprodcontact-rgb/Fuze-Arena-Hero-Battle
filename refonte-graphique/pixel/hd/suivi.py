# Page de suivi des héros HD (pour le propriétaire) : les 36 héros choisis, leur état, le dernier dessin.
# python3 refonte-graphique/pixel/hd/suivi.py  → refonte-graphique/pixel/hd/sortie/suivi.html (publiée sur claude.ai)
import os, sys, io, base64, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, HERE)
import hd
from PIL import Image

# (fichier hd, id du jeu, nom, élément, rôle, rareté, ce que c'est)
ROSTER = [
    ('berold', 'knights-1', 'Bérold', 'feu', 'protecteur', 'commun', 'hoplite'),
    ('aldric', 'knights-3', 'Aldric', 'feu', 'tireur', 'commun', 'moine du feu'),
    ('tybalt', 'knights-5', 'Tybalt', 'feu', 'assassin', 'rare', 'salamandre'),
    ('ysolde', 'knights-7', 'Ysolde', 'feu', 'soutien', 'rare', 'danseuse du feu'),
    ('garvin', 'knights-8', 'Garvin', 'feu', 'protecteur', 'épique', 'golem de lave'),
    ('lenore', 'knights-9', 'Lenore', 'feu', 'guerrier', 'épique', 'oni rouge'),
    ('kael', 'assassins-2', 'Kael', 'feu', 'guerrier', 'légendaire', 'guerrier de lave'),
    ('sable', 'assassins-3', 'Sable', 'feu', 'tireur', 'légendaire', 'déesse lionne'),
    ('rook', 'assassins-5', 'Rook', 'feu', 'soigneur', 'légendaire', 'harpie-phénix'),
    ('corvin', 'assassins-7', 'Corvin', 'vent', 'protecteur', 'commun', 'elfe des bois'),
    ('jinn', 'assassins-9', 'Jinn', 'vent', 'tireur', 'commun', 'archer des steppes'),
    ('zephyre', 'assassins-11', 'Zéphyre', 'vent', 'assassin', 'rare', 'ninja'),
    ('mira', 'mages-2', 'Mira', 'vent', 'protecteur', 'épique', 'valkyrie'),
    ('tessa', 'mages-4', 'Tessa', 'vent', 'tireur', 'épique', 'tête d\'aigle'),
    ('orin', 'mages-3', 'Orin', 'vent', 'guerrier', 'épique', 'tengu'),
    ('arcan', 'mages-7', 'Arcan', 'vent', 'soutien', 'épique', 'ogre au sac à vent'),
    ('eldra', 'mages-8', 'Eldra', 'vent', 'guerrier', 'légendaire', 'guerrière-singe'),
    ('myrr', 'mages-11', 'Myrr', 'vent', 'soigneur', 'légendaire', 'ange'),
    ('barzul', 'demons-3', 'Barzul', 'eau', 'tireur', 'commun', 'capitaine pirate'),
    ('lilou', 'demons-4', 'Lilou', 'eau', 'protecteur', 'rare', 'tortue boxeuse'),
    ('kesha', 'demons-5', 'Kesha', 'eau', 'assassin', 'rare', 'homme-requin'),
    ('zaroth', 'demons-8', 'Zaroth', 'eau', 'protecteur', 'épique', 'samouraï masqué'),
    ('velith', 'demons-9', 'Velith', 'eau', 'guerrier', 'épique', 'yéti'),
    ('nerith', 'demons-12', 'Nerith', 'eau', 'soigneur', 'épique', 'impératrice'),
    ('celia', 'angels-1', 'Célia', 'eau', 'soutien', 'épique', 'dame des neiges'),
    ('ilian', 'angels-2', 'Ilian', 'eau', 'guerrier', 'légendaire', 'roi des mers'),
    ('elyon', 'angels-6', 'Elyon', 'eau', 'soutien', 'légendaire', 'dragon des eaux'),
    ('solenn', 'angels-7', 'Solenn', 'terre', 'protecteur', 'commun', 'nain'),
    ('auriel', 'angels-10', 'Auriel', 'terre', 'protecteur', 'rare', 'cyclope'),
    ('gabryel', 'angels-11', 'Gabryel', 'terre', 'assassin', 'rare', 'homme-scorpion'),
    ('cyclope', 'myths-3', 'Astérion', 'terre', 'guerrier', 'épique', 'minotaure'),
    ('meduse', 'myths-4', 'Méduse', 'terre', 'tireur', 'épique', 'gorgone'),
    ('anubis', 'myths-7', 'Anubis', 'terre', 'soutien', 'épique', 'baron vaudou'),
    ('minotaure', 'myths-6', 'Minotaure', 'terre', 'soigneur', 'épique', 'reine du Nil ailée'),
    ('arachne', 'myths-10', 'Arachné', 'terre', 'assassin', 'légendaire', 'femme-araignée'),
    ('isis', 'myths-9', 'Isis', 'terre', 'tireur', 'légendaire', 'chasseur au crâne de cerf'),
]
VALIDES = {'berold', 'aldric', 'elyon', 'ilian', 'gabryel', 'meduse', 'barzul', 'arachne', 'kesha', 'celia', 'solenn', 'anubis', 'isis', 'kael', 'sable', 'tybalt', 'auriel', 'cyclope', 'zaroth', 'lilou'}
# héros dessinés dont les retours du propriétaire sont en train d'être faits : le retour demandé
RETOUCHES = {
    'lenore': "Manche de la massue bien droit, dans la continuité de la massue, qui ressort de la main.",
    'garvin': "Poings retravaillés (pouces repliés sous les doigts), un peu plus de lave, plus de détails sur la tête.",
    'velith': "Coude trop près de la main (effet poignet cassé) : éloigner la pliure du coude.",
    'nerith': "Refaire le nez.",
    'minotaure': "Petit trou à boucher.",
    'rook': "Transition du visage aux plumes moins sèche ; visage plus féminin et plus beau.",
    'ysolde': "Nez moins brouillon.",
}
# retouches faites, en attente du regard du propriétaire
FAITES = {'lenore', 'garvin', 'nerith', 'ysolde', 'rook', 'velith', 'minotaure'}
ELEMENTS = [('eau', 'Eau'), ('terre', 'Terre'), ('feu', 'Feu'), ('vent', 'Vent')]


def uri(im):
    b = io.BytesIO()
    im.save(b, 'PNG', optimize=True)
    return 'data:image/png;base64,' + base64.b64encode(b.getvalue()).decode()


def old_frame(cid):
    sheet = Image.open(os.path.join(ROOT, 'public', 'art', 'px', f'{cid}.webp')).convert('RGBA')
    cw = sheet.width // 8
    cell = sheet.crop((0, 0, cw, sheet.height))
    return cell.resize((cw // 3, sheet.height // 3), Image.NEAREST)


def state(pid):
    if pid in VALIDES:
        return 'valide'
    if pid in FAITES:
        return 'aregarder'
    if pid in RETOUCHES:
        return 'retouche'
    return 'afaire' if not os.path.exists(os.path.join(HERE, pid + '.txt')) else 'aregarder'


LABEL = {'valide': 'Validé', 'retouche': 'Retouche en cours', 'aregarder': 'À regarder', 'afaire': 'À faire'}


def card(r):
    pid, cid, name, el, role, rar, what = r
    st = state(pid)
    if st == 'afaire':
        img = f'<img class="old" src="{uri(old_frame(cid))}" alt="Ancien dessin de {name}">'
    else:
        img = f'<img src="{uri(hd.frames(pid)[0])}" alt="{name} en HD">'
    note = f'<p class="note">{RETOUCHES[pid]}</p>' if st == 'retouche' else (f'<p class="note done">Retouche faite : {RETOUCHES[pid]}</p>' if pid in RETOUCHES else '')
    return f'''<article class="card {st}">
  <div class="pic">{img}</div>
  <div class="txt">
    <div class="row"><h3>{name}</h3><span class="pill {st}">{LABEL[st]}</span></div>
    <p class="meta">{what} · {role} {rar}</p>
    {note}
  </div>
</article>'''


def main():
    counts = {k: sum(1 for r in ROSTER if state(r[0]) == k) for k in LABEL}
    done = len(ROSTER) - counts['afaire']
    secs = []
    for key, title in ELEMENTS:
        rows = [r for r in ROSTER if r[3] == key]
        order = {'valide': 0, 'aregarder': 1, 'retouche': 2, 'afaire': 3}
        rows.sort(key=lambda r: order[state(r[0])])
        n = sum(1 for r in rows if state(r[0]) != 'afaire')
        secs.append(f'<section class="el {key}"><header><h2>{title}</h2><span class="count">{n} / {len(rows)} dessinés</span></header>'
                    f'<div class="grid">{"".join(card(r) for r in rows)}</div></section>')
    today = datetime.date.today().strftime('%d/%m/%Y')
    html = open(os.path.join(HERE, 'suivi-modele.html'), encoding='utf-8').read()
    html = (html.replace('{{DATE}}', today).replace('{{DONE}}', str(done)).replace('{{TOTAL}}', str(len(ROSTER)))
            .replace('{{VALIDE}}', str(counts['valide'])).replace('{{RETOUCHE}}', str(counts['retouche']))
            .replace('{{AREGARDER}}', str(counts['aregarder'])).replace('{{AFAIRE}}', str(counts['afaire']))
            .replace('{{PCT}}', str(round(100 * done / len(ROSTER)))).replace('{{SECTIONS}}', '\n'.join(secs)))
    os.makedirs(os.path.join(HERE, 'sortie'), exist_ok=True)
    out = os.path.join(HERE, 'sortie', 'suivi.html')
    open(out, 'w', encoding='utf-8').write(html)
    print(out, counts)


if __name__ == '__main__':
    main()
