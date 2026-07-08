export default function Hero({ onCta }: { onCta: () => void }) {
  return (
    <section className="hero">
      <div className="hero__pig" aria-hidden="true">
        🐷
      </div>
      <h1 className="hero__title">Генератор паролей онлайн</h1>
      <p className="hero__brand">Svinopa$$</p>
      <p className="hero__tagline">Криптографически стойкие пароли с доставкой на email</p>
      <p className="hero__subtitle">
        Выберите тариф, оплатите картой — пароль появится на экране и придёт на email. На сервере
        пароли не храним. Бесплатно: <a href="/check">проверка пароля</a> и{" "}
        <a href="/watch">проверка утечек email</a>.
      </p>
      <button className="btn btn--primary btn--large" onClick={onCta}>
        Выбрать тариф
      </button>
    </section>
  );
}
