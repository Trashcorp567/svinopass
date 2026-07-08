export default function DeliveryInfo() {
  return (
    <section className="delivery-info" id="delivery">
      <h2 className="section-title">Как получить заказ</h2>
      <div className="delivery-info__grid">
        <div className="delivery-info__card">
          <h3>Цифровая услуга</h3>
          <p>
            Svinopass оказывает услугу по генерации криптографически стойкого пароля.
            Физическая доставка не осуществляется — результат передаётся в электронном виде.
          </p>
        </div>
        <div className="delivery-info__card">
          <h3>Сразу после оплаты</h3>
          <p>
            После успешной оплаты через ЮKassa вы будете перенаправлены на страницу заказа.
            Пароль отображается на экране один раз — сохраните его в надёжном месте.
          </p>
        </div>
        <div className="delivery-info__card">
          <h3>Дублирование на email</h3>
          <p>
            Копия пароля отправляется на указанный при оформлении email.
            Срок доставки — обычно в течение нескольких минут после оплаты.
          </p>
        </div>
        <div className="delivery-info__card">
          <h3>Если письмо не пришло</h3>
          <p>
            Проверьте папку «Спам». Если пароль уже был показан на сайте, повторная выдача
            невозможна — мы не храним пароли. По вопросам:{" "}
            <a href="/contacts">контакты поддержки</a>.
          </p>
        </div>
      </div>
    </section>
  );
}
