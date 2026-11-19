// Personnage « chibi » de trois-quarts, tourné vers la droite (2,5 têtes de haut), entièrement paramétrable.
// Repère : boîte 240 × 260, pieds à y = 250. Principes : un contour par grande partie (pas par pièce),
// des membres d'un seul tenant, peu d'éléments mais bien peints, front haut et yeux bas.
const { painter, tone, metal, mix, ln, sf, blob } = require('./kit.cjs');

const HEAD = 'M122 34 C152 32 174 52 176 84 C177 100 172 114 162 124 C154 131 146 135 136 135 C110 135 86 124 76 104 C66 82 70 52 92 40 C101 35 111 34 122 34 Z';
const EY = 99; // hauteur des yeux (bas dans la tête : grand front)

function eye(cx, cy, w, h, color, o = {}) {
  const id = 'e' + (o.k ?? '') + Math.round(cx);
  const white = `M${cx - w / 2} ${cy - h * 0.22} C${cx - w / 4} ${cy - h / 2 - 1} ${cx + w / 4} ${cy - h / 2 - 1} ${cx + w / 2} ${cy - h * 0.18} C${cx + w / 2 + 1} ${cy + h * 0.2} ${cx + w / 4} ${cy + h / 2} ${cx} ${cy + h / 2} C${cx - w / 4} ${cy + h / 2} ${cx - w / 2 - 1} ${cy + h * 0.2} ${cx - w / 2} ${cy - h * 0.22} Z`;
  const lash = `M${cx - w / 2 - 2.5} ${cy - h * 0.2} C${cx - w / 4} ${cy - h / 2 - 5.5} ${cx + w / 4} ${cy - h / 2 - 5.5} ${cx + w / 2 + 2.5} ${cy - h * 0.15} L${cx + w / 2} ${cy - h * 0.06} C${cx + w / 4} ${cy - h / 2 + 1.5} ${cx - w / 4} ${cy - h / 2 + 1.5} ${cx - w / 2} ${cy - h * 0.1} Z`;
  const ix = cx + w * 0.07, iy = cy + 1.2, irx = w * 0.37, iry = h * 0.43;
  let s = `<defs><clipPath id="${id}c"><path d="${white}"/></clipPath><linearGradient id="${id}g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${mix(color, '#12081c', 0.62)}"/><stop offset="0.55" stop-color="${color}"/><stop offset="1" stop-color="${mix(color, '#ffffff', 0.4)}"/></linearGradient></defs>`;
  s += `<path d="${white}" fill="${o.sclera ?? '#fbf6ef'}"/><g clip-path="url(#${id}c)">`;
  s += `<rect x="${cx - w}" y="${cy - h / 2 - 2}" width="${w * 2}" height="${h * 0.34}" fill="#3b2550" opacity="0.3"/>`;
  s += `<ellipse cx="${ix}" cy="${iy}" rx="${irx}" ry="${iry}" fill="url(#${id}g)"/>`;
  if (o.slit) s += `<ellipse cx="${ix}" cy="${iy}" rx="${w * 0.07}" ry="${iry * 0.8}" fill="#170a12"/>`;
  else s += `<ellipse cx="${ix + 0.5}" cy="${iy + 0.5}" rx="${irx * 0.5}" ry="${iry * 0.5}" fill="#170a12"/>`;
  s += `<ellipse cx="${ix}" cy="${iy + iry * 0.62}" rx="${irx * 0.6}" ry="${iry * 0.22}" fill="${mix(color, '#ffffff', 0.6)}" opacity="0.7"/>`;
  s += `<circle cx="${cx - w * 0.14}" cy="${cy - h * 0.2}" r="${w * 0.14}" fill="#fff"/><circle cx="${cx + w * 0.22}" cy="${cy + h * 0.2}" r="${w * 0.06}" fill="#fff" opacity="0.9"/>`;
  s += `</g><path d="${lash}" fill="${o.lash ?? '#2a1424'}"/>`;
  if (o.glow) s += `<ellipse cx="${ix}" cy="${iy}" rx="${irx * 1.5}" ry="${iry * 1.3}" fill="${color}" opacity="0.5" filter="url(#glow)"/>`;
  return s;
}

