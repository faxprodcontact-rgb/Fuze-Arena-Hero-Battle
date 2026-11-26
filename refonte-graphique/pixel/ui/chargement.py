#!/usr/bin/env python3
"""L'ÉCRAN DE CHARGEMENT en pixel art HD (partie 1 du plan, PLAN.md), refait le 25/11 à la demande du propriétaire :
« pas une image tirée du jeu mais construite de 0, qui montre 3 personnages dans un paysage en position de combat ;
le logo pas en pixel, en HD, beau ».

Puis (même jour) : « pas de héros, un beau décor animé », puis « enlève la montagne au premier plan, remplace-la par
les beaux nuages, place le logo au milieu, refais bien le colisée sur sa montagne derrière, que tout soit cohérent ».
Ce qu'on voit (paysage.py) : le ciel du soir, le soleil en haut à droite, des nuages hauts et des oiseaux au loin, des
montagnes pâles, le colisée sur son piton qui sort des nuages, la mer de nuages devant (trois rangées à trois vitesses)
et une brume qui passe. Le logo HD est au milieu de l'écran (un peu au-dessus : le colisée est dessous).
Le mécanisme des héros (HEROS : images clés de combat prises dans hd-meta.ts, respiration, ombres) est gardé, la liste
est vide.
En haut, le logo HD (vectoriel, logo_hd.py) ; en bas la barre de chargement en émail bleu nuit cerclé d'or.

Un pixel = un pixel des héros HD. Le dessin fait 256 × 555 (la forme d'un grand téléphone, 19,5:9) ; il est peint dans
un <canvas> à sa vraie taille par un petit script posé dans index.html (pas de Phaser : il s'affiche avant le code du
jeu), puis agrandi sans flou pour couvrir l'écran (les petits téléphones coupent un peu de ciel).

  python3 refonte-graphique/pixel/ui/logo_hd.py && python3 refonte-graphique/pixel/ui/chargement.py [--gif]
    → public/art/ui-px/chargement-fond.webp   le paysage fixe (+ les ombres des héros)
      public/art/ui-px/chargement-anim.webp   la planche : images des calques animés et des héros
      public/art/ui-px/chargement.webp        l'image fixe complète (sans logo) : écran du nom au premier lancement
      index.html                              style, dessin, logo et script entre les repères « chargement »
      refonte-graphique/pixel/sortie/ui/chargement.png (×2) / .gif (--gif)    aperçus
À relancer si le paysage, un des héros ou le logo changent.
"""
import os
import sys
import json
import math
import base64
import io
import re
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import uilib as U  # noqa: E402
import paysage  # noqa: E402

SW, SH = paysage.SW, paysage.SH         # le dessin (pixels HD)
ANCRE = 0.72                            # écran moins haut que le dessin : on coupe 72 % en haut, 28 % en bas

# Les héros : id, images clés (numéros dans src/game/hd-meta.ts), durée d'une image (0 = une seule image qui respire),
# palier de l'arête, x des pieds.
HEROS = []                              # décision du propriétaire (25/11) : pas de héros sur l'écran de chargement
SOUFFLE_MS = 900                        # la respiration : le haut du corps monte d'un pixel, une image sur deux

# La barre de chargement (pixels HD) : cadre d'or, émail bleu nuit ; la jauge d'or se remplit dedans.
BW, BH = 140, 14
BI = 4                                  # marge intérieure de la jauge (cadre + creux)

PRNG_JS = 'function R(a){return function(){a|=0;a=a+0x6D2B79F5|0;var t=Math.imul(a^a>>>15,1|a);' \
          't=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}}'


def mulberry(seed):
    """Le même tirage que R() du script (mulberry32) : les braises sont au même endroit dans l'aperçu et le jeu."""
    a = seed & 0xffffffff

    def imul(x, y):
        return ((x & 0xffffffff) * (y & 0xffffffff)) & 0xffffffff

    def nxt():
        nonlocal a
        a = (a + 0x6D2B79F5) & 0xffffffff
        t = imul(a ^ (a >> 15), 1 | a)
        t = ((t + imul(t ^ (t >> 7), 61 | t)) & 0xffffffff) ^ t
        return ((t ^ (t >> 14)) & 0xffffffff) / 4294967296
    return nxt


