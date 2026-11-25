// Sac : tous les objets, la forge (3 identiques → rareté au-dessus), le recyclage en poussière de forge,
// et le panneau d'un emplacement de héros (choisir l'objet, renforcer l'emplacement), affiché dans la fiche du héros.
import { useState } from 'preact/hooks';
import { describeStats } from '../../describe';
import { heroDef } from '../../../core/data/heroes';
import {
  FORGE_COUNT, GEAR_SLOTS, ITEM_RARITIES, SET_BONUS, SET_PIECES, SLOT_MAX_LEVEL, SLOT_STAT, itemBonus, itemMain, itemSubs,
  recycleDust, slotUpgradeCost,
  type GearSlot, type Item,
} from '../../../core/data/items';
import { ITEM_COLORS } from '../../art';
import { t } from '../../i18n';
import { equipItem, forgeItem, forgePartners, recycleItems, unequipItem, upgradeSlot } from '../../state/actions';
import { heroByUid, slotLevel } from '../../state/selectors';
import { useGame } from '../../state/store';
import type { PlayerState } from '../../state/types';
import { Btn, Cur, Icon, ItemIcon, Modal, Sign } from '../kit';
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
  const [picking, setPicking] = useState(false);
  const [picked, setPicked] = useState<Set<number>>(new Set());
  const items = sortItems(s.items.filter((it) => slot === 'all' || it.slot === slot));
  const free = (it: Item) => it.heroUid === undefined;
  const dust = s.items.filter((it) => picked.has(it.uid)).reduce((sum, it) => sum + recycleDust(it), 0);
  const toggle = (it: Item) => {
    if (!free(it)) return;
    const next = new Set(picked);
    if (next.has(it.uid)) next.delete(it.uid);
    else next.add(it.uid);
    setPicked(next);
  };
  const selectRarity = (rarity: number) => setPicked(new Set([...picked, ...s.items.filter((it) => free(it) && it.rarity === rarity).map((it) => it.uid)]));
  const stop = () => {
    setPicking(false);
    setPicked(new Set());
  };

  return (
    <div class="screen bag">
      <div class="row between">
        <h2>{t('bag.title')} <span class="muted">{s.items.length}</span></h2>
        <Cur k="dust" n={s.wallet.dust} />
      </div>
      {picking ? (
        <div class="recycle-bar">
          <div class="row between center-y">
            <span>{t('recycle.count', { n: picked.size })}</span>
            <Cur k="dust" n={dust} big />
          </div>
          <div class="row gap-s">
            {[0, 1, 2].map((r) => (
              <button class="chip" onClick={() => selectRarity(r)}><span class="chip-dot" style={{ background: ITEM_COLORS[r] }} />{t(`item.${r}`)}</button>
            ))}
            <button class="chip" aria-label="✕" onClick={() => setPicked(new Set())}><Sign name="cross" /></button>
          </div>
          <div class="row gap-s">
            <Btn kind="ghost" small wide onClick={stop}>{t('cancel')}</Btn>
            <Btn kind="red" small wide disabled={!picked.size} onClick={() => {
              const got = recycleItems([...picked]);
              stop();
              toast(t('bag.recycled', { n: got }));
            }}>{t('recycle.confirm')}</Btn>
          </div>
        </div>
      ) : (
        <div class="row gap-s">
          <Btn kind="gold" small wide onClick={() => open({ type: 'forge' })}><Icon name="weapon" size={18} /> {t('forge.title')}</Btn>
          <Btn kind="ghost" small wide onClick={() => setPicking(true)}><Icon name="recycle" size={20} /> {t('item.recycle')}</Btn>
        </div>
      )}
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
              <span class={`pickable${picking && !free(it) ? ' locked-item' : ''}${picked.has(it.uid) ? ' picked' : ''}`}>
                <ItemIcon item={it} heroDefId={o?.defId} level={o ? slotLevel(s, o.uid, it.slot) : 0}
                  onClick={() => (picking ? toggle(it) : open({ type: 'item', uid: it.uid }))} />
              </span>
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
          <div class="item-big">{t(`stat.${SLOT_STAT[item.slot]}`)} +{itemMain(item, o ? slotLevel(s, o.uid, item.slot) : 0)} %</div>
          {describeStats(itemSubs(item)) && <div class="small">{describeStats(itemSubs(item))}</div>}
          <div class="muted small">{t('item.chapter', { n: item.tier + 1 })}</div>
          {o && <div class="small">{t('item.wornBy', { n: heroDef(o.defId).name })}</div>}
        </div>
      </div>
      {item.set && (
        <div class={`set-line set-${item.set}`}>
          <strong>{t(`set.${item.set}`)}</strong>
          <span class="muted small">{o ? `${s.items.filter((it) => it.heroUid === o.uid && it.set === item.set).length} / ${SET_PIECES}` : `${SET_PIECES} ×`}</span>
          <span class="small">{describeStats(SET_BONUS[item.set])}</span>
        </div>
      )}
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

/** Y a-t-il dans le sac un objet meilleur que celui porté sur cet emplacement ? */
export function betterInBag(s: PlayerState, heroUid: number, slot: GearSlot): boolean {
  const current = s.items.find((it) => it.heroUid === heroUid && it.slot === slot);
  const now = current ? itemBonus(current) : 0;
  return s.items.some((it) => it.slot === slot && it.heroUid === undefined && itemBonus(it) > now);
}

/**
 * Un emplacement d'un héros : renforcer l'emplacement, et choisir l'objet d'un geste
 * (objets du sac d'abord, puis ceux portés par d'autres héros, qu'on peut leur reprendre).
 */
export function SlotPanel({ heroUid, slot }: { heroUid: number; slot: GearSlot }) {
  const s = useGame();
  const level = slotLevel(s, heroUid, slot);
  const current = s.items.find((it) => it.heroUid === heroUid && it.slot === slot);
  const now = current ? itemBonus(current) : 0;
  const bag = sortItems(s.items.filter((it) => it.slot === slot && it.heroUid === undefined));
  const worn = sortItems(s.items.filter((it) => it.slot === slot && it.heroUid !== undefined && it.heroUid !== heroUid));
  const cost = level < SLOT_MAX_LEVEL ? slotUpgradeCost(level) : null;
  const ok = !!cost && s.wallet.gold >= cost.gold && s.wallet.dust >= cost.dust;
  const choice = (it: Item) => {
    const o = owner(s, it);
    return (
      <span class="pickable">
        <ItemIcon item={it} level={level} hideLevel heroDefId={o?.defId} onClick={() => equipItem(it.uid, heroUid)} />
        {itemBonus(it) > now && <span class="better"><Sign name="up" /></span>}
      </span>
    );
  };
  return (
    <div class="slot-panel">
      <div class="row between center-y">
        <div class="grow slot-info">
          <strong>{t('slot.level', { n: level })} / {SLOT_MAX_LEVEL}</strong>
          {current && (
            <span class="muted">
              {t(`stat.${SLOT_STAT[slot]}`)} +{itemMain(current, level)} %{cost && <> → <b class="gold-text">+{itemMain(current, level + 1)} %</b></>}
            </span>
          )}
        </div>
        {current && <Btn kind="ghost" small onClick={() => unequipItem(current.uid)}>{t('item.unequip')}</Btn>}
      </div>
      {cost ? (
        <Btn kind="gold" wide disabled={!ok} onClick={() => upgradeSlot(heroUid, slot)}>
          {t('slot.upgrade')} <Cur k="gold" n={cost.gold} /> <Cur k="dust" n={cost.dust} />
        </Btn>
      ) : <p class="center gold-text">{t('slot.max')}</p>}
      {bag.length + worn.length === 0 ? <p class="muted center">{t('bag.empty')}</p> : (
        <div class="item-grid">
          {bag.map(choice)}
          {worn.map(choice)}
        </div>
      )}
    </div>
  );
}
