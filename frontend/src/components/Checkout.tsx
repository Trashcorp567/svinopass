import type { Tier } from "../api/client";

interface CheckoutProps {
  tier: Tier | null;
  email: string;
  onEmailChange: (email: string) => void;
  loading: boolean;
  onPay: () => void;
}

export default function Checkout({ tier, email, onEmailChange, loading, onPay }: CheckoutProps) {
  if (!tier) {
    return (
      <section className="checkout checkout--empty">
        <p>{"Пароль, просто класс! Покупай на svinopass"}</p>
      </section>
    );
  }

  const canPay = email.trim().length > 0 && !loading;

  return (
    <section className="checkout">
      <h2 className="section-title">{"\u041e\u043f\u043b\u0430\u0442\u0430"}</h2>
      <div className="checkout__box">
        <div className="checkout__info">
          <span className="checkout__tier">{tier.name}</span>
          <span className="checkout__amount">{tier.price_label}</span>
        </div>
        <p className="checkout__note">
          {"\u041e\u043f\u043b\u0430\u0442\u0430 \u0447\u0435\u0440\u0435\u0437 \u042eKassa. \u041f\u0430\u0440\u043e\u043b\u044c \u043f\u043e\u043a\u0430\u0436\u0435\u043c \u0441\u0440\u0430\u0437\u0443 \u0438 \u043e\u0442\u043f\u0440\u0430\u0432\u0438\u043c \u043d\u0430 email."}
          {" \u041c\u044b "}<strong>{"\u043d\u0435 \u0445\u0440\u0430\u043d\u0438\u043c"}</strong>{" \u043f\u0430\u0440\u043e\u043b\u0438 \u2014 \u0442\u043e\u043b\u044c\u043a\u043e \u0444\u0430\u043a\u0442 \u0437\u0430\u043a\u0430\u0437\u0430."}
        </p>
        <label className="checkout__label">
          {"Email \u0434\u043b\u044f \u0434\u043e\u0441\u0442\u0430\u0432\u043a\u0438 \u043f\u0430\u0440\u043e\u043b\u044f"}
          <input
            className="checkout__input"
            type="email"
            placeholder="you@example.com"
            value={email}
            onChange={(e) => onEmailChange(e.target.value)}
            required
          />
        </label>
        <button
          className="btn btn--primary btn--large"
          onClick={onPay}
          disabled={!canPay}
        >
          {loading ? "\u041f\u0435\u0440\u0435\u0445\u043e\u0434 \u043a \u043e\u043f\u043b\u0430\u0442\u0435..." : `\u041e\u043f\u043b\u0430\u0442\u0438\u0442\u044c ${tier.price_label}`}
        </button>
      </div>
    </section>
  );
}