export type UseCaseId = "bank" | "social" | "wifi" | "corp";

export type UseCasePreset = {
  id: UseCaseId;
  title: string;
  hint: string;
  recommendedTier: string;
};

export const USE_CASE_PRESETS: UseCasePreset[] = [
  {
    id: "bank",
    title: "Для банка",
    hint: "24+ символов, спецсимволы, без неоднозначных",
    recommendedTier: "bacon",
  },
  {
    id: "social",
    title: "Для соцсетей",
    hint: "20 символов, буквы и цифры",
    recommendedTier: "svinomat",
  },
  {
    id: "wifi",
    title: "Для Wi‑Fi гостей",
    hint: "16–20 символов, удобно продиктовать",
    recommendedTier: "svinomat",
  },
  {
    id: "corp",
    title: "Для корпоративки",
    hint: "32 символа, максимальная энтропия",
    recommendedTier: "legend",
  },
];

export const USE_CASE_LABELS: Record<UseCaseId, string> = {
  bank: "банка",
  social: "соцсетей",
  wifi: "Wi‑Fi",
  corp: "корпоративки",
};
