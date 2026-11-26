// Familles de boutons (proposition du 26/11/2026). Chaque bouton est un dessin vectoriel (SVG) fabriqué ici par le code,
// comme les pièces de px.ts : `installButtons()` les pose dans des variables CSS --bt-<famille>-<teinte>-<taille>[-down]
// (et --bt-<famille>-rond-<teinte>[-down] pour les boutons ronds). boutons.css les pose sur le ::before des boutons, en
// « 3 morceaux » (bouts gauche et droit fixes, milieu étiré) : un bouton peut avoir n'importe quelle largeur.
// Règles : une seule lumière en haut à droite (arêtes claires en haut et à droite, ombre en bas et à gauche), un seul
// contour sombre autour de chaque bouton, pas de rayures ni de hachures, des signes dessinés (jamais de lettres).
(function () {
  const INK = '#1c0f26';
  // tailles : hauteur totale (épaisseur comprise) et épaisseur (la « lèvre » qui disparaît quand on appuie)
  const SIZES = { xxl: { h: 84, lip: 7 }, xl: { h: 72, lip: 6 }, l: { h: 62, lip: 6 }, m: { h: 48, lip: 5 }, s: { h: 38, lip: 4 } };

  let uid = 0;
  const id = (p) => `${p}${++uid}`;
  const P = (pts) => 'M' + pts.map((p) => p.map((v) => +v.toFixed(2)).join(' ')).join('L') + 'Z';
  const url = (w, h, body) => `url("data:image/svg+xml,${encodeURIComponent(`<svg xmlns='http://www.w3.org/2000/svg' width='${w}' height='${h}' viewBox='0 0 ${w} ${h}'>${body}</svg>`)}")`;
  // dégradé linéaire en coordonnées réelles ; stops = [[décalage, couleur, opacité?], ...]
  const lin = (gid, x1, y1, x2, y2, stops) => `<linearGradient id='${gid}' gradientUnits='userSpaceOnUse' x1='${x1}' y1='${y1}' x2='${x2}' y2='${y2}'>${stops.map(([o, c, a]) => `<stop offset='${o}' stop-color='${c}'${a != null ? ` stop-opacity='${a}'` : ''}/>`).join('')}</linearGradient>`;
  const rad = (gid, cx, cy, rx, ry, stops) => `<radialGradient id='${gid}' gradientUnits='userSpaceOnUse' cx='${cx}' cy='${cy}' r='${rx}' gradientTransform='translate(${cx} ${cy}) scale(1 ${ry / rx}) translate(${-cx} ${-cy})'>${stops.map(([o, c, a]) => `<stop offset='${o}' stop-color='${c}'${a != null ? ` stop-opacity='${a}'` : ''}/>`).join('')}</radialGradient>`;
  // une arête éclairée : la forme en couleur claire, puis la même forme décalée vers le bas-gauche par-dessus, découpée
  // dans la forme : il reste un filet clair en haut et à droite (la lumière vient d'en haut à droite)
  const lit = (d, light, base, dx, dy, extra = '') => {
    const c = id('c');
    return `<clipPath id='${c}'><path d='${d}'/></clipPath><g clip-path='url(#${c})'><path d='${d}' fill='${light}'/><path d='${d}' fill='${base}' transform='translate(${-dx} ${dy})'/>${extra}</g>`;
  };
  // octogone (coins coupés) dans le rectangle x0,y0,x1,y1 ; c = [haut-gauche, haut-droit, bas-droit, bas-gauche]
  const oct = (x0, y0, x1, y1, c) => {
    const [a, b, d, e] = Array.isArray(c) ? c : [c, c, c, c];
    return P([[x0 + a, y0], [x1 - b, y0], [x1, y0 + b], [x1, y1 - d], [x1 - d, y1], [x0 + e, y1], [x0, y1 - e], [x0, y0 + a]]);
  };
  // rectangle arrondi
  const rr = (x0, y0, x1, y1, r) => `M${x0 + r} ${y0}H${x1 - r}A${r} ${r} 0 0 1 ${x1} ${y0 + r}V${y1 - r}A${r} ${r} 0 0 1 ${x1 - r} ${y1}H${x0 + r}A${r} ${r} 0 0 1 ${x0} ${y1 - r}V${y0 + r}A${r} ${r} 0 0 1 ${x0 + r} ${y0}Z`;
  const circ = (cx, cy, r) => `M${cx - r} ${cy}a${r} ${r} 0 1 0 ${2 * r} 0a${r} ${r} 0 1 0 ${-2 * r} 0Z`;

  /* ================================================================================================================
     1. ÉMAIL SERTI — un émail profond serti dans un cadre d'or, coins coupés (un sceau, une médaille)
     ================================================================================================================ */
  const EMAIL = {
    // bezel : cadre d'or [clair, moyen, sombre] ; face : émail [haut, bas] ; ink : couleur du texte et de son ombre
    or: { bez: ['#fff3b4', '#f2b53a', '#9c5414'], face: ['#ffe07a', '#f3a52c'], glow: '#fff8d0', lip: '#7a3a10' },
    nuit: { bez: ['#ffe7a0', '#d99a34', '#8a4a14'], face: ['#3a3f97', '#1b1d58'], glow: '#8fa2ff', lip: '#5e2c0e' },
    feu: { bez: ['#ffe7a0', '#d99a34', '#8a4a14'], face: ['#e8553a', '#8a1630'], glow: '#ffb27a', lip: '#5e2c0e' },
    eau: { bez: ['#ffe7a0', '#d99a34', '#8a4a14'], face: ['#3a8ff0', '#142a80'], glow: '#9fe0ff', lip: '#5e2c0e' },
    terre: { bez: ['#ffe7a0', '#d99a34', '#8a4a14'], face: ['#d98a34', '#7a3412'], glow: '#ffd99a', lip: '#5e2c0e' },
    vent: { bez: ['#ffe7a0', '#d99a34', '#8a4a14'], face: ['#34c27e', '#0c5a48'], glow: '#b8ffd0', lip: '#5e2c0e' },
    violet: { bez: ['#ffe7a0', '#d99a34', '#8a4a14'], face: ['#9a62f0', '#3c1a8a'], glow: '#e0c8ff', lip: '#5e2c0e' },
    rubis: { bez: ['#ffe7a0', '#d99a34', '#8a4a14'], face: ['#e04866', '#7a1238'], glow: '#ffb0c0', lip: '#5e2c0e' },
    off: { bez: ['#d9d6e6', '#9d99b4', '#5d5974'], face: ['#6e6a8c', '#45425f'], glow: '#b5b1cc', lip: '#3e3b52' },
  };
  function email(t, w, h, lip, down) {
    const T = EMAIL[t];
    const y0 = down ? lip - 1 : 0, yb = down ? h - 1 : h - lip; // haut de la face, bas de la face
    const c = h >= 56 ? 11 : h >= 44 ? 9 : 7;
    const g1 = id('g'), g2 = id('g'), g3 = id('g'), g4 = id('g');
    const bw = h >= 56 ? 4 : 3.5; // largeur du cadre d'or
    let s = `<defs>${lin(g1, w, y0, w - 2.2 * h, yb, [[0, T.bez[0]], [0.35, T.bez[1]], [1, T.bez[2]]])}`;
    s += lin(g2, 0, y0 + 2 + bw, 0, yb - 2 - bw, [[0, T.face[0]], [1, T.face[1]]]);
    s += rad(g3, w - c - 6, y0 + bw + 6, h * 0.9, h * 0.55, [[0, T.glow, 0.55], [1, T.glow, 0]]);
    s += lin(g4, 0, yb - 2, 0, h, [[0, T.lip], [1, T.lip]]);
    s += `</defs>`;
    // contour unique + épaisseur
    s += `<path d='${oct(0, y0, w, h, c)}' fill='${INK}'/>`;
    if (!down) s += `<path d='${oct(2, y0 + 2, w - 2, h - 2, c - 1)}' fill='${T.lip}'/>`;
    // cadre d'or, arête claire en haut à droite
    const bez = oct(2, y0 + 2, w - 2, yb, c - 1);
    s += lit(bez, T.bez[0], `url(#${g1})`, 1.5, 1.5);
    // émail : un creux sous le cadre (ombre en haut à droite, lumière en bas à gauche, comme un creux éclairé d'en haut à droite)
    const en = oct(2 + bw, y0 + 2 + bw, w - 2 - bw, yb - bw, Math.max(3, c - 1 - bw * 0.6));
    const cl = id('c');
    s += `<clipPath id='${cl}'><path d='${en}'/></clipPath><g clip-path='url(#${cl})'>`;
    s += `<path d='${en}' fill='${T.bez[2]}'/>`;
    s += `<path d='${en}' fill='url(#${g2})' transform='translate(-1.5 1.5)'/>`;
    s += `<path d='${en}' fill='url(#${g3})'/>`;
    // un reflet net de l'émail, en haut à droite (dans le bout droit : il ne s'étire pas)
    s += `<path d='M${w - 2 - bw - c * 1.9} ${y0 + 2 + bw + 2.5}h${c * 1.1}l${-3} ${3}h${-c * 1.1}z' fill='#fff' fill-opacity='0.5'/>`;
    s += `</g>`;
    return s;
  }

  /* ================================================================================================================
     2. PIERRE DE L'ARÈNE — une dalle taillée (coins éclatés, pas deux pareils) ; l'action principale est une pierre
        sombre où brûle une lumière (la couleur de l'élément), les autres une pierre claire gravée
     ================================================================================================================ */
  const PIERRE = {
    // pierre [arête claire, haut, bas, épaisseur] ; light : la lumière intérieure (rien = pierre éteinte)
    basalte: { st: ['#8a86a8', '#4d4a6a', '#2e2c47', '#1f1d33'], light: '#ffb53a', core: '#fff1b8' },
    feu: { st: ['#9a7f8e', '#56404f', '#33232f', '#22161f'], light: '#ff6a2a', core: '#ffe0a0' },
    eau: { st: ['#7f93ad', '#3f4f6c', '#232f47', '#161f33'], light: '#2fa4ff', core: '#d4f6ff' },
    terre: { st: ['#a08e78', '#5b4c3f', '#372c24', '#251d17'], light: '#f0a02f', core: '#fff0c0' },
    vent: { st: ['#7fa497', '#3f5e55', '#243a34', '#172722'], light: '#3fd884', core: '#dcffe6' },
    arcane: { st: ['#9a8ab8', '#4f4270', '#2e2549', '#1f1834'], light: '#b07bff', core: '#f3e6ff' },
    ardoise: { st: ['#d8d3e6', '#a7a1c2', '#7c7699', '#55506e'] },
    off: { st: ['#7a7790', '#4f4c63', '#38364a', '#28263a'] },
  };
  function pierre(t, w, h, lip, down) {
    const T = PIERRE[t];
    const y0 = down ? lip - 1 : 0, yb = down ? h - 1 : h - lip;
    const k = h >= 56 ? 1 : h >= 44 ? 0.8 : 0.65;
    const cc = [6 * k, 11 * k, 5 * k, 8 * k]; // coins éclatés : haut-gauche, haut-droit, bas-droit, bas-gauche
    const g1 = id('g'), g2 = id('g'), g3 = id('g');
    let s = `<defs>${lin(g1, w * 0.7, y0, w * 0.3, yb, [[0, T.st[1]], [1, T.st[2]]])}`;
    if (T.light) s += rad(g2, w / 2, (y0 + yb) / 2, w * 0.42, (yb - y0) * 0.62, [[0, T.light, 0.75], [0.55, T.light, 0.22], [1, T.light, 0]]);
    // quelques taches douces de la pierre (pas de grain répété)
    s += rad(g3, w * 0.22, yb * 0.7, h * 0.5, h * 0.3, [[0, '#000', 0.16], [1, '#000', 0]]);
    s += `</defs>`;
    s += `<path d='${oct(0, y0, w, h, cc)}' fill='${INK}' stroke='${INK}' stroke-width='1' stroke-linejoin='round'/>`;
    if (!down) s += `<path d='${oct(2, y0 + 2, w - 2, h - 2, cc.map((v) => v - 0.8))}' fill='${T.st[3]}'/>`;
    const face = oct(2, y0 + 2, w - 2, yb, cc.map((v) => v - 0.8));
    // biseau : un filet clair épais en haut et à droite, la pierre, puis le plat de la dalle
    s += lit(face, T.st[0], `url(#${g1})`, 2.5, 2.5,
      `<path d='${oct(6, y0 + 6, w - 6, yb - 4, cc.map((v) => Math.max(2, v - 3)))}' fill='url(#${g1})' />` +
      `<path d='${face}' fill='url(#${g3})'/>` +
      // un éclat dans le coin haut-droit (le coin cassé reçoit la lumière)
      `<path d='M${w - 2 - cc[1] - 7 * k} ${y0 + 2}l${4 * k} ${5 * k}l${6 * k} ${-1 * k}z' fill='${T.st[0]}' fill-opacity='0.55'/>` +
      (T.light ? `<path d='${face}' fill='url(#${g2})'/>` : ''));
    return s;
  }

  /* ================================================================================================================
     3. CRISTAL ÉLÉMENTAIRE — une gemme taillée en long, bouts en pointe, une lumière qui vient du cœur (la couleur de
        l'élément) ; des facettes nettes au lieu d'un reflet de bonbon
     ================================================================================================================ */
  const CRISTAL = {
    // [arête, facette haute, cœur, facette basse, épaisseur], light : lumière du cœur
    citrine: { c: ['#fff6c8', '#ffd45a', '#f5a524', '#b85c12', '#6e2e0c'], light: '#fff3b0' },
    feu: { c: ['#ffe0c0', '#ff9a5a', '#f0522e', '#9c1f22', '#5a0f1a'], light: '#ffd38a' },
    eau: { c: ['#dcf8ff', '#6fd0ff', '#2f8ff0', '#1a3fa8', '#0f2266'], light: '#d0f6ff' },
    terre: { c: ['#fff0cc', '#f0c070', '#d08a34', '#8a4a18', '#4f260c'], light: '#ffeab0' },
    vent: { c: ['#e0ffe6', '#7ff0a4', '#2fc274', '#127a52', '#0a4634'], light: '#d8ffe4' },
    amethyste: { c: ['#f4e4ff', '#c79cff', '#8c56f0', '#5226b0', '#2f136e'], light: '#f0dcff' },
    fume: { c: ['#c9c0ee', '#6a5fa6', '#3e3478', '#262058', '#160f38'], light: '#b9a8ff' },
    off: { c: ['#d6d4e2', '#9e9bb4', '#7a7792', '#55526c', '#38364a'] },
  };
  function cristal(t, w, h, lip, down) {
    const T = CRISTAL[t];
    const y0 = down ? lip - 1 : 0, yb = down ? h - 1 : h - lip;
    const fh = yb - y0, my = y0 + fh / 2, p = Math.round(fh * 0.42);
    const hex = (x0, ya, x1, yz, pp) => { const m = (ya + yz) / 2; return P([[x0 + pp, ya], [x1 - pp, ya], [x1, m], [x1 - pp, yz], [x0 + pp, yz], [x0, m]]); };
    const g1 = id('g'), g2 = id('g'), g3 = id('g');
    let s = `<defs>${lin(g1, 0, y0, 0, yb, [[0, T.c[1]], [0.5, T.c[2]], [1, T.c[3]]])}`;
    if (T.light) s += rad(g2, w / 2, my + 1, w * 0.36, fh * 0.42, [[0, T.light, down ? 0.95 : 0.7], [0.6, T.light, down ? 0.35 : 0.18], [1, T.light, 0]]);
    s += lin(g3, 0, y0, 0, my, [[0, '#fff', 0.55], [1, '#fff', 0.08]]);
    s += `</defs>`;
    // contour + épaisseur (la gemme est posée : sa tranche se voit en bas)
    s += `<path d='${hex(0, y0, w, h, p + 1)}' fill='${INK}' stroke='${INK}' stroke-width='1.5' stroke-linejoin='round'/>`;
    if (!down) s += `<path d='${hex(2.4, y0 + 2, w - 2.4, h - 2, p)}' fill='${T.c[4]}'/>`;
    const face = hex(2.4, y0 + 2, w - 2.4, yb, p);
    const ins = 6; // la table (la grande facette du milieu)
    const table = hex(2.4 + ins + 2, y0 + 2 + ins * 0.7, w - 2.4 - ins - 2, yb - ins * 0.7, p - ins * 0.35);
    const cl = id('c');
    s += `<clipPath id='${cl}'><path d='${face}'/></clipPath><g clip-path='url(#${cl})'>`;
    s += `<path d='${face}' fill='${T.c[3]}'/>`;
    // facettes du pourtour : en haut (claire), à droite (la plus claire : elle regarde la lumière), en bas et à gauche (sombres)
    s += `<path d='${P([[0, y0], [w, y0], [w, my], [0, my]])}' fill='${T.c[1]}'/>`;
    s += `<path d='${P([[w - p - 2, y0], [w, y0], [w, h], [w - p - 2, h]])}' fill='${T.c[0]}' fill-opacity='0.55'/>`;
    s += `<path d='${P([[0, my], [p + 6, my], [p + 6, h], [0, h]])}' fill='${T.c[4]}' fill-opacity='0.45'/>`;
    // la table : le cœur, sa lumière, et une facette claire en haut
    s += `<path d='${table}' fill='url(#${g1})'/>`;
    if (T.light) s += `<path d='${table}' fill='url(#${g2})'/>`;
    s += `<path d='${hex(2.4 + ins + 2, y0 + 2 + ins * 0.7, w - 2.4 - ins - 2, my + 1, p - ins * 0.35)}' fill='url(#${g3})' fill-opacity='0.55'/>`;
    // une étincelle nette sur l'arête haut-droite
    s += `<path d='M${w - p - 4} ${y0 + 3.2}h${-14}l${2} ${-1.2}h${14}z' fill='#fff' fill-opacity='0.9'/>`;
    s += `</g>`;
    return s;
  }

  /* ================================================================================================================
     4. ÉTENDARD — une bande d'étoffe tendue entre deux embouts de bronze (la bannière d'un clan), un fil d'or brodé
     ================================================================================================================ */
  const ETENDARD = {
    // étoffe [clair, haut, bas, pli], fil (broderie), bronze [clair, moyen, sombre]
    pourpre: { cl: ['#ff8a8a', '#c8304a', '#7c1234', '#560a26'], fil: '#ffcf5a', br: ['#ffe9a8', '#cf8a34', '#6e3412'] },
    nuit: { cl: ['#8a9cff', '#3a3f94', '#1e1f5e', '#141444'], fil: '#e9b94a', br: ['#ffe9a8', '#cf8a34', '#6e3412'] },
    royal: { cl: ['#d9a8ff', '#7a3fd0', '#40178a', '#2c0e66'], fil: '#ffd65a', br: ['#fff2bc', '#e0a640', '#7a3e12'] },
    feu: { cl: ['#ffb07a', '#d9482c', '#8a1a1e', '#5e0e14'], fil: '#ffd65a', br: ['#ffe9a8', '#cf8a34', '#6e3412'] },
    eau: { cl: ['#9ad8ff', '#2a74d0', '#123d86', '#0b2a62'], fil: '#ffd65a', br: ['#ffe9a8', '#cf8a34', '#6e3412'] },
    terre: { cl: ['#ffd08a', '#b8702a', '#6e3a14', '#4a240c'], fil: '#ffe08a', br: ['#ffe9a8', '#cf8a34', '#6e3412'] },
    vent: { cl: ['#a8f0c0', '#2a9a62', '#10583e', '#0a3c2a'], fil: '#ffd65a', br: ['#ffe9a8', '#cf8a34', '#6e3412'] },
    off: { cl: ['#c0bdd0', '#77748e', '#55526a', '#403e54'], fil: '#a9a6bd', br: ['#d8d6e2', '#8c89a0', '#4d4a60'] },
  };
  function etendard(t, w, h, lip, down) {
    const T = ETENDARD[t];
    const y0 = down ? lip - 1 : 0, yb = down ? h - 1 : h - lip;
    const cap = h >= 56 ? 13 : h >= 44 ? 11 : 9; // largeur d'un embout
    const ci = Math.round((yb - y0) * 0.1); // l'étoffe est un peu moins haute que les embouts
    const g1 = id('g'), g2 = id('g'), g3 = id('g');
    let s = `<defs>${lin(g1, 0, y0 + ci, 0, yb - ci, [[0, T.cl[1]], [1, T.cl[2]]])}`;
    s += lin(g2, 0, 0, cap, 0, [[0, T.br[2]], [0.55, T.br[1]], [1, T.br[0]]]);
    s += lin(g3, w - cap, 0, w, 0, [[0, T.br[2]], [0.45, T.br[1]], [1, T.br[0]]]);
    s += `</defs>`;
    // contour unique (étoffe + embouts) et épaisseur
    const outline = (ya, yz) => `M${cap} ${ya + ci}H${w - cap}V${ya}H${w - 3}Q${w} ${ya} ${w} ${ya + 3}V${yz - 3}Q${w} ${yz} ${w - 3} ${yz}H${w - cap}V${yz - ci}H${cap}V${yz}H3Q0 ${yz} 0 ${yz - 3}V${ya + 3}Q0 ${ya} 3 ${ya}H${cap}Z`;
    s += `<path d='${outline(y0, h)}' fill='${INK}' stroke='${INK}' stroke-width='1' stroke-linejoin='round'/>`;
    if (!down) s += `<path d='M${cap} ${h - 2 - ci}H${w - cap}V${yb}H${cap}Z' fill='${T.cl[3]}'/><path d='${rr(2, h - lip - 6, cap - 1, h - 2, 2)}' fill='${T.br[2]}'/><path d='${rr(w - cap + 1, h - lip - 6, w - 2, h - 2, 2)}' fill='#4a200c'/>`;
    // l'étoffe : arête claire en haut, plus sombre près des embouts (elle s'y enroule), un fil d'or brodé en haut et en bas
    const cloth = `M${cap - 1} ${y0 + ci + 2}H${w - cap + 1}V${yb - ci}H${cap - 1}Z`;
    const cl = id('c');
    s += `<clipPath id='${cl}'><path d='${cloth}'/></clipPath><g clip-path='url(#${cl})'>`;
    s += `<path d='${cloth}' fill='${T.cl[0]}'/><path d='${cloth}' fill='url(#${g1})' transform='translate(-1 2)'/>`;
    s += `<path d='M${cap - 1} ${y0}h7V${h}h-7z' fill='${T.cl[3]}' fill-opacity='0.55'/><path d='M${w - cap - 5} ${y0}h6V${h}h-6z' fill='${T.cl[3]}' fill-opacity='0.35'/>`;
    s += `<path d='M${cap - 1} ${y0 + ci + 6}H${w - cap + 1}' stroke='${T.fil}' stroke-width='1.6'/>`;
    s += `<path d='M${cap - 1} ${yb - ci - 4.5}H${w - cap + 1}' stroke='${T.fil}' stroke-opacity='0.8' stroke-width='1.6'/>`;
    s += `</g>`;
    // embouts de bronze : un cylindre éclairé à droite, une perle claire en haut
    for (const [x0, x1, g] of [[2, cap, g2], [w - cap, w - 2, g3]]) {
      s += `<path d='${rr(x0, y0 + 2, x1, yb, 2.5)}' fill='url(#${g})'/>`;
      s += `<path d='M${x0 + 1.5} ${y0 + 4.5}H${x1 - 1.5}' stroke='${T.br[0]}' stroke-width='1.4' stroke-linecap='round' stroke-opacity='0.9'/>`;
      s += `<path d='M${x0 + 1.5} ${yb - 3}H${x1 - 1.5}' stroke='${T.br[2]}' stroke-width='1.6' stroke-linecap='round'/>`;
    }
    return s;
  }

  /* ---------- boutons ronds (pause, automatique, vitesse, fermer) : un dessin entier, pas étiré ---------- */
  function round(fam, t, d, down) {
    const lip = 4, r = d / 2;
    const cy = down ? r + lip - 1 : r, cx = r; // centre de la face
    const g1 = id('g'), g2 = id('g');
    const H = d + lip;
    let s = '';
    if (fam === 'email') {
      const T = EMAIL[t];
      s += `<defs>${lin(g1, d, 0, 0, d, [[0, T.bez[0]], [0.4, T.bez[1]], [1, T.bez[2]]])}${lin(g2, 0, cy - r, 0, cy + r, [[0, T.face[0]], [1, T.face[1]]])}</defs>`;
      // octogone régulier (même coupe que les boutons)
      const o = (rr2, yc) => { const pts = []; for (let i = 0; i < 8; i++) { const a = Math.PI / 8 + i * Math.PI / 4; pts.push([cx + rr2 * Math.cos(a), yc + rr2 * Math.sin(a)]); } return P(pts); };
      const R = r / Math.cos(Math.PI / 8);
      s += `<path d='${o(R, down ? cy : cy + lip / 2)}' fill='${INK}' transform='scale(1 1)'/>`;
      if (!down) s += `<path d='${o(R - 2, cy + lip - 0.5)}' fill='${T.lip}'/>`;
      s += lit(o(R - 2, cy), T.bez[0], `url(#${g1})`, 1.4, 1.4);
      const en = o(R - 6, cy); const c2 = id('c');
      s += `<clipPath id='${c2}'><path d='${en}'/></clipPath><g clip-path='url(#${c2})'><path d='${en}' fill='${T.bez[2]}'/><path d='${en}' fill='url(#${g2})' transform='translate(-1.4 1.4)'/>`;
      s += `<path d='M${cx + r * 0.12} ${cy - r * 0.6}h${r * 0.38}l-2.5 2.6h${-r * 0.38}z' fill='#fff' fill-opacity='0.5'/></g>`;
    } else if (fam === 'pierre') {
      const T = PIERRE[t];
      s += `<defs>${lin(g1, d * 0.8, cy - r, d * 0.2, cy + r, [[0, T.st[1]], [1, T.st[2]]])}`;
      if (T.light) s += rad(g2, cx, cy, r * 0.8, r * 0.8, [[0, T.light, 0.55], [1, T.light, 0]]);
      s += `</defs>`;
      // une pierre ronde un peu irrégulière (galet taillé)
      const blob = (rad2, yc) => { const pts = []; const k = [1, 0.97, 1.01, 0.96, 1, 0.98, 1.02, 0.95, 1, 0.97, 1.01, 0.97]; for (let i = 0; i < 12; i++) { const a = i * Math.PI / 6; pts.push([cx + rad2 * k[i] * Math.cos(a), yc + rad2 * k[i] * Math.sin(a)]); } return P(pts); };
      s += `<path d='${blob(r, down ? cy : cy + lip / 2)}' fill='${INK}' stroke='${INK}' stroke-width='1.5' stroke-linejoin='round'/>`;
      if (!down) s += `<path d='${blob(r - 2, cy + lip - 0.5)}' fill='${T.st[3]}' stroke='${T.st[3]}' stroke-linejoin='round'/>`;
      s += lit(blob(r - 2, cy), T.st[0], `url(#${g1})`, 2.2, 2.2, T.light ? `<path d='${blob(r - 2, cy)}' fill='url(#${g2})'/>` : '');
    } else if (fam === 'cristal') {
      const T = CRISTAL[t];
      // un hexagone posé sur la pointe (une gemme ronde, taillée)
      const hx = (rad2, yc) => { const pts = []; for (let i = 0; i < 6; i++) { const a = -Math.PI / 2 + i * Math.PI / 3; pts.push([cx + rad2 * Math.cos(a), yc + rad2 * Math.sin(a)]); } return P(pts); };
      const R = r * 1.06;
      s += `<defs>${lin(g1, 0, cy - R, 0, cy + R, [[0, T.c[1]], [0.5, T.c[2]], [1, T.c[3]]])}`;
      if (T.light) s += rad(g2, cx, cy + 1, r * 0.6, r * 0.6, [[0, T.light, down ? 0.95 : 0.65], [1, T.light, 0]]);
      s += `</defs>`;
      s += `<path d='${hx(R, down ? cy : cy + lip / 2)}' fill='${INK}' stroke='${INK}' stroke-width='2' stroke-linejoin='round'/>`;
      if (!down) s += `<path d='${hx(R - 2, cy + lip - 0.5)}' fill='${T.c[4]}'/>`;
      const f = hx(R - 2, cy); const c2 = id('c');
      s += `<clipPath id='${c2}'><path d='${f}'/></clipPath><g clip-path='url(#${c2})'><path d='${f}' fill='${T.c[3]}'/>`;
      s += `<path d='M${cx} ${cy - R}L${cx + R} ${cy - R}L${cx + R} ${cy + R}L${cx} ${cy}Z' fill='${T.c[0]}' fill-opacity='0.5'/>`;
      s += `<path d='M${cx - R} ${cy - R}L${cx} ${cy - R}L${cx} ${cy}Z' fill='${T.c[1]}'/>`;
      s += `<path d='${hx(R - 7, cy)}' fill='url(#${g1})'/>`;
      if (T.light) s += `<path d='${hx(R - 7, cy)}' fill='url(#${g2})'/>`;
      s += `<path d='M${cx + 3} ${cy - R + 4.5}l${R * 0.42} ${R * 0.24}l-0.6 1.6l${-R * 0.42} ${-R * 0.24}z' fill='#fff' fill-opacity='0.85'/></g>`;
    } else {
      const T = ETENDARD[t];
      // un bouclier rond de bronze, l'étoffe au milieu
      s += `<defs>${lin(g1, d, 0, 0, d, [[0, T.br[0]], [0.45, T.br[1]], [1, T.br[2]]])}${lin(g2, 0, cy - r, 0, cy + r, [[0, T.cl[1]], [1, T.cl[2]]])}</defs>`;
      s += `<path d='${circ(cx, down ? cy : cy + lip / 2, r)}' fill='${INK}'/>`;
      if (!down) s += `<path d='${circ(cx, cy + lip - 0.5, r - 2)}' fill='${T.br[2]}'/>`;
      s += lit(circ(cx, cy, r - 2), T.br[0], `url(#${g1})`, 1.4, 1.4);
      const inner = circ(cx, cy, r - 6.5); const c2 = id('c');
      s += `<clipPath id='${c2}'><path d='${inner}'/></clipPath><g clip-path='url(#${c2})'><path d='${inner}' fill='${T.cl[3]}'/><path d='${inner}' fill='url(#${g2})' transform='translate(-1.4 1.6)'/></g>`;
    }
    return url(d, H, s);
  }

  const FAMILIES = {
    email: { draw: email, tones: Object.keys(EMAIL), L: { xxl: 21, xl: 19, l: 18, m: 15, s: 12 } },
    pierre: { draw: pierre, tones: Object.keys(PIERRE), L: { xxl: 23, xl: 21, l: 20, m: 17, s: 14 } },
    cristal: { draw: cristal, tones: Object.keys(CRISTAL), L: { xxl: 40, xl: 34, l: 30, m: 24, s: 19 } },
    etendard: { draw: etendard, tones: Object.keys(ETENDARD), L: { xxl: 22, xl: 21, l: 20, m: 18, s: 15 } },
  };

  function installButtons(root = document.documentElement) {
    const st = root.style;
    for (const [fam, F] of Object.entries(FAMILIES)) {
      for (const t of F.tones) {
        for (const [sz, { h, lip }] of Object.entries(SIZES)) {
          const L = F.L[sz], w = 2 * L + 40;
          for (const down of [false, true]) {
            st.setProperty(`--bt-${fam}-${t}-${sz}${down ? '-down' : ''}`, url(w, h, F.draw(t, w, h, lip, down)));
          }
        }
        for (const down of [false, true]) st.setProperty(`--bt-${fam}-rond-${t}${down ? '-down' : ''}`, round(fam, t, 44, down));
      }
    }
  }
  // les réglages d'un bouton (à poser dans son style) : dessin, dessin enfoncé, bouts, hauteur, épaisseur, couleurs du texte
  function buttonVars(fam, t, sz) {
    const F = FAMILIES[fam], { h, lip } = SIZES[sz], L = F.L[sz];
    const v = { '--sk': `var(--bt-${fam}-${t}-${sz})`, '--skd': `var(--bt-${fam}-${t}-${sz}-down)`, '--Ln': L, '--L': L + 'px', '--h': h + 'px', '--lip': lip + 'px' };
    Object.assign(v, textVars(fam, t));
    return v;
  }
  function textVars(fam, t) {
    if (fam === 'email') {
      if (t === 'or') return { '--tc': '#4a1a06', '--ts': '-1px 1px 0 #fff6c4b3' };
      if (t === 'off') return { '--tc': '#d6d3e4', '--ts': '0 2px 0 #2c2a3f99' };
      return { '--tc': '#fff4dc', '--ts': `0 2px 0 ${EMAIL[t].face[1]}, 0 0 2px ${EMAIL[t].face[1]}` };
    }
    if (fam === 'pierre') {
      const T = PIERRE[t];
      if (T.light) return { '--tc': T.core, '--ts': `0 0 5px ${T.light}, 0 0 12px ${T.light}, 0 2px 0 #0a061499` };
      if (t === 'ardoise') return { '--tc': '#332e4c', '--ts': '-1px 1px 0 #ffffff80' };
      return { '--tc': '#9e9ab6', '--ts': '-1px 1px 0 #0000004d' };
    }
    if (fam === 'cristal') {
      const T = CRISTAL[t];
      return { '--tc': t === 'off' ? '#f4f3fa' : '#ffffff', '--ts': `0 2px 0 ${T.c[4]}, 0 0 2px ${T.c[4]}${T.light ? `, 0 0 10px ${T.light}` : ''}` };
    }
    const T = ETENDARD[t];
    return { '--tc': t === 'off' ? '#e6e4ee' : '#fff3d6', '--ts': `0 2px 0 ${T.cl[3]}, 0 0 2px ${T.cl[3]}` };
  }
  function roundVars(fam, t) {
    return { '--skr': `var(--bt-${fam}-rond-${t})`, '--skrd': `var(--bt-${fam}-rond-${t}-down)`, ...textVars(fam, t) };
  }
  window.BT = { installButtons, buttonVars, roundVars, textVars, PAL: { EMAIL, PIERRE, CRISTAL, ETENDARD }, SIZES };
})();
