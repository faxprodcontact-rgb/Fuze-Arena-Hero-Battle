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
for an, a in js['anims'].items():
    av = a.get('av') or [0] * len(a['f'])
    for i, f in enumerate(a['f']):
        if f < 0: continue
        sx, sy, w, h, ax, ay = fr[f]
        dx = av[i] if i < len(av) else 0
        L = view[0] - (feet[0] + dx); T = view[1] - feet[1]
        R = view[0] + view[2] - (feet[0] + dx); B = view[1] + view[3] - feet[1]
        side = []
        if abs(ax - L) < 0.6: side.append('gauche')
        if abs(ay - T) < 0.6: side.append('haut')
        if abs(ax + w / up - R) < 0.6: side.append('droite')
        if abs(ay + h / up - B) < 0.6: side.append('bas')
        if side: out.append('%s#%d:%s' % (an, i, '/'.join(side)))
print(nom, 'OK' if not out else ' '.join(out[:12]) + (' …(%d)' % len(out) if len(out) > 12 else ''))
