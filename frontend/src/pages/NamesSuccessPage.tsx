import { useEffect, useState } from "react";
import { fetchOrderResult, type OrderResult } from "../api/client";
import NamesResult from "../components/NamesResult";

function getOrderId(): string | null {
  return new URLSearchParams(window.location.search).get("order_id");
}

export default function NamesSuccessPage() {
  const [result, setResult] = useState<OrderResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [waiting, setWaiting] = useState(true);
  const orderId = getOrderId();

  useEffect(() => {
    if (!orderId) {
      setError("Идентификатор заказа не найден");
      setWaiting(false);
      return;
    }

    let cancelled = false;

    (async () => {
      for (let attempt = 0; attempt < 30; attempt += 1) {
        try {
          const data = await fetchOrderResult(orderId);
          if ("status" in data && data.status === "pending") {
            await new Promise((r) => setTimeout(r, 2000));
            continue;
          }
          if (!cancelled) {
            setResult(data as OrderResult);
            setWaiting(false);
          }
          return;
        } catch (e) {
          if (!cancelled) {
            const message = e instanceof Error ? e.message : "Ошибка загрузки";
            setError(
              message === "Result already shown. Check your email."
                ? "Набор уже показан — проверьте email"
                : message,
            );
            setWaiting(false);
          }
          return;
        }
      }
      if (!cancelled) {
        setError("Оплата ещё обрабатывается. Проверьте почту через несколько минут.");
        setWaiting(false);
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [orderId]);

  if (waiting) {
    return (
      <section className="generator">
        <h2 className="section-title">Генерируем набор…</h2>
        <p className="checkout__note">Подбираем набор — обычно 5–15 секунд…</p>
      </section>
    );
  }

  if (error) {
    return (
      <div className="payment-success-error">
        <p className="error-banner">{error}</p>
        <a href="/names" className="btn btn--outline">
          К никам и именам
        </a>
      </div>
    );
  }

  if (result) {
    return <NamesResult result={result} />;
  }

  return null;
}
