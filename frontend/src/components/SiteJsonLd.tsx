import { SITE } from "../config/site";

const websiteJsonLd = {
  "@context": "https://schema.org",
  "@type": "WebSite",
  name: SITE.name,
  url: SITE.url,
  description:
    "Генератор криптографически стойких паролей. Разовая оплата — пароль на экране и на email.",
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
    </>
  );
}
