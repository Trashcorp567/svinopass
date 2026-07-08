import { LEGAL_LINKS, SITE } from "../config/site";

export default function SiteFooter() {
  return (
    <footer className="footer">
      <nav className="footer__nav" aria-label="Юридическая информация">
        <a href="/check">Проверить пароль</a>
        <a href="/watch">Свиной сторож</a>
        {LEGAL_LINKS.map((link) => (
          <a key={link.href} href={link.href}>
            {link.label}
          </a>
        ))}
      </nav>
      <div className="footer__seller">
        <p>
          {SITE.sellerName} · ИНН {SITE.inn}
        </p>
        <p>
          <a href={`mailto:${SITE.email}`}>{SITE.email}</a>
          {" · "}
          <a href={`tel:${SITE.phone.replace(/\s|[()]/g, "")}`}>{SITE.phone}</a>
        </p>
      </div>
      <p className="footer__copy">
        © {SITE.domain} {new Date().getFullYear()}
      </p>
    </footer>
  );
}
