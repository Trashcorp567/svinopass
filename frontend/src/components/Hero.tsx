export default function Hero({ onCta }: { onCta: () => void }) {
  return (
    <section className="hero">
      <div className="hero__pig" aria-hidden="true">
        🐷
      </div>
      <h1 className="hero__title">Svinopa$$</h1>
      <p className="hero__tagline">Генератор криптографически стойких паролей</p>
      <p className="hero__subtitle">
        Разовая услуга: выберите тариф с фиксированной ценой, оплатите картой — пароль появится
        на экране и придёт на email. На сервере пароли не храним.
      </p>
      <button className="btn btn--primary btn--large" onClick={onCta}>
        Выбрать тариф
      </button>
    </section>
  );
}
