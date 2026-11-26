// Le portrait du joueur (vague 3, 26/11/2026) : dans les réglages, une ligne « Portrait » montre le visage choisi ; la
// toucher ouvre la grille des visages des héros découverts (le choisi cerclé d'or, coché). Toucher un visage le choisit.
// Le portrait s'affiche en haut à gauche de l'accueil (app.tsx, `avatarOf`).
import { HEROES } from '../../../core/data/heroes';
import { RARITIES } from '../../../core/types';
import { ELEMENT_COLOR, heroImage } from '../../art';
import { t } from '../../i18n';
import { setAvatar } from '../../state/actions';
import { avatarOf } from '../../state/selectors';
import { useGame } from '../../state/store';
import { Modal, Sign } from '../kit';
import { close, open } from '../nav';
import '../sections/avatar.css';

/** La ligne des réglages : « Portrait », le visage choisi, un chevron. */
export function AvatarRow() {
  const s = useGame();
  const id = avatarOf(s);
  return (
    <button class="setting-row avatar-row" onClick={() => open({ type: 'avatar' })}>
      <span>{t('settings.avatar')}</span>
      <span class="row gap-s center-y">
        {id && <span class="avatar-face"><img src={heroImage(id)} alt="" /></span>}
        <Sign name="chev-s" class="chev" />
      </span>
    </button>
  );
}

/** La grille des visages : les héros découverts, les plus rares d'abord. */
export function AvatarModal() {
  const s = useGame();
  const current = avatarOf(s);
  const known = new Set(s.discovered);
  const rank = (r: string) => RARITIES.indexOf(r as never);
  const list = HEROES.filter((h) => known.has(h.id)).sort((a, b) => rank(b.rarity) - rank(a.rarity));
  return (
    <Modal title={t('settings.avatar')}>
      <div class="avatar-grid">
        {list.map((h) => (
          <button class={`avatar-pick${h.id === current ? ' on' : ''}`} style={{ '--el': ELEMENT_COLOR[h.element] } as never}
            aria-label={h.name} aria-pressed={h.id === current}
            onClick={() => { setAvatar(h.id); close(); }}>
            <img src={heroImage(h.id)} alt="" />
            {h.id === current && <span class="avatar-check"><Sign name="check" k={2} /></span>}
          </button>
        ))}
      </div>
    </Modal>
  );
}