# ------------------------------------------------------------------------------------------------ la planche
class Planche:
    """Range des images dans une planche (rangées, de la plus haute à la plus basse), 1 pixel vide entre elles."""

    def __init__(self, largeur=1536):
        self.L = largeur
        self.items = []

    def ajoute(self, im):
        self.items.append(im)
        return len(self.items) - 1

    def range(self):
        order = sorted(range(len(self.items)), key=lambda i: -self.items[i].height)
        pos = [None] * len(self.items)
        x = y = rh = 0
        for i in order:
            w, h = self.items[i].size
            if x + w > self.L:
                x, y, rh = 0, y + rh + 1, 0
            pos[i] = (x, y)
            x += w + 1
            rh = max(rh, h)
        self.img = Image.new('RGBA', (self.L, y + rh), (0, 0, 0, 0))
        for i, im in enumerate(self.items):
            self.img.alpha_composite(im, pos[i])
        used = np.nonzero(np.asarray(self.img)[:, :, 3].max(axis=0))[0]
        self.img = self.img.crop((0, 0, int(used.max()) + 1, self.img.height))
        self.pos = pos


def images_heros(meta, cid, idx, ms, top):
    """Les images d'un héros, toutes dans une même case (pieds au même point) : [(image, ax, ay)], ms."""
    ch = meta['chars'][cid]
    sheet = Image.open(os.path.join(U.PUBLIC, 'art', 'hd', f'{cid}.webp')).convert('RGBA')
    up = meta['up']
    fr = [ch['frames'][i] for i in idx]
    x0 = min(f[4] for f in fr)
    y0 = min(f[5] for f in fr) - 1             # une ligne de plus en haut pour la respiration
    x1 = max(f[4] + f[2] for f in fr)
    y1 = max(f[5] + f[3] for f in fr)
    ims = []
    for sx, sy, fw, fh, ax, ay in fr:
        cell = sheet.crop((sx * up, sy * up, (sx + fw) * up, (sy + fh) * up)).resize((fw, fh), Image.NEAREST)
        im = Image.new('RGBA', (x1 - x0, y1 - y0), (0, 0, 0, 0))
        im.alpha_composite(cell, (ax - x0, ay - y0))
        ims.append(im)
    if not ms:
        # respiration : tout ce qui est au-dessus du milieu du torse monte d'un pixel (la ligne du dessous est doublée)
        a = np.asarray(ims[0]).copy()
        ys = int(-y0 - top * 0.5)
        b = a.copy()
        b[:ys - 1] = a[1:ys]
        ims, ms = [ims[0], Image.fromarray(b, 'RGBA')], SOUFFLE_MS
    return ims, x0, y0, ms


def construit():
    meta = U.ts_json(os.path.join(U.ROOT, 'src', 'game', 'hd-meta.ts'), 'HD_ANIM')
    t, calques_p = paysage.dessine()
    P = paysage.P
    pl = Planche()
    calques = []
    for k, (z, g, d, ims) in enumerate(calques_p):
        ids = [pl.ajoute(im) for im in ims]
        if g == 'p':
            d = d + [k * 7919 + 17]
        calques.append((z, g, d, ids))
    fond = t.col.copy()
    Y, X = np.mgrid[0:SH, 0:SW]
    for cid, idx, ms, palier, fx in HEROS:
        fy = paysage.PALIERS[palier][2]
        ims, ax, ay, ms = images_heros(meta, cid, idx, ms, meta['chars'][cid]['top'])
        x, y = fx + ax, fy + ay
        w, h = ims[0].size
        ids = [pl.ajoute(im) for im in ims]
        calques.append((fy / 10000, 'b', [x, y, w, h, ms], ids))
        # l'ombre au sol : la largeur des pieds × 1,15, un ton plus sombre et plus violet
        a = np.asarray(ims[0])[:, :, 3] > 0
        cols = np.nonzero(a[max(0, -ay - 5):-ay + 1].any(axis=0))[0]
        rx = max(12, (cols.max() - cols.min() + 1) * 0.58)
        ry = max(3, rx * 0.18)
        cx = x + (cols.min() + cols.max()) / 2
        m = (((X - cx) / rx) ** 2 + ((Y - fy - 0.5) / ry) ** 2 <= 1) & (Y >= fy)
        cur = fond[m, :3].astype(float)
        fond[m, :3] = np.clip(cur * np.array([0.62, 0.58, 0.70]) + np.array([10, 4, 18]), 0, 255).astype(np.uint8)
    fond = Image.fromarray(fond, 'RGBA').convert('RGB')
    pl.range()
    calques.sort(key=lambda c: c[0])
    L = []
    for z, g, d, ids in calques:
        cases = []
        for i in ids:
            sx, sy = pl.pos[i]
            w, h = pl.items[i].size
            cases += [sx, sy] if g == 'b' else [sx, sy, w, h]
        L.append([g, *[round(v, 4) if isinstance(v, float) else v for v in d], cases])
    return {'w': SW, 'h': SH, 'P': P, 'L': L}, fond, pl.img



