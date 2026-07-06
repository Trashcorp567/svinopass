import { useEffect, useState } from "react";
import { fetchOrderResult, type OrderResult } from "../api/client";
import PasswordResult from "../components/PasswordResult";

const RESULT_CACHE_PREFIX = "svinopass_order_result:";
const resultCache = new Map<string, OrderResult>();
const inflightPolls = new Map<string, Promise<OrderResult>>();

interface PaymentSuccessProps {
  onWaitingChange?: (waiting: boolean) => void;
}

function getOrderId(): string | null {
  const params = new URLSearchParams(window.location.search);
  return params.get("order_id");
}

function getCachedResult(orderId: string): OrderResult | null {
  const memory = resultCache.get(orderId);
  if (memory) return memory;

  try {
    const raw = sessionStorage.getItem(`${RESULT_CACHE_PREFIX}${orderId}`);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as OrderResult;
    resultCache.set(orderId, parsed);
    return parsed;
  } catch {
    return null;
  }
}

function cacheResult(orderId: string, result: OrderResult): void {
  resultCache.set(orderId, result);
  try {
    sessionStorage.setItem(`${RESULT_CACHE_PREFIX}${orderId}`, JSON.stringify(result));
  } catch {
    // ignore storage quota errors
  }
}

function localizeError(message: string): string {
  const map: Record<string, string> = {
    "Order ID not found": "\u0418\u0434\u0435\u043d\u0442\u0438\u0444\u0438\u043a\u0430\u0442\u043e\u0440 \u0437\u0430\u043a\u0430\u0437\u0430 \u043d\u0435 \u043d\u0430\u0439\u0434\u0435\u043d",
    "Password already shown. Check your email.":
      "\u041f\u0430\u0440\u043e\u043b\u044c \u0443\u0436\u0435 \u043f\u043e\u043a\u0430\u0437\u0430\u043d \u2014 \u043f\u0440\u043e\u0432\u0435\u0440\u044c\u0442\u0435 email",
    "Payment is still processing. Check your email shortly.":
      "\u041e\u043f\u043b\u0430\u0442\u0430 \u0435\u0449\u0451 \u043e\u0431\u0440\u0430\u0431\u0430\u0442\u044b\u0432\u0430\u0435\u0442\u0441\u044f. \u041f\u0440\u043e\u0432\u0435\u0440\u044c\u0442\u0435 \u043f\u043e\u0447\u0442\u0443 \u0447\u0435\u0440\u0435\u0437 \u043d\u0435\u0441\u043a\u043e\u043b\u044c\u043a\u043e \u043c\u0438\u043d\u0443\u0442",
    "Error loading order": "\u041e\u0448\u0438\u0431\u043a\u0430 \u0437\u0430\u0433\u0440\u0443\u0437\u043a\u0438 \u0437\u0430\u043a\u0430\u0437\u0430",
  };
  return map[message] ?? message;
}

async function loadOrderResult(orderId: string): Promise<OrderResult> {
  const cached = getCachedResult(orderId);
  if (cached) return cached;

  const inflight = inflightPolls.get(orderId);
  if (inflight) return inflight;

  const promise = (async () => {
    let attempts = 0;
    const maxAttempts = 15;

    while (attempts < maxAttempts) {
      attempts += 1;
      const data = await fetchOrderResult(orderId);
      if ("status" in data && data.status === "pending") {
        await new Promise((r) => setTimeout(r, 2000));
        continue;
      }
      const result = data as OrderResult;
      cacheResult(orderId, result);
      return result;
    }

    throw new Error("Payment is still processing. Check your email shortly.");
  })();

  inflightPolls.set(orderId, promise);
  try {
    return await promise;
  } finally {
    inflightPolls.delete(orderId);
  }
}

export default function PaymentSuccess({ onWaitingChange }: PaymentSuccessProps) {
  const [result, setResult] = useState<OrderResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [waiting, setWaiting] = useState(true);
  const orderId = getOrderId();

  useEffect(() => {
    onWaitingChange?.(waiting);
  }, [waiting, onWaitingChange]);

  useEffect(() => {
    if (!orderId) {
      setError(localizeError("Order ID not found"));
      setWaiting(false);
      return;
    }

    let cancelled = false;

    loadOrderResult(orderId)
      .then((data) => {
        if (!cancelled) {
          setResult(data);
          setWaiting(false);
        }
      })
      .catch((e) => {
        if (!cancelled) {
          const message = e instanceof Error ? e.message : "Error loading order";
          setError(localizeError(message));
          setWaiting(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [orderId]);

  if (!orderId) {
    return (
      <div className="payment-success-error">
        <p className="error-banner">{"\u041d\u0435\u043a\u043e\u0440\u0440\u0435\u043a\u0442\u043d\u0430\u044f \u0441\u0441\u044b\u043b\u043a\u0430 \u043f\u043e\u0441\u043b\u0435 \u043e\u043f\u043b\u0430\u0442\u044b."}</p>
        <a href="/" className="btn btn--outline">{"\u041d\u0430 \u0433\u043b\u0430\u0432\u043d\u0443\u044e"}</a>
      </div>
    );
  }

  if (waiting) {
    return (
      <section className="generator">
        <h2 className="section-title">{"\u041e\u0431\u0440\u0430\u0431\u043e\u0442\u043a\u0430 \u043e\u043f\u043b\u0430\u0442\u044b\u2026"}</h2>
        <p className="checkout__note">{"\u041f\u043e\u0434\u043e\u0436\u0434\u0438\u0442\u0435, \u0433\u0435\u043d\u0435\u0440\u0438\u0440\u0443\u0435\u043c \u043f\u0430\u0440\u043e\u043b\u044c\u2026"}</p>
      </section>
    );
  }

  if (error) {
    return (
      <div className="payment-success-error">
        <p className="error-banner">{error}</p>
        <a href="/" className="btn btn--outline">{"\u041d\u0430 \u0433\u043b\u0430\u0432\u043d\u0443\u044e"}</a>
      </div>
    );
  }

  if (result) {
    return <PasswordResult result={result} />;
  }

  return null;
}