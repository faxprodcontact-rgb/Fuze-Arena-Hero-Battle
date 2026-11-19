// Mise à jour automatique : le jeu regarde régulièrement si une nouvelle version est en ligne
// (version.json) et se recharge tout seul. L'adresse change (?v=…) pour passer outre la mémoire du téléphone.
declare const __BUILD__: string;

const CHECK_EVERY = 2 * 60 * 1000;

async function check(): Promise<void> {
  try {
    const res = await fetch(`./version.json?t=${Date.now()}`, { cache: 'no-store' });
    if (!res.ok) return;
    const { build } = (await res.json()) as { build?: string };
    if (!build || build === __BUILD__) return;
    // Une seule tentative par version, pour ne jamais recharger en boucle.
    const key = 'hero-battle-update';
    if (sessionStorage.getItem(key) === build) return;
    sessionStorage.setItem(key, build);
    location.replace(`${location.pathname}?v=${build}${location.hash}`);
  } catch {
    // hors ligne ou page de la copie claude.ai : on garde la version actuelle
  }
}

export function watchUpdates(): void {
  if (!import.meta.env.PROD || location.protocol === 'file:') return;
  void check();
  setInterval(() => void check(), CHECK_EVERY);
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible') void check();
  });
}
