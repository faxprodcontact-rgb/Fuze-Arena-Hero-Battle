// Héros « vectoriels » : redessinés par le code d'après le dessin d'origine, dans le trait net des décors du jeu.
//
// Un héros est une liste de morceaux, du fond vers le devant. Chaque morceau a une silhouette (`d`) et un habillage
// (`body` : couleurs, ombres, reflets, traits). Le dessin se fait en deux passes :
//   1. toutes les silhouettes en sombre avec un trait épais → UN SEUL contour autour du personnage entier ;
//   2. toutes les couleurs par-dessus, qui recouvrent les traits intérieurs.
// Jamais de contour par morceau : là où deux morceaux se chevauchent, c'est une ombre portée qui les sépare
// (`shadow` : la silhouette du morceau, décalée, coupée par les morceaux qui la reçoivent).
// Pas de filtre SVG (trop lent une fois animé) : seulement des formes, des dégradés et des découpes.

/**
 * @param parts [{ id, d, body, cls?, shadow?, rim? }]
 *   cls    : classe d'animation (le contour, l'ombre et les couleurs du morceau bougent ensemble) ;
 *   shadow : [{ on: [ids des morceaux qui reçoivent l'ombre], dx, dy, color, o }]
 *   rim    : { on: [ids], color, w, o? } = filet fin, seulement là où le morceau passe devant ceux de la liste
 *            (peau sur peau : un bras devant le torse). Ce n'est pas un contour : il ne fait jamais le tour du morceau.
 * @param anime  true = image vivante (marge autour pour que rien ne soit coupé en bougeant), false = image fixe au cadre exact
 */
function figure({ w, h, pad = 24, outline = '#2a1430', ow = 4.4, defs = '', style = '', parts, anime = true }) {
  const m = anime ? pad : 0;
  const sil = parts.map((p) => `<path id="s-${p.id}" d="${p.d}"/>`).join('');
  const clips = parts.map((p) => `<clipPath id="c-${p.id}"><use href="#s-${p.id}"/></clipPath>`).join('');
  const wrap = (p, inner) => (p.cls && anime ? `<g class="${p.cls}">${inner}</g>` : inner);
  let unions = '';
  const union = (cid, on) => { unions += `<clipPath id="${cid}">${on.map((o) => `<use href="#s-${o}"/>`).join('')}</clipPath>`; return cid; };
  const ol = parts.map((p) => wrap(p, `<use href="#s-${p.id}"/>`)).join('');
  const col = parts.map((p) => {
    let under = '';
    (p.shadow || []).forEach((s, i) => {
      const cid = union(`u-${p.id}-${i}`, s.on);
      under += `<g clip-path="url(#${cid})">${wrap(p, `<use href="#s-${p.id}" transform="translate(${s.dx} ${s.dy})" fill="${s.color}" opacity="${s.o}"/>`)}</g>`;
    });
    if (p.rim) {
      const cid = union(`r-${p.id}`, p.rim.on);
      under += `<g clip-path="url(#${cid})">${wrap(p, `<use href="#s-${p.id}" fill="none" stroke="${p.rim.color}" stroke-width="${p.rim.w * 2}"${p.rim.o ? ` opacity="${p.rim.o}"` : ''}/>`)}</g>`;
    }
    return under + wrap(p, p.body);
  }).join('');
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="${-m} ${-m} ${w + 2 * m} ${h + 2 * m}" width="${w + 2 * m}" height="${h + 2 * m}">`
    + `<defs>${defs}${sil}${clips}${unions}</defs>${anime && style ? `<style>${style}</style>` : ''}`
    + `<g fill="${outline}" stroke="${outline}" stroke-width="${ow * 2}" stroke-linejoin="round" stroke-linecap="round">${ol}</g>`
    + `<g stroke-linecap="round" stroke-linejoin="round">${col}</g></svg>`;
}

/** Dégradé en ligne. `stops` = [[position, couleur, opacité?]] ; `user` = coordonnées du dessin (sinon de 0 à 1 dans la forme). */
function lin(id, x1, y1, x2, y2, stops, user = true) {
  return `<linearGradient id="${id}" x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}"${user ? ' gradientUnits="userSpaceOnUse"' : ''}>${stopsOf(stops)}</linearGradient>`;
}

/** Dégradé en rond. */
function rad(id, cx, cy, r, stops, user = true, extra = '') {
  return `<radialGradient id="${id}" cx="${cx}" cy="${cy}" r="${r}"${user ? ' gradientUnits="userSpaceOnUse"' : ''}${extra}>${stopsOf(stops)}</radialGradient>`;
}

function stopsOf(stops) {
  return stops.map(([o, c, a]) => `<stop offset="${o}" stop-color="${c}"${a === undefined ? '' : ` stop-opacity="${a}"`}/>`).join('');
}

const n = (v) => +v.toFixed(1);

// ---------- petits outils de dessin, communs à tous les héros ----------
const use = (id, fill) => `<use href="#s-${id}" fill="${fill}"/>`;
const clip = (id, inner) => `<g clip-path="url(#c-${id})">${inner}</g>`;
const line = (d, color, w = 2, o = 1) => `<path d="${d}" fill="none" stroke="${color}" stroke-width="${w}"${o < 1 ? ` opacity="${o}"` : ''}/>`;
const shape = (d, fill, o = 1) => `<path d="${d}" fill="${fill}"${o < 1 ? ` opacity="${o}"` : ''}/>`;
const dot = (cx, cy, r, fill, o = 1) => `<circle cx="${cx}" cy="${cy}" r="${r}" fill="${fill}"${o < 1 ? ` opacity="${o}"` : ''}/>`;
const oval = (cx, cy, rx, ry, fill, o = 1, rot = 0) => `<ellipse cx="${cx}" cy="${cy}" rx="${rx}" ry="${ry}" fill="${fill}"${o < 1 ? ` opacity="${o}"` : ''}${rot ? ` transform="rotate(${rot} ${cx} ${cy})"` : ''}/>`;

module.exports = { figure, lin, rad, n, use, clip, line, shape, dot, oval };
