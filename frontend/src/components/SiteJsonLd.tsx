import { SITE } from "../config/site";

const websiteJsonLd = {
  "@context": "https://schema.org",
  "@type": "WebSite",
  name: SITE.name,
  url: SITE.url,
  description:
    "Цифровые услуги онлайн: пароли, ники, карточки маркетплейсов, QR-картинки, проверка утечек.",
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

const servicesListJsonLd = {
  "@context": "https://schema.org",
  "@type": "ItemList",
  name: "Услуги Svinopass",
  itemListElement: [
    {
      "@type": "ListItem",
      position: 1,
      name: "Генератор паролей",
      url: `${SITE.url}/#pricing`,
    },
    {
      "@type": "ListItem",
      position: 2,
      name: "Проверка пароля и утечек",
      url: `${SITE.url}/check`,
    },
    {
      "@type": "ListItem",
      position: 3,
      name: "Ники и псевдонимы",
      url: `${SITE.url}/names`,
    },
    {
      "@type": "ListItem",
      position: 4,
      name: "Карточки для маркетплейсов",
      url: `${SITE.url}/sell`,
    },
    {
      "@type": "ListItem",
      position: 5,
      name: "QR-картинка",
      url: `${SITE.url}/qr`,
    },
    {
      "@type": "ListItem",
      position: 6,
      name: "Мониторинг утечек email",
      url: `${SITE.url}/watch`,
    },
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
        dangerouslySetInnerHTML={{ __html: JSON.stringify(servicesListJsonLd) }}
      />
    </>
  );
}
