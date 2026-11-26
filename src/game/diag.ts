// Essai du 26/11 (plantage sur iPhone en changeant de zone, introuvable sur ordinateur) : une « boîte noire ».
// - Le jeu note en continu (dans le téléphone) ce qui se passe : les derniers boutons touchés, les erreurs, et un
//   battement toutes les 250 ms ; un long silence entre deux battements = un gel.
// - Avec l'adresse `?diag=1`, une petite fenêtre montre au lancement ce qu'avait noté la partie d'avant (celle qui a
//   planté) : le propriétaire en fait une capture. `?diag=0` la retire.
// - `?leger=1` : mode léger pour chercher la cause (plus aucune animation CSS, pas de combat sur l'accueil) ; `?leger=0`.
// Tout cela est à retirer avant la bêta.

const KEY = 'fuze-diag';
const PREV = 'fuze-diag-prev';

interface Record {
  start: number; beat: number; gap: number; gapAt: string; clean: boolean;
  crumbs: string[]; errors: string[]; ua: string;
}

function flag(name: string, key: string): boolean {
  try {
    const q = new URLSearchParams(location.search).get(name);
    if (q === '1') localStorage.setItem(key, '1');
    if (q === '0') localStorage.removeItem(key);
    return localStorage.getItem(key) === '1';
  } catch { return false; }
}

export function startDiag(): void {
  const show = flag('diag', 'fuze-diag-show');
  if (flag('leger', 'fuze-leger')) {
    document.documentElement.classList.add('leger');
    const st = document.createElement('style');
    st.textContent = '.leger *, .leger *::before, .leger *::after { animation: none !important; transition: none !important; }';
    document.head.appendChild(st);
  }
  bisect();
  let prev: Record | null = null;
  try {
    const old = localStorage.getItem(KEY);
    if (old) { localStorage.setItem(PREV, old); prev = JSON.parse(old) as Record; }
  } catch { /* pas de mémoire du téléphone : rien à noter */ }

  const t0 = Date.now();
  const rec: Record = { start: t0, beat: t0, gap: 0, gapAt: '', clean: false, crumbs: [], errors: [], ua: navigator.userAgent };
  const here = () => `${((Date.now() - t0) / 1000).toFixed(1)} s`;
  const save = () => { try { localStorage.setItem(KEY, JSON.stringify(rec)); } catch { /* plein : tant pis */ } };
  const crumb = (what: string) => { rec.crumbs.push(`${here()} ${what}`); if (rec.crumbs.length > 25) rec.crumbs.shift(); save(); };

  document.addEventListener('click', (e) => {
    const el = (e.target as Element | null)?.closest('button, [role=button], a');
    if (!el) return;
    const label = (el.getAttribute('aria-label') || el.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 28);
    crumb(`toucher « ${label} » (${(el.className || '').toString().split(' ')[0]})`);
  }, true);
  window.addEventListener('error', (e) => { rec.errors.push(`${here()} ${e.message} @${(e.filename || '').split('/').pop()}:${e.lineno}`); save(); });
  window.addEventListener('unhandledrejection', (e) => { rec.errors.push(`${here()} promesse : ${String((e as PromiseRejectionEvent).reason).slice(0, 120)}`); save(); });
  document.addEventListener('visibilitychange', () => { crumb(`page ${document.visibilityState}`); });
  window.addEventListener('pagehide', () => { rec.clean = true; save(); });
  setInterval(() => {
    const now = Date.now();
    const gap = now - rec.beat;
    if (gap > rec.gap && document.visibilityState === 'visible') { rec.gap = gap; rec.gapAt = here(); }
    rec.beat = now;
    save();
  }, 250);
  crumb('lancement');

  if (show) showPanel(prev);
}

