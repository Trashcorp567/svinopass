import type { OrderResult } from "../api/client";

interface WatchResultProps {
  result: OrderResult;
}

function formatDate(value: string | null | undefined): string {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleDateString("ru-RU");
}

export default function WatchResult({ result }: WatchResultProps) {
  const breaches = result.breaches ?? [];

  return (
    <section className="generator watch-result" id="result">
      <h2 className="section-title">Сторож на посту</h2>
      <div className="generator__meta">
        <span>
          Email: <strong>{result.monitored_email}</strong>
        </span>
        <span>
          Активен до: <strong>{formatDate(result.expires_at)}</strong>
        </span>
        <span className={result.email_sent ? "generator__online" : "generator__offline"}>
          {result.email_sent ? "Подтверждение отправлено на email" : "Письмо не отправлено"}
        </span>
      </div>

      <div className="generator__result watch-result__panel">
        <p className="watch__preview-title">
          Сейчас в утечках: <strong>{result.breach_count ?? 0}</strong>
        </p>
        {breaches.length === 0 ? (
          <p className="checkout__note">В публичных утечках не встречался.</p>
        ) : (
          <ul className="watch__breach-list">
            {breaches.map((breach) => (
              <li key={breach.name}>
                <strong>{breach.title}</strong>
                <span>
                  {breach.domain} · {breach.breach_date}
                </span>
              </li>
            ))}
          </ul>
        )}
        <p className="checkout__note generator__warning">{result.warning}</p>
        <div className="generator__actions">
          <a href="/watch" className="btn btn--outline">
            Продлить мониторинг
          </a>
          <a href="/" className="btn btn--outline">
            На главную
          </a>
        </div>
      </div>
    </section>
  );
}
