import { SITE } from "../config/site";

export default function Hero({ onCta }: { onCta: () => void }) {
  return (
    <section className="hero">
      <div className="hero__glow" aria-hidden />
      <div className="hero__pig" aria-hidden="true">
        🐷
      </div>
      <p className="hero__eyebrow">Svinopa$$</p>
      <h1 className="hero__title">{SITE.name}</h1>
      <p className="hero__tagline">{SITE.tagline}</p>
      <p className="hero__subtitle">
        Пароли, ники, карточки для маркетплейсов и инструменты безопасности — всё на одной главной.
        Выберите категорию и тариф ниже.
      </p>
      <button className="btn btn--primary btn--large" onClick={onCta}>
        Выбрать услугу
      </button>
    </section>
  );
}
