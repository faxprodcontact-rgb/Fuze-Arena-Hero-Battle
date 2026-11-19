// Sac : tous les objets, la forge (3 identiques → rareté au-dessus), le recyclage en poussière de forge,
// et la fenêtre d'un emplacement de héros (choisir l'objet, renforcer l'emplacement).
import { useState } from 'preact/hooks';
import { heroDef } from '../../../core/data/heroes';
import {
  FORGE_COUNT, GEAR_SLOTS, ITEM_RARITIES, SLOT_MAX_LEVEL, equippedBonus, itemBonus, recycleDust, slotUpgradeCost,
  type GearSlot, type Item,
} from '../../../core/data/items';
import { ITEM_COLORS } from '../../art';
import { t } from '../../i18n';
import { equipItem, forgeAll, forgeItem, forgePartners, recycleItems, unequipItem, upgradeSlot } from '../../state/actions';
import { heroByUid, slotLevel } from '../../state/selectors';
import { useGame } from '../../state/store';
import type { PlayerState } from '../../state/types';
import { Btn, Cur, Icon, ItemIcon, Modal } from '../kit';
import { close, open, toast } from '../nav';

function owner(s: PlayerState, item: Item) {
  return item.heroUid !== undefined ? heroByUid(s, item.heroUid) : undefined;
}

function sortItems(items: Item[]): Item[] {
  return [...items].sort((a, b) => b.rarity - a.rarity || itemBonus(b) - itemBonus(a));
}

export function BagView() {
  const s = useGame();
  const [slot, setSlot] = useState<GearSlot | 'all'>('all');
  const items = sortItems(s.items.filter((it) => slot === 'all' || it.slot === slot));
  const low = s.items.filter((it) => it.heroUid === undefined && it.rarity <= 1);
  return (
    <div class="screen bag">
      <div class="row between">
        <h2>{t('bag.title')} <span class="muted">{s.items.length}</span></h2>
        <Cur k="dust" n={s.wallet.dust} />
      </div>
      <div class="row gap-s">
        <Btn kind="gold" small wide onClick={() => toast(t('bag.forged', { n: forgeAll().length }))}>{t('bag.forgeAll')}</Btn>
        <Btn kind="ghost" small wide disabled={!low.length} onClick={() => toast(t('bag.recycled', { n: recycleItems(low.map((it) => it.uid)) }))}>
          {t('bag.recycleLow')}
        </Btn>
      </div>
      <div class="chips">
        <button class={`chip${slot === 'all' ? ' on' : ''}`} onClick={() => setSlot('all')}>{t('all')}</button>
        {GEAR_SLOTS.map((g) => (
          <button class={`chip${slot === g ? ' on' : ''}`} onClick={() => setSlot(g)}><Icon name={g} size={16} /> {t(`slot.${g}`)}</button>
        ))}
      </div>
      {items.length === 0 ? <p class="center muted">{t('bag.empty')}</p> : (
        <div class="item-grid">
          {items.map((it) => {
            const o = owner(s, it);
            return (
              <ItemIcon item={it} heroDefId={o?.defId} level={o ? slotLevel(s, o.uid, it.slot) : 0}
                onClick={() => open({ type: 'item', uid: it.uid })} />
            );
          })}
        </div>
      )}
    </div>
  );
}

export function ItemModal({ uid }: { uid: number }) {
  const s = useGame();
  const item = s.items.find((it) => it.uid === uid);
  if (!item) return null;
  const o = owner(s, item);
  const partners = forgePartners(s, item);
  const canForge = !o && item.rarity < ITEM_RARITIES - 1;
  return (
    <Modal title={`${t(`slot.${item.slot}`)} · ${t(`item.${item.rarity}`)}`}>
      <div class="item-top" style={{ '--rar': ITEM_COLORS[item.rarity] } as never}>
        <ItemIcon item={item} level={o ? slotLevel(s, o.uid, item.slot) : 0} />
        <div>
          <div class="item-big">+{itemBonus(item)} %</div>
          <div class="muted small">{t('item.chapter', { n: item.tier + 1 })}</div>
          {o && <div class="small">{t('item.wornBy', { n: heroDef(o.defId).name })}</div>}
        </div>
      </div>
      {canForge && (
        <section class="block">
          <div class="row between center-y">
            <span class="row gap-s center-y">
              <span class="rar-dot" style={{ background: ITEM_COLORS[item.rarity] }} />→<span class="rar-dot" style={{ background: ITEM_COLORS[item.rarity + 1] }} />
            </span>
            <span class={partners.length + 1 >= FORGE_COUNT ? 'gold-text' : 'muted'}>{t('item.forgeNeed', { have: Math.min(FORGE_COUNT, partners.length + 1) })}</span>
          </div>
          <Btn kind="gold" wide disabled={partners.length + 1 < FORGE_COUNT} onClick={() => {
            const made = forgeItem(item.uid);
            close();
            if (made) open({ type: 'item', uid: made.uid });
          }}>{t('item.forge')}</Btn>
        </section>
      )}
      <div class="row gap">
        {o ? (
          <Btn kind="ghost" wide onClick={() => unequipItem(item.uid)}>{t('item.unequip')}</Btn>
        ) : (
          <Btn kind="red" wide onClick={() => { recycleItems([item.uid]); close(); }}>
            {t('item.recycle')} <Cur k="dust" n={recycleDust(item)} />
          </Btn>
        )}
      </div>
    </Modal>
  );
}

export function SlotModal({ heroUid, slot }: { heroUid: number; slot: GearSlot }) {
  const s = useGame();
  const hero = heroByUid(s, heroUid);
  if (!hero) return null;
  const level = slotLevel(s, heroUid, slot);
  const current = s.items.find((it) => it.heroUid === heroUid && it.slot === slot);
  const bag = sortItems(s.items.filter((it) => it.slot === slot && it.heroUid === undefined));
  const cost = level < SLOT_MAX_LEVEL ? slotUpgradeCost(level) : null;
  const ok = !!cost && s.wallet.gold >= cost.gold && s.wallet.dust >= cost.dust;
  return (
    <Modal title={`${heroDef(hero.defId).name} · ${t(`slot.${slot}`)}`}>
      <section class="block">
        <div class="row between center-y">
          <ItemIcon item={current} slot={slot} level={level} onClick={() => current && open({ type: 'item', uid: current.uid })} />
          <div class="grow slot-info">
            <strong>{t('slot.level', { n: level })} / {SLOT_MAX_LEVEL}</strong>
            {current && (
              <span class="muted">
                +{equippedBonus(current, level)} %{cost && <> → <b class="gold-text">+{equippedBonus(current, level + 1)} %</b></>}
              </span>
            )}
          </div>
        </div>
        {cost ? (
          <Btn kind="gold" wide disabled={!ok} onClick={() => upgradeSlot(heroUid, slot)}>
            {t('slot.upgrade')} <Cur k="gold" n={cost.gold} /> <Cur k="dust" n={cost.dust} />
          </Btn>
        ) : <p class="center gold-text">{t('slot.max')}</p>}
        {current && <Btn kind="ghost" small onClick={() => unequipItem(current.uid)}>{t('item.unequip')}</Btn>}
      </section>
      <h3>{t('slot.choose')}</h3>
      {bag.length === 0 ? <p class="muted">{t('bag.empty')}</p> : (
        <div class="item-grid">
          {bag.map((it) => <ItemIcon item={it} level={level} hideLevel onClick={() => equipItem(it.uid, heroUid)} />)}
        </div>
      )}
    </Modal>
  );
}
