// Le SIGNE DU REPOS d'un héros dans les menus (demande du 27/11 : « une petite animation lente mais visible de ce qui
// lui est propre : arme, cheveux… partout, même quand on obtient le héros »). L'image des menus (art/vecto/<id>.webp)
// est remplacée par sa base (les zones qui bougent vidées) et, par-dessus, une bande d'images par zone qui défile en
// CSS (steps) : refonte-graphique/ui-moderne/heros/repos.py, table vecto-repos.ts. Seulement là où le héros est seul et
// en grand (fiche, tirage, estrade) : peu de mémoire graphique (iPhone). Sans signe : l'image fixe.
// Corrigé le 27/11 : les zones peuvent déborder du cadre de l'image (une plume, une flamme qui en sortait était coupée
// net) ; chaque image de la bande a une gouttière (plus de fil de l'image voisine au bord d'une zone) ; les noms des
// fichiers changent avec leur contenu (un jeu resté ouvert sur l'ancienne version ne mélange plus mesures et images).
import { useState } from 'preact/hooks';
import { artUrl } from '../art-url';
import { VECTO_REPOS } from '../vecto-repos';

export function VectoImage({ id, src, live = true, style, class: cls }: {
  id: string; src: string; live?: boolean; style?: Record<string, string>; class?: string;
}) {
  // si une image du signe manque (la copie claude.ai, limitée en fichiers, ne les a pas ; une ancienne version) : l'image fixe
  const [failed, setFailed] = useState(false);
  const r = live && !failed ? VECTO_REPOS[id] : undefined;
  if (!r) return <img class={cls} src={src} alt="" draggable={false} style={style} />;
  const [W, H] = r.taille;
  const pc = (v: number, t: number) => `${((v / t) * 100).toFixed(3)}%`;
  const fail = () => setFailed(true);
  return (
    <span class={`vl ${cls ?? ''}`} style={style}>
      <img src={artUrl(`art/vecto/repos/${id}-${r.v}-base.webp`)} alt="" draggable={false} onError={fail} />
      {r.zones.map(([x, y, w, h], k) => (
        <span class="vl-z" style={{ left: pc(x, W), top: pc(y, H), width: pc(w, W), height: pc(h, H) }}>
          <img src={artUrl(`art/vecto/repos/${id}-${r.v}-${k}.webp`)} alt="" draggable={false} onError={fail}
            style={{ width: pc(r.n * (w + 2 * r.g), w), left: pc(-r.g, w), animationDuration: `${r.ms}ms`, animationTimingFunction: `steps(${r.n})` }} />
        </span>
      ))}
    </span>
  );
}
