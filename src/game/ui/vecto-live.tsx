// Le SIGNE DU REPOS d'un héros dans les menus (demande du 27/11 : « une petite animation lente mais visible de ce qui
// lui est propre : arme, cheveux… partout, même quand on obtient le héros »). L'image des menus (art/vecto/<id>.webp)
// est remplacée par sa base (les zones qui bougent vidées) et, par-dessus, une bande d'images par zone qui défile en
// CSS (steps) : refonte-graphique/ui-moderne/heros/repos.py, table vecto-repos.ts. Seulement là où le héros est seul et
// en grand (fiche, tirage, estrade) : peu de mémoire graphique (iPhone). Sans signe : l'image fixe.
import { useState } from 'preact/hooks';
import { artUrl } from '../art-url';
import { VECTO_REPOS } from '../vecto-repos';

export function VectoImage({ id, src, live = true, style, class: cls }: {
  id: string; src: string; live?: boolean; style?: Record<string, string>; class?: string;
}) {
  // si les images du signe manquent (la copie claude.ai, limitée en fichiers, ne les a pas) : l'image fixe
  const [failed, setFailed] = useState(false);
  const r = live && !failed ? VECTO_REPOS[id] : undefined;
  if (!r) return <img class={cls} src={src} alt="" draggable={false} style={style} />;
  const [W, H] = r.taille;
  const pc = (v: number, t: number) => `${((v / t) * 100).toFixed(3)}%`;
  return (
    <span class={`vl ${cls ?? ''}`} style={style}>
      <img src={artUrl(`art/vecto/repos/${id}-base.webp`)} alt="" draggable={false} onError={() => setFailed(true)} />
      {r.zones.map(([x, y, w, h], k) => (
        <span class="vl-z" style={{ left: pc(x, W), top: pc(y, H), width: pc(w, W), height: pc(h, H) }}>
          <img src={artUrl(`art/vecto/repos/${id}-${k}.webp`)} alt="" draggable={false}
            style={{ width: `${r.n * 100}%`, animationDuration: `${r.ms}ms`, animationTimingFunction: `steps(${r.n})` }} />
        </span>
      ))}
    </span>
  );
}
