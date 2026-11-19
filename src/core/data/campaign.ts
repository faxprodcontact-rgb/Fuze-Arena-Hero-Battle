// Puissance demandée pour chaque niveau de campagne.
// Points d'ancrage réglés par `npm run simuler -- --calibrer` (voir docs/simulations.md),
// entre deux points la puissance monte de façon régulière (interpolation logarithmique).

export interface Anchor {
  stage: number;
  power: number;
}

export const CAMPAIGN_ANCHORS: Anchor[] = [
  { stage: 1, power: 50 },
  { stage: 15, power: 870 },
  { stage: 120, power: 3287 },
  { stage: 360, power: 10282 },
  { stage: 600, power: 21068 },
  { stage: 800, power: 33657 },
  { stage: 950, power: 46020 },
  { stage: 1100, power: 77061 },
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
