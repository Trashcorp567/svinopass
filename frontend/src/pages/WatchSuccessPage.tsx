import { useEffect, useState } from "react";
import { fetchOrderResult, type OrderResult } from "../api/client";
import WatchResult from "../components/WatchResult";

function getOrderId(): string | null {
  return new URLSearchParams(window.location.search).get("order_id");
}

export default function WatchSuccessPage() {
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
      for (let attempt = 0; attempt < 15; attempt += 1) {
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
            setError(e instanceof Error ? e.message : "Ошибка загрузки");
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
        <h2 className="section-title">Подключаем сторожа…</h2>
        <p className="checkout__note">Проверяем утечки и активируем мониторинг.</p>
      </section>
    );
  }

  if (error) {
    return (
      <div className="payment-success-error">
        <p className="error-banner">{error}</p>
        <a href="/watch" className="btn btn--outline">
          К сторожу
        </a>
      </div>
    );
  }

  if (result) {
    return <WatchResult result={result} />;
  }

  return null;
}
