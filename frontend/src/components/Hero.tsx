export default function Hero({ onCta }: { onCta: () => void }) {
  return (
    <section className="hero">
      <div className="hero__pig" aria-hidden="true">🐷</div>
      <h1 className="hero__title">Svinopa$$</h1>
      <p className="hero__tagline">Единственный пароль, подходящий достойной свинке</p>
      <p className="hero__subtitle">
        Криптографически стойкие пароли по подписке на хрюканье.
        Покажем сразу, отправим на почту — на сервере не храним.
      </p>
      <button className="btn btn--primary btn--large" onClick={onCta}>
        Выбрать тариф 💰
      </button>
    </section>
  );
}
