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
    description: "Оценка силы и поиск в базах утечек (HIBP).",
  },
  {
    href: "/watch",
    name: "Проверка утечек email",
    description: "Бесплатный снимок и подписка на мониторинг.",
  },
  {
    href: "/names",
    name: "Ники и псевдонимы",
    description: "Платные наборы English-ников, псевдонимов и био для соцсетей и игр.",
  },
] as const;

export default function SeoServices() {
  return (
    <section className="seo-services" aria-labelledby="seo-services-title">
      <h2 id="seo-services-title" className="section-title">
        Услуги Svinopass
      </h2>
      <p className="seo-services__lead">
        {SITE.name} — генератор паролей онлайн с доставкой на email. Бесплатно: проверка пароля и
        проверка утечек email.
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
