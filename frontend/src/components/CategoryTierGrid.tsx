import type { Tier } from "../api/client";

interface CategoryTierGridProps {
  tiers: Tier[];
  hrefForTier: (tierId: string) => string;
  ctaLabel?: string;
}

export default function CategoryTierGrid({
  tiers,
  hrefForTier,
  ctaLabel = "Оформить",
}: CategoryTierGridProps) {
  if (tiers.length === 0) {
    return <p className="service-hub__empty">Тарифы временно недоступны.</p>;
  }

  return (
    <div className="pricing__grid service-hub__tier-grid">
      {tiers.map((tier) => (
        <article key={tier.id} className="pricing__card service-hub__tier-card">
          <h3>{tier.name}</h3>
          <div className="pricing__price">{tier.price_label}</div>
          <p className="pricing__desc">{tier.description}</p>
          <ul>
            {tier.features.map((feature) => (
              <li key={feature}>{feature}</li>
            ))}
          </ul>
          <a href={hrefForTier(tier.id)} className="btn btn--primary">
            {ctaLabel}
          </a>
        </article>
      ))}
    </div>
  );
}
