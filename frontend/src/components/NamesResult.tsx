import { useState } from "react";
import type { OrderResult } from "../api/client";

interface NamesResultProps {
  result: OrderResult;
}

const KIND_TITLES: Record<string, string> = {
  nicknames: "Ваши ники",
  names: "Ваши псевдонимы",
  social: "Ваш соцпак",
};

const CATEGORY_LABELS: Record<string, string> = {
  neutral: "Нейтральный",
  funny: "Шуточный",
  gaming: "Игровой",
  svino: "Свино-бренд",
};

export default function NamesResult({ result }: NamesResultProps) {
  const [copied, setCopied] = useState(false);
  const items = result.creative_items ?? [];
  const bios = result.creative_bios ?? [];
  const title = KIND_TITLES[result.creative_kind ?? ""] ?? "Ваш набор";
  const categoryLabel =
    (result.creative_category && CATEGORY_LABELS[result.creative_category]) ||
    result.creative_category;

  const copyText = [
    ...items.map((item, i) => `${i + 1}. ${item}`),
    ...(bios.length ? ["", "Био:", ...bios.map((bio) => `• ${bio}`)] : []),
  ].join("\n");

  const handleCopy = async () => {
    if (!copyText) return;
    await navigator.clipboard.writeText(copyText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <section className="generator names-result" id="result">
      <h2 className="section-title">{title}</h2>
      <div className="generator__meta">
        <span>
          Тариф: <strong>{result.tier_name}</strong>
        </span>
        {categoryLabel && (
          <span>
            Стиль: <strong>{categoryLabel}</strong>
          </span>
        )}
        <span className={result.email_sent ? "generator__online" : "generator__offline"}>
          {result.email_sent
            ? "Отправлено на email"
            : "Письмо не отправлено — сохраните с экрана"}
        </span>
      </div>
      <div className="generator__result">
        <ol className="names-result__list">
          {items.map((item, index) => (
            <li key={item}>
              <span className="names-result__index">{index + 1}</span>
              <code>{item}</code>
            </li>
          ))}
        </ol>
        {bios.length > 0 && (
          <div className="names-result__bios">
            <h3>Био для профиля</h3>
            <ul>
              {bios.map((bio) => (
                <li key={bio}>{bio}</li>
              ))}
            </ul>
          </div>
        )}
        <p className="checkout__note generator__warning">{result.warning}</p>
        <div className="generator__actions">
          <button className="btn btn--outline" type="button" onClick={() => void handleCopy()}>
            {copied ? "Скопировано!" : "Скопировать всё"}
          </button>
          <a href="/names" className="btn btn--outline">
            Сгенерировать ещё
          </a>
        </div>
      </div>
    </section>
  );
}
