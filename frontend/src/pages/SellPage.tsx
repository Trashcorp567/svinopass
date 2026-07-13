import { useEffect, useMemo, useState, type ChangeEvent } from "react";
import {
  createSellCheckout,
  fetchTiers,
  stageSellImage,
  type Tier,
} from "../api/client";
import { SELL_TIER_IDS, SELL_TIER_PLATFORM, type SellTierId } from "../config/sellTiers";

const ACCEPTED_TYPES = ["image/jpeg", "image/png", "image/webp"];

export default function SellPage() {
  const [tiers, setTiers] = useState<Tier[]>([]);
  const [selectedTier, setSelectedTier] = useState<SellTierId>("ozon_card");
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [stagingId, setStagingId] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [productName, setProductName] = useState("");
  const [productCategory, setProductCategory] = useState("");
  const [productHints, setProductHints] = useState("");
  const [email, setEmail] = useState("");
  const [agreed, setAgreed] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchTiers()
      .then((all) => {
        setTiers(all.filter((t) => t.product_type === "seller"));
        const params = new URLSearchParams(window.location.search);
        const tier = params.get("tier");
        if (tier && SELL_TIER_IDS.includes(tier as SellTierId)) {
          setSelectedTier(tier as SellTierId);
        }
      })
      .catch(console.error);
  }, []);

  useEffect(() => {
    return () => {
      if (previewUrl) URL.revokeObjectURL(previewUrl);
    };
  }, [previewUrl]);

  const selectedTierInfo = tiers.find((t) => t.id === selectedTier) ?? null;
  const platformLabel = SELL_TIER_PLATFORM[selectedTier];

  const canPay = useMemo(
    () =>
      Boolean(selectedTierInfo) &&
      Boolean(stagingId) &&
      email.trim().length > 0 &&
      agreed &&
      !loading &&
      !uploading,
    [selectedTierInfo, stagingId, email, agreed, loading, uploading],
  );

  const handleFileChange = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    setError(null);

    if (!ACCEPTED_TYPES.includes(file.type)) {
      setError("Поддерживаются JPEG, PNG и WebP");
      return;
    }
    if (file.size > 5 * 1024 * 1024) {
      setError("Фото до 5 МБ");
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
      setError(e instanceof Error ? e.message : "Не удалось загрузить фото");
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
        selectedTier,
        email.trim(),
        stagingId,
        productName.trim(),
        productCategory.trim(),
        productHints.trim(),
      );
      window.location.href = checkout.confirmation_url;
    } catch (e) {
      setError(e instanceof Error ? e.message : "Ошибка оплаты");
      setLoading(false);
    }
  };

  return (
    <section className="sell">
      <div className="sell__hero">
        <h1 className="section-title">Карточка для маркетплейса</h1>
        <p className="sell__lead">
          Загрузите фото товара — получите заголовки и описание под{" "}
          <strong>{platformLabel}</strong>. Тексты приходят на экран и email.{" "}
          <strong>Проверьте факты перед публикацией.</strong>
        </p>
      </div>

      <div className="sell__grid">
        <div className="sell__panel">
          <h2 className="sell__subtitle">Тариф</h2>
          <div className="sell__tier-grid">
            {SELL_TIER_IDS.map((tierId) => {
              const tier = tiers.find((t) => t.id === tierId);
              if (!tier) return null;
              return (
                <button
                  key={tierId}
                  type="button"
                  className={`sell__tier-card${selectedTier === tierId ? " sell__tier-card--active" : ""}`}
                  onClick={() => setSelectedTier(tierId)}
                >
                  <span className="sell__tier-name">{tier.name}</span>
                  <span className="sell__tier-price">{tier.price_label}</span>
                  <span className="sell__tier-desc">{tier.description}</span>
                </button>
              );
            })}
          </div>

          <h2 className="sell__subtitle">Фото товара</h2>
          <label className="sell__upload">
            <input
              type="file"
              accept="image/jpeg,image/png,image/webp"
              onChange={(e) => void handleFileChange(e)}
            />
            <span className="sell__upload-box">
              {previewUrl ? (
                <img src={previewUrl} alt="Превью товара" className="sell__preview" />
              ) : (
                <span>Нажмите, чтобы выбрать фото (до 5 МБ)</span>
              )}
            </span>
          </label>
          {uploading && <p className="checkout__note">Загружаем фото…</p>}
          {stagingId && !uploading && (
            <p className="checkout__note sell__ready">Фото готово к оплате</p>
          )}

          <label className="checkout__label">
            Название товара (опционально)
            <input
              className="checkout__input"
              value={productName}
              onChange={(e) => setProductName(e.target.value)}
              maxLength={120}
              placeholder="Например: Термокружка 450 мл"
            />
          </label>
          <label className="checkout__label">
            Категория (опционально)
            <input
              className="checkout__input"
              value={productCategory}
              onChange={(e) => setProductCategory(e.target.value)}
              maxLength={120}
              placeholder="Посуда / спорт / электроника"
            />
          </label>
          <label className="checkout__label">
            Подсказки для текста (опционально)
            <textarea
              className="checkout__input sell__textarea"
              value={productHints}
              onChange={(e) => setProductHints(e.target.value)}
              maxLength={500}
              rows={4}
              placeholder="Материал, размер, комплектация, ключевые выгоды"
            />
          </label>
        </div>

        <div className="sell__panel sell__panel--checkout">
          <label className="checkout__label">
            Email для доставки
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
            <input
              type="checkbox"
              checked={agreed}
              onChange={(e) => setAgreed(e.target.checked)}
            />
            <span>
              Принимаю{" "}
              <a href="/offer" target="_blank" rel="noopener noreferrer">
                публичную оферту
              </a>{" "}
              и{" "}
              <a href="/privacy" target="_blank" rel="noopener noreferrer">
                политику конфиденциальности
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
            {loading
              ? "Переход к оплате..."
              : `Оплатить ${selectedTierInfo?.price_label ?? ""}`}
          </button>
        </div>
      </div>
    </section>
  );
}
