// Outil de test : le choix des combattants du combat d'essai HD (5 héros et 5 monstres au plus), ou les 60 à la
// suite. Les visages viennent des planches HD (public/art/hd/<id>.webp, case `visage` de hd-meta.ts).
import { useState } from 'preact/hooks';
import { t } from '../../i18n';
import { HD_CHARS, HD_HEROES, HD_MONSTERS, HD_UP, hdTrialAll, hdTrialBattle } from '../../hd-roster';
import { Btn, Modal } from '../kit';
import { close, startBattle } from '../nav';

const MAX = 5;

function random(ids: string[]): string[] {
  const pool = ids.slice();
  const out: string[] = [];
  while (out.length < MAX && pool.length) out.push(pool.splice(Math.floor(Math.random() * pool.length), 1)[0]!);
  return out;
}

/** Le dernier choix, gardé le temps de la session (on revient ici après le combat). */
let last: { heroes: string[]; monsters: string[] } | null = null;

/** Le visage d'un personnage : un carré de sa planche HD, agrandi sans flou. */
function Face({ id, n, onClick }: { id: string; n: number; onClick: () => void }) {
  const c = HD_CHARS[id]!;
  const [vx, vy, side] = c.visage as [number, number, number];
  const sw = c.size[0]! / HD_UP, sh = c.size[1]! / HD_UP;
  return (
    <button class={`hd-face${n ? ' on' : ''}`} onClick={onClick}>
      <span class="hd-face-art" style={{
        backgroundImage: `url(art/hd/${id}.webp)`,
        backgroundSize: `${(sw / side) * 100}% ${(sh / side) * 100}%`,
        backgroundPosition: `${(vx / Math.max(1, sw - side)) * 100}% ${(vy / Math.max(1, sh - side)) * 100}%`,
      }} />
      {n > 0 && <span class="hd-face-n">{n}</span>}
    </button>
  );
}

function Grid({ ids, chosen, set }: { ids: string[]; chosen: string[]; set: (v: string[]) => void }) {
  const toggle = (id: string) => {
    if (chosen.includes(id)) set(chosen.filter((x) => x !== id));
    else if (chosen.length < MAX) set([...chosen, id]);
  };
  return <div class="hd-grid">{ids.map((id) => <Face id={id} n={chosen.indexOf(id) + 1} onClick={() => toggle(id)} />)}</div>;
}

export function HdPick() {
  const [heroes, setHeroes] = useState(() => last?.heroes ?? random(HD_HEROES));
  const [monsters, setMonsters] = useState(() => last?.monsters ?? random(HD_MONSTERS));
  last = { heroes, monsters };
  const go = (req: ReturnType<typeof hdTrialAll>) => {
    close();
    startBattle(req);
  };
  return (
    <Modal title={t('settings.hd')} center>
      <div class="hd-pick">
        <h3>{t('nav.heroes')} <span class="hd-count">{heroes.length}/{MAX}</span></h3>
        <Grid ids={HD_HEROES} chosen={heroes} set={setHeroes} />
        <h3>{t('hdpick.monsters')} <span class="hd-count">{monsters.length}/{MAX}</span></h3>
        <Grid ids={HD_MONSTERS} chosen={monsters} set={setMonsters} />
        <div class="hd-pick-btns">
          <Btn kind="ghost" small onClick={() => { setHeroes(random(HD_HEROES)); setMonsters(random(HD_MONSTERS)); }}>{t('hdpick.random')}</Btn>
          <Btn kind="purple" small onClick={() => go(hdTrialAll())}>{t('hdpick.all', { n: HD_HEROES.length + HD_MONSTERS.length })}</Btn>
          <Btn kind="gold" disabled={!heroes.length || !monsters.length} onClick={() => go(hdTrialBattle(heroes, monsters))}>{t('fight')}</Btn>
        </div>
      </div>
    </Modal>
  );
}
