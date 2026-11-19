// Mode Défense : on pose jusqu'à 5 héros autour du chemin, puis les vagues de monstres passent seules.
// Chaque monstre qui atteint le camp coûte une vie ; les étoiles dépendent des vies restantes.
import { useEffect, useRef, useState } from 'preact/hooks';
import {
  DEFENSE_H, DEFENSE_HEROES, DEFENSE_LEVELS, DEFENSE_PADS, DEFENSE_PATH, DEFENSE_RANGE, DEFENSE_REWARD, DEFENSE_STAGE_PER_LEVEL, DEFENSE_W,
} from '../../../core/data/defense';
import { incomePerHour } from '../../../core/data/economy';
import { heroDef } from '../../../core/data/heroes';
import { heroImage } from '../../art';
import { runDefense } from '../../defense-scene';
import { fmt, t } from '../../i18n';
import {
  autoDefense, defensePlacement, defensePower, defenseRequest, finishDefense, placeDefender, removeDefender, swapPads,
  type DefenseRequest,
} from '../../state/actions';
import { heroByUid, heroPower } from '../../state/selectors';
import { useGame } from '../../state/store';
import { Btn, Cur, HeroCard, Icon, Page } from '../kit';
import { close, open, toast } from '../nav';

function StarRow({ n }: { n: number }) {
  return <span class="def-stars">{'★'.repeat(n)}<span class="off">{'★'.repeat(3 - n)}</span></span>;
}

/** L'écran du mode, dans Aventure : le prochain niveau, et les niveaux déjà gagnés à refaire pour les étoiles. */
export function DefenseScreen() {
  const s = useGame();
  const next = Math.min(DEFENSE_LEVELS, s.defense.level + 1);
  const done = s.defense.level >= DEFENSE_LEVELS;
  const replays = Object.entries(s.defense.stars)
    .map(([l, n]) => [Number(l), n] as const)
    .filter(([, n]) => n < 3)
    .sort((a, b) => b[0] - a[0])
    .slice(0, 4);
  return (
    <section class="list">
      <div class="card center defense-card">
        <h1>{t('adv.defense')}</h1>
        <MiniMap />
        {!done && (
          <>
            <strong class="def-level">{t('dungeon.level', { n: next })}</strong>
            <div class="def-rewards">
              <span class="power-chip"><Icon name="power" size={16} />{fmt(defensePower(next))}</span>
              <Cur k="gold" n={Math.round(incomePerHour(next * DEFENSE_STAGE_PER_LEVEL) * DEFENSE_REWARD.goldHours)} />
              <Cur k="gems" n={DEFENSE_REWARD.gemsPerStar * 3} />
            </div>
            <Btn kind="green" wide onClick={() => open({ type: 'defensePrep', level: next })}>{t('defense.prepare')}</Btn>
          </>
        )}
      </div>
      {replays.map(([level, n]) => (
        <div class="card row between center-y">
          <span><strong>{t('dungeon.level', { n: level })}</strong> <StarRow n={n} /></span>
          <Btn kind="ghost" small onClick={() => open({ type: 'defensePrep', level })}>{t('defense.replay')}</Btn>
        </div>
      ))}
    </section>
  );
}

