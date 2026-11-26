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
