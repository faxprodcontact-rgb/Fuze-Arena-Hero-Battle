// Renaissance : [héros niv. X] → [héros niv. 1] + ce qu'on récupère (tout est rendu), contre quelques gemmes.
// En dessous, les héros qui ont quelque chose à rendre, les plus forts d'abord.
import { useState } from 'preact/hooks';
import { RESET_COST } from '../../../core/data/modes';
import { heroDef } from '../../../core/data/heroes';
import type { Hero } from '../../../core/types';
import { ELEMENT_COLOR } from '../../art';
import { t } from '../../i18n';
import { canReset, heroRefund, resetHero } from '../../state/actions';
import { heroByUid, heroPower } from '../../state/selectors';
import { useGame } from '../../state/store';
import { Btn, Cur, HeroCard, Icon, Page, Sign } from '../kit';
import { open, toast } from '../nav';

export function ResetPage({ uid }: { uid?: number }) {
  const s = useGame();
  const list = s.heroes.filter((h) => canReset(s, h)).sort((a, b) => heroPower(s, b) - heroPower(s, a));
  const [picked, setPicked] = useState<number | undefined>(uid ?? list[0]?.uid);
  const hero: Hero | undefined = picked !== undefined ? heroByUid(s, picked) : undefined;
  const target = hero && canReset(s, hero) ? hero : list[0];
  const back = target ? heroRefund(s, target) : null;
  const ok = s.wallet.gems >= RESET_COST;

  return (
    <Page title={t('detail.reset')}>
      {target && back ? (
        <section class="fuse-stage fuse-altar reset-stage" style={{ '--el': ELEMENT_COLOR[heroDef(target.defId).element] } as never}>
          <div class="fuse-main">
            <div class="fuse-big"><HeroCard hero={target} /><span class="reset-lv">{t('lv')} {target.level}</span></div>
            <Sign name="op-arrow" class="fuse-op" />
            <div class="fuse-big"><HeroCard hero={{ ...target, level: 1 }} /><span class="reset-lv">{t('lv')} 1</span></div>
          </div>
          <div class="reset-back">
            <Cur k="gold" n={back.gold} big />
            <Cur k="essence" n={back.essence} big />
            {back.dust > 0 && <Cur k="dust" n={back.dust} big />}
            {back.items > 0 && <span class="cur cur-big"><Icon name="weapon" size={22} /> {back.items}</span>}
          </div>
          <Btn kind="red" wide disabled={!ok} onClick={() => open({
            type: 'confirm',
            text: `${t('detail.reset')} ?`,
            onYes: () => {
              if (resetHero(target.uid)) toast('✓');
            },
          })}>
            {t('detail.reset')} <Cur k="gems" n={RESET_COST} />
          </Btn>
        </section>
      ) : <p class="center muted">{t('reset.none')}</p>}

      {list.length > 0 && (
        <div class="roster fuse-roster">
          {list.map((h) => (
            <HeroCard hero={h} small power={heroPower(s, h)} selected={h.uid === target?.uid} onClick={() => setPicked(h.uid)} />
          ))}
        </div>
      )}
    </Page>
  );
}
