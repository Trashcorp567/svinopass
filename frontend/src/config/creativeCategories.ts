export interface CreativeCategory {
  id: string;
  label: string;
  description: string;
  requires_seeds: boolean;
  optional_seeds: boolean;
}

export const CREATIVE_TIER_IDS = ["klichki", "imena", "socpak"] as const;
export type CreativeTierId = (typeof CREATIVE_TIER_IDS)[number];

export const CREATIVE_TIER_LABELS: Record<CreativeTierId, string> = {
  klichki: "15 ников",
  imena: "15 псевдонимов",
  socpak: "10 ников + 3 био",
};
