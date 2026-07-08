import { useState } from "react";
import QRCode from "react-qr-code";
import type { OrderResult } from "../api/client";

interface QrResultProps {
  result: OrderResult;
}

function formatExpires(value: string | null | undefined): string | null {
  if (!value) return null;
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return null;
  return date.toLocaleDateString("ru-RU");
}

export default function QrResult({ result }: QrResultProps) {
  const [copied, setCopied] = useState(false);
  const url = result.image_qr_url ?? "";
  const expires = formatExpires(result.image_qr_expires_at ?? undefined);

  const handleCopy = async () => {
    if (!url) return;
    await navigator.clipboard.writeText(url);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <section className="generator qr-result" id="result">
      <h2 className="section-title">Ваш QR готов</h2>
      <div className="generator__meta">
        <span>
          Тариф: <strong>{result.tier_name}</strong>
        </span>
        {expires && (
          <span>
            Доступно до: <strong>{expires}</strong>
          </span>
        )}
        <span className={result.email_sent ? "generator__online" : "generator__offline"}>
          {result.email_sent ? "Отправлено на email" : "Письмо не отправлено — сохраните с экрана"}
        </span>
      </div>

      <div className="generator__result">
        {url && (
          <div className="generator__qr" aria-label="QR-код на картинку">
            <p className="generator__qr-hint">
              Отсканируйте — откроется картинка в браузере (только изображение)
            </p>
            <div className="generator__qr-frame">
              <QRCode value={url} size={200} level="M" bgColor="#1a0f14" fgColor="#f8c8dc" />
            </div>
            <p className="qr-result__url">
              <a href={url} target="_blank" rel="noopener noreferrer">
                {url}
              </a>
            </p>
          </div>
        )}

        <p className="checkout__note generator__warning">{result.warning}</p>
        <div className="generator__actions">
          <button className="btn btn--outline" type="button" onClick={() => void handleCopy()}>
            {copied ? "Скопировано!" : "Скопировать ссылку"}
          </button>
          <a href="/qr" className="btn btn--outline">
            Создать ещё
          </a>
        </div>
      </div>
    </section>
  );
}
