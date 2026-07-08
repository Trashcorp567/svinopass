import { useEffect, useState } from "react";
import { fetchOrderResult, type OrderResult } from "../api/client";
import QrResult from "../components/QrResult";

function getOrderId(): string | null {
  return new URLSearchParams(window.location.search).get("order_id");
}

export default function QrSuccessPage() {
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
                ? "QR уже показан — проверьте email"
                : message,
            );
            setWaiting(false);
          }
          return;
        }
      }
      if (!cancelled) {
        setError("Обработка занимает больше времени. Проверьте почту.");
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
        <h2 className="section-title">Готовим QR…</h2>
        <p className="checkout__note">Публикуем картинку — обычно несколько секунд…</p>
      </section>
    );
  }

  if (error) {
    return (
      <div className="payment-success-error">
        <p className="error-banner">{error}</p>
        <a href="/qr" className="btn btn--outline">
          К QR-картинке
        </a>
      </div>
    );
  }

  if (result) {
    return <QrResult result={result} />;
  }

  return null;
}
