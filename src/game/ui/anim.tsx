// Le halo des menus, en pixel art (nouvelle DA) : derrière un trophée, un héros fusionné, un tirage rare, un Légendaire.
// Le coffre et le sablier animés de l'ancien style sont devenus des pictos de la planche (chestClosed / chestReady /
// chestOpen, hourglass) ; leurs mouvements sont de petits sauts en CSS (style.css).
import './anim.css';
import { HALO_FRAMES, PX, haloStrip } from './px';

/** Un halo de signes qui tourne (bande d'images dessinée par haloStrip, jouée par steps()). */
export function Halo({ size = 150, color = '#ffc531', class: cls = '' }: { size?: number; color?: string; class?: string }) {
  const d = Math.round(size / PX);
  const w = d * PX;
  return (
    <span class={`anim halo-anim ${cls}`} aria-hidden="true" style={{
      width: `${w}px`, height: `${w}px`, '--hw': `${w}px`,
      backgroundImage: `url(${haloStrip(d, color)})`, backgroundSize: `${w * HALO_FRAMES}px ${w}px`,
    }} />
  );
}
