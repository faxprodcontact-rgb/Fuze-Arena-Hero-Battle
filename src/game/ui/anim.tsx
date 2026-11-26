// Le halo des menus, dans le style moderne (lisse) : derrière un trophée, un héros fusionné, un tirage rare, un Légendaire.
// Le coffre et le sablier animés de l'ancien style sont devenus des pictos de la planche (chestClosed / chestReady /
// chestOpen, hourglass) ; leurs mouvements sont de petits sauts en CSS (style.css).
import './anim.css';
import { haloLayers } from './px';

/** Un halo : une lueur qui respire et huit étincelles qui tournent lentement (dessins de haloLayers, px.ts). */
export function Halo({ size = 150, color = '#ffc531', class: cls = '' }: { size?: number; color?: string; class?: string }) {
  const h = haloLayers(color);
  return (
    <span class={`anim halo-anim ${cls}`} aria-hidden="true" style={{ width: `${size}px`, height: `${size}px`, backgroundImage: h.glow }}>
      <i class="halo-spin" style={{ backgroundImage: h.spin }} />
    </span>
  );
}
