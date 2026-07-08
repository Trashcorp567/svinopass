import type { Tier } from "../api/client";

interface PricingProps {
  tiers: Tier[];
  selectedTier: string | null;
  recommendedFor: { tierId: string; label: string } | null;
  onSelect: (tierId: string) => void;
}

export default function Pricing({ tiers, selectedTier, recommendedFor, onSelect }: PricingProps) {
  return (
    <section className="pricing" id="pricing">
      <h2 className="section-title">Услуги и цены</h2>
      <p className="pricing__intro">
        Разовая оплата за генерацию одного пароля. Цены фиксированы, в рублях РФ.
      </p>
      <div className="pricing__grid">
        {tiers.map((tier) => (
          <article
            key={tier.id}
            className={`pricing__card ${selectedTier === tier.id ? "pricing__card--selected" : ""}`}
            onClick={() => onSelect(tier.id)}
          >
            {recommendedFor?.tierId === tier.id && (
              <span className="pricing__badge">Рекомендуем для {recommendedFor.label}</span>
            )}
            <h3>{tier.name}</h3>
            <div className="pricing__price">{tier.price_label}</div>
            <p className="pricing__desc">{tier.description}</p>
            <ul>
              {tier.features.map((f) => (
                <li key={f}>{f}</li>
              ))}
            </ul>
            <button
              className={`btn ${selectedTier === tier.id ? "btn--primary" : "btn--outline"}`}
              onClick={(e) => {
                e.stopPropagation();
                onSelect(tier.id);
              }}
            >
              {selectedTier === tier.id ? "Выбрано ✓" : "Выбрать"}
            </button>
          </article>
        ))}
      </div>
    </section>
  );
}
