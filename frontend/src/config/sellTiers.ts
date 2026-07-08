export const SELL_TIER_IDS = ["ozon_card", "wb_card", "avito_card", "sell_pack"] as const;

export type SellTierId = (typeof SELL_TIER_IDS)[number];

export const SELL_TIER_PLATFORM: Record<SellTierId, string> = {
  ozon_card: "Ozon",
  wb_card: "Wildberries",
  avito_card: "Avito",
  sell_pack: "Ozon + WB + Avito",
};
