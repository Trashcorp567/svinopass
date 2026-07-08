import { SITE } from "../config/site";

const TOOLS = [
  {
    href: "/#pricing",
    name: "Генератор паролей онлайн",
    description: "Криптостойкий пароль с доставкой на email после оплаты.",
  },
  {
    href: "/check",
    name: "Проверка пароля",
    description: "Оценка силы и поиск в базах утечек.",
  },
  {
    href: "/watch",
    name: "Проверка утечек email",
    description: "Бесплатный снимок и подписка на мониторинг.",
  },
  {
    href: "/qr",
    name: "QR-картинка",
    description: "QR со ссылкой на изображение. Хостинг 30 дней.",
  },
  {
    href: "/names",
    name: "Ники и псевдонимы",
    description: "Платные наборы ников, псевдонимов и био для соцсетей и игр.",
  },
  {
    href: "/sell",
    name: "Карточка маркетплейса",
    description: "Описание товара для Ozon, Wildberries и Avito по фото.",
  },
] as const;

export default function SeoServices() {
  return (
    <section className="seo-services" aria-labelledby="seo-services-title">
      <h2 id="seo-services-title" className="section-title">
        Услуги Svinopass
      </h2>
      <p className="seo-services__lead">
        {SITE.name} — {SITE.tagline.toLowerCase()}. Генератор паролей, проверка утечек, ники,
        карточки для маркетплейсов и QR-картинки.
      </p>
      <ul className="seo-services__list">
        {TOOLS.map((tool) => (
          <li key={tool.href}>
            <a href={tool.href} className="seo-services__card">
              <strong>{tool.name}</strong>
              <span>{tool.description}</span>
            </a>
          </li>
        ))}
      </ul>
    </section>
  );
}