function showPanel(prev: Record | null): void {
  const box = document.createElement('div');
  box.style.cssText = 'position:fixed;z-index:100000;left:8px;right:8px;top:max(8px,env(safe-area-inset-top));max-height:70vh;overflow:auto;'
    + 'background:#0b0820f2;color:#e8e4ff;font:12px/1.35 ui-monospace,Menlo,monospace;padding:10px 12px;border-radius:12px;'
    + 'border:1px solid #ffc94d88;white-space:pre-wrap;word-break:break-word';
  const lines: string[] = [];
  if (!prev) lines.push('Boîte noire : rien de noté la dernière fois.');
  else {
    const dur = ((prev.beat - prev.start) / 1000).toFixed(1);
    lines.push(`Partie précédente : ${dur} s, ${prev.clean ? 'fermée normalement' : 'COUPÉE (plantage ?)'}`);
    lines.push(`Plus long gel : ${(prev.gap / 1000).toFixed(1)} s (à ${prev.gapAt})`);
    lines.push(`Mode léger : ${document.documentElement.classList.contains('leger') ? 'oui' : 'non'}`);
    lines.push('', 'Derniers gestes :', ...prev.crumbs.slice(-14));
    if (prev.errors.length) lines.push('', 'Erreurs :', ...prev.errors.slice(-8));
    lines.push('', prev.ua);
  }
  box.textContent = lines.join('\n');
  const x = document.createElement('button');
  x.textContent = '✕';
  x.style.cssText = 'position:absolute;top:4px;right:6px;background:none;border:0;color:#ffc94d;font-size:18px';
  x.onclick = () => box.remove();
  box.appendChild(x);
  document.body.appendChild(box);
}

// ---------- Test automatique de l'onglet Héros (`?bisect=1`, 26/11) ----------
// Il ouvre l'onglet Héros plusieurs fois, en cachant à chaque fois une partie différente de l'écran ; si la page plante,
// Safari la recharge et le test note « PLANTE » pour cette partie, puis passe à la suivante. À la fin : le résultat.
const VARIANTS: [string, string][] = [
  ['complet', ''],
  ['sans le fond', '.backdrop { display: none !important; }'],
  ['sans la salle du haut', '.hall { display: none !important; }'],
  ['sans la grille', '.hall-scroll { display: none !important; }'],
  ['grille sans décor de carte', '.hcard-aura, .hcard-frame, .hcard::before, .hcard::after { display: none !important; } .hcard { background: #333 !important; --crest: none !important; }'],
  ['grille sans les héros', '.hcard-fig, .hcard-face { display: none !important; }'],
  ['sans filtres', '*, *::before, *::after { filter: none !important; backdrop-filter: none !important; -webkit-backdrop-filter: none !important; }'],
  ['sans masques', '*, *::before, *::after { mask: none !important; -webkit-mask: none !important; }'],
  ['sans ombres', '*, *::before, *::after { box-shadow: none !important; text-shadow: none !important; }'],
];
const BKEY = 'fuze-bisect';

function bisect(): void {
  let st: { i: number; pending?: number; res: string[] } | null = null;
  try {
    if (new URLSearchParams(location.search).get('bisect') === '1' && !localStorage.getItem(BKEY)) localStorage.setItem(BKEY, JSON.stringify({ i: 0, res: [] }));
    const raw = localStorage.getItem(BKEY);
    st = raw ? JSON.parse(raw) : null;
  } catch { return; }
  if (!st) return;
  const save = () => { try { localStorage.setItem(BKEY, JSON.stringify(st)); } catch { /* rien */ } };
  if (st.pending !== undefined) { st.res.push(`${VARIANTS[st.pending]![0]} : PLANTE`); st.pending = undefined; st.i++; save(); }
  const box = document.createElement('div');
  box.style.cssText = 'position:fixed;z-index:100001;left:8px;right:8px;bottom:max(8px,env(safe-area-inset-bottom));background:#0b0820f2;color:#e8e4ff;'
    + 'font:13px/1.4 ui-monospace,Menlo,monospace;padding:10px 12px;border-radius:12px;border:1px solid #ffc94d88;white-space:pre-wrap;pointer-events:none';
  const show = (text: string) => { box.textContent = text; if (!box.isConnected) document.body.appendChild(box); };
  const done = st.res.join('\n');
  if (st.i >= VARIANTS.length) {
    try { localStorage.removeItem(BKEY); } catch { /* rien */ }
    window.addEventListener('load', () => show(`Test terminé : fais une capture.\n\n${done}`));
    setTimeout(() => show(`Test terminé : fais une capture.\n\n${done}`), 3000);
    return;
  }
  const [name, css] = VARIANTS[st.i]!;
  const style = document.createElement('style');
  style.textContent = css;
  document.head.appendChild(style);
  st.pending = st.i;
  save();
  const status = () => show(`Test automatique ${st!.i + 1} / ${VARIANTS.length} : ${name}…\nNe touche à rien (si Safari affiche une erreur, rouvre le même lien).\n\n${done}`);
  setTimeout(status, 1500);
  setTimeout(() => (document.querySelector('.tabbar-btn:nth-child(2)') as HTMLElement | null)?.click(), 3000);
  setTimeout(() => {
    st!.res.push(`${name} : OK`);
    st!.pending = undefined;
    st!.i++;
    save();
    location.reload();
  }, 10000);
}