# ------------------------------------------------------------------------------------------------ le rendu (comme le script)
def particules(c, t, P):
    x0, y0, x1, y1, n, v0, v1, vx0, vx1, vy0, vy1, amp, per, ims_ms, seed = c[1:16]
    cases = c[16]
    ims = [cases[k:k + 4] for k in range(0, len(cases), 4)]
    rnd = mulberry(seed)
    slots = max(n, math.ceil(n * P / ((v0 + v1) / 2)))
    out = []
    for k in range(slots):
        life = min(P, v0 + rnd() * (v1 - v0))
        born = (k + rnd()) * P / slots
        px0 = x0 + rnd() * (x1 - x0)
        py0 = y0 + rnd() * (y1 - y0)
        vx = vx0 + rnd() * (vx1 - vx0)
        vy = vy0 + rnd() * (vy1 - vy0)
        ph = rnd() * 6.283
        age = (t - born) % P
        if age >= life:
            continue
        s = age / 1000
        x = px0 + vx * s + amp * math.sin(ph + 2 * math.pi * age / max(1, per))
        y = py0 + vy * s
        fi = int((age + ph * 100) // ims_ms) % len(ims) if ims_ms else min(len(ims) - 1, int(age / life * len(ims)))
        sx, sy, w, h = ims[fi]
        out.append((int(math.floor(x - w / 2 + 0.5)), int(math.floor(y - h / 2 + 0.5)), sx, sy, w, h))
    return out


def rendu(M, fond, planche, t):
    im = fond.convert('RGBA').copy()
    P = M['P']
    for c in M['L']:
        g = c[0]
        if g == 'b':
            x, y, w, h, ms, cases = c[1:7]
            nf = len(cases) // 2
            i = int(t // ms) % nf if ms else 0
            sx, sy = cases[2 * i], cases[2 * i + 1]
            im.alpha_composite(planche.crop((sx, sy, sx + w, sy + h)), (x, y))
        elif g == 'd':
            x, y, w, h, vx, vy, cases = c[1:8]
            sx, sy, tw, th = cases
            tile = planche.crop((sx, sy, sx + tw, sy + th))
            ox = int(math.floor(t / 1000 * vx + 0.5)) % tw
            oy = int(math.floor(t / 1000 * vy + 0.5)) % th
            band = Image.new('RGBA', (w, h), (0, 0, 0, 0))
            for yy in range(-th, h + th, th):
                for xx in range(-tw, w + tw, tw):
                    band.alpha_composite(tile, (xx + ox, yy + oy)) if 0 <= xx + ox and 0 <= yy + oy else \
                        band.paste(tile, (xx + ox, yy + oy), tile)
            lay = Image.new('RGBA', im.size, (0, 0, 0, 0))
            lay.paste(band, (x, y))
            im.alpha_composite(lay)
        else:
            lay = Image.new('RGBA', im.size, (0, 0, 0, 0))
            for x, y, sx, sy, w, h in particules(c, t, P):
                spr = planche.crop((sx, sy, sx + w, sy + h))
                lay.paste(spr, (x, y), spr)
            im.alpha_composite(lay)
    return im


# ------------------------------------------------------------------------------------------------ la barre
def barre():
    """Le cadre de la barre : un seul contour sombre, un cerclage d'or (clair en haut à droite), l'émail bleu nuit
    creusé dedans (ombre en haut, reflet en bas). Les coins sont coupés en marches."""
    T = U.Toile(BW, BH)
    X, Y = T.X, T.Y

    def rond(r):          # rectangle aux coins coupés, rentré de r pixels
        m = (X >= r) & (X < BW - r) & (Y >= r) & (Y < BH - r)
        for (cx, cy) in ((r, r), (BW - 1 - r, r), (r, BH - 1 - r), (BW - 1 - r, BH - 1 - r)):
            for dx, dy in ((0, 0), (1, 0), (0, 1)):
                xx = cx + (dx if cx < BW / 2 else -dx)
                yy = cy + (dy if cy < BH / 2 else -dy)
                m[yy, xx] = False
        return m
    out, rim, inner = rond(0), rond(1), rond(3)
    T.peint(out, U.CONTOUR)
    T.peint(rim, '#e3a23a')
    T.peint(rim & (Y <= 2), '#ffe08a')
    T.peint(rim & (Y >= BH - 3), '#a8601c')
    T.peint(rim & (X >= BW - 3) & (Y < BH - 3), '#ffd26a')
    T.peint(rim & (X <= 2) & (Y > 2), '#c27a24')
    T.peint(rond(2), '#5a2a1c')                       # le joint sombre entre l'or et l'émail
    T.peint(inner, '#1d2758')
    T.peint(inner & (Y == 3), '#10163a')              # le creux : l'ombre du bord du haut
    T.peint(inner & (Y == BH - 4), '#33408a')         # le reflet de l'émail en bas
    return T.image()


# ------------------------------------------------------------------------------------------------ index.html
def data_uri(im):
    b = io.BytesIO()
    im.save(b, 'WEBP', lossless=True, method=6)
    return 'data:image/webp;base64,' + base64.b64encode(b.getvalue()).decode()


def html(M):
    """Le style (head) et le dessin + script (body) de l'écran de chargement."""
    svg = open(os.path.join(U.PUBLIC, 'art', 'ui', 'logo.svg'), encoding='utf-8').read()
    vw, vh = [float(v) for v in re.search(r'viewBox="[\d.-]+ [\d.-]+ ([\d.]+) ([\d.]+)"', svg).groups()]
    svg = svg.replace('<svg ', '<svg class="logo" ', 1)
    # la jauge (style moderne, 26/11) : une pilule de verre sombre, l'or qui la remplit en douceur, vite au début puis de
    # plus en plus lentement, jusqu'à 92 %
    pts = [(0, 0), (8, 0.30), (20, 0.52), (40, 0.70), (65, 0.82), (100, 0.92)]
    kf = [f'{p}%{{width:{v * 100:.0f}%}}' for p, v in pts]
    style = f"""<style>
      /* écran de chargement (fabriqué par refonte-graphique/pixel/ui/chargement.py) : visible pendant le téléchargement
         du jeu, retiré par main.tsx. Le dessin est peint à sa vraie taille ({SW} × {SH}) dans le canvas puis agrandi
         sans flou : --px = la taille d'un pixel du dessin, assez grande pour couvrir l'écran (colonne de 480 px au plus). */
      #splash {{ position: fixed; inset: 0; z-index: 9999; background: #120c1c; transition: opacity .5s; }}
      #splash.gone {{ opacity: 0; pointer-events: none; }}
      #splash .sp {{ position: absolute; top: 0; bottom: 0; left: 50%; width: min(100%, 480px); transform: translateX(-50%); overflow: hidden;
        --px: max(calc(min(100vw, 480px) / {SW}), calc(100vh / {SH})); background: #2a1424; }}
      @supports (height: 100dvh) {{ #splash .sp {{ --px: max(calc(min(100vw, 480px) / {SW}), calc(100dvh / {SH})); }} }}
      #splash canvas, #splash .logo, #splash .load {{ position: absolute; }}
      #splash canvas {{ image-rendering: pixelated; }}
      #splash canvas {{ width: calc(var(--px) * {SW}); height: calc(var(--px) * {SH}); left: calc(50% - var(--px) * {SW / 2}); top: calc((100% - var(--px) * {SH}) * {ANCRE}); }}
      /* le logo est vectoriel (net à toutes les tailles) : au milieu de l'écran (un peu au-dessus : le colisée est
         dessous), 62 % de la colonne, 280 px et 19 % de la hauteur au plus */
      #splash .logo {{ left: 50%; top: calc(45% + env(safe-area-inset-top, 0px) / 2); width: min(62%, 280px, calc(19vh * {vw / vh:.3f})); height: auto; aspect-ratio: {vw:.0f} / {vh:.0f}; overflow: visible; transform: translate(-50%, -50%); }}
      #splash .load {{ left: 50%; bottom: calc(env(safe-area-inset-bottom, 0px) + 30px); width: min(62%, 240px); height: 14px; transform: translateX(-50%);
        padding: 3px; border-radius: 999px; background: #0d0826b8; box-shadow: inset 0 0 0 1px #ffffff2e, 0 4px 14px #0a062099; }}
      #splash .load i {{ display: block; height: 100%; border-radius: 999px; overflow: hidden; }}
      #splash .load b {{ display: block; height: 100%; width: 0; border-radius: 999px; animation: splash-load 6s ease-out forwards;
        background: linear-gradient(90deg, #ffb21f, #ffe27a); box-shadow: inset 0 2px 0 #ffffff80, 0 0 8px #ffc22e99; }}
      @keyframes splash-load {{ {' '.join(kf)} }}
      #splash.done .load b {{ width: 100%; animation: none; transition: width .25s; }}
    </style>"""
    data = json.dumps(M, separators=(',', ':'))
    script = (
        '<script>(function(){try{'
        f'var M={data};{PRNG_JS}'
        "var c=document.getElementById('sp-c'),g=c.getContext('2d'),B=new Image(),S=new Image(),t0=performance.now(),last=-1;"
        "B.src='art/ui-px/chargement-fond.webp';S.src='art/ui-px/chargement-anim.webp';g.imageSmoothingEnabled=false;"
        # les particules : chaque place renaît au même endroit à chaque période (comme dans le jeu)
        "M.L.forEach(function(l){if(l[0]!=='p')return;var r=R(l[15]),P=M.P,n=l[5],s=Math.max(n,Math.ceil(n*P/((l[6]+l[7])/2))),q=[];"
        "for(var k=0;k<s;k++)q.push([Math.min(P,l[6]+r()*(l[7]-l[6])),(k+r())*P/s,l[1]+r()*(l[3]-l[1]),l[2]+r()*(l[4]-l[2]),"
        "l[8]+r()*(l[9]-l[8]),l[10]+r()*(l[11]-l[10]),r()*6.283]);l.q=q});"
        "function f(now){if(!c.isConnected)return;requestAnimationFrame(f);var t=now-t0;if(t-last<40)return;last=t;"
        "if(!B.naturalWidth)return;g.drawImage(B,0,0);if(!S.naturalWidth)return;"
        "M.L.forEach(function(l){var x,y,w,h,k,e;"
        "if(l[0]==='b'){e=l[6];k=l[5]?Math.floor(t/l[5])%(e.length/2):0;g.drawImage(S,e[2*k],e[2*k+1],l[3],l[4],l[1],l[2],l[3],l[4])}"
        "else if(l[0]==='d'){e=l[7];var tw=e[2],th=e[3],ox=((Math.floor(t/1e3*l[5]+.5)%tw)+tw)%tw,oy=((Math.floor(t/1e3*l[6]+.5)%th)+th)%th;"
        "g.save();g.beginPath();g.rect(l[1],l[2],l[3],l[4]);g.clip();"
        "for(y=-th;y<l[4]+th;y+=th)for(x=-tw;x<l[3]+tw;x+=tw)g.drawImage(S,e[0],e[1],tw,th,l[1]+x+ox,l[2]+y+oy,tw,th);g.restore()}"
        "else{e=l[16];var P=M.P;l.q.forEach(function(p){var a=((t-p[1])%P+P)%P;if(a>=p[0])return;var s=a/1e3,ni=e.length/4,"
        "i=l[14]?Math.floor((a+p[6]*100)/l[14])%ni:Math.min(ni-1,Math.floor(a/p[0]*ni));w=e[4*i+2];h=e[4*i+3];"
        "x=p[2]+p[4]*s+l[12]*Math.sin(p[6]+2*Math.PI*a/Math.max(1,l[13]));y=p[3]+p[5]*s;"
        "g.drawImage(S,e[4*i],e[4*i+1],w,h,Math.floor(x-w/2+.5),Math.floor(y-h/2+.5),w,h)})}})}"
        "requestAnimationFrame(f)}catch(e){}})()</script>"
    )
    body = (f'<div id="splash"><div class="sp"><canvas id="sp-c" width="{SW}" height="{SH}"></canvas>'
            + svg + '<div class="load">'
            f'<i><b></b></i></div></div></div>\n    '
            + script)
    pre = ('<link rel="preload" as="image" type="image/webp" href="art/ui-px/chargement-fond.webp" />\n    '
           '<link rel="preload" as="image" type="image/webp" href="art/ui-px/chargement-anim.webp" />')
    return style, body, pre


def remplace(texte, nom, contenu):
    a, b = f'<!-- {nom}:debut -->', f'<!-- {nom}:fin -->'
    i, j = texte.index(a), texte.index(b)
    return texte[:i + len(a)] + '\n    ' + contenu + '\n    ' + texte[j:]


def main():
    M, fond, planche = construit()
    out = U.OUT_DIR
    n1 = U.sauve(fond, os.path.join(out, 'chargement-fond.webp'))
    n2 = U.sauve(planche, os.path.join(out, 'chargement-anim.webp'))
    fixe = rendu(M, fond, planche, 0).convert('RGB')
    n3 = U.sauve(fixe, os.path.join(out, 'chargement.webp'))
    print(f'fond {n1} o, planche {planche.size} {n2} o, image fixe {n3} o, {len(M["L"])} calques')
    style, body, pre = html(M)
    p = os.path.join(U.ROOT, 'index.html')
    t = open(p, encoding='utf-8').read()
    t = remplace(t, 'chargement-style', style)
    t = remplace(t, 'chargement-precharge', pre)
    t = remplace(t, 'chargement', body)
    open(p, 'w', encoding='utf-8').write(t)
    print('index.html mis à jour', len(style) + len(body), 'caractères')
    # aperçu : le dessin seul (×2) ; l'écran entier avec le logo (vectoriel) est filmé dans le navigateur
    U.sauve(fixe.resize((SW * 2, SH * 2), Image.NEAREST), os.path.join(U.SORTIE, 'chargement.png'))
    lg = os.path.join(U.SORTIE, 'logo-hd.png')            # le logo rendu par le navigateur (capture Playwright)
    if '--gif' in sys.argv and os.path.exists(lg):
        # 3 s comme sur un iPhone 390 × 844 : le dessin ×2, le logo lisse par-dessus, la jauge qui avance
        logo = Image.open(lg).convert('RGBA')
        k = 2 * SW / 390                                   # pixels de l'aperçu par point de l'écran
        lw = round(min(390 * 0.62, 280, 844 * 0.19 * logo.width / logo.height) * k)
        logo = logo.resize((lw, round(lw * logo.height / logo.width)), Image.LANCZOS)
        ims = []
        for i, t in enumerate(range(0, 3000, 150)):
            im = rendu(M, fond, planche, t).resize((SW * 2, SH * 2), Image.NEAREST)
            im.alpha_composite(logo, ((SW * 2 - lw) // 2, round((844 * 0.45 + 47 / 2) * k - logo.height / 2)))
            b = barre()
            fw = int(min(0.92, 0.2 + t / 3000 * 0.6) * (BW - 2 * BI))
            jauge = Image.new('RGBA', (fw, BH - 2 * BI))
            for y, c in enumerate(('#fff6c0', '#ffd84a', '#ffd84a', '#f5a524', '#f5a524', '#c0601a')):
                jauge.paste(c, (0, y, fw, y + 1))
            b.alpha_composite(jauge, (BI, BI))
            b = b.resize((BW * 2, BH * 2), Image.NEAREST)
            im.alpha_composite(b, (SW - BW, SH * 2 - round(34 * k) - 2 * (12 + BH)))
            ims.append(im.convert('RGB').quantize(255, method=Image.Quantize.MEDIANCUT))
        ims[0].save(os.path.join(U.SORTIE, 'chargement.gif'), save_all=True, append_images=ims[1:], duration=150,
                    loop=0)

if __name__ == '__main__':
    main()
