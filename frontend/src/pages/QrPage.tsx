import { useEffect, useState, type ChangeEvent } from "react";
import { createSellCheckout, fetchTiers, stageSellImage, type Tier } from "../api/client";

const ACCEPTED_TYPES = ["image/jpeg", "image/png", "image/webp"];
const TIER_ID = "qr_pic";

export default function QrPage() {
  const [tier, setTier] = useState<Tier | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [stagingId, setStagingId] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [email, setEmail] = useState("");
  const [agreed, setAgreed] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchTiers()
      .then((all) => setTier(all.find((t) => t.id === TIER_ID) ?? null))
      .catch(console.error);
  }, []);

  useEffect(() => {
    return () => {
      if (previewUrl) URL.revokeObjectURL(previewUrl);
    };
  }, [previewUrl]);

  const canPay =
    Boolean(tier) && Boolean(stagingId) && email.trim().length > 0 && agreed && !loading && !uploading;

  const handleFileChange = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    setError(null);

    if (!ACCEPTED_TYPES.includes(file.type)) {
      setError("Только JPEG, PNG и WebP — без видео и аудио");
      return;
    }
    if (file.size > 5 * 1024 * 1024) {
      setError("Картинка до 5 МБ");
      return;
    }

    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setPreviewUrl(URL.createObjectURL(file));
    setStagingId(null);
    setUploading(true);
    try {
      const staged = await stageSellImage(file);
      setStagingId(staged.staging_id);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Не удалось загрузить картинку");
      setPreviewUrl(null);
    } finally {
      setUploading(false);
    }
  };

  const handlePay = async () => {
    if (!canPay || !stagingId) return;
    setLoading(true);
    setError(null);
    try {
      const checkout = await createSellCheckout(
        TIER_ID,
        email.trim(),
        stagingId,
        "",
        "",
        "",
      );
      window.location.href = checkout.confirmation_url;
    } catch (e) {
      setError(e instanceof Error ? e.message : "Ошибка оплаты");
      setLoading(false);
    }
  };

  return (
    <section className="qr-page">
      <div className="qr-page__hero">
        <h1 className="section-title">QR-картинка</h1>
        <p className="qr-page__lead">
          Загрузите <strong>изображение</strong> — получите QR со ссылкой. По скану откроется картинка в
          браузере. Хостинг <strong>30 дней</strong>.
        </p>
      </div>

      <div className="qr-page__grid">
        <div className="qr-page__panel">
          <h2 className="qr-page__subtitle">Картинка</h2>
          <label className="sell__upload">
            <input
              type="file"
              accept="image/jpeg,image/png,image/webp"
              onChange={(e) => void handleFileChange(e)}
            />
            <span className="sell__upload-box">
              {previewUrl ? (
                <img src={previewUrl} alt="Превью" className="sell__preview" />
              ) : (
                <span>JPEG, PNG или WebP до 5 МБ</span>
              )}
            </span>
          </label>
          {uploading && <p className="checkout__note">Загружаем…</p>}
          {stagingId && !uploading && (
            <p className="checkout__note sell__ready">Картинка готова к оплате</p>
          )}

          {tier && (
            <div className="qr-page__tier">
              <span className="qr-page__tier-name">{tier.name}</span>
              <span className="qr-page__tier-price">{tier.price_label}</span>
              <p className="qr-page__tier-desc">{tier.description}</p>
            </div>
          )}
        </div>

        <div className="qr-page__panel qr-page__panel--checkout">
          <label className="checkout__label">
            Email для доставки QR и ссылки
            <input
              className="checkout__input"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              autoComplete="email"
            />
          </label>

          <label className="checkout__consent">
            <input type="checkbox" checked={agreed} onChange={(e) => setAgreed(e.target.checked)} />
            <span>
              Принимаю{" "}
              <a href="/offer" target="_blank" rel="noopener noreferrer">
                оферту
              </a>{" "}
              и{" "}
              <a href="/privacy" target="_blank" rel="noopener noreferrer">
                политику
              </a>
            </span>
          </label>

          {error && <p className="error-banner">{error}</p>}

          <button
            className="btn btn--primary btn--large"
            type="button"
            disabled={!canPay}
            onClick={() => void handlePay()}
          >
            {loading ? "Переход к оплате..." : `Оплатить ${tier?.price_label ?? ""}`}
          </button>
        </div>
      </div>
    </section>
  );
}
