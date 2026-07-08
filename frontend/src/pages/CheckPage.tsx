import { useState } from "react";
import {
  analyzePasswordFull,
  SCORE_LABELS,
  type HealthResult,
} from "../lib/passwordAnalysis";

export default function CheckPage() {
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<HealthResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleCheck = async () => {
    if (!password.trim()) {
      setError("Введите пароль для проверки");
      setResult(null);
      return;
    }
    setError(null);
    setLoading(true);
    try {
      const data = await analyzePasswordFull(password);
      setResult(data);
    } catch {
      setError("Не удалось выполнить проверку");
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="check">
      <h1 className="section-title">Проверка пароля и утечек онлайн</h1>
      <p className="check__brand">Хрюк-чек · Svinopass</p>
      <p className="check__lead">
        Бесплатная проверка пароля: оценка силы, энтропия и поиск в базах утечек —{" "}
        <strong>в браузере</strong>. Пароль не отправляется на сервер Svinopass; для утечек
        используется k-anonymity (HIBP): на внешний API уходит только часть SHA-1 хеша.
      </p>

      <div className="check__box">
        <label className="checkout__label" htmlFor="check-password">
          Пароль для проверки
        </label>
        <div className="check__input-row">
          <input
            id="check-password"
            className="checkout__input"
            type={showPassword ? "text" : "password"}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && void handleCheck()}
            autoComplete="off"
            spellCheck={false}
          />
          <button
            type="button"
            className="btn btn--outline btn--small"
            onClick={() => setShowPassword((v) => !v)}
          >
            {showPassword ? "Скрыть" : "Показать"}
          </button>
        </div>

        <button
          type="button"
          className="btn btn--primary btn--large check__submit"
          onClick={() => void handleCheck()}
          disabled={loading}
        >
          {loading ? "Проверяем…" : "Проверить хрюк-чеком"}
        </button>
      </div>

      {error && <p className="error-banner">{error}</p>}

      {result && (
        <div className={`check__result check__result--${result.score}`}>
          <p className="check__score">
            Оценка: <strong>{SCORE_LABELS[result.score]}</strong>
          </p>
          <ul className="check__metrics">
            <li>Энтропия: {result.entropyBits} бит</li>
            <li>Длина: {result.length} символов</li>
            <li>
              Классы:{" "}
              {[
                result.hasLower && "a-z",
                result.hasUpper && "A-Z",
                result.hasDigit && "0-9",
                result.hasSymbol && "спецсимволы",
              ]
                .filter(Boolean)
                .join(", ") || "нет"}
            </li>
          </ul>

          {result.warnings.length > 0 && (
            <div className="check__warnings">
              <p className="check__warnings-title">Замечания:</p>
              <ul>
                {result.warnings.map((w) => (
                  <li key={w}>{w}</li>
                ))}
              </ul>
            </div>
          )}

          <p className="check__breach">
            {result.breachCheckFailed && "Проверка утечек недоступна (сеть или HIBP)."}
            {!result.breachCheckFailed && result.breachCount === 0 && "В публичных утечках не встречался."}
            {!result.breachCheckFailed &&
              result.breachCount !== null &&
              result.breachCount > 0 &&
              `Найден в ${result.breachCount.toLocaleString("ru-RU")} утечках — смените пароль.`}
          </p>

          <a href="/#pricing" className="btn btn--primary">
            Сгенерировать нормальный →
          </a>
        </div>
      )}

      <nav className="check__related" aria-label="Связанные инструменты">
        <p>
          Нужен новый пароль? <a href="/#pricing">Заказать генерацию</a> или{" "}
          <a href="/watch">проверка утечек email</a>.
        </p>
      </nav>
    </section>
  );
}
