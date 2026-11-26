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
const KEEP = /\.hcard-(common|uncommon|rare|epic|legendary|legend|mythic|myth)\b|\.(el|elem|element)-(water|fire|earth|wind)\b/;
const W = `:where(${ON})`;
/** Le sélecteur sous l'essai, à la MÊME priorité que l'original (:where ne compte pas). */
function prefix(sel: string): string {
  const s = sel.trim();
  if (s.startsWith(':root')) return ':root:where([data-theme="pierre"])' + s.slice(5);
  if (/^html\b/.test(s)) return `html:where([data-theme="pierre"])${s.slice(4)}`;
  return `${W} ${s}`;
}
/** Une couleur codée dans une adresse data: (%23rrggbb). */
const recolor = (v: string) => stoneText(v).replace(/%23([0-9a-fA-F]{6})\b/g, (_m, h: string) => '%23' + stoneText('#' + h).slice(1));

/** Les sélecteurs complets d'une règle (les règles imbriquées `& .x` sous `:root { … }` sont dépliées). */
function selectorsOf(r: Rule): string[] {
  const parent = r.parent;
  if (!parent || parent.type !== 'rule') return r.selectors;
  const ps = selectorsOf(parent as Rule);
  return ps.flatMap((p) => r.selectors.map((s) => (s.includes('&') ? s.replace(/&/g, p) : `${p} ${s}`)));
}
const spec = (sel: string) => {
  const t = sel.replace(/:where\([^)]*\)/g, '').replace(/:(is|not|has)\(([^,)]*)[^)]*\)/g, ' $2 ');
  const ids = (t.match(/#[\w-]+/g) || []).length;
  const cls = (t.match(/\.[\w-]+|\[[^\]]+\]|:(?!:)[\w-]+/g) || []).length;
  const els = (t.replace(/\[[^\]]+\]/g, '').match(/(^|[\s>+~])[a-z][\w-]*/gi) || []).length;
  return ids * 10000 + cls * 100 + els;
};
/** Les classes du sujet d'un sélecteur (son dernier morceau) : `.a .b.c-d` → b, c-d. */
const subject = (sel: string) => {
  const last = sel.replace(/\([^)]*\)/g, '').trim().split(/[\s>+~]+/).pop() ?? '';
  return [...last.matchAll(/\.([\w-]+)|(:root)/g)].map((m) => m[1] ?? m[2]!);
};

// Une règle recopiée passe APRÈS tout le CSS : à priorité égale, elle battrait aussi les règles qui venaient après
// l'originale (ex. `.hcard { --c2 }` puis `.hcard-rare { --c2 }`). Ces règles d'après (même priorité, même sujet ou une
// variante `sujet-xxx`, même propriété) sont donc recopiées elles aussi, à leur place, pour garder l'ordre d'origine.
type Done = { prop: string; sp: number; sub: string[] };
const done: Done[] = [];
const follows = (prop: string, sels: string[]) => sels.some((s2) => {
  const sp = spec(s2), sub2 = subject(s2);
  return done.some((e) => e.prop === prop && e.sp === sp && e.sub.some((c1) => sub2.some((c2) => c2 === c1 || c2.startsWith(c1 + '-'))));
});

let rules = 0, decls = 0, replays = 0;
const out = postcss.root();
for (const f of files) {
  const root = postcss.parse(fs.readFileSync(path.join(UI, f), 'utf8'), { from: f });
  const parts: postcss.ChildNode[] = [];
  root.walkRules((r: Rule) => {
    // pas les images clés (on ne peut pas les préfixer) : leurs couleurs restent
    for (let p = r.parent; p; p = (p as Container).parent as Container) if (p.type === 'atrule' && /keyframes$/.test((p as AtRule).name)) return;
    const sels = selectorsOf(r);
    // les couleurs de rareté et d'élément ne bougent pas (cadres des cartes de héros, pastilles d'élément)
    const keep = KEEP.test(sels.join(','));
    const nr = postcss.rule({ selectors: sels.map(prefix) });
    for (const d of r.nodes) {
      if (d.type !== 'decl') continue;
      const v = keep ? d.value : recolor(d.value);
      const replay = follows(d.prop, sels);
      if (v === d.value && !replay) continue;
      nr.append({ prop: d.prop, value: v, important: d.important });
      if (v !== d.value) decls++; else replays++;
      for (const s1 of sels) done.push({ prop: d.prop, sp: spec(s1), sub: subject(s1) });
    }
    if (!nr.nodes.length) return;
    // recopier les @media / @supports qui entourent la règle
    let node: postcss.ChildNode = nr;
    for (let p = r.parent; p; p = p.parent as Container) {
      if (p.type !== 'atrule') continue;
      const a = postcss.atRule({ name: (p as AtRule).name, params: (p as AtRule).params });
      a.append(node);
      node = a;
    }
    parts.push(node);
    rules++;
  });
  if (parts.length) { out.append(postcss.comment({ text: ` ${f} ` })); for (const p of parts) out.append(p); }
}
const banner = `/* FABRIQUÉ par refonte-graphique/ui-moderne/theme/pierre.ts — ne pas modifier à la main (relancer le script).
   Essai d'habillage « pierre » (26/11) : allumé par ?theme=pierre (src/game/ui/theme.ts). ${rules} règles, ${decls} couleurs. */\n`;
fs.writeFileSync(OUT, banner + out.toString().replace(/\n{3,}/g, '\n\n') + '\n');
console.log(`${path.relative(ROOT, OUT)} : ${rules} règles, ${decls} couleurs, ${replays} recopiées pour l'ordre, ${(fs.statSync(OUT).size / 1024).toFixed(1)} Ko`);
