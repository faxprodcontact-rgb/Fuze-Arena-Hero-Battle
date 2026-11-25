// Forge : [objet] + [objet] + [objet] = [rareté au-dessus]. Ce qui manque est grisé.
// En dessous, les objets du sac regroupés (même emplacement, même rareté), les forgeables en premier.
import { useState } from 'preact/hooks';
import { FORGE_COUNT, ITEM_RARITIES, SLOT_STAT, itemMain, type GearSlot, type Item } from '../../../core/data/items';
import { ITEM_COLORS } from '../../art';
import { t } from '../../i18n';
import { forgeAll, forgeItem } from '../../state/actions';
import { useGame } from '../../state/store';
import type { PlayerState } from '../../state/types';
import { Btn, Icon, ItemIcon, Page, Sign } from '../kit';
import { toast } from '../nav';

interface Group {
  key: string;
  slot: GearSlot;
  rarity: number;
  items: Item[];
}

function groups(s: PlayerState): Group[] {
  const map = new Map<string, Group>();
  for (const it of s.items) {
    if (it.heroUid !== undefined || it.rarity >= ITEM_RARITIES - 1) continue;
    const key = `${it.slot}-${it.rarity}`;
    const g = map.get(key) ?? { key, slot: it.slot, rarity: it.rarity, items: [] };
    g.items.push(it);
    map.set(key, g);
  }
  for (const g of map.values()) g.items.sort((a, b) => a.tier - b.tier);
  return [...map.values()].sort(
    (a, b) => Number(b.items.length >= FORGE_COUNT) - Number(a.items.length >= FORGE_COUNT) || b.items.length - a.items.length || b.rarity - a.rarity,
  );
}

export function ForgePage() {
  const s = useGame();
  const list = groups(s);
  const [key, setKey] = useState<string | undefined>(list[0]?.key);
  const g = list.find((x) => x.key === key) ?? list[0];
  const used = g ? g.items.slice(0, FORGE_COUNT) : [];
  const result = g && { slot: g.slot, rarity: g.rarity + 1, tier: Math.max(...used.map((it) => it.tier)) };

  return (
    <Page title={t('forge.title')}>
      {g && result ? (
        <section class="fuse-stage">
          <div class="forge-row">
            {Array.from({ length: FORGE_COUNT }, (_, i) => (
              <>
                {i > 0 && <Sign name="op-plus" class="fuse-plus" />}
                {used[i] ? <ItemIcon item={used[i]} /> : (
                  <span class="item item-empty missing" style={{ '--rar': ITEM_COLORS[g.rarity] } as never}><span class="item-ghost"><Icon name={g.slot} size={30} /></span></span>
                )}
              </>
            ))}
            <Sign name="op-eq" class="fuse-op" />
            <span class="forge-result"><ItemIcon item={{ uid: 0, ...result }} /></span>
          </div>
          <p class="center muted small">{t(`stat.${SLOT_STAT[g.slot]}`)} +{itemMain(used[0]!)} % → <b class="gold-text">+{itemMain(result)} %</b></p>
          <Btn kind="gold" wide disabled={g.items.length < FORGE_COUNT} onClick={() => {
            if (forgeItem(g.items[0]!.uid)) toast('✓');
          }}>{t('item.forge')}</Btn>
        </section>
      ) : <div class="empty"><Icon name="forge" size={96} /><p class="muted">{t('bag.empty')}</p></div>}

      {list.length > 0 && <div class="row between">
        <strong>{t('bag.title')}</strong>
        <Btn kind="ghost" small onClick={() => toast(t('bag.forged', { n: forgeAll().length }))}>{t('bag.forgeAll')}</Btn>
      </div>}
      <div class="item-grid">
        {list.map((x) => (
          <button class={`forge-pick${x.key === g?.key ? ' on' : ''}${x.items.length >= FORGE_COUNT ? ' ready' : ''}`} onClick={() => setKey(x.key)}>
            <ItemIcon item={x.items[0]} />
            <span class="forge-count">{Math.min(x.items.length, 99)} / {FORGE_COUNT}</span>
          </button>
        ))}
      </div>
    </Page>
  );
}
