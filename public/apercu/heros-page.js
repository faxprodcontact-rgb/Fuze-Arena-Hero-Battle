// Galerie des 72 héros et des 72 monstres (site de test). Dessins redessinés par Hailuo (window.HAILUO) quand ils
// existent, sinon les morceaux du dessin par le code assemblés au repos avec leur contour.
(() => {
  const D = window.HEROS, E = D.E, HL = window.HAILUO || {}, M = window.MONSTRES;
  const SLOT = { fast: ['Rapide', '#7c8596'], tank: ['Costaud', '#7c8596'], shooter: ['Tireur', '#7c8596'], caster: ['Sorts', '#7c8596'], elite: ['Élite', '#e0731a'], boss: ['Boss', '#d8283a'] };
  const ELBG = { fire: '#f1d6c2', wind: '#d3ece4', water: '#cfe0f4', earth: '#e2dcc0' };
  const EL = { fire: ['Feu', '#d8502a', '#f1d6c2'], wind: ['Vent', '#2a9a8e', '#d3ece4'], water: ['Eau', '#3a78d8', '#cfe0f4'], earth: ['Terre', '#7a8a34', '#e2dcc0'] };
  const RAR = { common: ['Commun', '#7c8596'], rare: ['Rare', '#2f6fe0'], epic: ['Épique', '#8a3ce0'], legendary: ['Légendaire', '#c98a10'] };
  const ROLE = { protector: 'Protecteur', warrior: 'Guerrier', marksman: 'Tireur', assassin: 'Assassin', healer: 'Soigneur', support: 'Soutien' };
  const grid = document.getElementById('grid'), tabs = document.getElementById('tabs');
  const A = document.createElement('canvas'), B = document.createElement('canvas'), LC = document.createElement('canvas');
  function render(cv, h, img) {
    const dpr = Math.min(3, window.devicePixelRatio || 1), W = cv.width = Math.round(cv.clientWidth * dpr), H = cv.height = Math.round(cv.clientHeight * dpr);
    const g = cv.getContext('2d'), q = H / 292 * Math.min(1.12, h.scale) * 0.9, ox = W / 2 - 106 * q, oy = H * 0.95 - 228 * q;
    const put = (c, p) => c.drawImage(img, p.x, p.y, p.w, p.h, ox + p.ox * q, oy + p.oy * q, p.w / E * q, p.h / E * q);
    g.fillStyle = 'rgba(40,28,16,.2)'; g.beginPath(); g.ellipse(W / 2, H * 0.95, 62 * q, 12 * q, 0, 0, 6.3); g.fill();
    const wh = HL[h.id];
    if (wh) { // dessin Hailuo : une seule image, l'aura est l'ombre colorée de l'image elle-même
      const aura = { epic: '#b06cff', legendary: '#ffc94a', elite: '#ff8a2a', boss: '#ff2a3a' }[h.rarity || h.slot];
      if (aura) { g.shadowColor = aura; g.shadowBlur = 16 * q; }
      g.drawImage(img, ox + wh.ox * q, oy + wh.oy * q, wh.w * q, wh.h * q); g.shadowBlur = 0; g.shadowColor = 'transparent';
      return;
    }
    const E = h.E || window.HEROS.E;
    for (const p of h.parts) if (p.name === 'glow') put(g, p);
    A.width = B.width = W; A.height = B.height = H;
    const a = A.getContext('2d'), b = B.getContext('2d');
    const soft = +h.rig.soft || 0, body = h.parts.filter((p) => p.name !== 'glow' && p.name !== 'shine');
    // un seul contour : chaque morceau pose une ombre douce sur ceux du dessous, découpée par la silhouette entière
    for (const p of body) put(b, p);
    if (soft) { a.shadowColor = 'rgba(26,12,46,0.5)'; a.shadowBlur = (3 + 3 * soft) * q; a.shadowOffsetY = q; }
    for (const p of body) put(a, p);
    a.shadowColor = 'transparent'; a.shadowBlur = 0; a.shadowOffsetY = 0;
    if (soft) {
      a.globalCompositeOperation = 'destination-in'; a.drawImage(B, 0, 0);
      const m = 0.5 + 0.5 * soft; LC.width = W; LC.height = H; const d = LC.getContext('2d');
      for (const [dx, dy, col, bl] of [[5, -7, `rgba(26,12,46,${0.42 * m})`, 6.4], [-4, 6, `rgba(255,246,216,${0.34 * m})`, 4.4]]) {
        d.globalCompositeOperation = 'copy'; d.drawImage(B, 0, 0); d.globalCompositeOperation = 'destination-out'; d.drawImage(B, dx * m * q, dy * m * q);
        a.globalCompositeOperation = 'source-atop'; a.shadowColor = col; a.shadowBlur = bl * m * q; a.shadowOffsetX = 3 * W; a.drawImage(LC, -3 * W, 0);
      }
      a.globalCompositeOperation = 'source-over'; a.shadowColor = 'transparent'; a.shadowBlur = 0; a.shadowOffsetX = 0;
    }
    b.globalCompositeOperation = 'source-in'; b.fillStyle = '#190c24'; b.fillRect(0, 0, W, H);
    const r = Math.max(1, (soft ? 1.25 + 1.25 * soft : 1.6) * q), aura = { epic: '#b06cff', legendary: '#ffc94a' }[h.rarity];
    if (aura) { g.shadowColor = aura; g.shadowBlur = 16 * q; g.drawImage(B, 0, 0); g.drawImage(B, 0, 0); g.shadowBlur = 0; g.shadowColor = 'transparent'; }
    for (let i = 0; i < 8; i++) g.drawImage(B, Math.cos(i * 0.785) * r, Math.sin(i * 0.785) * r);
    g.drawImage(A, 0, 0);
    for (const p of h.parts) if (p.name === 'shine') put(g, p);
  }
  const seen = new IntersectionObserver((list) => { for (const e of list) if (e.isIntersecting) { seen.unobserve(e.target); const h = e.target.hero, img = new Image(); img.onload = () => render(e.target, h, img); img.src = HL[h.id] ? 'hl/' + h.id + '.webp' : (h.slot ? 'm/' : 'h/') + h.id + '.png'; } }, { rootMargin: '300px' });
  function show(el) {
    grid.innerHTML = '';
    for (const b of tabs.children) b.classList.toggle('on', b.dataset.el === el);
    const list = el === 'monsters' ? (M ? M.list.map((m) => ({ ...m, E: M.E })) : []) : D.list.filter((x) => x.element === el);
    for (const h of list) {
      const card = document.createElement('div'); card.className = 'card';
      card.style.setProperty('--r', h.slot ? SLOT[h.slot][1] : RAR[h.rarity][1]); card.style.setProperty('--bg', h.slot ? ELBG[h.element] : EL[el][2]);
      const cv = document.createElement('canvas'); cv.hero = h; card.appendChild(cv);
      const name = document.createElement('b'); name.textContent = (h.leader ? '♛ ' : '') + h.name; card.appendChild(name);
      const sub = document.createElement('i'); sub.textContent = h.slot ? SLOT[h.slot][0] : RAR[h.rarity][0] + ' · ' + ROLE[h.role]; card.appendChild(sub);
      const from = document.createElement('small'); from.textContent = h.slot ? h.familyName : h.from; card.appendChild(from);
      grid.appendChild(card); seen.observe(cv);
    }
    try { history.replaceState(null, '', '#' + el); } catch (e) { /* aperçu sans historique */ }
  }
  EL.monsters = ['Monstres', '#b0443a', '#e6dccb'];
  for (const el of Object.keys(EL)) { const b = document.createElement('button'); b.textContent = EL[el][0]; b.dataset.el = el; b.style.setProperty('--c', EL[el][1]); b.onclick = () => show(el); tabs.appendChild(b); }
  show(EL[location.hash.slice(1)] ? location.hash.slice(1) : 'fire');
})();
