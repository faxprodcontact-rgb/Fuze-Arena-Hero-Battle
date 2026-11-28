# Les images de combat qui touchent le bord de leur vue (donc coupées) : pour chaque personnage, chaque animation.
import json, os, sys, subprocess
UI = '/home/user/Fuze-Arena-Hero-Battle/refonte-graphique/ui-moderne'
sys.path.insert(0, UI)
import jeu_export_vecto as J
nom = sys.argv[1]
folder = J.folder_of(nom)
m = J.load_jeu(folder)
A, D, JE = m.ANIM, m.DESSIN, m.JEU
view = tuple(JE.get('vue', getattr(A, 'VIEW')))
feet = JE.get('pieds', getattr(D, 'FEET'))
js = json.load(open(os.path.join(folder, 'jeu.json')))
up = js['up']
fr = js['frames']
out = []
grd = JE.get('sol', getattr(D, 'GRD', feet[1]))
for an, a in js['anims'].items():
    # la spéciale est rendue dans une vue élargie (l'éclat, 28/11) ; ce qui est sur la cible aussi (posé à `cible`, sol)
    v = J.vue_speciale(view, JE['speciale']) if an == 'speciale' else view
    av = a.get('avance') or [0] * len(a['f'])
    cells = [(i, f, (feet[0] + (av[i] if i < len(av) else 0), feet[1]), '') for i, f in enumerate(a['f'])]
    if 'cible' in a and 'cible' in JE[an if an != 'pose' else 'attaque']:
        cx = JE[an]['cible'][0]
        cells += [(i, f, (cx, grd), 'cible') for i, f in enumerate(a['cible'])]
    for i, f, (fx, fy), lab in cells:
        if f < 0: continue
        sx, sy, w, h, ax, ay = fr[f]
        L = v[0] - fx; T = v[1] - fy
        R = v[0] + v[2] - fx; B = v[1] + v[3] - fy
        side = []
        if abs(ax - L) < 0.6: side.append('gauche')
        if abs(ay - T) < 0.6: side.append('haut')
        if abs(ax + w / up - R) < 0.6: side.append('droite')
        if abs(ay + h / up - B) < 0.6: side.append('bas')
        if side: out.append('%s%s#%d:%s' % (an, lab and '-' + lab, i, '/'.join(side)))
print(nom, 'OK' if not out else ' '.join(out[:12]) + (' …(%d)' % len(out) if len(out) > 12 else ''))
