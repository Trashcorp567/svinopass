import { SITE } from "../config/site";

const PAGE_SCHEMA: Record<string, object> = {
  "/check": {
    "@context": "https://schema.org",
    "@type": "WebApplication",
    name: "Проверка пароля и утечек онлайн",
    url: `${SITE.url}/check`,
    applicationCategory: "SecurityApplication",
    operatingSystem: "Web",
    offers: { "@type": "Offer", price: "0", priceCurrency: "RUB" },
    description: "Бесплатная проверка силы пароля и поиск в базах утечек.",
  },
  "/watch": {
    "@context": "https://schema.org",
    "@type": "Service",
    name: "Проверка утечек email — Свиной сторож",
    url: `${SITE.url}/watch`,
    provider: { "@type": "Organization", name: SITE.name },
    description: "Проверка email в публичных базах утечек и еженедельный мониторинг.",
    offers: { "@type": "Offer", price: "199", priceCurrency: "RUB" },
  },
  "/names": {
    "@context": "https://schema.org",
    "@type": "Service",
    name: "Генератор ников и псевдонимов",
    url: `${SITE.url}/names`,
    provider: { "@type": "Organization", name: SITE.name },
    description: "Платные наборы ников, псевдонимов и био для соцсетей и игр.",
    offers: { "@type": "Offer", price: "99", priceCurrency: "RUB" },
  },
};

export default function PageJsonLd({ pathname }: { pathname: string }) {
  const schema = PAGE_SCHEMA[pathname];
  if (!schema) return null;
  return (
    <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }} />
  );
}
