import { useState } from "react";
import type { OrderResult, SellerCard } from "../api/client";

interface SellResultProps {
  result: OrderResult;
}

function cardToText(card: SellerCard): string {
  const titles = card.titles.map((title, i) => `${i + 1}. ${title}`).join("\n");
  const bullets = (card.bullets ?? []).map((line) => `• ${line}`).join("\n");
  return [
    `=== ${card.platform_label} ===`,
    "Заголовки:",
    titles,
    "",
    "Описание:",
    card.description,
    bullets ? `\nБуллеты:\n${bullets}` : "",
  ]
    .filter(Boolean)
    .join("\n");
}

export default function SellResult({ result }: SellResultProps) {
  const [copied, setCopied] = useState(false);
  const cards = result.seller_cards ?? [];

  const copyText = [
    result.seller_vision_summary ? `Что на фото: ${result.seller_vision_summary}` : "",
    ...cards.map(cardToText),
  ]
    .filter(Boolean)
    .join("\n\n");

  const handleCopy = async () => {
    if (!copyText) return;
    await navigator.clipboard.writeText(copyText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <section className="generator sell-result" id="result">
      <h2 className="section-title">Тексты для маркетплейса</h2>
      <div className="generator__meta">
        <span>
          Тариф: <strong>{result.tier_name}</strong>
        </span>
        {result.seller_source && (
          <span>
            Источник: <strong>{result.seller_source === "yandexgpt" ? "Yandex GPT" : "шаблон"}</strong>
          </span>
        )}
        <span className={result.email_sent ? "generator__online" : "generator__offline"}>
          {result.email_sent
            ? "Отправлено на email"
            : "Письмо не отправлено — сохраните с экрана"}
        </span>
      </div>

      {result.seller_source === "template" && (
        <p className="checkout__note generator__warning sell-result__fallback">
          AI не смог разобрать фото — ниже черновик по подсказкам. Допишите характеристики
          вручную или попробуйте снова с названием и описанием товара.
        </p>
      )}

      {result.seller_vision_summary && (
        <p className="sell-result__vision">{result.seller_vision_summary}</p>
      )}

      <div className="generator__result sell-result__cards">
        {cards.map((card) => (
          <article key={card.platform} className="sell-result__card">
            <h3>{card.platform_label}</h3>
            <div className="sell-result__titles">
              <h4>Заголовки</h4>
              <ol>
                {card.titles.map((title) => (
                  <li key={title}>
                    <code>{title}</code>
                  </li>
                ))}
              </ol>
            </div>
            <div className="sell-result__description">
              <h4>Описание</h4>
              <p>{card.description}</p>
            </div>
            {(card.bullets ?? []).length > 0 && (
              <ul className="sell-result__bullets">
                {card.bullets!.map((line) => (
                  <li key={line}>{line}</li>
                ))}
              </ul>
            )}
          </article>
        ))}

        <p className="checkout__note generator__warning">{result.warning}</p>
        <div className="generator__actions">
          <button className="btn btn--outline" type="button" onClick={() => void handleCopy()}>
            {copied ? "Скопировано!" : "Скопировать всё"}
          </button>
          <a href="/sell" className="btn btn--outline">
            Сгенерировать ещё
          </a>
        </div>
      </div>
    </section>
  );
}
