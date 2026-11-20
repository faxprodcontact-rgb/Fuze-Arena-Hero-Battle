// Galerie des 72 héros (site de test) : chaque carte assemble les morceaux du héros, au repos, avec son contour.
(() => {
  const D = window.HEROS, E = D.E;
  const EL = { fire: ['Feu', '#d8502a', '#f1d6c2'], wind: ['Vent', '#2a9a8e', '#d3ece4'], water: ['Eau', '#3a78d8', '#cfe0f4'], earth: ['Terre', '#7a8a34', '#e2dcc0'] };
  const RAR = { common: ['Commun', '#7c8596'], rare: ['Rare', '#2f6fe0'], epic: ['Épique', '#8a3ce0'], legendary: ['Légendaire', '#c98a10'] };
  const ROLE = { protector: 'Protecteur', warrior: 'Guerrier', marksman: 'Tireur', assassin: 'Assassin', healer: 'Soigneur', support: 'Soutien' };
  const grid = document.getElementById('grid'), tabs = document.getElementById('tabs');
  const A = document.createElement('canvas'), B = document.createElement('canvas');
  function render(cv, h, img) {
    const dpr = Math.min(3, window.devicePixelRatio || 1), W = cv.width = Math.round(cv.clientWidth * dpr), H = cv.height = Math.round(cv.clientHeight * dpr);
    const g = cv.getContext('2d'), q = H / 292 * Math.min(1.12, h.scale) * 0.9, ox = W / 2 - 106 * q, oy = H * 0.95 - 228 * q;
    const put = (c, p) => c.drawImage(img, p.x, p.y, p.w, p.h, ox + p.ox * q, oy + p.oy * q, p.w / E * q, p.h / E * q);
    g.fillStyle = 'rgba(40,28,16,.2)'; g.beginPath(); g.ellipse(W / 2, H * 0.95, 62 * q, 12 * q, 0, 0, 6.3); g.fill();
    for (const p of h.parts) if (p.name === 'glow') put(g, p);
    A.width = B.width = W; A.height = B.height = H;
    const a = A.getContext('2d'), b = B.getContext('2d');
    for (const p of h.parts) if (p.name !== 'glow') put(a, p);
    b.drawImage(A, 0, 0); b.globalCompositeOperation = 'source-in'; b.fillStyle = '#190c24'; b.fillRect(0, 0, W, H);
    const r = Math.max(1, 1.6 * q);
    for (let i = 0; i < 8; i++) g.drawImage(B, Math.cos(i * 0.785) * r, Math.sin(i * 0.785) * r);
    g.drawImage(A, 0, 0);
  }
  const seen = new IntersectionObserver((list) => { for (const e of list) if (e.isIntersecting) { seen.unobserve(e.target); const h = e.target.hero, img = new Image(); img.onload = () => render(e.target, h, img); img.src = 'h/' + h.id + '.png'; } }, { rootMargin: '300px' });
  function show(el) {
    grid.innerHTML = '';
    for (const b of tabs.children) b.classList.toggle('on', b.dataset.el === el);
    for (const h of D.list.filter((x) => x.element === el)) {
      const card = document.createElement('div'); card.className = 'card'; card.style.setProperty('--r', RAR[h.rarity][1]); card.style.setProperty('--bg', EL[el][2]);
      const cv = document.createElement('canvas'); cv.hero = h; card.appendChild(cv);
      const name = document.createElement('b'); name.textContent = (h.leader ? '♛ ' : '') + h.name; card.appendChild(name);
      const sub = document.createElement('i'); sub.textContent = RAR[h.rarity][0] + ' · ' + ROLE[h.role]; card.appendChild(sub);
      const from = document.createElement('small'); from.textContent = h.from; card.appendChild(from);
      grid.appendChild(card); seen.observe(cv);
    }
    try { history.replaceState(null, '', '#' + el); } catch (e) { /* aperçu sans historique */ }
  }
  for (const el of Object.keys(EL)) { const b = document.createElement('button'); b.textContent = EL[el][0]; b.dataset.el = el; b.style.setProperty('--c', EL[el][1]); b.onclick = () => show(el); tabs.appendChild(b); }
  show(EL[location.hash.slice(1)] ? location.hash.slice(1) : 'fire');
})();
