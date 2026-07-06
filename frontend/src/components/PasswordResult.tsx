import { useState } from "react";
import type { OrderResult } from "../api/client";

interface PasswordResultProps {
  result: OrderResult;
}

export default function PasswordResult({ result }: PasswordResultProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(result.password);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <section className="generator" id="result">
      <h2 className="section-title">{"\u0412\u0430\u0448 \u043f\u0430\u0440\u043e\u043b\u044c \u0433\u043e\u0442\u043e\u0432"}</h2>
      <div className="generator__meta">
        <span>{"\u0422\u0430\u0440\u0438\u0444:"} <strong>{result.tier_name}</strong></span>
        <span>{"\u0417\u0430\u043a\u0430\u0437:"} <strong>{result.order_id.slice(0, 8)}{"\u2026"}</strong></span>
        <span className={result.email_sent ? "generator__online" : "generator__offline"}>
          {result.email_sent ? "\u041e\u0442\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u043e \u043d\u0430 email" : "Email \u043d\u0435 \u043e\u0442\u043f\u0440\u0430\u0432\u043b\u0435\u043d"}
        </span>
      </div>
      <div className="generator__result">
        <div className="generator__password">{result.password}</div>
        <div className="generator__stats">{"\u042d\u043d\u0442\u0440\u043e\u043f\u0438\u044f:"} <strong>{result.entropy_bits}</strong> {"\u0431\u0438\u0442"}</div>
        <p className="checkout__note generator__warning">{result.warning}</p>
        <button className="btn btn--outline" onClick={handleCopy}>
          {copied ? "\u0421\u043a\u043e\u043f\u0438\u0440\u043e\u0432\u0430\u043d\u043e!" : "\u0421\u043a\u043e\u043f\u0438\u0440\u043e\u0432\u0430\u0442\u044c"}
        </button>
      </div>
    </section>
  );
}