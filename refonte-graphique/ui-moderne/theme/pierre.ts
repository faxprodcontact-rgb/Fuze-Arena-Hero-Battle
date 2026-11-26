// L'essai d'habillage « pierre » (26/11) : fabrique src/game/ui/theme-pierre.css à partir de TOUS les fichiers CSS de
// l'interface. Chaque règle qui emploie un bleu foncé raisin est recopiée sous :root[data-theme="pierre"], avec ses
// couleurs passées en pierre de basalte (stoneHex de src/game/ui/theme.ts : la même conversion que les dessins).
//
//   npx tsx refonte-graphique/ui-moderne/theme/pierre.ts
//
// À relancer après chaque changement de couleur dans un fichier CSS (sinon l'essai garde l'ancienne couleur).
// Les règles recopiées gardent leur priorité (:where(...) ne compte pas) ; le fichier est importé en dernier (main.tsx),
// donc il gagne à priorité égale. Les jetons (:root) passent sous :root[data-theme="pierre"]. Les filets d'or ajoutés
// à la main sont dans src/game/ui/theme-pierre-or.css.
import fs from 'node:fs';
import path from 'node:path';
import postcss, { type AtRule, type Container, type Rule } from 'postcss';
import { stoneText } from '../../../src/game/ui/theme';

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '../../..');
const UI = path.join(ROOT, 'src/game/ui');
const OUT = path.join(UI, 'theme-pierre.css');
const files = ['style.css', 'anim.css', ...fs.readdirSync(path.join(UI, 'sections')).filter((f) => f.endsWith('.css')).sort().map((f) => `sections/${f}`)];

const ON = ':root[data-theme="pierre"]';
const W = `:where(${ON})`;
function prefix(sel: string): string {
  const s = sel.trim();
  if (s.startsWith(':root')) return ON + s.slice(5);
  if (/^html\b/.test(s)) return `html[data-theme="pierre"]${s.slice(4)}`;
  return `${W} ${s}`;
}
/** Une couleur codée dans une adresse data: (%23rrggbb). */
const recolor = (v: string) => stoneText(v).replace(/%23([0-9a-fA-F]{6})\b/g, (_m, h: string) => '%23' + stoneText('#' + h).slice(1));

let rules = 0, decls = 0;
const out = postcss.root();
for (const f of files) {
  const src = fs.readFileSync(path.join(UI, f), 'utf8');
  const root = postcss.parse(src, { from: f });
  const head = postcss.comment({ text: ` ${f} ` });
  let any = false;
  const parts: postcss.ChildNode[] = [];
  root.walkRules((r: Rule) => {
    // pas les images clés (on ne peut pas les préfixer) : leurs couleurs restent
    for (let p = r.parent; p; p = (p as Container).parent as Container) if (p.type === 'atrule' && /keyframes$/.test((p as AtRule).name)) return;
    const changed = r.nodes.filter((d) => d.type === 'decl' && recolor(d.value) !== d.value);
    if (!changed.length) return;
    const nr = postcss.rule({ selectors: r.selectors.map(prefix) });
    for (const d of changed) if (d.type === 'decl') { nr.append({ prop: d.prop, value: recolor(d.value), important: d.important }); decls++; }
    // recopier les @media / @supports qui entourent la règle
    let node: postcss.ChildNode = nr;
    for (let p = r.parent; p && p.type === 'atrule'; p = p.parent as Container) {
      const a = postcss.atRule({ name: (p as AtRule).name, params: (p as AtRule).params });
      a.append(node);
      node = a;
    }
    parts.push(node);
    rules++; any = true;
  });
  if (any) { out.append(head); for (const p of parts) out.append(p); }
}
const banner = `/* FABRIQUÉ par refonte-graphique/ui-moderne/theme/pierre.ts — ne pas modifier à la main (relancer le script).
   Essai d'habillage « pierre » (26/11) : allumé par ?theme=pierre (src/game/ui/theme.ts). ${rules} règles, ${decls} couleurs. */\n`;
fs.writeFileSync(OUT, banner + out.toString().replace(/\n{3,}/g, '\n\n') + '\n');
console.log(`${path.relative(ROOT, OUT)} : ${rules} règles, ${decls} déclarations, ${(fs.statSync(OUT).size / 1024).toFixed(1)} Ko`);
