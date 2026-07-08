import { useState } from "react";
import { createCheckout, previewWatchEmail, type BreachSummary } from "../api/client";
import WatchActionPlan from "../components/WatchActionPlan";

export default function WatchPage() {
  const [email, setEmail] = useState("");
  const [agreed, setAgreed] = useState(false);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [payLoading, setPayLoading] = useState(false);
  const [previewError, setPreviewError] = useState<string | null>(null);
  const [payError, setPayError] = useState<string | null>(null);
  const [preview, setPreview] = useState<{ breach_count: number; breaches: BreachSummary[] } | null>(
    null,
  );

  const handlePreview = async () => {
    if (!email.trim()) return;
    setPreviewLoading(true);
    setPreviewError(null);
    try {
      const data = await previewWatchEmail(email.trim());
      setPreview(data);
    } catch (e) {
      setPreview(null);
      setPreviewError(e instanceof Error ? e.message : "Ошибка проверки");
    } finally {
      setPreviewLoading(false);
    }
  };

  const handlePay = async () => {
    if (!email.trim() || !agreed) return;
    setPayLoading(true);
    setPayError(null);
    try {
      const checkout = await createCheckout("storozh", email.trim());
      window.location.href = checkout.confirmation_url;
    } catch (e) {
      setPayError(e instanceof Error ? e.message : "Ошибка оплаты");
      setPayLoading(false);
    }
  };

  return (
    <section className="watch">
      <h1 className="section-title">Проверка утечек email</h1>
      <p className="watch__brand">Свиной сторож · Svinopass</p>
      <p className="watch__lead">
        Бесплатный снимок: проверяем ваш email в публичных базах утечек. Подписка — еженедельный
        мониторинг и письмо, если появилось что-то новое. <strong>199₽ / 30 дней.</strong>
      </p>

      <div className="watch__box">
        <label className="checkout__label" htmlFor="watch-email">
          Email для мониторинга
        </label>
        <input
          id="watch-email"
          className="checkout__input"
          type="email"
          value={email}
          onChange={(e) => {
            setEmail(e.target.value);
            setPreview(null);
          }}
          placeholder="you@example.com"
          autoComplete="email"
        />

        <div className="watch__actions">
          <button
            className="btn btn--outline"
            type="button"
            disabled={!email.trim() || previewLoading}
            onClick={() => void handlePreview()}
          >
            {previewLoading ? "Проверяем…" : "Бесплатный снимок сейчас"}
          </button>
        </div>

        {previewError && <p className="error-banner">{previewError}</p>}

        {preview && (
          <div className="watch__preview">
            <p className="watch__preview-title">
              Сейчас в утечках: <strong>{preview.breach_count}</strong>
            </p>
            {preview.breach_count === 0 ? (
              <p className="checkout__note">В публичных утечках не встречался.</p>
            ) : (
              <ul className="watch__breach-list">
                {preview.breaches.map((breach) => (
                  <li key={breach.name}>
                    <strong>{breach.title}</strong>
                    <span>
                      {breach.domain} · {breach.breach_date}
                    </span>
                  </li>
                ))}
              </ul>
            )}
            <p className="checkout__note">
              Снимок — только сейчас. Подписка пришлёт письмо, когда появятся <em>новые</em> утечки.
            </p>
            <WatchActionPlan breachCount={preview.breach_count} />
          </div>
        )}

        <label className="checkout__agree">
          <input type="checkbox" checked={agreed} onChange={(e) => setAgreed(e.target.checked)} />
          <span>
            Согласен с{" "}
            <a href="/offer" target="_blank" rel="noreferrer">
              офертой
            </a>{" "}
            и{" "}
            <a href="/privacy" target="_blank" rel="noreferrer">
              политикой
            </a>
          </span>
        </label>

        <button
          className="btn btn--primary watch__pay"
          type="button"
          disabled={!email.trim() || !agreed || payLoading}
          onClick={() => void handlePay()}
        >
          {payLoading ? "Переход к оплате…" : "Подключить за 199₽/мес"}
        </button>
        {payError && <p className="error-banner">{payError}</p>}
      </div>

      <ul className="watch__features">
        <li>Проверка через LeakCheck (публичные базы утечек)</li>
        <li>Уведомления раз в неделю при новых утечках</li>
        <li>Продление — повторная оплата на этой странице</li>
      </ul>
      <p className="watch__credit">
        <a href="https://leakcheck.io/" target="_blank" rel="noreferrer">
          Powered by LeakCheck
        </a>
      </p>
    </section>
  );
}
