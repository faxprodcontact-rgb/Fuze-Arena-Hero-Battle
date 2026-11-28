// Puissance demandée pour chaque niveau de campagne.
// Points d'ancrage réglés par `npm run simuler -- --calibrer` (voir docs/simulations.md),
// entre deux points la puissance monte de façon régulière (interpolation logarithmique).

export interface Anchor {
  stage: number;
  power: number;
}

export const CAMPAIGN_ANCHORS: Anchor[] = [
  { stage: 1, power: 30 },
  { stage: 15, power: 600 },
  { stage: 150, power: 6000 },
  { stage: 260, power: 11000 },
  { stage: 380, power: 18000 },
  { stage: 500, power: 26000 },
  { stage: 680, power: 40000 },
  { stage: 860, power: 60000 },
  { stage: 980, power: 80000 },
  { stage: 1070, power: 95000 },
  { stage: 1140, power: 105000 },
  { stage: 1200, power: 115000 },
];

export function curveFromAnchors(anchors: readonly Anchor[]): (stage: number) => number {
  return (stage: number) => {
    const first = anchors[0]!;
    if (stage <= first.stage) return first.power;
    for (let i = 1; i < anchors.length; i++) {
      const a = anchors[i - 1]!;
      const b = anchors[i]!;
      if (stage <= b.stage || i === anchors.length - 1) {
        const k = (stage - a.stage) / (b.stage - a.stage);
        return a.power * (b.power / a.power) ** k;
      }
    }
    return first.power;
  };
}

export const stagePower = curveFromAnchors(CAMPAIGN_ANCHORS);
