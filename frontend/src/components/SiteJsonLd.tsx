import { SITE } from "../config/site";

const websiteJsonLd = {
  "@context": "https://schema.org",
  "@type": "WebSite",
  name: SITE.name,
  url: SITE.url,
  description:
    "Пароли с доставкой на email, проверка утечек, ники, карточки для маркетплейсов и QR-картинки.",
  inLanguage: "ru-RU",
};

const organizationJsonLd = {
  "@context": "https://schema.org",
  "@type": "Organization",
  name: SITE.name,
  url: SITE.url,
  email: SITE.email,
  telephone: SITE.phone.replace(/\s|[()]/g, ""),
  founder: {
    "@type": "Person",
    name: SITE.sellerName,
  },
};

const webAppJsonLd = {
  "@context": "https://schema.org",
  "@type": "WebApplication",
  name: SITE.name,
  url: SITE.url,
  applicationCategory: "SecurityApplication",
  operatingSystem: "Web",
  offers: {
    "@type": "Offer",
    price: "99",
    priceCurrency: "RUB",
    description: "Генерация криптостойкого пароля с доставкой на email",
  },
  featureList: [
    "Генератор паролей",
    "Проверка пароля и утечек",
    "Ники и псевдонимы",
    "Карточки для маркетплейсов",
    "QR-картинки",
  ],
};

export default function SiteJsonLd() {
  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(websiteJsonLd) }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(organizationJsonLd) }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(webAppJsonLd) }}
      />
    </>
  );
}