function blade(a, b, w, tip = 0.82) {
  const v = [b[0] - a[0], b[1] - a[1]], len = Math.hypot(...v), u = [v[0] / len, v[1] / len], n = [-u[1], u[0]];
  const at = (t, k) => [a[0] + u[0] * t * len + n[0] * k, a[1] + u[1] * t * len + n[1] * k];
  const p = (q) => `${q[0].toFixed(1)} ${q[1].toFixed(1)}`;
  return {
    d: `M${p(at(0, -w / 2))} L${p(at(tip, -w / 2 * 0.86))} L${p(at(1, 0))} L${p(at(tip, w / 2 * 0.86))} L${p(at(0, w / 2))} Z`,
    mid: `M${p(at(0.04, 0))} L${p(at(tip - 0.06, 0))}`, edge: `M${p(at(0.02, w / 2 * 0.72))} L${p(at(tip, w / 2 * 0.62))} L${p(at(0.985, 0.6))}`, at, p,
  };
}
const quad = (a, b, w) => { const { at, p } = blade(a, b, w, 1); return `M${p(at(0, -w / 2))} L${p(at(1, -w / 2))} L${p(at(1, w / 2))} L${p(at(0, w / 2))} Z`; };

function chibi(c) {
  const P = painter(c.light ?? [0.5, -0.85]);
  const { S, raw, cast } = P;
  const T = {};
  for (const [k, v] of Object.entries(c.colors)) T[k] = typeof v === 'string' ? tone(v) : v;
  const skin = T.skin, hair = T.hair, cloth = T.cloth, pants = T.pants ?? tone('#3c3550'), steel = T.metal ?? metal('#bcc3d2'), gold = T.gold ?? metal('#e6ac3c');
  const boot = T.boot ?? tone('#5a3826'), accent = T.accent ?? cloth, wood = T.wood ?? tone('#8a5a34'), belt = T.belt ?? tone('#6e4428');
  const sleeve = T.sleeve ?? cloth, glove = T.glove ?? skin;
  const G = (f) => { raw('<g filter="url(#ol)">'); f(); raw('</g>'); }; // une grande partie = un seul contour
  const robe = c.outfit === 'robe';

  // ================= Derrière : écharpe, cheveux longs, capuche, carquois =================
  G(() => {
    if (c.scarf) {
      S('M98 132 C74 122 48 128 26 148 C48 152 66 154 80 160 C70 168 62 178 58 190 C76 180 92 166 104 148 Z', T.scarf, { sh: 7, inner: sf('M94 138 C74 134 54 138 36 146', T.scarf.light, 3, 0.5, 1) + sf('M96 146 C84 154 72 166 64 180', T.scarf.shadow, 4, 0.45, 2) });
    }
    if (c.hairStyle === 'long') S('M68 76 C58 44 90 18 124 18 C160 18 186 44 182 82 C180 98 174 110 170 120 L96 124 C96 156 86 192 66 214 C52 226 38 228 28 224 C44 206 48 176 52 146 C56 118 62 96 68 76 Z', hair, { sh: 11, inner:
      sf('M74 110 C70 150 60 190 42 220', hair.shadow, 6, 0.45, 3) + sf('M86 124 C82 158 74 190 58 214', hair.light, 3, 0.45, 2) });
    if (c.hairStyle === 'spiky') S('M72 100 C62 92 46 90 30 92 C44 82 56 76 66 72 C56 60 46 50 36 42 C52 42 68 46 80 52 C76 38 70 24 62 12 C80 18 96 26 108 36 L176 44 C186 60 184 76 178 88 L78 114 Z', hair, { sh: 9 });
    if (c.hood) S('M60 100 C48 54 80 14 124 12 C166 10 194 42 188 86 L176 102 L86 126 C72 120 64 110 60 100 Z M72 46 C56 36 38 40 24 54 C42 54 58 60 68 74 Z', T.hood, {});
    if (c.ears === 'goblin') S('M170 78 C184 66 200 62 212 66 C202 78 192 90 178 98 Z', skin, { far: true });
    if (c.quiver) {
      S('M58 118 L82 108 L100 170 L78 180 Z', belt, {});
      for (const [x, y] of [[57, 104], [68, 99]]) raw(`<path d="M${x} ${y + 16} L${x - 6} ${y - 6} L${x + 2} ${y} L${x + 4} ${y - 10} L${x + 9} ${y + 12} Z" fill="${accent.base}"/>`);
    }
  });

  // ================= Corps : jambes, tunique (ou robe), ceinture, plastron =================
  G(() => {
    if (c.farArm !== false) S('M138 138 C154 146 164 158 170 170 L158 180 C150 168 140 160 132 152 Z', sleeve, { far: true, rim: false });
    let body;
    if (robe) {
      body = S('M90 134 C104 126 136 126 150 134 C158 160 168 204 178 244 C144 254 96 254 66 246 C76 206 84 166 90 134 Z', cloth, { sh: 11, inner:
        sf('M98 190 C94 212 88 232 82 248', cloth.shadow, 8, 0.4, 4) +
        `<path d="M119 130 C117 170 113 210 106 254 L146 254 C141 210 137 170 135 130 Z" fill="${accent.base}"/><path d="M119 130 C117 170 113 210 106 254 L146 254 C141 210 137 170 135 130 Z" fill="url(#vol)"/>` +
        ln('M119 130 C117 170 113 210 106 254', gold.base, 2.6) + ln('M135 130 C137 170 141 210 146 254', gold.base, 2.6) + ln('M68 241 C96 249 144 249 176 239', gold.base, 4) });
      S('M88 172 C108 181 134 181 152 172 L153 184 C134 193 108 193 88 185 Z', T.sash ?? gold, { rim: false });
    } else {
      // jambes d'un seul tenant (pantalon puis botte, sans trait entre les deux)
      S('M122 198 L146 196 C150 206 154 214 158 222 L136 230 C132 220 126 210 122 198 Z', pants, { far: true, rim: false });
      S('M134 222 C134 232 132 242 136 250 L180 250 C182 242 174 234 164 228 L158 218 Z', boot, { far: true, rim: false });
      S('M96 198 L120 198 C120 208 118 218 117 228 L92 228 C92 218 94 208 96 198 Z', pants, { rim: false });
      S('M90 224 C88 232 82 240 84 250 L128 250 C130 242 124 234 118 230 L118 224 Z', boot, { inner: sf('M100 232 C110 232 118 236 122 242', boot.light, 2.4, 0.5, 1) });
      // tunique d'un seul tenant (buste + pans)
      body = S('M90 134 C104 126 136 126 150 134 C154 152 156 178 160 204 C138 214 102 214 80 206 C84 180 86 154 90 134 Z', cloth, { sh: 10, inner:
        sf('M98 188 C96 198 94 204 92 210', cloth.shadow, 7, 0.35, 3) + ln('M81 204.5 C102 212.5 138 212.5 160 202.5', (T.trim ?? gold).base, 3.4) });
      S('M87 172 C108 181 134 181 154 172 L155 184 C134 193 108 193 86 185 Z', belt, { rim: false });
      raw(`<rect x="126" y="174.5" width="14" height="14" rx="3" fill="${gold.base}" stroke="${gold.edge}" stroke-width="1.6"/><rect x="130.2" y="178.7" width="5.6" height="5.6" rx="1" fill="${belt.shadow}"/>`);
      if (c.outfit === 'plate') {
        const pl = T.plate ?? steel;
        S('M96 135 C108 129 136 129 148 135 C152 149 150 162 144 172 C132 178 108 178 100 172 C92 160 92 148 96 135 Z', pl, { line: 2, inner:
          sf('M140 138 C146 148 146 160 141 169', '#ffffff', 5, 0.6, 2) + ln('M131 131 C137 145 137 160 131 176', pl.shadow, 2, 0.45) + (c.emblem ?? '') });
      }
    }
    cast(body, `<ellipse cx="126" cy="131" rx="46" ry="15" fill="#1a0c2e" filter="url(#g3)"/>`, 0.5);
  });

  // ================= Arme posée sur l'épaule (derrière la tête) =================
  if (c.weapon === 'hammerShoulder' || c.weapon === 'axeShoulder') G(() => {
    S(quad([134, 174], [44, 78], 9), wood, { rim: false });
    raw('<g transform="rotate(-43 46 80)">');
    if (c.weapon === 'hammerShoulder') {
      S('M12 58 L80 58 Q84 58 84 62 L84 98 Q84 102 80 102 L12 102 Q8 102 8 98 L8 62 Q8 58 12 58 Z', steel, { sh: 8, inner: sf('M14 63 L78 63', '#fff', 3, 0.8, 1) + `<rect x="36" y="58" width="20" height="44" fill="${gold.base}"/><rect x="36" y="58" width="20" height="44" fill="url(#vol)"/>` });
    } else {
      S('M40 60 C20 44 2 50 -8 70 C-10 88 -4 108 12 118 C22 104 34 100 46 100 Z M58 64 L78 72 L78 88 L58 96 Z', steel, { sh: 9, inner: sf('M-4 72 C-4 88 2 102 12 112', '#fff', 4, 0.85, 1) });
      S('M40 56 L58 56 L58 104 L40 104 Z', tone('#3c3350'), { rim: false });
    }
    raw('</g>');
  });

  // ================= Tête : cou, visage, cheveux, coiffe =================
  G(() => {
    if (c.scarf) S('M94 126 C108 138 138 138 154 126 L154 141 C138 151 108 151 94 141 Z', T.scarf, { inner: sf('M100 134 C116 142 134 142 148 134', T.scarf.shadow, 4, 0.4, 2) });
    const covered = c.hairStyle || c.hood || c.helmet;
    const head = S(HEAD, skin, { sh: 12, hl: 6, inner:
      (covered ? blob('M74 74 C100 60 150 58 180 70 L182 50 L70 50 Z', skin.shadow, 0.5, 3) : '') +
      blob('M156 124 C144 134 118 134 102 124 C114 140 146 140 160 128 Z', skin.shadow, 0.45, 2) +
      `<ellipse cx="110" cy="114" rx="12" ry="6.5" fill="${c.blush ?? '#ff7d6e'}" opacity="0.4" filter="url(#g2)"/><ellipse cx="168" cy="110" rx="7" ry="5.5" fill="${c.blush ?? '#ff7d6e'}" opacity="0.36" filter="url(#g2)"/>` });
    void head;
    if (c.ears === 'goblin') S('M90 88 C66 72 42 70 22 78 C40 90 56 108 80 116 C88 114 94 100 90 88 Z', skin, { line: 1.6, inner: sf('M84 94 C68 82 50 78 34 80', skin.shadow, 4, 0.5, 1) });
    else if (c.ears === 'elf' && !c.hood) S('M90 94 C72 84 52 72 36 68 C50 86 66 104 82 114 C88 114 92 104 90 94 Z', skin, { line: 1.6 });
    else if (!c.hood && !c.helmet) S('M86 90 C76 86 70 96 73 106 C76 114 84 116 90 110 Z', skin, { line: 1.6, inner: ln('M84 96 C79 98 78 104 81 109', skin.shadow, 2.2) });
    // visage (yeux bas dans la tête)
    const E = c.eyes ?? {};
    if (c.mouth === 'beard') S('M94 108 C108 122 152 122 174 104 C178 126 168 146 150 154 C132 160 110 152 100 136 C96 128 92 118 94 108 Z M124 113 C134 107 148 107 158 111 C152 121 134 121 124 113 Z', hair, { sh: 9, line: 1.6, inner:
      sf('M112 128 C114 138 120 146 128 152', hair.shadow, 5, 0.45) + sf('M140 130 C142 140 142 148 140 154', hair.light, 3, 0.4, 1) });
    raw(eye(128, EY, E.w ?? 24, E.h ?? 26, E.color ?? '#3f7fd6', { ...E, k: 'n' + c.id }));
    raw(eye(160, EY - 2, (E.w ?? 24) * 0.62, (E.h ?? 26) * 0.92, E.color ?? '#3f7fd6', { ...E, k: 'f' + c.id }));
    const bc = c.browColor ?? hair.shadow;
    if (c.brows !== false) raw(c.angry
      ? `<path d="M108 72 C120 72 134 78 146 88 L143 93 C133 85 121 81 109 79 Z" fill="${bc}"/><path d="M152 88 C158 80 166 74 174 72 L174 78 C166 80 160 86 154 92 Z" fill="${bc}"/>`
      : `<path d="M110 76 C120 71 134 74 145 82 L143 87.5 C133 81 121 78 111 82 Z" fill="${bc}"/><path d="M152 82 C158 76 166 73 173 73 L173 79 C166 79 159 83 153 87.5 Z" fill="${bc}"/>`);
    if (c.nose === 'goblin') S('M146 104 C158 102 172 108 180 118 C168 122 154 120 146 114 Z', skin, { sh: 4, line: 1.4 });
    else raw(`<path d="M149 105 L153.5 112 L146 112.5 Z" fill="${skin.shadow}" opacity="0.7"/>`);
    if (c.mouth === 'smirk') raw(ln('M138 121 C143 125 150 124 155 118', '#7a2c30', 2.4));
    if (c.mouth === 'smile') raw(`<path d="M137 118 C142 128 152 127 156 116 C150 120 143 121 137 118 Z" fill="#7a2030"/><path d="M139.5 119.4 C144 121.6 150 121 154 118 L153.4 120 C149 123 144 123 140.6 121.6 Z" fill="#fff"/>`);
    if (c.mouth === 'calm') raw(ln('M140 121 C144 123.5 149 123.5 153 121', '#8a3a3c', 2.2));
    if (c.mouth === 'fangs') raw(`<path d="M132 121 C140 129 154 127 160 117 C152 121 142 123 132 121 Z" fill="#4a1420"/><path d="M137 122 l2.6 -8 l3 8 Z M150 120 l2.6 -8 l3 7 Z" fill="#fff8e6"/>`);
    if (c.mouth === 'mask') S('M90 108 C112 118 152 116 175 102 C177 116 170 128 158 134 C144 139 118 139 102 131 C94 126 90 118 90 108 Z', T.hood, { line: 1.4, inner: sf('M100 120 C118 128 146 126 166 114', T.hood.light, 2, 0.4, 1) });
    if (c.warpaint) raw(`<path d="M104 108 l14 3 l-1 5 l-14 -3 Z" fill="${c.warpaint}" opacity="0.9"/>`);
    // cheveux de devant (un seul bloc, un trait doux)
    if (c.hairStyle === 'spiky') S('M70 92 C64 64 78 42 98 32 L100 14 L114 28 L128 8 L138 27 L158 16 L158 34 C172 42 180 56 182 76 L171 62 L163 72 L151 56 L140 70 L127 54 L113 70 L100 58 L92 76 L84 68 L80 88 Z', hair, { sh: 9, line: 1.6, inner:
      sf('M96 46 C112 36 138 34 160 44', hair.light, 6, 0.6, 2) + ln('M104 18 C104 28 100 38 94 46 M129 12 C130 24 128 34 124 42 M156 20 C154 30 150 38 144 44', hair.light, 1.6, 0.7) });
    if (c.hairStyle === 'long') S('M72 92 C64 56 90 28 124 28 C156 28 180 48 182 80 C172 76 160 66 154 52 C146 66 130 76 112 78 C104 78 96 74 92 66 C90 86 88 110 82 132 C74 120 70 106 72 92 Z', hair, { sh: 9, line: 1.6, inner:
      sf('M90 46 C110 34 142 34 166 48', hair.light, 6, 0.6, 2) });
    if (c.hairStyle === 'short') S('M82 76 C92 54 128 46 160 54 C170 58 176 66 178 74 C168 72 158 66 152 58 C144 70 128 78 112 78 C100 78 90 78 82 76 Z', hair, { sh: 6, line: 1.4 });
    if (c.hairStyle === 'mohawk') S('M92 46 C96 20 122 2 152 6 C142 16 140 28 144 40 C130 34 110 36 92 46 Z', hair, { line: 1.6, inner: ln('M104 36 C110 22 124 12 140 10', hair.light, 2, 0.7) });
    if (c.headband) S('M72 64 C100 52 152 50 180 60 L181 71 C152 61 100 63 71 76 Z', T.band, { sh: 4, line: 1.4 });
    if (c.circlet) raw(ln('M76 66 C104 52 152 50 180 62', gold.edge, 6) + ln('M76 66 C104 52 152 50 180 62', gold.base, 3.6) +
      `<path d="M150 46 l7 9 l-7 9 l-7 -9 Z" fill="${accent.base}" stroke="${gold.edge}" stroke-width="2"/><path d="M150 49 l4 6 l-4 0 Z" fill="#fff" opacity="0.8"/>`);
    if (c.helmet === 'horned') {
      S('M76 56 C54 48 40 30 38 8 C52 24 70 32 90 38 Z', tone('#efe6d2'), { line: 1.6 });
      S('M170 46 C188 38 200 24 202 4 C190 20 178 28 160 34 Z', tone('#efe6d2'), { far: true, line: 1.6 });
      const hm = T.helm ?? steel;
      S('M66 88 C60 48 90 22 124 22 C160 22 186 48 182 84 C164 76 140 74 120 76 C110 78 102 82 98 86 C96 98 94 110 92 122 C76 116 68 102 66 88 Z', hm, { sh: 11, line: 1.8, inner:
        sf('M92 40 C112 28 144 28 166 42', '#ffffff', 7, 0.7, 2) +
        `<path d="M116 20 L132 20 L134 78 L114 78 Z" fill="${gold.base}"/><path d="M116 20 L132 20 L134 78 L114 78 Z" fill="url(#vol)"/>` +
        ln('M98 86 C104 80 112 77 120 76 C140 74 164 76 182 84', gold.base, 5) });
    }
    if (c.hood) {
      S('M58 100 C46 56 80 14 124 12 C166 10 196 44 188 90 C184 72 168 54 146 50 C120 46 98 54 86 72 C78 86 78 106 84 128 C72 122 62 112 58 100 Z', T.hood, { sh: 12, line: 1.8, inner:
        sf('M88 36 C110 22 146 22 170 40', T.hood.light, 7, 0.5, 2) + sf('M70 72 C66 88 68 102 76 116', T.hood.shadow, 7, 0.45, 3) });
      if (c.ears === 'elf') S('M88 96 C70 86 50 74 34 70 C48 88 64 106 80 116 C86 116 90 106 88 96 Z', skin, { line: 1.6 });
    }
    if (c.skullcap) S('M78 62 C80 32 104 16 130 18 C156 20 176 36 178 62 C162 54 142 50 126 52 C108 52 92 56 78 62 Z', tone('#ebe3d0'), { line: 1.6, inner:
      `<ellipse cx="112" cy="38" rx="8" ry="7" fill="#2a1a24"/><ellipse cx="148" cy="37" rx="7" ry="7" fill="#2a1a24"/><path d="M130 42 l4 8 l-8 0 Z" fill="#2a1a24"/>` });
    if (c.leader) raw(`<g transform="translate(124 2)"><path d="M-17 8 L-20 -10 L-9 -1 L0 -14 L9 -1 L20 -10 L17 8 Z" fill="#e6ac3c" stroke="#5a3508" stroke-width="2" stroke-linejoin="round"/><path d="M-15 5 L15 5" stroke="#fff3bc" stroke-width="2"/><circle cx="0" cy="-2" r="2.6" fill="#e0344a"/></g>`);
  });

  // ================= Main du fond et ce qu'elle tient =================
  G(() => {
    if (c.offhand === 'shield') S('M150 116 C172 108 198 114 214 128 C218 162 210 198 188 226 C166 212 150 182 146 150 C146 138 148 126 150 116 Z', T.shield ?? steel, { sh: 12, inner:
      `<path d="M158 125 C174 119 194 123 206 133 C208 160 202 190 188 211 C172 199 160 176 156 150 Z" fill="${(T.shieldFace ?? accent).base}"/><path d="M158 125 C174 119 194 123 206 133 C208 160 202 190 188 211 C172 199 160 176 156 150 Z" fill="url(#vol)"/>` +
      sf('M164 132 C176 126 192 128 202 136', '#ffffff', 6, 0.5, 2) + sf('M160 152 C164 176 174 194 188 206', '#1d1030', 9, 0.3, 3) + (c.shieldEmblem ?? '') });
    if (c.offhand === 'bow') {
      S('M170 92 C176 96 196 120 200 156 C198 192 180 218 172 224 L166 220 C176 210 190 188 190 156 C188 126 174 104 164 98 Z', T.bow ?? wood, { sh: 4, rim: false });
      raw(`<path d="M168 95 L146 154 L170 222" stroke="#f4efe6" stroke-width="1.4" fill="none" opacity="0.9"/>`);
      raw(`<path d="M140 153 L224 150" stroke="#6a4424" stroke-width="3.2" stroke-linecap="round"/><path d="M222 144 L238 150 L222 156 L226 150 Z" fill="#dfe6f0"/><path d="M140 153 l-8 -7 l14 2 Z M140 153 l-8 7 l14 -2 Z" fill="${accent.base}"/>`);
    }
    if (c.offhand === 'staff' || c.offhand === 'skullStaff') {
      S(quad([176, 250], [176, 72], 8), wood, { rim: false });
      if (c.offhand === 'staff') {
        raw(`<circle cx="176" cy="48" r="30" fill="${c.orb ?? '#6fd0ff'}" opacity="0.5" filter="url(#glow)"/>`);
        S('M160 80 C148 66 150 42 166 30 C160 46 164 62 174 72 Z M192 80 C204 66 202 42 186 30 C192 46 188 62 178 72 Z', gold, { sh: 3 });
        raw(`<circle cx="176" cy="50" r="13.5" fill="${c.orb ?? '#6fd0ff'}"/><circle cx="176" cy="50" r="13.5" fill="url(#orbg)"/><ellipse cx="171" cy="44" rx="5" ry="3.4" fill="#fff" opacity="0.95"/>`);
      } else {
        raw(`<circle cx="178" cy="52" r="24" fill="${c.orb ?? '#b46cff'}" opacity="0.35" filter="url(#glow)"/>`);
        S('M158 66 C156 44 166 30 178 30 C190 30 198 44 194 66 C190 74 184 78 176 78 C168 78 162 74 158 66 Z', tone('#ebe3d0'), { inner: `<ellipse cx="170" cy="52" rx="5.5" ry="6.5" fill="#22121c"/><ellipse cx="186" cy="52" rx="5" ry="6.5" fill="#22121c"/><path d="M178 60 l3 6 l-6 0 Z" fill="#22121c"/><circle cx="170" cy="52" r="2.6" fill="${c.orb ?? '#b46cff'}"/><circle cx="186" cy="52" r="2.6" fill="${c.orb ?? '#b46cff'}"/>` });
      }
    }
    if (c.offhand === 'dagger') { const b2 = blade([176, 178], [212, 198], 9, 0.7); S(b2.d, steel, { sh: 3, inner: ln(b2.edge, '#fff', 1.6, 0.9) }); }
    if (c.farArm !== false) S('M160 172 a9.5 9.5 0 1 0 19 2 a9.5 9.5 0 1 0 -19 -2 Z', glove, { far: c.offhand === 'shield', sh: 4, hl: 3, rim: false });
  });

  // ================= Bras avant (d'un seul tenant), arme, épaulière =================
  G(() => {
    const armored = c.outfit === 'plate' && c.armPlate !== false;
    if (c.pose === 'shoulder') {
      S('M86 136 C76 146 74 160 82 170 C92 178 106 176 120 170 L116 152 C108 156 100 156 98 150 C98 146 100 142 104 140 C98 134 90 134 86 136 Z', sleeve, { sh: 7 });
      S('M112 153 a10.5 10.5 0 1 0 21 3 a10.5 10.5 0 1 0 -21 -3 Z', glove, { sh: 4, hl: 3, rim: false });
    } else if (c.pose === 'draw') {
      S('M86 136 C76 146 76 158 86 164 C102 170 124 166 146 162 L144 144 C128 148 112 150 102 146 C102 144 103 142 104 140 C98 134 90 134 86 136 Z', sleeve, { sh: 7 });
      S('M138 147 a9.5 9.5 0 1 0 19 2 a9.5 9.5 0 1 0 -19 -2 Z', glove, { sh: 4, hl: 3, rim: false });
    } else {
      S('M86 136 C76 148 76 164 86 176 C98 186 114 190 130 188 L132 170 C120 170 108 166 102 158 C100 152 102 146 104 140 C98 134 90 134 86 136 Z', sleeve, { sh: 7 });
      if (c.weapon === 'greatsword') {
        const bl = blade([150, 170], [214, 82], 22, 0.84), bt = T.blade ?? metal('#d5deeb');
        S(quad([124, 192], [148, 172], 8), belt, { rim: false });
        S(bl.d, bt, { sh: 5, inner: ln(bl.mid, bt.shadow, 5, 0.5) + ln(bl.edge, '#ffffff', 2.4) + (c.bladeGlow ? sf(bl.mid, c.bladeGlow, 7, 0.75, 2) + ln(bl.mid, '#fff2c0', 1.6, 0.95) : '') });
        S(quad([132, 152], [166, 190], 11), gold, { sh: 3 });
        if (c.bladeGlow) raw(`<path d="${bl.d}" fill="${c.bladeGlow}" opacity="0.28" filter="url(#glow)"/>`);
      }
      if (c.weapon === 'dagger') {
        const b1 = blade([146, 174], [196, 150], 10, 0.72);
        S(b1.d, steel, { sh: 3, inner: ln(b1.edge, '#fff', 1.8, 0.95) });
        S(quad([140, 166], [150, 184], 6), gold, { sh: 2, rim: false });
      }
      if (c.weapon === 'club') S('M134 184 L150 170 C162 150 182 132 204 128 C216 132 220 146 214 158 C198 170 176 176 158 186 L142 194 Z', wood, { sh: 8, inner:
        [[192, 138], [204, 150], [182, 158]].map(([x, y]) => `<path d="M${x} ${y} l4 -9 l5 8 Z" fill="#e2dccc"/>`).join('') });
      S('M126 171 a10.5 10.5 0 1 0 21 3 a10.5 10.5 0 1 0 -21 -3 Z', glove, { sh: 4, hl: 3, rim: false });
    }
    void armored;
    if (c.pad) {
      const pt = T.padTone ?? steel;
      S(c.pad === 'big' ? 'M62 142 C62 116 92 106 114 122 C120 138 110 154 92 158 C76 158 64 152 62 142 Z' : 'M70 140 C72 122 96 116 110 128 C112 140 104 150 92 152 C80 152 72 148 70 140 Z', pt, { sh: 8, inner:
        sf(c.pad === 'big' ? 'M72 128 C84 116 100 116 110 126' : 'M78 130 C86 122 98 122 106 130', '#ffffff', 5, 0.7, 1) + ln(c.pad === 'big' ? 'M64 142 C74 152 96 154 112 138' : 'M72 141 C80 150 98 150 110 134', gold.base, 4) });
    }
  });
  return { defs: P.defs, body: P.body };
}
module.exports = { chibi, tone, metal, mix };
