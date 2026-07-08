import type { MouseEvent } from "react";
import { LEGAL_LINKS } from "../config/site";

interface SiteHeaderProps {
  onHomeNav?: (event: MouseEvent<HTMLAnchorElement>) => void;
}

export default function SiteHeader({ onHomeNav }: SiteHeaderProps) {
  return (
    <header className="header">
      <a href="/" className="header__logo" onClick={onHomeNav}>
        Svinopass
      </a>
      <nav className="header__nav">
        <a href="/" onClick={onHomeNav}>
          Главная
        </a>
        <a href="/#pricing">Тарифы</a>
        <a href="/check">Проверить пароль</a>
        <a href="/watch">Свиной сторож</a>
        {LEGAL_LINKS.map((link) => (
          <a key={link.href} href={link.href}>
            {link.label}
          </a>
        ))}
      </nav>
    </header>
  );
}
