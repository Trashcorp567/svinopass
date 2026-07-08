import { useState } from "react";
import QRCode from "react-qr-code";
import type { OrderResult } from "../api/client";

interface PasswordResultProps {
  result: OrderResult;
}

export default function PasswordResult({ result }: PasswordResultProps) {
  const [copied, setCopied] = useState(false);
  const isBackup = result.product_type === "backup_codes" && result.backup_codes?.length;

  const copyText = isBackup
    ? result.backup_codes!.map((code, i) => `${i + 1}. ${code}`).join("\n")
    : (result.password ?? "");

  const handleCopy = async () => {
    if (!copyText) return;
    await navigator.clipboard.writeText(copyText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <section className="generator" id="result">
      <h2 className="section-title">
        {isBackup ? "Ваши коды восстановления" : "Ваш пароль готов"}
      </h2>
      <div className="generator__meta">
        <span>
          Тариф: <strong>{result.tier_name}</strong>
        </span>
        <span>
          Заказ: <strong>{result.order_id.slice(0, 8)}…</strong>
        </span>
        <span className={result.email_sent ? "generator__online" : "generator__offline"}>
          {result.email_sent
            ? "Отправлено на email"
            : "Письмо не отправлено — сохраните с экрана"}
        </span>
      </div>
      <div className="generator__result">
        {isBackup ? (
          <ol className="backup-codes__list">
            {result.backup_codes!.map((code) => (
              <li key={code}>
                <code>{code}</code>
              </li>
            ))}
          </ol>
        ) : (
          <>
            <div className="generator__password">{result.password}</div>
            {result.password && (
              <div className="generator__qr" aria-label="QR-код пароля">
                <p className="generator__qr-hint">
                  Отсканируйте камерой — удобно сохранить в менеджер паролей или заметки
                </p>
                <div className="generator__qr-frame">
                  <QRCode
                    value={result.password}
                    size={168}
                    level="M"
                    bgColor="#1a0f14"
                    fgColor="#f8c8dc"
                  />
                </div>
              </div>
            )}
            {result.entropy_bits != null && (
              <div className="generator__stats">
                Энтропия: <strong>{result.entropy_bits}</strong> бит
              </div>
            )}
          </>
        )}
        <p className="checkout__note generator__warning">{result.warning}</p>
        <div className="generator__actions">
          <button className="btn btn--outline" onClick={() => void handleCopy()}>
            {copied ? "Скопировано!" : isBackup ? "Скопировать все коды" : "Скопировать"}
          </button>
          {result.tier === "legend" && (
            <a
              className="btn btn--outline"
              href={`/api/orders/${result.order_id}/report`}
              download
            >
              Скачать свинорепорт (PDF)
            </a>
          )}
        </div>
      </div>
    </section>
  );
}
