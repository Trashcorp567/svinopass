import type { Tier, GenerationMode } from "../api/client";

interface CheckoutProps {
  tier: Tier | null;
  email: string;
  onEmailChange: (email: string) => void;
  mode: GenerationMode;
  onModeChange: (mode: GenerationMode) => void;
  agreed: boolean;
  onAgreedChange: (agreed: boolean) => void;
  loading: boolean;
  onPay: () => void;
}

export default function Checkout({
  tier,
  email,
  onEmailChange,
  mode,
  onModeChange,
  agreed,
  onAgreedChange,
  loading,
  onPay,
}: CheckoutProps) {
  if (!tier) {
    return (
      <section className="checkout checkout--empty" id="checkout">
        <p>Выберите тариф выше, чтобы перейти к оплате.</p>
      </section>
    );
  }

  const canPay = email.trim().length > 0 && agreed && !loading;
  const isPasswordTier = tier.product_type !== "backup_codes";

  return (
    <section className="checkout" id="checkout">
      <h2 className="section-title">Оплата</h2>
      <div className="checkout__box">
        <div className="checkout__info">
          <span className="checkout__tier">{tier.name}</span>
          <span className="checkout__amount">{tier.price_label}</span>
        </div>
        <label className="checkout__label">
          Email для доставки пароля
          <input
            className="checkout__input"
            type="email"
            placeholder="you@example.com"
            value={email}
            onChange={(e) => onEmailChange(e.target.value)}
            required
          />
        </label>
        {isPasswordTier && (
          <label className="checkout__consent checkout__mode">
            <input
              type="checkbox"
              checked={mode === "passphrase"}
              onChange={(e) => onModeChange(e.target.checked ? "passphrase" : "random")}
            />
            <span>
              Слова вместо абракадабры (passphrase: 4 слова + цифра + символ, ≈50+ бит энтропии)
            </span>
          </label>
        )}
        <label className="checkout__consent">
          <input
            type="checkbox"
            checked={agreed}
            onChange={(e) => onAgreedChange(e.target.checked)}
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
            , согласен с условиями{" "}
            <a href="/delivery" target="_blank" rel="noopener noreferrer">
              получения цифрового заказа
            </a>
          </span>
        </label>
        <button className="btn btn--primary btn--large" onClick={onPay} disabled={!canPay}>
          {loading ? "Переход к оплате..." : `Оплатить ${tier.price_label}`}
        </button>
      </div>
    </section>
  );
}
