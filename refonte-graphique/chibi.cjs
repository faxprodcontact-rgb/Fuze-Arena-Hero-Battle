// Personnage « chibi » de trois-quarts, tourné vers la droite (2,5 têtes de haut), entièrement paramétrable.
// Repère : boîte 240 × 260, pieds à y = 250, centre du corps à x = 120.
const { painter, tone, metal, mix, ln, sf, blob } = require('./kit.cjs');

const HEAD = 'M122 34 C152 32 174 52 176 82 C177 98 172 112 160 122 C152 130 140 134 128 134 C106 134 84 124 74 104 C64 82 70 52 92 40 C101 35 111 34 122 34 Z';
const TORSO = 'M90 134 C104 126 136 126 150 134 C154 150 154 168 148 184 C134 192 104 192 92 184 C86 168 86 150 90 134 Z';

function eye(cx, cy, w, h, color, o = {}) {
  const id = 'e' + Math.round(cx * 100 + cy) + (o.k ?? '');
  const white = `M${cx - w / 2} ${cy - h * 0.22} C${cx - w / 4} ${cy - h / 2 - 1} ${cx + w / 4} ${cy - h / 2 - 1} ${cx + w / 2} ${cy - h * 0.18} C${cx + w / 2 + 1} ${cy + h * 0.2} ${cx + w / 4} ${cy + h / 2} ${cx} ${cy + h / 2} C${cx - w / 4} ${cy + h / 2} ${cx - w / 2 - 1} ${cy + h * 0.2} ${cx - w / 2} ${cy - h * 0.22} Z`;
  const lash = `M${cx - w / 2 - 2.5} ${cy - h * 0.2} C${cx - w / 4} ${cy - h / 2 - 5.5} ${cx + w / 4} ${cy - h / 2 - 5.5} ${cx + w / 2 + 2.5} ${cy - h * 0.15} L${cx + w / 2} ${cy - h * 0.06} C${cx + w / 4} ${cy - h / 2 + 1.5} ${cx - w / 4} ${cy - h / 2 + 1.5} ${cx - w / 2} ${cy - h * 0.1} Z`;
  const ix = cx + w * 0.07, iy = cy + 1.2, irx = w * 0.37, iry = h * 0.43;
  let s = `<defs><clipPath id="${id}c"><path d="${white}"/></clipPath><linearGradient id="${id}g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${mix(color, '#12081c', 0.62)}"/><stop offset="0.55" stop-color="${color}"/><stop offset="1" stop-color="${mix(color, '#ffffff', 0.4)}"/></linearGradient></defs>`;
  s += `<path d="${white}" fill="${o.sclera ?? '#fbf6ef'}"/><g clip-path="url(#${id}c)">`;
  s += `<rect x="${cx - w}" y="${cy - h / 2 - 2}" width="${w * 2}" height="${h * 0.34}" fill="#3b2550" opacity="0.3"/>`;
  s += `<ellipse cx="${ix}" cy="${iy}" rx="${irx}" ry="${iry}" fill="url(#${id}g)"/>`;
  s += `<ellipse cx="${ix}" cy="${iy}" rx="${irx}" ry="${iry}" fill="none" stroke="${mix(color, '#12081c', 0.7)}" stroke-width="1.3"/>`;
  if (o.slit) s += `<ellipse cx="${ix}" cy="${iy}" rx="${w * 0.07}" ry="${iry * 0.8}" fill="#170a12"/>`;
  else s += `<ellipse cx="${ix + 0.5}" cy="${iy + 0.5}" rx="${irx * 0.5}" ry="${iry * 0.5}" fill="#170a12"/>`;
  s += `<ellipse cx="${ix}" cy="${iy + iry * 0.62}" rx="${irx * 0.6}" ry="${iry * 0.22}" fill="${mix(color, '#ffffff', 0.6)}" opacity="0.7"/>`;
  s += `<circle cx="${cx - w * 0.14}" cy="${cy - h * 0.2}" r="${w * 0.14}" fill="#fff"/><circle cx="${cx + w * 0.22}" cy="${cy + h * 0.2}" r="${w * 0.06}" fill="#fff" opacity="0.9"/>`;
  s += `</g><path d="${lash}" fill="${o.lash ?? '#2a1424'}"/>`;
  if (o.glow) s += `<ellipse cx="${ix}" cy="${iy}" rx="${irx * 1.5}" ry="${iry * 1.3}" fill="${color}" opacity="0.5" filter="url(#glow)"/>`;
  return s;
}

/** Lame droite : de la garde `a` vers la pointe `b`, largeur `w`. */
function blade(a, b, w, tip = 0.82) {
  const v = [b[0] - a[0], b[1] - a[1]], len = Math.hypot(...v), u = [v[0] / len, v[1] / len], n = [-u[1], u[0]];
  const at = (t, k) => [a[0] + u[0] * t * len + n[0] * k, a[1] + u[1] * t * len + n[1] * k];
  const p = (q) => `${q[0].toFixed(1)} ${q[1].toFixed(1)}`;
  return {
    d: `M${p(at(0, -w / 2))} L${p(at(tip, -w / 2 * 0.86))} L${p(at(1, 0))} L${p(at(tip, w / 2 * 0.86))} L${p(at(0, w / 2))} Z`,
    mid: `M${p(at(0.04, 0))} L${p(at(tip - 0.06, 0))}`, edge: `M${p(at(0.02, w / 2 * 0.72))} L${p(at(tip, w / 2 * 0.62))} L${p(at(0.985, 0.6))}`,
    edge2: `M${p(at(0.02, -w / 2 * 0.72))} L${p(at(tip, -w / 2 * 0.62))}`, at, p,
  };
}
const quad = (a, b, w) => { const bl = blade(a, b, w, 1); const { at, p } = bl; return `M${p(at(0, -w / 2))} L${p(at(1, -w / 2))} L${p(at(1, w / 2))} L${p(at(0, w / 2))} Z`; };

