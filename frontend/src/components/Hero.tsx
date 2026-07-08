import { SITE } from "../config/site";

export default function Hero({ onCta }: { onCta: () => void }) {
  return (
    <section className="hero">
      <div className="hero__pig" aria-hidden="true">
        🐷
      </div>
      <h1 className="hero__title">{SITE.name}</h1>
      <p className="hero__brand">Svinopa$$</p>
      <p className="hero__tagline">{SITE.tagline}</p>
      <p className="hero__subtitle">
        На главной — <strong>генератор паролей</strong> с доставкой на email. Ещё бесплатно:{" "}
        <a href="/check">проверка пароля</a> и <a href="/watch">проверка утечек</a>. Платно:{" "}
        <a href="/names">ники</a>, <a href="/sell">карточки для маркетплейсов</a>,{" "}
        <a href="/qr">QR-картинки</a>. Пароли на сервере не храним.
      </p>
      <button className="btn btn--primary btn--large" onClick={onCta}>
        Выбрать тариф
      </button>
    </section>
  );
}
