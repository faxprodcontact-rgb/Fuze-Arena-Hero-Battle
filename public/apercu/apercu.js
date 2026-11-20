// Aperçu des animations de combat (site de test) : les personnages v5 sont animés morceau par morceau
// (jambes, buste, tête, bras, arme). Dessins fabriqués par refonte-graphique/export5.cjs.
(() => {
  const D = window.APERCU, E = D.E;
  const cv = document.getElementById('cv'), ctx = cv.getContext('2d');
  const SW = 720, SH = 980, GT = 560, SQ = 0.8;
  // mêmes places que dans le jeu (fight-view.ts)
  const HERO_X = { 3: 95, 4: 95, 2: 198, 0: 300, 1: 300 }, ENEMY_X = { 0: 420, 1: 420, 2: 522, 3: 625, 4: 625 };
  const ROW_DY = { 0: 90, 3: 90, 2: 180, 1: 270, 4: 270 };
  const px = (x) => 360 + (x - 360) * SQ;
  const TEAM = { hero: { 0: 'protector', 1: 'warrior', 2: 'healer', 3: 'archer', 4: 'assassin' }, foe: { 0: 'grunt', 1: 'rogue', 2: 'brute', 3: 'shaman', 4: 'hunter' } };
  const STATS = { // PV, dégâts, délai entre deux attaques (s), taille, hauteur de la barre de vie
    protector: [900, 55, 2.3, 0.58, 12], warrior: [620, 95, 1.9, 0.58, 4], healer: [460, 60, 2.4, 0.58, 4], archer: [430, 85, 2.0, 0.58, 24], assassin: [480, 105, 1.7, 0.58, 24],
    grunt: [560, 70, 2.1, 0.54, 12], rogue: [470, 85, 1.8, 0.54, 44], brute: [980, 90, 2.6, 0.64, 12], shaman: [440, 70, 2.5, 0.54, 22], hunter: [420, 75, 2.1, 0.54, 24],
  };
  // points d'articulation (repère du dessin : boîte 200 × 240, pieds à y = 228)
  const PIV = { swing: [86, 130], far: [130, 130], head: [106, 119], back: [96, 122], torso: [106, 176] };
  const RAD = Math.PI / 180;
  const ease = { out: (t) => 1 - (1 - t) ** 3, io: (t) => (t < 0.5 ? 4 * t * t * t : 1 - (-2 * t + 2) ** 3 / 2), back: (t) => 1 + 2.7 * (t - 1) ** 3 + 1.7 * (t - 1) ** 2 };
  const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
  const seg = (p, a, b) => clamp((p - a) / (b - a));
  let seed = 7; const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);

  // ---------- personnages : les gobelins de la première démonstration + les 72 héros ----------
  const ROLE_STATS = { protector: [950, 55, 2.3], warrior: [640, 95, 1.9], marksman: [440, 85, 2.0], assassin: [480, 105, 1.7], healer: [470, 60, 2.4], support: [520, 70, 2.3] };
  const CH = {};
  for (const n of Object.keys(D.chars)) { const c = D.chars[n], st = STATS[n]; CH[n] = { ...c, E, src: 'a/' + n + '.png', stats: st.slice(0, 3), k: st[3], top: st[4], rig: c.rig.atk === 'stab' ? { farWind: -25, farHit: 55, ...c.rig } : c.rig }; }
  const HS = window.HEROS ? window.HEROS.list : [];
  for (const h of HS) CH[h.id] = { enemy: false, rig: h.rig, parts: h.parts, E: window.HEROS.E, src: 'h/' + h.id + '.png', stats: ROLE_STATS[h.role], role: h.role, label: h.name, aura: { epic: '#b06cff', legendary: '#ffc94a' }[h.rarity],
    k: 0.56 * Math.max(0.86, Math.min(1.22, h.scale)), top: Math.max(-34, Math.min(...h.parts.filter((p) => p.name !== 'glow' && p.name !== 'shine').map((p) => p.oy))) };
  const img = {};
  const image = (n) => img[n] || (img[n] = Object.assign(new Image(), { src: CH[n].src }));
  const bg = new Image(); bg.src = 'bg.jpg';
  for (const n of Object.keys(CH)) {
    const c = CH[n], r = c.rig;
    c.group = {};
    for (const p of c.parts) {
      let g = p.name === 'legs' ? 'legs' : p.name === 'torso' || p.name === 'afterBody' ? 'torso' : p.name === 'head' || p.name === 'afterHead' ? 'head' : p.name === 'back' ? (c.enemy ? 'head' : 'back') : 'torso';
      if (r.swing && r.swing.includes(p.name)) g = 'swing';
      if (r.far && r.far.includes(p.name)) g = 'far';
      if (p.name === 'glow') g = r.glow || 'torso';
      if (r.grp && r.grp[p.name]) g = r.grp[p.name];
      c.group[p.name] = g;
    }
  }
  /** Tire deux équipes : 5 héros au hasard (un protecteur et un guerrier devant), contre des gobelins ou 5 autres héros. */
  let fights = 0;
  function pickTeams() {
    const R = () => Math.random(), used = new Set();
    const take = (roles) => { const pool = HS.filter((h) => roles.includes(h.role) && !used.has(h.id)); const h = pool[Math.floor(R() * pool.length)]; used.add(h.id); return h.id; };
    const team = () => ({ 0: take(['protector']), 1: take(['warrior']), 2: take(['healer', 'support']), 3: take(['marksman']), 4: take(['assassin', 'support', 'healer']) });
    const vsHeroes = HS.length >= 10 && fights % 2 === 1; fights++;
    return { hero: HS.length >= 10 ? team() : TEAM.hero, foe: vsHeroes ? team() : TEAM.foe };
  }

  // ---------- état du combat ----------
  let units = [], shots = [], fx = [], nums = [], time = 0, shake = 0, dim = 0, over = 0, speed = 1, paused = false;
  function reset() {
    units = []; shots = []; fx = []; nums = []; over = 0; dim = 0; seed = 7 + Math.floor(time * 10) % 50;
    const teams = pickTeams();
    for (const side of ['hero', 'foe']) for (const slot of [0, 1, 2, 3, 4]) {
      const name = teams[side][slot], c0 = CH[name], [hp, atk, cd] = c0.stats, k = c0.k, top = c0.top; image(name);
      const x = px((side === 'hero' ? HERO_X : ENEMY_X)[slot]), y = GT + ROW_DY[slot] + 56;
      units.push({ name, side, slot, c: c0, k, top, hx: x, hy: y, x, y, hp, max: hp, shown: hp, atk, cd, wait: 0.6 + rnd() * cd, energy: side === 'hero' ? 30 + rnd() * 40 : rnd() * 40,
        ph: rnd() * 6, act: null, hurt: 0, dead: 0, dir: side === 'hero' ? 1 : -1, heals: 0 });
    }
  }
  const alive = (side) => units.filter((u) => u.side === side && !u.dead);
  const foesOf = (u) => alive(u.side === 'hero' ? 'foe' : 'hero');
  function pickTarget(u, ranged) {
    const f = foesOf(u); if (!f.length) return null;
    if (ranged) return f[Math.floor(rnd() * f.length)];
    const tier = (t) => (t.slot < 2 ? 0 : t.slot === 2 ? 1 : 2), best = Math.min(...f.map(tier));
    return f.filter((t) => tier(t) === best).sort((a, b) => Math.abs(a.hy - u.hy) - Math.abs(b.hy - u.hy))[0];
  }
  function startAction(u, skill) {
    const r = u.c.rig, ranged = r.atk === 'shoot' || r.atk === 'cast';
    if (r.heal && !skill && ++u.heals % 3 === 0) { // la soigneuse soigne de temps en temps l'allié le plus blessé
      const ally = alive(u.side).sort((a, b) => a.hp / a.max - b.hp / b.max)[0];
      if (ally && ally.hp < ally.max * 0.8) { u.act = { type: 'cast', t: 0, d: 0.9, target: ally, heal: true, done: {} }; return; }
    }
    const target = pickTarget(u, ranged); if (!target) return;
    const d = { slash: 0.85, smash: 1.0, stab: 0.8, shoot: 0.75, cast: 0.9 }[r.atk];
    u.act = { type: r.atk, t: skill ? -0.45 : 0, d, target, skill, done: {} };
    if (skill) { u.energy = 0; dim = 1; ring(u.x, u.y, r.fx || (u.side === 'hero' ? '#ffe27a' : '#ff6a5a'), 70); }
  }
  // ---------- effets ----------
  const ring = (x, y, color, size = 40, life = 0.45) => fx.push({ kind: 'ring', x, y, color, size, t: 0, life });
  const spark = (x, y, color, n = 8, v = 140) => { for (let i = 0; i < n; i++) { const a = rnd() * 6.28, s = v * (0.4 + rnd() * 0.6); fx.push({ kind: 'dot', x, y, vx: Math.cos(a) * s, vy: Math.sin(a) * s - 40, color, size: 2 + rnd() * 3, t: 0, life: 0.35 + rnd() * 0.25 }); } };
  const slashFx = (x, y, dir, color, size = 46) => fx.push({ kind: 'slash', x, y, dir, color, size, t: 0, life: 0.22 });
  const dust = (x, y) => { for (let i = 0; i < 5; i++) fx.push({ kind: 'dust', x: x + (rnd() - 0.5) * 30, y: y - rnd() * 6, vx: (rnd() - 0.5) * 50, vy: -20 - rnd() * 20, size: 6 + rnd() * 6, t: 0, life: 0.45 }); };
  function damage(src, t, mult = 1, color) {
    if (!t || t.dead) return;
    const crit = rnd() < 0.18, v = Math.round(src.atk * mult * (0.85 + rnd() * 0.3) * (crit ? 1.6 : 1));
    t.hp = Math.max(0, t.hp - v); t.hurt = 0.28; t.hurtDir = src.dir; t.energy = Math.min(100, t.energy + 8);
    nums.push({ x: t.x + (rnd() - 0.5) * 20, y: t.y - 110 * t.k, text: String(v), color: crit ? '#ffd23f' : '#fff', big: crit || mult > 1.5, t: 0 });
    spark(t.x, t.y - 60 * t.k, color || '#fff', crit ? 12 : 7);
    if (t.hp <= 0) { t.dead = 0.001; t.act = null; }
  }
  function heal(src, t, mult = 1) {
    if (!t || t.dead) return;
    const v = Math.round(src.atk * 2.2 * mult); t.hp = Math.min(t.max, t.hp + v);
    nums.push({ x: t.x, y: t.y - 110 * t.k, text: '+' + v, color: '#6dff9a', big: false, t: 0 });
    ring(t.x, t.y, '#6dff9a', 44); for (let i = 0; i < 8; i++) fx.push({ kind: 'plus', x: t.x + (rnd() - 0.5) * 50, y: t.y - rnd() * 80 * t.k, vy: -50 - rnd() * 30, t: 0, life: 0.7, size: 5 + rnd() * 4 });
  }
  const chest = (u) => [u.x, u.y - 70 * u.k];
  function shoot(u, t, kind, color, mult, isHeal) {
    const from = kind === 'arrow' ? [u.x + u.dir * 72 * u.k, u.y - 99 * u.k] : [u.x + u.dir * 60 * u.k, u.y - 195 * u.k];
    shots.push({ kind, color, from, to: t, t: 0, d: kind === 'arrow' ? 0.22 : 0.4, hit: () => (isHeal ? heal(u, t, mult) : (damage(u, t, mult, color), kind === 'orb' && ring(t.x, t.y - 60 * t.k, color, 36))) });
  }

  // ---------- déroulement d'une action : renvoie la pose du personnage ----------
  function actionPose(u, P, dt) {
    const a = u.act, r = u.c.rig, T = a.target;
    a.t += dt;
    if (a.t < 0) { // charge avant une compétence
      const c = 1 + a.t / 0.45; P.scale = 1 + 0.12 * Math.sin(c * Math.PI); P.lean = -6 * c; P.aura = c; P.auraColor = r.fx; return;
    }
    const p = a.t / a.d, once = (k, at, fn) => { if (p >= at && !a.done[k]) { a.done[k] = 1; fn(); } };
    const m = a.skill ? 2.3 : 1, col = a.skill ? (r.fx || '#ffe27a') : (r.fx || '#fff');
    if (a.type === 'shoot') {
      const pull = ease.out(seg(p, 0, 0.4)) * (1 - seg(p, 0.4, 0.5));
      P.swing = -16 * pull + 8 * Math.sin(seg(p, 0.4, 0.7) * Math.PI); P.lean = -5 * pull; P.dx = -5 * Math.sin(seg(p, 0.4, 0.8) * Math.PI);
      once('s', 0.4, () => { shoot(u, T, 'arrow', '#fff', m); if (a.skill) for (const o of foesOf(u).filter((x) => x !== T).slice(0, 2)) shoot(u, o, 'arrow', col, 1.4); });
    } else if (a.type === 'cast') {
      const up = ease.out(seg(p, 0, 0.42)) * (1 - ease.io(seg(p, 0.55, 1)));
      P.far = -12 * up; P.farY = -9 * up; P.glow = 1 + 1.2 * up; P.lean = -4 * up; P.swing = -20 * up;
      once('s', 0.45, () => {
        if (a.heal) shoot(u, T, 'orb', '#6dff9a', 1, true);
        else if (a.skill && r.heal) alive(u.side).forEach((o) => heal(u, o, 1.3));
        else { shoot(u, T, 'orb', r.fx || '#fff', m); if (a.skill) for (const o of foesOf(u).filter((x) => x !== T).slice(0, 1)) shoot(u, o, 'orb', r.fx || '#fff', 1.6); }
      });
    } else { // corps à corps : élan, bond, coup, retour
      const reach = (a.type === 'smash' ? 62 : 54) * (u.k + T.k);
      const sx = T.x - u.dir * reach, sy = T.y + 2;
      const go = ease.out(seg(p, 0.16, 0.36)), back = ease.io(seg(p, 0.66, 1)), w = go * (1 - back);
      u.x = u.hx + (sx - u.hx) * w; u.y = u.hy + (sy - u.hy) * w;
      P.hop = -22 * Math.sin(seg(p, 0.16, 0.36) * Math.PI) - 10 * Math.sin(back * Math.PI);
      const wind = ease.out(seg(p, 0, 0.2)), hit = ease.back(seg(p, 0.36, 0.47)), rel = ease.io(seg(p, 0.6, 0.9));
      P.swing = (r.wind * wind + (r.hit - r.wind) * hit) * (1 - rel);
      P.lean = (-9 * wind + 22 * hit) * (1 - rel);
      if (a.type === 'stab') { P.far = ((r.farWind ?? 0) * wind + ((r.farHit ?? 0) - (r.farWind ?? 0)) * ease.back(seg(p, 0.46, 0.56))) * (1 - rel); P.dx = 8 * hit * (1 - rel); }
      once('d', 0.17, () => dust(u.hx, u.hy));
      once('h', 0.42, () => {
        damage(u, T, m * (a.type === 'stab' ? 0.6 : 1), col); slashFx(T.x - u.dir * 8, T.y - 64 * T.k, u.dir, col, a.skill ? 70 : 46);
        if (a.type === 'smash') { shake = a.skill ? 14 : 7; ring(T.x, T.y, '#fff', a.skill ? 110 : 60); dust(T.x, T.y); }
        if (a.skill && a.type !== 'stab') for (const o of foesOf(u).filter((x) => x !== T && Math.abs(x.hx - T.hx) < 90)) damage(u, o, 1.3, col);
      });
      if (a.type === 'stab') once('h2', 0.53, () => { damage(u, T, m * 0.6, col); slashFx(T.x - u.dir * 2, T.y - 50 * T.k, -u.dir, col, a.skill ? 64 : 40); });
      if (a.skill && a.type === 'stab') once('h3', 0.6, () => { damage(u, T, m * 0.6, col); slashFx(T.x, T.y - 76 * T.k, u.dir, col, 70); });
    }
    if (p >= 1) { u.act = null; u.x = u.hx; u.y = u.hy; u.wait = u.cd * (0.85 + rnd() * 0.3); }
  }

  function update(dt) {
    time += dt;
    shake *= Math.pow(0.001, dt); dim = Math.max(0, dim - dt * 1.6);
    for (const u of units) {
      if (u.dead) { u.dead += dt; continue; }
      u.shown += (u.hp - u.shown) * Math.min(1, dt * 8);
      if (u.hurt > 0) u.hurt -= dt;
      if (!u.act && !over) {
        u.wait -= dt;
        if (u.wait <= 0 && !units.some((o) => o.act && o.act.target === u && o.act.type !== 'shoot' && o.act.type !== 'cast')) {
          const skill = u.energy >= 100; startAction(u, skill); if (!skill) u.energy = Math.min(100, u.energy + 26);
        }
      }
    }
    for (const s of shots) { s.t += dt; if (s.t >= s.d && !s.done) { s.done = 1; s.hit(); } }
    shots = shots.filter((s) => !s.done);
    for (const f of fx) { f.t += dt; if (f.vx !== undefined) { f.x += f.vx * dt; } if (f.vy !== undefined) { f.y += f.vy * dt; if (f.kind === 'dot') f.vy += 380 * dt; } }
    fx = fx.filter((f) => f.t < f.life);
    for (const n of nums) n.t += dt; nums = nums.filter((n) => n.t < 0.9);
    if (!over && (!alive('hero').length || !alive('foe').length)) over = 0.001;
    if (over) { over += dt; if (over > 2.6) reset(); }
  }

  // ---------- dessin d'un personnage : morceaux assemblés hors écran, puis contour de la silhouette ----------
  let ofx = 0, ofy = 0;
  const ST = (a, b, c, d, e, f) => ctx.setTransform(a, b, c, d, e + ofx, f + ofy);
  const A = document.createElement('canvas'), B = document.createElement('canvas'), ag = A.getContext('2d'), bgx = B.getContext('2d');
  const OX = 150, OY = 110, BW = 500, BH = 370; // cadre hors écran (unités de dessin) : de la place pour les armes en mouvement
  /** Place un morceau selon son groupe (le repère de base, en unités de dessin, est déjà posé). */
  function groupTransform(g, grp, P, piv) {
    if (grp === 'legs') return;
    g.translate(P.dx, P.bob); g.translate(piv.torso[0], piv.torso[1]); g.rotate(P.lean * RAD); g.translate(-piv.torso[0], -piv.torso[1]);
    if (grp === 'torso') return;
    const pv = piv[grp], ang = grp === 'swing' ? P.swing : grp === 'far' ? P.far : grp === 'head' ? P.head : P.back;
    if (grp === 'far') g.translate(0, P.farY);
    g.translate(pv[0], pv[1]); g.rotate(ang * RAD); g.translate(-pv[0], -pv[1]);
  }
  function drawUnit(u, V) {
    const c = u.c, q = u.k * V, im = image(u.name), E = c.E;
    const P = { dx: 0, bob: Math.sin(time * 2.4 + u.ph) * 1.3, lean: 0, swing: Math.sin(time * 2.4 + u.ph + 1) * 2.2, far: Math.sin(time * 2.4 + u.ph + 2) * 1.5, farY: 0,
      head: Math.sin(time * 1.3 + u.ph) * 1.6, back: Math.sin(time * 2.1 + u.ph) * 5, hop: 0, scale: 1, glow: 1 + 0.15 * Math.sin(time * 3 + u.ph), aura: 0 };
    if (u.act) actionPose(u, P, 0);
    let alpha = 1, fall = 0;
    if (u.hurt > 0) { const h = u.hurt / 0.28; P.dx -= 7 * h; P.lean -= 9 * h; P.head -= 8 * h; }
    if (u.dead) { const d = clamp(u.dead / 0.7); fall = ease.out(d) * -82; alpha = 1 - seg(u.dead, 0.5, 1.1); P.bob = 0; if (alpha <= 0) return; }
    const X = u.x * V, Y = (u.y + P.hop) * V, flip = u.dir < 0 ? -1 : 1, s = q * P.scale;
    // ombre au sol
    ST(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 0.34 * alpha * (1 + P.hop / 60);
    ctx.fillStyle = '#1c1208'; ctx.beginPath(); ctx.ellipse(X, u.y * V, 62 * q, 14 * q, 0, 0, 6.3); ctx.fill(); ctx.globalAlpha = 1;
    if (P.aura) { ctx.globalAlpha = 0.5 * Math.sin(P.aura * Math.PI); ctx.fillStyle = P.auraColor || '#ffe27a'; ctx.beginPath(); ctx.ellipse(X, u.y * V, 90 * q * P.aura, 22 * q * P.aura, 0, 0, 6.3); ctx.fill(); ctx.globalAlpha = 1; }
    // morceaux → A
    const w = Math.ceil(BW * s), h = Math.ceil(BH * s);
    if (A.width !== w || A.height !== h) { A.width = B.width = w; A.height = B.height = h; } else { ag.setTransform(1, 0, 0, 1, 0, 0); ag.clearRect(0, 0, w, h); }
    // une arme portée sur l'épaule passe devant la tête quand elle s'abat
    const over = c.rig.top && P.swing > 35, list = over ? [...c.parts.filter((p) => !c.rig.top.includes(p.name)), ...c.parts.filter((p) => c.rig.top.includes(p.name))] : c.parts;
    let shineP = null;
    for (const p of list) {
      if (p.name === 'shine') { shineP = p; continue; } // l'éclat se dessine en dernier, par-dessus
      if (p.name === 'glow') { // halo : directement à l'écran, derrière le personnage
        ST(flip * s, 0, 0, s, X - flip * 106 * s, Y - 228 * s); groupTransform(ctx, c.group.glow, P, c.rig.piv || PIV);
        const cx = p.ox + p.w / E / 2, cy = p.oy + p.h / E / 2; ctx.translate(cx, cy); ctx.scale(P.glow, P.glow); ctx.translate(-cx, -cy);
        ctx.globalAlpha = alpha * Math.min(1, 0.6 * P.glow); ctx.drawImage(im, p.x, p.y, p.w, p.h, p.ox, p.oy, p.w / E, p.h / E); ctx.globalAlpha = 1; continue;
      }
      ag.setTransform(s, 0, 0, s, OX * s, OY * s); groupTransform(ag, c.group[p.name], P, c.rig.piv || PIV);
      ag.drawImage(im, p.x, p.y, p.w, p.h, p.ox, p.oy, p.w / E, p.h / E);
    }
    if (u.hurt > 0) { ag.setTransform(1, 0, 0, 1, 0, 0); ag.globalCompositeOperation = 'source-atop'; ag.fillStyle = `rgba(255,255,255,${0.5 * u.hurt / 0.28})`; ag.fillRect(0, 0, w, h); ag.globalCompositeOperation = 'source-over'; }
    // silhouette sombre → B, puis contour = 8 copies décalées
    bgx.setTransform(1, 0, 0, 1, 0, 0); bgx.globalCompositeOperation = 'copy'; bgx.drawImage(A, 0, 0); bgx.globalCompositeOperation = 'source-in'; bgx.fillStyle = '#190c24'; bgx.fillRect(0, 0, w, h);
    ST(flip, 0, 0, 1, X, Y); ctx.rotate(fall * RAD); ctx.globalAlpha = alpha;
    const ox = -(OX + 106) * s, oy = -(OY + 228) * s, r = Math.max(1, 1.6 * q);
    if (c.aura && !u.dead) { // aura des hautes raretés : la silhouette projette un halo de couleur
      ctx.shadowColor = c.aura; ctx.shadowBlur = (13 + 4 * Math.sin(time * 2 + u.ph)) * q / 0.56;
      ctx.drawImage(B, ox, oy); ctx.drawImage(B, ox, oy); ctx.shadowBlur = 0; ctx.shadowColor = 'transparent';
    }
    for (let i = 0; i < 8; i++) ctx.drawImage(B, ox + Math.cos(i * 0.785) * r, oy + Math.sin(i * 0.785) * r);
    ctx.drawImage(A, ox, oy); ctx.globalAlpha = 1;
    if (shineP && !u.dead) { // l'éclat : il suit son objet et scintille
      const tw = 0.5 + 0.5 * Math.sin(time * 3.2 + u.ph * 2.3), cx = shineP.ox + shineP.w / E / 2, cy = shineP.oy + shineP.h / E / 2;
      ST(flip * s, 0, 0, s, X - flip * 106 * s, Y - 228 * s); groupTransform(ctx, c.group.shine, P, c.rig.piv || PIV);
      ctx.translate(cx, cy); ctx.rotate(0.5 * Math.sin(time * 1.7 + u.ph)); ctx.scale(0.7 + 0.45 * tw, 0.7 + 0.45 * tw); ctx.translate(-cx, -cy);
      ctx.globalAlpha = alpha * (0.5 + 0.5 * tw); ctx.drawImage(im, shineP.x, shineP.y, shineP.w, shineP.h, shineP.ox, shineP.oy, shineP.w / E, shineP.h / E); ctx.globalAlpha = 1;
    }
  }
  function bars(u, V) {
    if (u.dead) return;
    const w = 52 * V, x = u.x * V - w / 2, y = (u.y - (228 - u.top) * u.k - 14) * V, hgt = 8 * V;
    ST(1, 0, 0, 1, 0, 0);
    ctx.fillStyle = 'rgba(18,10,28,.85)'; rr(x - 2 * V, y - 2 * V, w + 4 * V, hgt + 4 * V, 5 * V); ctx.fill();
    ctx.fillStyle = u.side === 'hero' ? '#3ccf7a' : '#e5484d'; rr(x, y, Math.max(0, w * u.shown / u.max), hgt, 3.5 * V); ctx.fill();
    ctx.fillStyle = 'rgba(255,255,255,.35)'; rr(x, y, Math.max(0, w * u.shown / u.max), 3 * V, 1.5 * V); ctx.fill();
    ctx.fillStyle = u.energy >= 100 ? '#ffd23f' : '#4fd1ff'; rr(x, y + 11 * V, w * u.energy / 100, 3.4 * V, 1.5 * V); ctx.fill();
  }
  function rr(x, y, w, h, r) { ctx.beginPath(); if (w <= 0) return; r = Math.min(r, w / 2, h / 2); ctx.moveTo(x + r, y); ctx.arcTo(x + w, y, x + w, y + h, r); ctx.arcTo(x + w, y + h, x, y + h, r); ctx.arcTo(x, y + h, x, y, r); ctx.arcTo(x, y, x + w, y, r); }

  function drawFx(V) {
    ST(V, 0, 0, V, 0, 0);
    for (const s of shots) {
      const p = s.t / s.d, [tx, ty] = chest(s.to), x = s.from[0] + (tx - s.from[0]) * p, y = s.from[1] + (ty - s.from[1]) * p - Math.sin(p * Math.PI) * (s.kind === 'arrow' ? 14 : 34);
      if (s.kind === 'arrow') {
        const a = Math.atan2(ty - s.from[1] - Math.cos(p * Math.PI) * 14, tx - s.from[0]);
        ctx.save(); ctx.translate(x, y); ctx.rotate(a); ctx.strokeStyle = '#190c24'; ctx.lineWidth = 5; ctx.lineCap = 'round'; ctx.beginPath(); ctx.moveTo(-24, 0); ctx.lineTo(4, 0); ctx.stroke();
        ctx.strokeStyle = '#d9b98a'; ctx.lineWidth = 2.6; ctx.beginPath(); ctx.moveTo(-24, 0); ctx.lineTo(4, 0); ctx.stroke();
        ctx.fillStyle = s.color === '#fff' ? '#e9eef5' : s.color; ctx.strokeStyle = '#190c24'; ctx.lineWidth = 1.6; ctx.beginPath(); ctx.moveTo(12, 0); ctx.lineTo(0, -5.5); ctx.lineTo(0, 5.5); ctx.closePath(); ctx.fill(); ctx.stroke();
        ctx.globalAlpha = 0.35; ctx.strokeStyle = '#fff'; ctx.lineWidth = 2; ctx.beginPath(); ctx.moveTo(-60, 0); ctx.lineTo(-26, 0); ctx.stroke(); ctx.restore();
      } else {
        const g = ctx.createRadialGradient(x, y, 0, x, y, 22); g.addColorStop(0, '#fff'); g.addColorStop(0.3, s.color); g.addColorStop(1, 'rgba(255,255,255,0)');
        ctx.fillStyle = g; ctx.beginPath(); ctx.arc(x, y, 22, 0, 6.3); ctx.fill();
        if (rnd() < 0.8) fx.push({ kind: 'dot', x, y, vx: (rnd() - 0.5) * 30, vy: (rnd() - 0.5) * 30, color: s.color, size: 3, t: 0, life: 0.3 });
      }
    }
    for (const f of fx) {
      const p = f.t / f.life; ctx.globalAlpha = 1 - p;
      if (f.kind === 'ring') { ctx.strokeStyle = f.color; ctx.lineWidth = 5 * (1 - p) + 1; ctx.beginPath(); ctx.ellipse(f.x, f.y, f.size * ease.out(p), f.size * 0.3 * ease.out(p), 0, 0, 6.3); ctx.stroke(); }
      else if (f.kind === 'dot') { ctx.fillStyle = f.color; ctx.beginPath(); ctx.arc(f.x, f.y, f.size * (1 - p * 0.6), 0, 6.3); ctx.fill(); }
      else if (f.kind === 'dust') { ctx.globalAlpha = 0.5 * (1 - p); ctx.fillStyle = '#e9dcc0'; ctx.beginPath(); ctx.arc(f.x, f.y, f.size * (0.6 + p), 0, 6.3); ctx.fill(); }
      else if (f.kind === 'plus') { ctx.fillStyle = '#6dff9a'; ctx.fillRect(f.x - f.size / 2, f.y - f.size * 0.18, f.size, f.size * 0.36); ctx.fillRect(f.x - f.size * 0.18, f.y - f.size / 2, f.size * 0.36, f.size); }
      else if (f.kind === 'slash') { // croissant : la trace du coup
        ctx.save(); ctx.translate(f.x, f.y); ctx.scale(f.dir, 1); ctx.rotate(-0.5 + p * 0.5); const R = f.size * (0.8 + 0.3 * ease.out(p));
        ctx.fillStyle = f.color; ctx.beginPath(); ctx.arc(0, 0, R, -1.25, 1.25); ctx.arc(-R * 0.42, 0, R * 1.05, 0.98, -0.98, true); ctx.closePath(); ctx.fill();
        ctx.globalAlpha *= 0.9; ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.arc(0, 0, R * 0.96, -1.05, 1.05); ctx.arc(-R * 0.3, 0, R * 1.02, 0.86, -0.86, true); ctx.closePath(); ctx.fill(); ctx.restore();
      }
    }
    ctx.globalAlpha = 1;
    ctx.textAlign = 'center'; ctx.lineJoin = 'round';
    for (const n of nums) {
      const p = n.t / 0.9, sc = (n.big ? 30 : 22) * (1 + 0.5 * Math.max(0, 1 - n.t * 8));
      ctx.globalAlpha = 1 - seg(p, 0.6, 1); ctx.font = `900 ${sc}px system-ui, sans-serif`; ctx.lineWidth = 5; ctx.strokeStyle = '#190c24';
      const y = n.y - 46 * ease.out(p); ctx.strokeText(n.text, n.x, y); ctx.fillStyle = n.color; ctx.fillText(n.text, n.x, y);
    }
    ctx.globalAlpha = 1;
  }

  // ---------- cadrage : la scène du jeu (720 × 980) tient dans l'écran, le ciel remplit le haut ----------
  let V = 1, offX = 0, offY = 0, dpr = 1;
  function resize() {
    dpr = Math.min(3, window.devicePixelRatio || 1);
    cv.width = Math.round(innerWidth * dpr); cv.height = Math.round(innerHeight * dpr);
    const bar = 64 * dpr;
    V = Math.min((cv.height - bar) / SH, cv.width / SW); // comme dans le jeu : toute la largeur du terrain
    offX = (cv.width - SW * V) / 2; offY = cv.height - bar - SH * V;
  }
  addEventListener('resize', resize); resize();

  function frame(now) {
    const raw = Math.min(0.05, (now - (frame.last || now)) / 1000); frame.last = now;
    const dt = paused ? 0 : raw * speed;
    if (!units.length) reset();
    if (units.every((u) => image(u.name).complete && image(u.name).naturalWidth)) {
      // les actions avancent ici (une seule fois par image), le dessin relit ensuite la pose
      for (const u of units) if (u.act && !u.dead) { const P = { }; actionPose(u, P, dt); }
      update(dt);
      ofx = offX + (Math.random() - 0.5) * shake * dpr; ofy = offY + (Math.random() - 0.5) * shake * dpr;
      ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.fillStyle = '#161233'; ctx.fillRect(0, 0, cv.width, cv.height);
      ST(1, 0, 0, 1, 0, 0);
      if (bg.complete) { ctx.drawImage(bg, 0, 0, SW * V, SH * V); if (offY > 0) ctx.drawImage(bg, 0, 0, bg.width, 2, 0, -offY - 20, SW * V, offY + 21); } // le ciel se prolonge vers le haut
      if (dim > 0) { ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.fillStyle = `rgba(12,8,30,${0.45 * Math.min(1, dim * 2)})`; ctx.fillRect(0, 0, cv.width, cv.height); }
      const order = [...units].sort((a, b) => a.y - b.y);
      for (const u of order) drawUnit(u, V);
      for (const u of order) bars(u, V);
      drawFx(V);
      if (over > 0.5) {
        const win = alive('hero').length > 0, a = seg(over, 0.5, 0.9);
        ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = a; ctx.textAlign = 'center'; ctx.font = `900 ${54 * dpr}px system-ui, sans-serif`; ctx.lineJoin = 'round'; ctx.lineWidth = 10 * dpr; ctx.strokeStyle = '#190c24';
        const ty = offY + 470 * V; ctx.strokeText(win ? 'Victoire' : 'Défaite', cv.width / 2, ty); ctx.fillStyle = win ? '#ffd23f' : '#ff6a5a'; ctx.fillText(win ? 'Victoire' : 'Défaite', cv.width / 2, ty); ctx.globalAlpha = 1;
      }
    }
    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);

  // ---------- commandes ----------
  const $ = (id) => document.getElementById(id);
  $('pause').onclick = () => { paused = !paused; $('pause').classList.toggle('on', paused); };
  $('slow').onclick = () => { speed = speed === 0.3 ? 1 : 0.3; $('slow').classList.toggle('on', speed === 0.3); $('fast').classList.remove('on'); };
  $('fast').onclick = () => { speed = speed === 2 ? 1 : 2; $('fast').classList.toggle('on', speed === 2); $('slow').classList.remove('on'); };
  $('again').onclick = () => reset();
  cv.addEventListener('pointerdown', (e) => { // toucher un personnage : il lance sa compétence
    const x = (e.clientX * dpr - offX) / V, y = (e.clientY * dpr - offY) / V;
    let best = null, bd = 70;
    for (const u of units) { if (u.dead) continue; const d = Math.hypot(u.x - x, u.y - 60 * u.k - y); if (d < bd) { bd = d; best = u; } }
    if (best && !best.act && !over) { best.energy = 100; startAction(best, true); }
  });
})();
