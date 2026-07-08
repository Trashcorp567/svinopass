import { useEffect, useState } from "react";
import { fetchOrderResult, type OrderResult } from "../api/client";
import SellResult from "../components/SellResult";

function getOrderId(): string | null {
  return new URLSearchParams(window.location.search).get("order_id");
}

export default function SellSuccessPage() {
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
      for (let attempt = 0; attempt < 45; attempt += 1) {
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
                ? "Тексты уже показаны — проверьте email"
                : message,
            );
            setWaiting(false);
          }
          return;
        }
      }
      if (!cancelled) {
        setError("Генерация занимает больше времени. Проверьте почту через несколько минут.");
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
        <h2 className="section-title">Генерируем тексты…</h2>
        <p className="checkout__note">
          Анализируем фото и пишем описание — обычно 15–40 секунд…
        </p>
      </section>
    );
  }

  if (error) {
    return (
      <div className="payment-success-error">
        <p className="error-banner">{error}</p>
        <a href="/sell" className="btn btn--outline">
          К карточкам маркетплейса
        </a>
      </div>
    );
  }

  if (result) {
    return <SellResult result={result} />;
  }

  return null;
}