/** La carte en petit : le chemin et les emplacements, avec les héros posés. */
function MiniMap({ selected, onPad }: { selected?: number; onPad?: (pad: number) => void }) {
  const s = useGame();
  const placement = defensePlacement(s);
  const d = DEFENSE_PATH.map(([x, y], i) => `${i ? 'L' : 'M'}${x} ${y}`).join(' ');
  return (
    <div class={`def-map${onPad ? ' big' : ''}`}>
      <svg viewBox={`0 0 ${DEFENSE_W} ${DEFENSE_H}`} preserveAspectRatio="xMidYMid meet" onClick={(e) => {
        // Le toucher est converti en position sur la carte : on prend l'emplacement le plus proche.
        if (!onPad) return;
        const svg = e.currentTarget as SVGSVGElement;
        const m = svg.getScreenCTM();
        if (!m) return;
        const p = new DOMPoint(e.clientX, e.clientY).matrixTransform(m.inverse());
        let best = -1;
        let dist = 90;
        DEFENSE_PADS.forEach(([x, y], i) => {
          const d = Math.hypot(p.x - x, p.y - y);
          if (d < dist) { dist = d; best = i; }
        });
        if (best >= 0) onPad(best);
      }}>
        <rect width={DEFENSE_W} height={DEFENSE_H} fill="#2f5a3d" />
        <path d={d} fill="none" stroke="#6b4a2a" stroke-width="86" stroke-linejoin="round" stroke-linecap="round" />
        <path d={d} fill="none" stroke="#c08a4a" stroke-width="70" stroke-linejoin="round" stroke-linecap="round" />
        {DEFENSE_PADS.map(([x, y], pad) => {
          const uid = placement.find(([, p]) => p === pad)?.[0];
          const hero = uid !== undefined ? heroByUid(s, uid) : undefined;
          const range = hero ? (heroDef(hero.defId).ranged ? DEFENSE_RANGE.ranged : DEFENSE_RANGE.melee) : 0;
          return (
            <g class="def-pad">
              {selected === pad && hero && <circle pointer-events="none" cx={x} cy={y} r={range} fill="#ffe27a22" stroke="#ffe27a" stroke-width="4" stroke-dasharray="14 10" />}
              <ellipse cx={x} cy={y + 34} rx="48" ry="16" fill={selected === pad ? '#ffe27a' : '#a9aec4'} stroke="#8a8fa8" stroke-width="6" />
              {hero ? <image href={heroImage(hero.defId)} x={x - 55} y={y - 62} width="110" height="110" />
                : onPad && <text x={x} y={y + 20} text-anchor="middle" font-size="48" fill="#ffffffaa">+</text>}
            </g>
          );
        })}
        <polygon points={`${360 - 60},${DEFENSE_H - 40} 360,${DEFENSE_H - 110} ${360 + 60},${DEFENSE_H - 40}`} fill="#7d6aa8" />
      </svg>
    </div>
  );
}

/** Préparation : poser les héros sur la carte. Toucher un emplacement le choisit ; toucher un héros le pose dessus. */
export function DefensePrep({ level }: { level: number }) {
  const s = useGame();
  const [pad, setPad] = useState<number | undefined>(undefined);
  const placement = defensePlacement(s);
  const placed = new Map(placement.map(([u, p]) => [u, p]));
  const power = placement.reduce((sum, [u]) => sum + heroPower(s, heroByUid(s, u)!), 0);
  const need = defensePower(level);
  const roster = [...s.heroes].sort((a, b) => heroPower(s, b) - heroPower(s, a));

  const tapPad = (p: number) => {
    if (pad === undefined) return setPad(p);
    if (pad !== p) swapPads(pad, p);
    setPad(undefined);
  };
  const tapHero = (uid: number) => {
    if (placed.has(uid) && (pad === undefined || placed.get(uid) === pad)) {
      removeDefender(uid);
      return;
    }
    const free = DEFENSE_PADS.map((_, i) => i).find((i) => !placement.some(([, p]) => p === i));
    const target = pad ?? free;
    if (target === undefined) return toast(t('heroes.full'));
    if (placeDefender(uid, target) === 'full') toast(t('heroes.full'));
    setPad(undefined);
  };

  return (
    <Page title={`${t('adv.defense')} · ${t('dungeon.level', { n: level })}`}>
      <div class="row between center-y">
        <span class={`power-chip ${power >= need ? 'ok' : 'low'}`}><Icon name="power" size={16} />{fmt(power)} / {fmt(need)}</span>
        <span class="muted">{placement.length} / {DEFENSE_HEROES}</span>
      </div>
      <MiniMap selected={pad} onPad={tapPad} />
      <div class="row gap-s">
        <Btn kind="ghost" small wide onClick={autoDefense}>{t('auto')}</Btn>
        <Btn kind="red" small wide disabled={!placement.length} onClick={() => {
          const req = defenseRequest(level);
          if (!req) return;
          close();
          open({ type: 'defenseRun', req });
        }}>{t('fight')}</Btn>
      </div>
      <div class="roster">
        {roster.map((h) => (
          <HeroCard hero={h} small power={heroPower(s, h)} selected={placed.has(h.uid)} onClick={() => tapHero(h.uid)} />
        ))}
      </div>
    </Page>
  );
}

/** La partie elle-même, en plein écran. */
export function DefenseRun({ req }: { req: DefenseRequest }) {
  const host = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (!host.current) return;
    return runDefense(host.current, req.setup, (lives) => {
      const gain = finishDefense(req, lives);
      close();
      open({ type: 'gain', title: `${t('adv.defense')} ${req.level}`, gain, win: lives > 0 });
    });
  }, [req]);
  return <div class="battle" ref={host} />;
}
