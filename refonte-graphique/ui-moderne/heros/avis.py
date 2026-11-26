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
                     'rk': h['r']})
        files[f"img/{h['id']}.webp"] = os.path.relpath(img, suivi.RACINE)
        files[f"gif/{h['id']}.gif"] = os.path.relpath(gif, suivi.RACINE)
    total = len(tous)
    html = open(os.path.join(os.path.dirname(__file__), 'avis-modele.html'), encoding='utf-8').read()
    data = json.dumps({'heroes': rows, 'total': total}, ensure_ascii=False).replace('<', '\\u003c')
    open(os.path.join(PAGE, 'index.html'), 'w', encoding='utf-8').write(html.replace('__DATA__', data))
    json.dump(files, open(os.path.join(PAGE, 'fichiers.json'), 'w'), indent=0)
    print(f'avis : {len(rows)} héros sur {total} → {os.path.relpath(PAGE, suivi.RACINE)}/index.html')


if __name__ == '__main__':
    main()
