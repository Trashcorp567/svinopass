import LegalPage from "../components/LegalPage";
import { SITE } from "../config/site";

export default function ContactsPage() {
  return (
    <LegalPage title="Контакты и реквизиты">
      <div className="contacts">
        <section className="contacts__block">
          <h2>Продавец (самозанятый)</h2>
          <dl className="contacts__list">
            <div>
              <dt>ФИО</dt>
              <dd>{SITE.sellerName}</dd>
            </div>
            <div>
              <dt>ИНН</dt>
              <dd>{SITE.inn}</dd>
            </div>
            <div>
              <dt>Статус</dt>
              <dd>Плательщик налога на профессиональный доход (самозанятый)</dd>
            </div>
          </dl>
        </section>

        <section className="contacts__block">
          <h2>Как связаться</h2>
          <dl className="contacts__list">
            <div>
              <dt>Email</dt>
              <dd>
                <a href={`mailto:${SITE.email}`}>{SITE.email}</a>
              </dd>
            </div>
            <div>
              <dt>Телефон</dt>
              <dd>
                <a href={`tel:${SITE.phone.replace(/\s|[()]/g, "")}`}>{SITE.phone}</a>
              </dd>
            </div>
            <div>
              <dt>Время ответа</dt>
              <dd>{SITE.supportHours}</dd>
            </div>
            <div>
              <dt>Почтовый адрес</dt>
              <dd>{SITE.postalAddress}</dd>
            </div>
            <div>
              <dt>Сайт</dt>
              <dd>
                <a href={SITE.url}>{SITE.url}</a>
              </dd>
            </div>
          </dl>
        </section>

        <section className="contacts__block">
          <h2>Услуги</h2>
          <p>
            Онлайн-сервис генерации криптографически стойких паролей. Оплата банковской картой через
            ЮKassa. Цены и описания тарифов — на{" "}
            <a href="/#pricing">главной странице</a>.
          </p>
        </section>
      </div>
    </LegalPage>
  );
}
