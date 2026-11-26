// Mise à jour automatique : le jeu regarde régulièrement si une nouvelle version est en ligne
// (version.json) ; la nouvelle version s'installe au lancement ou au retour dans le jeu, jamais en pleine partie.
// L'adresse change (?v=…) pour passer outre la mémoire du téléphone.
declare const __BUILD__: string;

const CHECK_EVERY = 2 * 60 * 1000;

/** Une version plus récente attend : on ne recharge jamais en pleine partie (demande du 26/11 : le jeu « buggait »
 * parce qu'il se rechargeait tout seul à chaque envoi), seulement au retour dans le jeu ou au lancement. */
let pending: string | null = null;

function reload(build: string): void {
  // Une seule tentative par version, pour ne jamais recharger en boucle.
  const key = 'hero-battle-update';
  if (sessionStorage.getItem(key) === build) return;
  sessionStorage.setItem(key, build);
  location.replace(`${location.pathname}?v=${build}${location.hash}`);
}

async function check(now = false): Promise<void> {
  try {
    const res = await fetch(`./version.json?t=${Date.now()}`, { cache: 'no-store' });
    if (!res.ok) return;
    const { build } = (await res.json()) as { build?: string };
    if (!build || build === __BUILD__) return;
    if (now) reload(build);
    else pending = build;
  } catch {
    // hors ligne ou page de la copie claude.ai : on garde la version actuelle
  }
}

export function watchUpdates(): void {
  if (!import.meta.env.PROD || location.protocol === 'file:') return;
  // au lancement : on prend tout de suite la dernière version ; ensuite on la note sans interrompre la partie
  void check(true);
  setInterval(() => void check(), CHECK_EVERY);
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'hidden') void check();
    // de retour dans le jeu (après l'avoir quitté) : la nouvelle version s'installe à ce moment-là
    else if (pending) reload(pending);
  });
}
