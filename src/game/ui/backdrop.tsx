// Les fonds des menus, style moderne (26/11/2026) : des illustrations vectorielles lisses dessinées par le code
// (backdrop-kit.tsx), une par onglet — la salle des héros, la nuit de l'invocation, la terre d'aventure, le donjon de la
// guilde — et un fond calme pour les pages (courrier, forge, fusion…). Une seule lumière, en haut à droite ; le sol est
// toujours plat, d'un bord à l'autre ; là où se pose le contenu, le fond reste calme. Mouvements : sections/backdrops.css.
// Le dessin n'est fait qu'une fois (Frozen) : l'application se redessine chaque seconde, le fond n'a pas à suivre.
import { Component, type JSX } from 'preact';
import './sections/backdrops.css';
import { AdventureBackdrop } from './backdrop-adventure';
import { SummonBackdrop } from './backdrop-summon';
import { HeroesBackdrop } from './backdrop-heroes';
import { GuildBackdrop } from './backdrop-guild';
import { Glow, H, Motes, Soft, VGrad, Vol, W, cloud, f, hills, spark } from './backdrop-kit';

export type BackdropKind = 'heroes' | 'summon' | 'adventure' | 'guild' | 'page';

/** Le fond des pages : raisin profond, une lueur en haut à droite, deux lignes de collines douces en bas, des nuages. */
function PageBackdrop() {
  const P = 'bp';
  return (
    <svg viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="xMidYMax slice">
      <defs>
        <Soft p={P} />
        <VGrad id={`${P}-sky`} stops={[[0, '#2e2273'], [0.45, '#22195c'], [1, '#160f3d']]} />
        <Glow id={`${P}-light`} c="#b59cff" a={0.42} />
        <VGrad id={`${P}-hill`} y1={680} y2={H} stops={[[0, '#33287f'], [1, '#1d1550']]} />
        <VGrad id={`${P}-hill2`} y1={730} y2={H} stops={[[0, '#251b62'], [1, '#150f3d']]} />
      </defs>
      <rect width={W} height={H} fill={`url(#${P}-sky)`} />
      <circle class="bk-breathe" cx="350" cy="40" r="300" fill={`url(#${P}-light)`} />
      <g opacity="0.16">
        <g class="bk-cloud"><Vol p={P} d={cloud(-30, 210, 150, 2)} fill="#c9b8ff" line={0} shade={0} rim={0} /></g>
        <g class="bk-cloud bk-slow"><Vol p={P} d={cloud(250, 420, 170, 9)} fill="#c9b8ff" line={0} shade={0} rim={0} /></g>
      </g>
      <Vol p={P} d={hills(17, 720, 46, 130)} fill={`url(#${P}-hill)`} line={0} depth={6} shade={0.25} rim={0.18} />
      <Vol p={P} d={hills(23, 778, 34, 110)} fill={`url(#${P}-hill2)`} line={0} depth={6} shade={0.25} rim={0.14} />
      <Motes seed={8} n={10} x0={10} x1={380} y0={300} y1={780} color="#d9ccff" />
      {[[318, 118, 5], [58, 300, 4], [300, 560, 3.5]].map(([x, y, k], i) => <path class={`bk-twinkle${i % 2 ? ' bk-late' : ''}`} style={{ transformOrigin: `${f(x!)}px ${f(y!)}px` }} d={spark(x!, y!, k!)} fill="#fff" opacity="0.8" />)}
    </svg>
  );
}

const SCENES: Record<BackdropKind, () => JSX.Element> = {
  heroes: HeroesBackdrop, summon: SummonBackdrop, adventure: AdventureBackdrop, guild: GuildBackdrop, page: PageBackdrop,
};

/** Dessiné une fois, redessiné seulement si le décor change. */
class Frozen extends Component<{ kind: BackdropKind }> {
  shouldComponentUpdate(next: { kind: BackdropKind }) { return next.kind !== this.props.kind; }
  render({ kind }: { kind: BackdropKind }) { const Scene = SCENES[kind]; return <Scene />; }
}

/** Le fond d'un écran. */
export function Backdrop({ kind }: { kind: BackdropKind }) {
  return <div class={`backdrop bk backdrop-${kind}`} aria-hidden="true"><Frozen kind={kind} /></div>;
}