function chibi(c) {
  const P = painter(c.light ?? [0.5, -0.85]);
  const { S, raw, cast } = P;
  const T = {};
  for (const [k, v] of Object.entries(c.colors)) T[k] = typeof v === 'string' ? tone(v) : v;
  const skin = T.skin, hair = T.hair, cloth = T.cloth, cloth2 = T.cloth2 ?? T.cloth, steel = T.metal ?? metal('#b9c0d0'), gold = T.gold ?? metal('#e6ac3c');
  const leather = T.leather ?? tone('#7a4a2c'), boot = T.boot ?? tone('#5a3826'), accent = T.accent ?? cloth;
  const dark = '#1b0d26';

  // ================= 1. Derrière le personnage =================
  if (c.back === 'cape' || c.cape) {
    const cp = S('M94 132 C70 138 50 162 42 192 C36 212 28 230 14 246 C38 252 60 246 84 252 C94 222 100 180 102 140 Z', T.cape ?? accent, { sh: 12, inner:
      sf('M70 160 C60 196 48 224 34 246', (T.cape ?? accent).shadow, 9, 0.6, 3) + sf('M88 160 C84 200 76 228 66 250', (T.cape ?? accent).shadow, 9, 0.5, 3) +
      sf('M80 158 C74 196 62 226 50 248', (T.cape ?? accent).light, 4, 0.45, 2) +
      ln('M14 245 C38 251 60 245 84 251', gold.base, 5) + ln('M14 243.5 C38 249.5 60 243.5 84 249.5', gold.light, 1.2, 0.9) });
    void cp;
  }
  if (c.scarf) {
    S('M96 130 C74 124 50 130 28 148 C50 150 72 150 96 146 Z', T.scarf, { inner: sf('M90 136 C70 134 52 138 36 146', T.scarf.light, 3, 0.6, 1) });
    S('M94 138 C76 146 62 162 56 182 C74 172 90 160 102 148 Z', T.scarf, { inner: sf('M92 144 C80 152 70 164 62 176', T.scarf.shadow, 4, 0.5, 2) });
  }
  if (c.hairStyle === 'long') {
    S('M70 70 C56 100 50 140 44 176 C40 196 34 210 26 222 C46 224 66 214 80 198 C92 180 98 150 100 120 Z', hair, { sh: 10, inner:
      sf('M72 96 C64 136 56 176 40 216', hair.shadow, 5, 0.6) + sf('M86 104 C82 146 74 180 60 208', hair.shadow, 4, 0.5) + ln('M80 100 C74 140 66 176 52 208', hair.light, 1.6, 0.8) });
    S('M66 80 C58 44 88 18 124 18 C160 18 186 44 182 80 C180 96 174 108 170 118 L80 120 C72 108 68 94 66 80 Z', hair, {});
  }
  if (c.hairStyle === 'spiky') {
    for (const d of ['M78 62 L38 40 L68 86 Z', 'M72 86 L30 88 L72 108 Z', 'M94 30 L72 0 L116 22 Z', 'M124 22 L130 -8 L152 22 Z', 'M158 28 L182 6 L176 44 Z', 'M82 44 L50 14 L98 30 Z']) S(d, hair, { sh: 5 });
    S('M70 98 C58 70 64 38 92 24 C122 12 162 18 178 42 C186 58 184 74 178 86 L76 112 Z', hair, {});
  }
  if (c.hood) {
    S('M72 46 C56 36 38 40 24 54 C42 54 58 60 68 74 Z', T.hood, {});
    S('M60 98 C48 54 80 14 124 12 C166 10 194 42 188 86 L176 100 L84 124 C70 118 64 108 60 98 Z', T.hood, {});
  }
  if (c.ears === 'goblin') S('M170 74 C184 62 200 58 212 62 C202 74 192 86 178 94 Z', skin, { far: true, inner: sf('M176 78 C186 70 196 66 204 66', skin.shadow, 3, 0.6, 1) });
  if (c.quiver) {
    S('M58 118 L82 108 L100 170 L78 180 Z', leather, { inner: ln('M62 128 L86 118 M70 150 L92 142', gold.base, 2.4) });
    for (const [x, y] of [[56, 104], [66, 98], [76, 100]]) raw(`<path d="M${x} ${y + 16} L${x - 6} ${y - 6} L${x + 2} ${y} L${x + 4} ${y - 10} L${x + 8} ${y + 12} Z" fill="${accent.base}" stroke="${accent.outline}" stroke-width="1.4"/>`);
  }

  // ================= 2. Jambes et bras du fond =================
  const robe = c.outfit === 'robe';
  if (!robe) {
    const lf = S('M120 180 C126 196 134 208 138 220 L158 216 C154 202 148 190 144 178 Z', cloth2, { far: true });
    S('M130 214 C128 228 130 240 134 248 L178 248 C182 240 174 230 164 224 C158 216 142 210 130 214 Z', boot, { far: true, inner: ln('M136 243 L177 243', boot.outline, 2.4, 0.7) + sf('M150 222 C160 224 168 230 172 236', boot.light, 2, 0.6, 1) });
    void lf;
  }
  if (c.farArm !== false) S('M140 140 C152 148 162 158 168 170 L156 178 C150 168 142 160 134 154 Z', T.sleeve ?? cloth, { far: true });

  // ================= 3. Jambe avant, torse, tenue =================
  if (!robe) {
    const ln2 = S('M96 180 C92 196 90 210 90 222 L112 224 C114 210 118 196 120 182 Z', cloth2, {});
    const bt = S('M82 218 C80 232 80 242 84 250 L128 250 C132 242 126 232 116 226 C110 220 92 214 82 218 Z', boot, { inner: ln('M86 245 L127 245', boot.outline, 2.4, 0.7) + sf('M100 224 C110 226 118 232 122 238', boot.light, 2, 0.7, 1) });
    S('M80 214 C92 208 108 208 118 214 L118 226 C108 221 92 221 80 227 Z', c.outfit === 'plate' ? steel : leather, { inner: c.outfit === 'plate' ? ln('M84 217 C94 213 106 213 115 217', '#fff', 1.6, 0.8) : ln('M98 211 L98 224', gold.base, 3) });
    if (c.outfit === 'plate') S('M88 196 C92 188 108 188 112 196 C114 206 108 212 100 212 C92 212 86 206 88 196 Z', steel, { inner: ln('M91 196 C96 191 104 191 109 196', '#fff', 1.6, 0.85) + `<circle cx="100" cy="201" r="2.2" fill="${steel.shadow}"/>` });
    void ln2; void bt;
  }
  let torso;
  if (robe) {
    torso = S('M90 134 C104 126 136 126 150 134 C158 160 168 204 178 244 C144 254 96 254 66 246 C76 206 84 166 90 134 Z', cloth, { sh: 10, inner:
      sf('M100 190 C96 212 90 232 84 248', cloth.shadow, 7, 0.5, 3) + sf('M150 190 C156 212 162 230 168 246', cloth.shadow, 7, 0.5, 3) + sf('M112 196 C110 216 106 234 102 250', cloth.light, 3, 0.5, 2) +
      `<path d="M118 132 C116 170 112 210 104 252 L146 252 C140 210 136 170 136 132 Z" fill="${accent.base}"/><path d="M118 132 C116 170 112 210 104 252 L146 252 C140 210 136 170 136 132 Z" fill="url(#vol)"/>` +
      ln('M118 132 C116 170 112 210 104 252', gold.base, 3) + ln('M136 132 C136 170 140 210 146 252', gold.base, 3) +
      `<path d="M127 196 l7 10 l-7 10 l-7 -10 Z" fill="${gold.base}" stroke="${gold.outline}" stroke-width="1.2"/><path d="M127 200 l4 6 l-4 6" fill="${gold.light}"/>` +
      ln('M68 240 C96 248 144 248 176 238', gold.base, 4) + ln('M68 238 C96 246 144 246 176 236', gold.light, 1.2, 0.8) });
    S('M112 244 C112 238 126 238 130 246 L130 252 L110 252 Z', boot, {});
    S('M88 172 C108 180 134 180 152 172 L153 184 C134 192 108 192 88 185 Z', T.sash ?? gold, { inner: ln('M90 175 C108 183 134 183 151 175', (T.sash ?? gold).light, 1.4, 0.8) });
  } else {
    torso = S(TORSO, cloth, { inner: sf('M96 150 C94 164 96 176 100 184', cloth.shadow, 6, 0.4, 3) });
    S('M86 180 C84 194 82 204 80 212 C102 222 138 222 160 210 C158 200 156 190 152 180 C134 190 106 190 86 180 Z', c.outfit === 'plate' ? cloth2 : cloth2, { inner:
      sf('M100 190 C98 200 96 208 94 216', cloth2.shadow, 5, 0.6) + sf('M124 192 C124 202 124 210 124 218', cloth2.shadow, 5, 0.5) + sf('M112 192 C111 202 110 210 109 218', cloth2.light, 2.4, 0.5, 1) +
      ln('M80 211 C102 221 138 221 160 209', gold.base, 3) });
    if (c.outfit === 'plate') {
      S('M96 136 C108 130 136 130 148 136 C152 150 150 164 144 174 C132 180 108 180 100 174 C92 162 92 148 96 136 Z', T.plate ?? steel, { inner:
        ln('M132 132 C138 146 138 162 132 178', '#ffffff', 2.6, 0.85) + ln('M135.5 133 C141.5 147 141.5 162 135.5 177', (T.plate ?? steel).shadow, 1.8, 0.6) +
        sf('M144 140 C148 150 148 162 144 170', '#ffffff', 5, 0.5, 2) + sf('M100 142 C96 154 98 166 104 174', '#1d1840', 6, 0.35, 3) +
        (c.emblem ?? '') +
        [[102, 142], [104, 170], [144, 142]].map(([x, y]) => `<circle cx="${x}" cy="${y}" r="2.2" fill="${(T.plate ?? steel).shadow}"/><circle cx="${x - 0.6}" cy="${y - 0.6}" r="1" fill="#fff"/>`).join('') });
    } else {
      raw(ln('M96 138 C112 152 134 166 150 178', leather.base, 6) + ln('M96 136.5 C112 150.5 134 164.5 150 176.5', leather.light, 1.4, 0.8));
      raw(`<circle cx="124" cy="158" r="5" fill="${gold.outline}"/><circle cx="124" cy="158" r="3.6" fill="${gold.base}"/><circle cx="123" cy="157" r="1.4" fill="${gold.light}"/>`);
    }
    S('M88 172 C108 181 134 181 152 172 L153 185 C134 194 108 194 88 186 Z', leather, { inner: ln('M90 175.5 C108 184 134 184 151 175.5', leather.light, 1.3, 0.8) });
    raw(`<rect x="124" y="174" width="17" height="17" rx="3.5" fill="${gold.outline}"/><rect x="125.6" y="175.4" width="13.8" height="13.8" rx="2.6" fill="${gold.base}"/><rect x="129" y="179" width="7" height="7" rx="1.5" fill="${leather.shadow}"/><path d="M126.6 177 L138.4 177" stroke="${gold.light}" stroke-width="1.4"/>`);
  }
  // ombre de la tête sur le buste
  cast(torso, `<ellipse cx="124" cy="132" rx="46" ry="15" fill="#1a0c2e" filter="url(#g3)"/>`, 0.5);

  // ================= 4. Arme posée sur l'épaule (derrière la tête) =================
  if (c.weapon === 'hammerShoulder' || c.weapon === 'axeShoulder' || c.weapon === 'clubShoulder') {
    const a = [132, 172], b = [44, 78];
    S(quad(a, b, 9), T.haft ?? tone('#8a5a34'), { inner: ln(`M128 166 L124 172 M120 158 L116 164 M112 150 L108 156`, '#3a2414', 2) });
    if (c.weapon === 'hammerShoulder') {
      raw('<g transform="rotate(-43 46 80)">');
      S('M14 58 L78 58 L82 66 L82 94 L78 102 L14 102 L10 94 L10 66 Z', steel, { inner: ln('M16 62 L76 62', '#fff', 2.4, 0.85) + `<rect x="36" y="58" width="20" height="44" fill="${gold.base}"/><rect x="36" y="58" width="20" height="44" fill="url(#vol)"/>` + ln('M38 60 L38 100', gold.light, 1.6, 0.9) + `<path d="M46 70 l6 10 l-6 10 l-6 -10 Z" fill="${accent.base}" stroke="${accent.outline}" stroke-width="1.2"/>` });
      raw('</g>');
    } else if (c.weapon === 'axeShoulder') {
      raw('<g transform="rotate(-43 46 80)">');
      S('M40 60 C20 44 2 50 -8 70 C-10 88 -4 108 12 118 C22 104 34 100 46 100 Z', steel, { sh: 9, inner: sf('M-4 72 C-4 88 2 102 12 112', '#fff', 4, 0.9, 1) + ln('M34 66 C22 56 8 58 0 70', steel.shadow, 2, 0.7) });
      S('M40 56 L58 56 L58 104 L40 104 Z', tone('#3c3350'), {});
      S('M58 64 L78 72 L78 88 L58 96 Z', steel, {});
      raw('</g>');
    } else {
      raw('<g transform="rotate(-43 46 80)">');
      S('M20 60 C36 52 60 54 72 66 C80 78 78 94 66 102 C50 108 28 106 18 94 C12 82 12 68 20 60 Z', T.haft ?? tone('#8a5a34'), { inner: [[28, 66], [48, 60], [66, 74], [60, 96], [36, 100], [20, 84]].map(([x, y]) => `<path d="M${x} ${y} l5 -9 l5 9 Z" fill="#d9d2c4" stroke="#4a4038" stroke-width="1.2"/>`).join('') });
      raw('</g>');
    }
  }

  // ================= 5. Tête =================
  S('M112 124 L138 124 L136 140 L114 140 Z', skin, { rim: false });
  if (c.scarf) S('M94 126 C108 138 138 138 154 126 L154 141 C138 151 108 151 94 141 Z', T.scarf, { inner: sf('M100 134 C116 142 134 142 148 134', T.scarf.shadow, 4, 0.5, 2) + ln('M98 130 C114 140 136 140 150 130', T.scarf.light, 1.4, 0.7) });
  const head = S(HEAD, skin, { sh: 11, hl: 6, inner:
    blob('M150 122 C140 132 116 132 100 122 C112 138 142 138 156 126 Z', skin.shadow, 0.5, 2) +
    `<ellipse cx="110" cy="110" rx="12" ry="6.5" fill="${c.blush ?? '#ff7d6e'}" opacity="0.4" filter="url(#g2)"/><ellipse cx="168" cy="106" rx="7" ry="5.5" fill="${c.blush ?? '#ff7d6e'}" opacity="0.36" filter="url(#g2)"/>` });
  // oreille
  if (c.ears === 'elf') S('M90 90 C72 80 52 68 36 64 C50 82 66 100 82 110 C88 110 92 100 90 90 Z', skin, { inner: sf('M84 94 C72 86 58 76 46 70', skin.shadow, 3, 0.6, 1) });
  else if (c.ears === 'goblin') S('M90 84 C66 68 42 66 22 74 C40 86 56 104 80 112 C88 110 94 96 90 84 Z', skin, { inner: sf('M84 90 C68 78 50 74 34 76', skin.shadow, 4, 0.6, 1) + ln('M82 96 C70 88 58 84 46 82', skin.light, 1.4, 0.6) });
  else if (!c.hood && c.helmet !== 'horned') S('M86 86 C76 82 70 92 73 102 C76 110 84 112 90 106 Z', skin, { inner: ln('M84 92 C78 94 77 100 80 105', skin.shadow, 2.4) });
  // visage
  const E = c.eyes ?? {};
  if (c.mouth === 'beard') {
    S('M94 106 C108 120 150 120 172 102 C176 122 166 142 148 150 C130 156 108 148 98 132 C94 124 92 114 94 106 Z', hair, { sh: 9, inner:
      sf('M108 122 C110 134 116 142 124 148', hair.shadow, 4, 0.6) + sf('M132 124 C132 136 134 144 138 150', hair.shadow, 4, 0.5) + ln('M120 124 C120 134 124 142 130 148', hair.light, 1.4, 0.8) + ln('M146 120 C148 130 148 138 146 146', hair.light, 1.4, 0.7) });
    S('M122 110 C132 104 146 104 156 108 C150 118 132 118 122 110 Z', hair, { sh: 4 });
  }
  raw(eye(128, 94, E.w ?? 24, E.h ?? 26, E.color ?? '#3f7fd6', { ...E, k: 'n' + (c.id ?? '') }));
  raw(eye(160, 92, (E.w ?? 24) * 0.62, (E.h ?? 26) * 0.92, E.color ?? '#3f7fd6', { ...E, k: 'f' + (c.id ?? '') }));
  const bc = c.browColor ?? hair.shadow;
  if (c.brows !== false) raw(c.angry
    ? `<path d="M108 66 C120 66 134 72 146 82 L143 87 C133 79 121 75 109 73 Z" fill="${bc}"/><path d="M152 82 C158 74 166 68 174 66 L174 72 C166 74 160 80 154 86 Z" fill="${bc}"/>`
    : `<path d="M110 70 C120 65 134 68 145 76 L143 81.5 C133 75 121 72 111 76 Z" fill="${bc}"/><path d="M152 76 C158 70 166 67 173 67 L173 73 C166 73 159 77 153 81.5 Z" fill="${bc}"/>`);
  if (c.nose === 'goblin') S('M146 100 C158 98 172 104 180 114 C168 118 154 116 146 110 Z', skin, { sh: 4, inner: `<circle cx="166" cy="111" r="1.8" fill="${skin.outline}"/>` });
  else raw(`<path d="M149 100 L153.5 107 L146 107.5 Z" fill="${skin.shadow}" opacity="0.75"/><circle cx="150.5" cy="102" r="1.4" fill="#fff" opacity="0.7"/>`);
  if (c.mouth === 'smirk') raw(ln('M138 117 C143 121 150 120 155 114', '#7a2c30', 2.4) + ln('M142 123 C146 124 149 123 151 122', skin.shadow, 1.4, 0.7));
  if (c.mouth === 'smile') raw(`<path d="M137 114 C142 124 152 123 156 112 C150 116 143 117 137 114 Z" fill="#7a2030"/><path d="M139.5 115.4 C144 117.6 150 117 154 114 L153.4 116 C149 119 144 119 140.6 117.6 Z" fill="#fff"/>`);
  if (c.mouth === 'calm') raw(ln('M140 117 C144 119.5 149 119.5 153 117', '#8a3a3c', 2.2));
  if (c.mouth === 'fangs') raw(`<path d="M132 118 C140 126 154 124 160 114 C152 118 142 120 132 118 Z" fill="#4a1420"/><path d="M137 119 l2.6 -8 l3 8 Z M150 117 l2.6 -8 l3 7 Z" fill="#fff8e6" stroke="#4a3a2a" stroke-width="0.9"/>`);
  if (c.mouth === 'mask') S('M90 104 C112 114 152 112 174 98 C176 114 168 128 154 134 C140 138 118 138 102 130 C94 124 90 114 90 104 Z', T.hood, { inner: sf('M100 116 C118 124 146 122 166 110', T.hood.light, 2, 0.5, 1) + ln('M148 104 L152 132', T.hood.shadow, 1.6, 0.6) });
  if (c.warpaint) raw(`<path d="M104 104 l14 3 l-1 5 l-14 -3 Z M162 100 l9 -2 l1 5 l-9 2 Z" fill="${c.warpaint}" opacity="0.9"/>`);

  // cheveux de devant (le bandeau passe dessous)
  if (c.headband) {
    S('M70 62 C100 48 152 46 182 56 L182 67 C152 57 100 59 70 73 Z', T.band, { sh: 4, inner: ln('M72 65 C100 52 152 50 181 59', T.band.light, 1.4, 0.8) });
  }
  if (c.hairStyle === 'spiky') {
    S('M70 88 C64 62 78 40 98 30 L100 12 L114 26 L128 6 L138 25 L158 14 L158 32 C172 40 180 54 182 72 L172 56 L165 66 L153 50 L142 64 L128 47 L114 64 L100 51 L92 68 L84 60 L80 82 Z', hair, { sh: 9, inner:
      sf('M96 44 C112 34 138 32 160 42', hair.light, 5, 0.7, 2) +
      ln('M104 16 C104 26 100 36 94 44 M129 10 C130 22 128 32 124 40 M156 18 C154 28 150 36 144 42', hair.light, 1.8, 0.85) +
      ln('M128 48 C126 40 122 34 116 30 M153 51 C152 44 148 38 142 34 M100 52 C98 46 96 42 92 38', hair.shadow, 1.8, 0.6) });
  }
  if (c.hairStyle === 'long') {
    S('M70 88 C62 52 90 26 124 26 C156 26 180 46 182 76 C172 72 160 62 154 48 C146 62 130 72 112 74 C104 74 96 70 92 62 C88 76 80 84 70 88 Z', hair, { sh: 9, inner:
      sf('M90 44 C110 32 142 32 166 46', hair.light, 6, 0.75, 2) + ln('M94 42 C112 33 140 33 160 43', '#ffffff', 1.5, 0.85) + ln('M154 50 C150 58 142 64 132 68', hair.shadow, 1.8, 0.6) });
    S('M80 74 C70 96 70 122 78 146 C86 132 90 112 90 92 Z', hair, { inner: ln('M82 84 C78 102 78 120 80 134', hair.light, 1.4, 0.8) });
  }
  if (c.hairStyle === 'short') S('M82 72 C92 50 128 42 160 50 C170 54 176 62 178 70 C168 68 158 62 152 54 C144 66 128 74 112 74 C100 74 90 74 82 72 Z', hair, { sh: 6, inner: sf('M100 56 C118 48 142 48 160 54', hair.light, 4, 0.8, 1) });
  if (c.hairStyle === 'mohawk') S('M92 44 C96 18 122 0 152 4 C142 14 140 26 144 38 C130 32 110 34 92 44 Z', hair, { inner: ln('M104 34 C110 20 124 10 140 8', hair.light, 2, 0.8) + ln('M116 36 C120 26 128 18 138 14', hair.shadow, 2, 0.6) });
  // coiffes
  if (c.circlet) raw(ln('M74 62 C102 48 152 46 180 58', gold.outline, 6.5) + ln('M74 62 C102 48 152 46 180 58', gold.base, 4) + ln('M76 60.5 C104 47 150 45 178 56.5', gold.light, 1.2, 0.9) +
    `<path d="M150 42 l7 9 l-7 9 l-7 -9 Z" fill="${accent.base}" stroke="${gold.outline}" stroke-width="2"/><path d="M150 45 l4 6 l-4 0 Z" fill="#fff" opacity="0.8"/>`);
  if (c.helmet === 'horned') {
    S('M76 54 C54 46 40 28 38 6 C52 22 70 30 90 36 Z', tone('#efe6d2'), { inner: ln('M50 28 C58 36 68 42 78 46', '#b8a888', 2, 0.7) + ln('M44 16 C50 24 58 30 66 34', '#b8a888', 1.6, 0.6) });
    S('M170 44 C188 36 200 22 202 2 C190 18 178 26 160 32 Z', tone('#efe6d2'), { far: true });
    S('M64 86 C58 46 90 20 124 20 C160 20 186 46 182 82 L153 75 L151 100 L143 100 L142 75 C126 72 110 74 98 81 C96 94 94 106 92 118 C76 112 66 100 64 86 Z', T.helm ?? steel, { sh: 10, inner:
      sf('M92 38 C112 26 144 26 166 40', '#ffffff', 6, 0.8, 2) + ln('M96 36 C114 27 142 27 162 37', '#ffffff', 1.6, 0.9) +
      ln('M124 21 C126 38 126 56 124 73', (T.helm ?? steel).shadow, 2.4, 0.5) + `<path d="M117 20 L131 20 L133 74 L115 74 Z" fill="${gold.base}"/><path d="M117 20 L131 20 L133 74 L115 74 Z" fill="url(#vol)"/>` + ln('M119 22 L118 72', gold.light, 1.6, 0.9) +
      ln('M98 81 C110 74 126 72 142 75 M153 75 L182 82', gold.base, 5) + ln('M98 79.5 C110 72.5 126 70.5 142 73.5', gold.light, 1.2, 0.9) +
      [[76, 92], [84, 108]].map(([x, y]) => `<circle cx="${x}" cy="${y}" r="2.4" fill="${(T.helm ?? steel).shadow}"/><circle cx="${x - 0.6}" cy="${y - 0.6}" r="1" fill="#fff"/>`).join('') });
  }
  if (c.hood) {
    S('M58 98 C46 54 80 12 124 10 C166 8 196 42 188 88 C184 68 168 50 146 46 C120 42 98 50 86 68 C78 82 78 102 84 124 C72 118 62 110 58 98 Z', T.hood, { sh: 11, inner:
      sf('M88 34 C110 20 146 20 170 38', T.hood.light, 6, 0.6, 2) + sf('M70 70 C66 86 68 100 76 114', T.hood.shadow, 6, 0.5, 3) +
      ln('M188 88 C184 68 168 50 146 46 C120 42 98 50 86 68 C78 82 78 102 84 124', c.hoodTrim ?? gold.base, 3) });
  }
  if (c.hood && c.ears === 'elf') S('M88 92 C70 82 50 70 34 66 C48 84 64 102 80 112 C86 112 90 102 88 92 Z', skin, { inner: sf('M82 96 C70 88 56 78 44 72', skin.shadow, 3, 0.6, 1) });
  if (c.skullcap) S('M78 58 C80 30 104 14 130 16 C156 18 176 34 178 58 C162 50 142 46 126 48 C108 48 92 52 78 58 Z', tone('#ebe3d0'), { inner:
    `<ellipse cx="112" cy="36" rx="8" ry="7" fill="#2a1a24"/><ellipse cx="148" cy="35" rx="7" ry="7" fill="#2a1a24"/><path d="M130 40 l4 8 l-8 0 Z" fill="#2a1a24"/>` + ln('M96 30 C100 24 106 20 112 18', '#fff', 2, 0.8) });
  if (c.leader) raw(`<g transform="translate(124 4)"><path d="M-17 8 L-20 -10 L-9 -1 L0 -14 L9 -1 L20 -10 L17 8 Z" fill="#e6ac3c" stroke="#5a3508" stroke-width="2.4" stroke-linejoin="round"/><path d="M-15 5 L15 5" stroke="#fff3bc" stroke-width="2"/><circle cx="0" cy="-2" r="2.6" fill="#e0344a"/></g>`);

  // ================= 6. Objets de la main du fond (devant le corps) =================
  if (c.offhand === 'shield') {
    const sd = 'M150 116 C172 108 198 114 214 128 C218 162 210 198 188 226 C166 212 150 182 146 150 C146 138 148 126 150 116 Z';
    S(sd, T.shield ?? steel, { sh: 12, inner:
      `<path d="M158 124 C174 118 194 122 206 132 C208 160 202 190 188 212 C172 200 160 176 156 150 Z" fill="${(T.shieldFace ?? accent).base}"/><path d="M158 124 C174 118 194 122 206 132 C208 160 202 190 188 212 C172 200 160 176 156 150 Z" fill="url(#vol)"/>` +
      sf('M162 130 C176 124 192 126 202 134', '#ffffff', 5, 0.6, 2) + sf('M160 150 C164 174 174 192 188 206', '#1d1030', 8, 0.35, 3) +
      (c.shieldEmblem ?? '') +
      ln('M152 118 C172 110 198 116 212 129', '#ffffff', 2, 0.9) +
      [[156, 122], [208, 132], [188, 218], [150, 152], [212, 166]].map(([x, y]) => `<circle cx="${x}" cy="${y}" r="2.6" fill="${(T.shield ?? steel).shadow}"/><circle cx="${x - 0.7}" cy="${y - 0.7}" r="1.1" fill="#fff"/>`).join('') });
  }
  if (c.offhand === 'bow') {
    S('M170 92 C176 96 196 120 200 156 C198 192 180 218 172 224 L166 220 C176 210 190 188 190 156 C188 126 174 104 164 98 Z', T.bow ?? tone('#8a5a34'), { sh: 4, inner: ln('M172 98 C184 112 194 132 195 156', (T.bow ?? tone('#8a5a34')).light, 1.6, 0.8) });
    raw(`<path d="M168 95 L146 154 L170 222" stroke="#f4efe6" stroke-width="1.4" fill="none" opacity="0.9"/>`);
    raw(`<rect x="184" y="146" width="14" height="20" rx="3" fill="${leather.outline}"/><rect x="185.4" y="147.4" width="11.2" height="17.2" rx="2" fill="${leather.base}"/>`);
    // flèche encochée
    raw(`<path d="M140 153 L226 150" stroke="#5a3a20" stroke-width="3.2"/><path d="M140 152 L226 149" stroke="#c9a070" stroke-width="1"/><path d="M222 144 L238 150 L222 156 L226 150 Z" fill="#dfe6f0" stroke="#3a4050" stroke-width="1.3"/><path d="M140 153 l-8 -7 l14 2 Z M140 153 l-8 7 l14 -2 Z" fill="${accent.base}" stroke="${accent.outline}" stroke-width="1"/>`);
  }
  if (c.offhand === 'staff' || c.offhand === 'skullStaff') {
    S(quad([176, 250], [176, 70], 8), T.haft ?? tone('#8a5a34'), { inner: ln('M174 246 L174 76', (T.haft ?? tone('#8a5a34')).light, 1.4, 0.7) + ln('M172 150 L180 156 M172 160 L180 166', gold.base, 2.4) });
    if (c.offhand === 'staff') {
      raw(`<circle cx="176" cy="48" r="30" fill="${c.orb ?? '#6fd0ff'}" opacity="0.5" filter="url(#glow)"/>`);
      S('M160 78 C150 66 150 44 164 32 C160 46 164 62 174 70 Z', gold, { sh: 3 });
      S('M192 78 C202 66 202 44 188 32 C192 46 188 62 178 70 Z', gold, { sh: 3 });
      raw(`<circle cx="176" cy="50" r="15.5" fill="${mix(c.orb ?? '#6fd0ff', '#0a1840', 0.75)}"/><circle cx="176" cy="50" r="13.5" fill="${c.orb ?? '#6fd0ff'}"/><circle cx="176" cy="50" r="13.5" fill="url(#orbg)"/><ellipse cx="171" cy="44" rx="5" ry="3.4" fill="#fff" opacity="0.95"/><circle cx="182" cy="57" r="1.8" fill="#fff" opacity="0.8"/>`);
    } else {
      S('M158 66 C156 44 166 30 178 30 C190 30 198 44 194 66 C190 74 184 78 176 78 C168 78 162 74 158 66 Z', tone('#ebe3d0'), { inner: `<ellipse cx="170" cy="52" rx="5.5" ry="6.5" fill="#22121c"/><ellipse cx="186" cy="52" rx="5" ry="6.5" fill="#22121c"/><path d="M178 60 l3 6 l-6 0 Z" fill="#22121c"/>` + ln('M168 70 L168 76 M174 71 L174 77 M180 71 L180 77 M186 70 L186 76', '#22121c', 1.6) });
      raw(`<circle cx="170" cy="52" r="3" fill="${c.orb ?? '#b46cff'}"/><circle cx="186" cy="52" r="3" fill="${c.orb ?? '#b46cff'}"/><circle cx="178" cy="52" r="24" fill="${c.orb ?? '#b46cff'}" opacity="0.35" filter="url(#glow)"/>`);
    }
  }
  if (c.offhand === 'dagger') {
    const b2 = blade([178, 176], [214, 196], 9, 0.7);
    S(b2.d, steel, { sh: 3, inner: ln(b2.edge2, '#fff', 1.6, 0.9) });
  }
  // main du fond
  if (c.farArm !== false) S('M160 170 a9.5 9.5 0 1 0 19 2 a9.5 9.5 0 1 0 -19 -2 Z', T.glove ?? skin, { far: c.offhand === 'shield', sh: 4, hl: 3 });

  // ================= 7. Bras avant, arme, épaulière =================
  const sleeve = T.sleeve ?? cloth;
  const up = 'M84 138 C77 150 79 164 87 174 L104 168 C99 160 98 150 102 142 Z';
  if (c.pose === 'shoulder') {
    S(up, sleeve, {});
    S('M80 160 C88 174 102 176 120 170 L116 152 C106 156 98 156 92 150 Z', c.outfit === 'plate' ? steel : sleeve, { inner: c.outfit === 'plate' ? ln('M88 164 C98 170 108 170 118 166', '#fff', 1.8, 0.8) : '' });
    S('M112 152 a10.5 10.5 0 1 0 21 3 a10.5 10.5 0 1 0 -21 -3 Z', T.glove ?? skin, { sh: 4, hl: 3, inner: ln('M118 150 C122 154 122 160 120 164', (T.glove ?? skin).shadow, 1.6, 0.7) });
  } else if (c.pose === 'draw') {
    S(up, sleeve, {});
    S('M84 156 C100 168 122 166 146 162 L144 144 C126 148 108 150 96 146 Z', sleeve, { inner: c.bracer ? `<path d="M118 148 L140 145 L142 162 L120 165 Z" fill="${leather.base}"/>` + ln('M124 148 L126 164 M132 147 L134 163', leather.shadow, 1.6) : '' });
    S('M138 146 a9.5 9.5 0 1 0 19 2 a9.5 9.5 0 1 0 -19 -2 Z', T.glove ?? skin, { sh: 4, hl: 3 });
  } else {
    // bras vers l'avant, arme tenue dans la main avant
    S(up, sleeve, {});
    S('M86 164 C96 178 112 186 132 186 L134 169 C120 169 108 164 100 156 Z', c.outfit === 'plate' ? steel : sleeve, { inner: c.outfit === 'plate' ? ln('M94 168 C104 176 118 180 132 180', '#fff', 1.8, 0.8) + ln('M108 164 L104 180 M120 168 L118 184', steel.shadow, 1.6, 0.7) : (c.bracer ? `<path d="M106 162 L130 168 L130 186 L104 180 Z" fill="${leather.base}"/>` + ln('M112 164 L110 181 M122 167 L121 184', leather.shadow, 1.6) : '') });
    if (c.weapon === 'greatsword') {
      const g = [150, 170], tp = [214, 82];
      const bl = blade(g, tp, 22, 0.84);
      S(quad([126, 190], [148, 172], 8), leather, { inner: ln('M130 184 L136 190 M136 178 L142 184', leather.outline, 1.8) });
      raw(`<circle cx="123" cy="193" r="7.5" fill="${gold.outline}"/><circle cx="123" cy="193" r="5.6" fill="${gold.base}"/><circle cx="121.6" cy="191.6" r="2" fill="${gold.light}"/>`);
      S(bl.d, T.blade ?? metal('#d5deeb'), { sh: 5, inner:
        ln(bl.mid, (T.blade ?? metal('#d5deeb')).shadow, 5, 0.55) + ln(bl.edge, '#ffffff', 2.4) + ln(bl.edge2, '#8f9bb4', 1.4, 0.8) + (c.bladeGlow ? sf(bl.mid, c.bladeGlow, 7, 0.75, 2) + ln(bl.mid, '#fff2c0', 1.6, 0.95) : '') });
      S(quad([132, 152], [166, 190], 11), gold, { sh: 3, inner: `<circle cx="149" cy="171" r="4.6" fill="${accent.base}" stroke="${gold.outline}" stroke-width="1.4"/><circle cx="147.8" cy="169.8" r="1.5" fill="#fff"/>` });
      if (c.bladeGlow) raw(`<path d="${bl.d}" fill="${c.bladeGlow}" opacity="0.28" filter="url(#glow)"/>`);
    }
    if (c.weapon === 'dagger') {
      const b1 = blade([146, 174], [196, 150], 10, 0.72);
      S(b1.d, steel, { sh: 3, inner: ln(b1.edge, '#fff', 1.8, 0.95) + ln(b1.mid, steel.shadow, 1.6, 0.6) });
      S(quad([140, 166], [150, 184], 6), gold, { sh: 2 });
    }
    if (c.weapon === 'club') {
      S('M134 184 L150 170 C162 150 182 132 204 128 C216 132 220 146 214 158 C198 170 176 176 158 186 L142 194 Z', T.haft ?? tone('#8a5a34'), { inner:
        ln('M156 172 C170 154 186 140 204 134', (T.haft ?? tone('#8a5a34')).light, 2, 0.7) + [[190, 136], [206, 142], [196, 158], [176, 160]].map(([x, y]) => `<path d="M${x} ${y} l4 -9 l5 8 Z" fill="#dcd4c4" stroke="#4a4038" stroke-width="1.2"/>`).join('') });
    }
    S('M126 170 a10.5 10.5 0 1 0 21 3 a10.5 10.5 0 1 0 -21 -3 Z', T.glove ?? skin, { sh: 4, hl: 3, inner: ln('M134 168 C138 172 138 178 136 182', (T.glove ?? skin).shadow, 1.6, 0.7) });
  }
  if (c.pad) {
    const pd = c.pad === 'big' ? 'M62 142 C62 116 92 106 114 122 C120 138 110 154 92 158 C76 158 64 152 62 142 Z' : 'M70 140 C72 122 96 116 110 128 C112 140 104 150 92 152 C80 152 72 148 70 140 Z';
    const pt = T.padTone ?? steel;
    S(pd, pt, { sh: 8, inner: (c.pad === 'big'
      ? sf('M72 128 C84 116 100 116 110 126', '#ffffff', 5, 0.8, 1) + ln('M64 142 C74 152 96 154 112 138', gold.base, 4.5) + ln('M64 140.5 C74 150.5 96 152.5 112 136.5', gold.light, 1.2, 0.9) + `<path d="M86 122 l7 -16 l8 14 Z" fill="${pt.base}" stroke="${pt.outline}" stroke-width="1.6"/>`
      : sf('M78 130 C86 122 98 122 106 130', '#ffffff', 4, 0.8, 1) + ln('M72 141 C80 150 98 150 110 134', gold.base, 3.6)) +
      `<circle cx="94" cy="138" r="2.4" fill="${pt.shadow}"/><circle cx="93.4" cy="137.4" r="1" fill="#fff"/>` });
  }
  return { defs: P.defs, body: P.body };
}
module.exports = { chibi, tone, metal, mix };
