// Les pages légales EN LIGNE (28/11/2026) : règles de confidentialité et conditions d'utilisation, demandées par Google
// (écran de connexion), Apple et les magasins. Fabriquées à chaque construction (plugin de vite.config.ts) à partir des
// MÊMES textes que dans le jeu (legal.ts) : confidentialite.html, conditions.html, mentions.html, à la racine du site.
// Une page = le texte français puis l'anglais (ancre #en), aux couleurs du jeu.
import { legalDoc, type LegalDoc } from './legal';

const PAGES: { doc: LegalDoc; file: string; fr: string; en: string }[] = [
  { doc: 'privacy', file: 'confidentialite.html', fr: 'Règles de confidentialité', en: 'Privacy policy' },
  { doc: 'terms', file: 'conditions.html', fr: "Conditions d'utilisation", en: 'Terms of service' },
  { doc: 'notice', file: 'mentions.html', fr: 'Mentions légales', en: 'Legal notice' },
];

const esc = (s: string) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

function body(doc: LegalDoc, lang: 'fr' | 'en'): string {
  return legalDoc(doc, lang).map((b) => ('h' in b ? `<h2>${esc(b.h)}</h2>` : `<p>${esc(b.p)}</p>`)).join('\n');
}

function page(p: (typeof PAGES)[number]): string {
  const others = PAGES.filter((x) => x !== p).map((x) => `<a href="${x.file}">${esc(x.fr)}</a>`).join(' · ');
  return `<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(p.fr)} — Fuze Arena – Hero Battle</title>
<link rel="icon" href="art/ui-px/icone-192.png">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Lilita+One&family=Fredoka:wght@500;600&display=swap">
<style>
  :root { color-scheme: dark; }
  body { margin: 0; background: #1b1426; color: #efe6ff; font: 500 16px/1.6 Fredoka, system-ui, sans-serif; }
  main { max-width: 720px; margin: 0 auto; padding: 28px max(18px, env(safe-area-inset-left)) 60px; }
  header { display: flex; align-items: center; gap: 14px; margin-bottom: 10px; }
  header img { width: 56px; height: 56px; border-radius: 14px; }
  .game { font-family: 'Lilita One', Fredoka, sans-serif; color: #ffcf5a; font-size: 20px; }
  h1 { font-family: 'Lilita One', Fredoka, sans-serif; font-weight: 400; color: #ffcf5a; font-size: 30px; margin: 18px 0 4px; }
  h2 { font-family: 'Lilita One', Fredoka, sans-serif; font-weight: 400; color: #fff; font-size: 20px; margin: 26px 0 6px; }
  p { margin: 6px 0; color: #d9cdee; }
  a { color: #ffcf5a; }
  .lang { margin: 6px 0 0; font-size: 14px; }
  hr { border: 0; border-top: 1px solid #4a3e5c; margin: 42px 0 10px; }
  footer { margin-top: 40px; font-size: 14px; color: #a898c0; }
</style>
</head>
<body>
<main>
<header><img src="art/ui-px/icone-192.png" alt=""><span class="game">Fuze Arena – Hero Battle</span></header>
<h1>${esc(p.fr)}</h1>
<p class="lang"><a href="#en">English version</a></p>
${body(p.doc, 'fr')}
<hr>
<h1 id="en">${esc(p.en)}</h1>
${body(p.doc, 'en')}
<footer>Un jeu de FAXSTUDIO – Simon Ribic · A FAXSTUDIO – Simon Ribic game<br>${others} · <a href="./">Jouer / Play</a></footer>
</main>
</body>
</html>
`;
}

/** Les pages à écrire à la racine du site : [nom du fichier, contenu]. */
export function legalPages(): [string, string][] {
  return PAGES.map((p) => [p.file, page(p)]);
}
