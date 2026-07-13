import { useState, type CSSProperties } from "react";
import type { GenerationMode, Tier } from "../api/client";
import {
  FREE_SECURITY_TOOLS,
  SERVICE_CATEGORIES,
  tierPageHref,
  type ServiceCategoryId,
} from "../config/serviceCategories";
import { type UseCaseId } from "../config/useCases";
import UseCasePicker from "./UseCasePicker";
import Pricing from "./Pricing";
import Checkout from "./Checkout";
import CategoryTierGrid from "./CategoryTierGrid";

interface ServiceHubProps {
  tiers: Tier[];
  selectedTier: string | null;
  activeUseCase: UseCaseId | null;
  recommendedFor: { tierId: string; label: string } | null;
  email: string;
  generationMode: GenerationMode;
  agreed: boolean;
  payLoading: boolean;
  onUseCaseSelect: (useCaseId: UseCaseId, tierId: string) => void;
  onTierSelect: (tierId: string) => void;
  onEmailChange: (email: string) => void;
  onModeChange: (mode: GenerationMode) => void;
  onAgreedChange: (agreed: boolean) => void;
  onPay: () => void;
}

function tiersForCategory(tiers: Tier[], category: ServiceCategoryId): Tier[] {
  switch (category) {
    case "passwords":
      return tiers.filter(
        (t) => t.product_type === "password" || t.product_type === "backup_codes",
      );
    case "logins":
      return tiers.filter((t) => t.product_type === "creative");
    case "seller":
      return tiers.filter((t) => t.product_type === "seller");
    case "security":
      return tiers.filter((t) => t.product_type === "watch" || t.product_type === "image_qr");
    default:
      return [];
  }
}

export default function ServiceHub({
  tiers,
  selectedTier,
  activeUseCase,
  recommendedFor,
  email,
  generationMode,
  agreed,
  payLoading,
  onUseCaseSelect,
  onTierSelect,
  onEmailChange,
  onModeChange,
  onAgreedChange,
  onPay,
}: ServiceHubProps) {
  const [activeCategory, setActiveCategory] = useState<ServiceCategoryId>("passwords");
  const category = SERVICE_CATEGORIES.find((c) => c.id === activeCategory)!;
  const categoryTiers = tiersForCategory(tiers, activeCategory);
  const passwordTiers = tiersForCategory(tiers, "passwords");
  const selected = passwordTiers.find((t) => t.id === selectedTier) ?? null;

  return (
    <section className="service-hub" id="pricing">
      <div className="service-hub__head">
        <h2 className="section-title">Услуги</h2>
        <p className="service-hub__lead">Выберите категорию — ниже откроются тарифы и оформление.</p>
      </div>

      <div className="service-hub__categories" role="tablist" aria-label="Категории услуг">
        {SERVICE_CATEGORIES.map((item) => (
          <button
            key={item.id}
            type="button"
            role="tab"
            aria-selected={activeCategory === item.id}
            className={`service-hub__category${activeCategory === item.id ? " service-hub__category--active" : ""}`}
            style={
              activeCategory === item.id
                ? ({ "--cat-accent": item.accent } as CSSProperties)
                : undefined
            }
            onClick={() => setActiveCategory(item.id)}
          >
            <span className="service-hub__category-icon" aria-hidden>
              {item.icon}
            </span>
            <span className="service-hub__category-label">{item.label}</span>
            <span className="service-hub__category-desc">{item.description}</span>
          </button>
        ))}
      </div>

      <div
        className="service-hub__panel"
        role="tabpanel"
        style={{ "--cat-accent": category.accent } as CSSProperties}
      >
        <header className="service-hub__panel-head">
          <span className="service-hub__panel-icon" aria-hidden>
            {category.icon}
          </span>
          <div>
            <h3 className="service-hub__panel-title">{category.label}</h3>
            <p className="service-hub__panel-desc">{category.description}</p>
          </div>
        </header>

        {activeCategory === "passwords" && (
          <div className="service-hub__password-flow">
            <UseCasePicker activeUseCase={activeUseCase} onSelect={onUseCaseSelect} />
            <Pricing
              tiers={passwordTiers}
              selectedTier={selectedTier}
              recommendedFor={recommendedFor}
              onSelect={onTierSelect}
            />
            <Checkout
              tier={selected}
              email={email}
              onEmailChange={onEmailChange}
              mode={generationMode}
              onModeChange={onModeChange}
              agreed={agreed}
              onAgreedChange={onAgreedChange}
              loading={payLoading}
              onPay={onPay}
            />
          </div>
        )}

        {activeCategory === "logins" && (
          <>
            <p className="service-hub__panel-note">
              Наборы ников и псевдонимов с выбором стиля — оформление на отдельной странице.
            </p>
            <CategoryTierGrid
              tiers={categoryTiers}
              hrefForTier={(tierId) => tierPageHref("logins", tierId)}
            />
          </>
        )}

        {activeCategory === "seller" && (
          <>
            <p className="service-hub__panel-note">
              Загрузите фото товара — получите заголовки и описание под лимиты площадки.
            </p>
            <CategoryTierGrid
              tiers={categoryTiers}
              hrefForTier={(tierId) => tierPageHref("seller", tierId)}
            />
          </>
        )}

        {activeCategory === "security" && (
          <>
            <div className="service-hub__free-grid">
              {FREE_SECURITY_TOOLS.map((tool) => (
                <a key={tool.href} href={tool.href} className="service-hub__free-card">
                  <span className="service-hub__free-badge">{tool.badge}</span>
                  <strong>{tool.name}</strong>
                  <span>{tool.description}</span>
                </a>
              ))}
            </div>
            <p className="service-hub__panel-note">Платные инструменты безопасности:</p>
            <CategoryTierGrid
              tiers={categoryTiers}
              hrefForTier={(tierId) => tierPageHref("security", tierId)}
              ctaLabel="Подключить"
            />
          </>
        )}
      </div>
    </section>
  );
}
