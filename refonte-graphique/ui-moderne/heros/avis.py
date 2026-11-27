"""Page de relecture des héros vectoriels pour le propriétaire (26/11/2026).

python3 refonte-graphique/ui-moderne/heros/avis.py
→ refonte-graphique/ui-moderne/heros/avis/index.html (+ liste des fichiers à publier dans avis/fichiers.json).

Chaque héros fini (STATUT « fait » ou « à revoir ») : son dessin, son animation, une zone de texte, un crayon pour
entourer sur le dessin, et « OK » / « à reprendre ». Tout est enregistré dans la base de la page (capacité `db`,
collection `avis`, un document par héros : text, status, strokes, at) : Claude le relit avec ArtifactData.
Publier avec root = racine du dépôt et les fichiers de avis/fichiers.json ; ne pas changer l'adresse de la page.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import suivi  # noqa: E402

PAGE = os.path.join(suivi.HEROS, 'avis')


def main():
    os.makedirs(PAGE, exist_ok=True)
    rows, files = [], {}
    tous = suivi.heros()
    for h in sorted(tous, key=lambda h: (suivi.ORDRE.index(h['r']), h['el'], h['name'])):
        f = os.path.join(suivi.SORTIE_V, suivi.slug(h['name']), 'STATUT.txt')
        img = os.path.join(suivi.RACINE, 'public', 'art', 'vecto', f"{h['art']}.webp")
        gif = os.path.join(suivi.PAGE, 'gif', f"{h['id']}.gif")
        if not (os.path.exists(f) and os.path.exists(img) and os.path.exists(gif)):
            continue
        rows.append({'id': h['id'], 'name': h['name'], 'r': suivi.RARETE[h['r']], 'el': suivi.ELEMENT[h['el']],
                     'rk': h['r'], 'v': int(max(os.path.getmtime(img), os.path.getmtime(gif))) % 100000})
        files[f"img/{h['id']}.webp"] = os.path.relpath(img, suivi.RACINE)
        files[f"gif/{h['id']}.gif"] = os.path.relpath(gif, suivi.RACINE)
    total = len(tous)
    html = open(os.path.join(os.path.dirname(__file__), 'avis-modele.html'), encoding='utf-8').read()
    data = json.dumps({'heroes': rows, 'total': total}, ensure_ascii=False).replace('<', '\\u003c')
    open(os.path.join(PAGE, 'index.html'), 'w', encoding='utf-8').write(html.replace('__DATA__', data))
    json.dump(files, open(os.path.join(PAGE, 'fichiers.json'), 'w'), indent=0)
    print(f'avis : {len(rows)} héros sur {total} → {os.path.relpath(PAGE, suivi.RACINE)}/index.html')


# Monstres redessinés en vectoriel (demande du 27/11) : page d'avis à part, refonte-graphique/ui-moderne/heros/avis-monstres/
# [id de dessin, dossier, nom, rôle, élément]
MONSTRES = [
    ('mon-arachne-costaud', 'araignee-cuirassee', 'Araignée cuirassée', 'costaud', 'terre'),
    ('mon-arachne-rapide', 'araignee-bondissante', 'Araignée bondissante', 'rapide', 'terre'),
    ('mon-meduse-costaud', 'naga-bouclier', 'Naga au bouclier', 'costaud', 'terre'),
    ('mon-meduse-sorts', 'pretresse-serpent', 'Prêtresse serpent', 'sorts', 'terre'),
    ('mon-kesha-rapide', 'homme-poisson', 'Homme-poisson', 'rapide', 'eau'),
    ('mon-kesha-costaud', 'crabe-geant', 'Crabe géant', 'costaud', 'eau'),
    ('mon-kesha-sorts', 'meduse-eclair', 'Méduse éclair', 'sorts', 'eau'),
    ('mon-barzul-rapide', 'matelot', 'Matelot', 'rapide', 'eau'),
    ('mon-barzul-costaud', 'canonnier', 'Canonnier', 'costaud', 'eau'),
    ('mon-lenore-rapide', 'diablotin', 'Diablotin', 'rapide', 'feu'),
    ('mon-lenore-costaud', 'oni-brute', 'Oni brute', 'costaud', 'feu'),
    ('mon-kael-rapide', 'lutin-magma', 'Lutin de magma', 'rapide', 'feu'),
    ('mon-kael-costaud', 'golem-lave', 'Golem de lave', 'costaud', 'feu'),
    ('mon-kael-tireur', 'salamandre', 'Salamandre', 'tireur', 'feu'),
    ('mon-orin-costaud', 'moine-tengu', 'Moine tengu', 'costaud', 'vent'),
    ('mon-eldra-costaud', 'gorille-guerrier', 'Gorille guerrier', 'costaud', 'vent'),
    ('boss-feu', 'dragon', 'Dragon', 'grand boss', 'feu'),
    ('boss-eau', 'leviathan', 'Léviathan', 'grand boss', 'eau'),
    ('boss-terre', 'titan', 'Titan', 'grand boss', 'terre'),
    ('boss-vent', 'oiseau-tempete', 'Oiseau-tempête', 'grand boss', 'vent'),
]


def monstres():
    page = os.path.join(suivi.HEROS, 'avis-monstres')
    os.makedirs(os.path.join(page, 'gif'), exist_ok=True)
    rows, files = [], {}
    sans = set(os.environ.get('AVIS_SANS', '').split(','))  # monstres encore en cours de dessin
    for art, dos, nom, role, el in MONSTRES:
        if dos in sans:
            continue
        f = os.path.join(suivi.SORTIE_V, dos, 'STATUT.txt')
        img = os.path.join(suivi.RACINE, 'public', 'art', 'vecto', f'{art}.webp')
        g = os.path.join(suivi.SORTIE_V, dos, 'anim.gif')
        gif = os.path.join(page, 'gif', f'{art}.gif')
        if not (os.path.exists(f) and os.path.exists(img) and os.path.exists(g)):
            continue
        if not os.path.exists(gif) or os.path.getmtime(g) > os.path.getmtime(gif):
            try:
                suivi.gif_petit(g, gif)
            except Exception:
                print(f'  (gif de {nom} en cours d\'écriture : passé)')
                continue
        rows.append({'id': art, 'name': nom, 'r': role, 'el': el,
                     'rk': 'boss' if art.startswith('boss') else 'mon',
                     'v': int(max(os.path.getmtime(img), os.path.getmtime(gif))) % 100000})
        files[f'img/{art}.webp'] = os.path.relpath(img, suivi.RACINE)
        files[f'gif/{art}.gif'] = os.path.relpath(gif, suivi.RACINE)
    html = open(os.path.join(os.path.dirname(__file__), 'avis-modele.html'), encoding='utf-8').read()
    for a, b in (('Avis sur les héros', 'Avis sur les monstres'), ('Pour chaque héros', 'Pour chaque monstre'),
                 ('sur le héros', 'sur le monstre'), ('Aucun héros ici', 'Aucun monstre ici'),
                 ('héros sur ${DATA.total}', 'monstres sur ${DATA.total}'), ('un héros sans avis', 'un monstre sans avis')):
        html = html.replace(a, b)
    data = json.dumps({'heroes': rows, 'total': len(MONSTRES)}, ensure_ascii=False).replace('<', '\\u003c')
    open(os.path.join(page, 'index.html'), 'w', encoding='utf-8').write(html.replace('__DATA__', data))
    json.dump(files, open(os.path.join(page, 'fichiers.json'), 'w'), indent=0)
    print(f'avis des monstres : {len(rows)} sur {len(MONSTRES)} → {os.path.relpath(page, suivi.RACINE)}/index.html')


if __name__ == '__main__':
    monstres() if '--monstres' in sys.argv else main()
