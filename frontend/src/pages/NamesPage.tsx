import { useEffect, useMemo, useState } from "react";
import {
  createCreativeCheckout,
  fetchCreativeCategories,
  fetchTiers,
  type CreativeCategory,
  type Tier,
} from "../api/client";
import { CREATIVE_TIER_IDS, type CreativeTierId } from "../config/creativeCategories";

function parseSeedInput(value: string): string[] {
  const word = value.trim().split(/[,;\s]+/).filter(Boolean)[0];
  return word ? [word] : [];
}

export default function NamesPage() {
  const [tiers, setTiers] = useState<Tier[]>([]);
  const [categories, setCategories] = useState<CreativeCategory[]>([]);
  const [selectedTier, setSelectedTier] = useState<CreativeTierId>("klichki");
  const [selectedCategory, setSelectedCategory] = useState<string>("funny");
  const [seedInput, setSeedInput] = useState("");
  const [email, setEmail] = useState("");
  const [agreed, setAgreed] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([fetchTiers(), fetchCreativeCategories()])
      .then(([allTiers, allCategories]) => {
        setTiers(allTiers.filter((t) => t.product_type === "creative"));
        setCategories(allCategories);
        if (allCategories.length > 0) {
          setSelectedCategory(allCategories[0].id);
        }
        const params = new URLSearchParams(window.location.search);
        const tier = params.get("tier");
        if (tier && CREATIVE_TIER_IDS.includes(tier as CreativeTierId)) {
          setSelectedTier(tier as CreativeTierId);
        }
      })
      .catch(console.error);
  }, []);

  const activeCategory = categories.find((c) => c.id === selectedCategory) ?? null;
  const seedWords = useMemo(() => parseSeedInput(seedInput), [seedInput]);
  const selectedTierInfo = tiers.find((t) => t.id === selectedTier) ?? null;
  const showSeedField = Boolean(activeCategory?.optional_seeds);

  const seedsValid =
    !activeCategory ||
    !activeCategory.requires_seeds ||
    seedWords.length > 0;

  const canPay =
    Boolean(selectedTierInfo) &&
    Boolean(activeCategory) &&
    email.trim().length > 0 &&
    agreed &&
    seedsValid &&
    !loading;

  const handlePay = async () => {
    if (!canPay || !activeCategory) return;
    setLoading(true);
    setError(null);
    try {
      const checkout = await createCreativeCheckout(
        selectedTier,
        email.trim(),
        selectedCategory,
        seedWords,
      );
      window.location.href = checkout.confirmation_url;
    } catch (e) {
      setError(e instanceof Error ? e.message : "Ошибка оплаты");
      setLoading(false);
    }
  };

  return (
    <section className="names">
      <div className="names__hero">
        <h1 className="section-title">Ники и псевдонимы</h1>
        <p className="names__lead">
          Выберите тариф, стиль и опциональное слово-опору — получите готовый набор на экране и на
          email. Ники на английском.{" "}
          <strong>Занятость ников в соцсетях и играх не проверяется.</strong>
        </p>
      </div>

      <div className="names__grid">
        <div className="names__panel">
          <h2 className="names__subtitle">Тариф</h2>
          <div className="names__tier-grid">
            {CREATIVE_TIER_IDS.map((tierId) => {
              const tier = tiers.find((t) => t.id === tierId);
              if (!tier) return null;
              return (
                <button
                  key={tierId}
                  type="button"
                  className={`names__tier-card${selectedTier === tierId ? " names__tier-card--active" : ""}`}
                  onClick={() => setSelectedTier(tierId)}
                >
                  <span className="names__tier-name">{tier.name}</span>
                  <span className="names__tier-price">{tier.price_label}</span>
                  <span className="names__tier-desc">{tier.description}</span>
                </button>
              );
            })}
          </div>

          <h2 className="names__subtitle">Стиль</h2>
          <div className="names__category-grid">
            {categories.map((category) => (
              <button
                key={category.id}
                type="button"
                className={`names__category-card${selectedCategory === category.id ? " names__category-card--active" : ""}`}
                onClick={() => setSelectedCategory(category.id)}
              >
                <span className="names__category-label">{category.label}</span>
                <span className="names__category-desc">{category.description}</span>
              </button>
            ))}
          </div>
        </div>

        <div className="names__panel names__panel--checkout">
          {showSeedField && (
            <label className="checkout__label names__seed-label">
              Слово-опора (опционально, одно)
              <input
                className="checkout__input"
                type="text"
                value={seedInput}
                onChange={(e) => setSeedInput(e.target.value)}
                placeholder="bacon"
                maxLength={16}
              />
            </label>
          )}

          <label className="checkout__label">
            Email для доставки
            <input
              className="checkout__input"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              autoComplete="email"
            />
          </label>

          <label className="checkout__consent">
            <input
              type="checkbox"
              checked={agreed}
              onChange={(e) => setAgreed(e.target.checked)}
            />
            <span>
              Принимаю{" "}
              <a href="/offer" target="_blank" rel="noopener noreferrer">
                публичную оферту
              </a>{" "}
              и{" "}
              <a href="/privacy" target="_blank" rel="noopener noreferrer">
                политику конфиденциальности
              </a>
            </span>
          </label>

          {error && <p className="error-banner">{error}</p>}

          <button
            className="btn btn--primary btn--large"
            type="button"
            disabled={!canPay}
            onClick={() => void handlePay()}
          >
            {loading
              ? "Переход к оплате..."
              : `Оплатить ${selectedTierInfo?.price_label ?? ""}`}
          </button>
        </div>
      </div>
    </section>
  );
}
