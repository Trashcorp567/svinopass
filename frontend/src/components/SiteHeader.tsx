import { useEffect, useRef, useState, type MouseEvent } from "react";
import { LEGAL_LINKS } from "../config/site";
import { NAV_GROUPS } from "../config/navigation";

interface SiteHeaderProps {
  onHomeNav?: (event: MouseEvent<HTMLAnchorElement>) => void;
  onOpenPigGame?: () => void;
}

export default function SiteHeader({ onHomeNav, onOpenPigGame }: SiteHeaderProps) {
  const [menuOpen, setMenuOpen] = useState(false);
  const [openDropdown, setOpenDropdown] = useState<string | null>(null);
  const navRef = useRef<HTMLElement>(null);

  useEffect(() => {
    document.body.style.overflow = menuOpen ? "hidden" : "";
    return () => {
      document.body.style.overflow = "";
    };
  }, [menuOpen]);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent | globalThis.MouseEvent) => {
      if (!navRef.current?.contains(event.target as Node)) {
        setOpenDropdown(null);
      }
    };
    document.addEventListener("mousedown", handleClickOutside as EventListener);
    return () => document.removeEventListener("mousedown", handleClickOutside as EventListener);
  }, []);

  const closeMenu = () => setMenuOpen(false);

  return (
    <>
      <header className="header">
        <a href="/" className="header__logo" onClick={onHomeNav}>
          Svinopass
        </a>

        <nav
          ref={navRef}
          className="header__nav header__nav--desktop"
          aria-label="Основная навигация"
        >
          <a href="/" className="header__nav-link" onClick={onHomeNav}>
            Главная
          </a>
          {NAV_GROUPS.map((group) => (
            <div
              key={group.id}
              className={`header__dropdown${openDropdown === group.id ? " header__dropdown--open" : ""}`}
            >
              <button
                type="button"
                className="header__dropdown-btn"
                aria-expanded={openDropdown === group.id}
                onClick={() =>
                  setOpenDropdown((current) => (current === group.id ? null : group.id))
                }
              >
                {group.label}
                <span className="header__dropdown-caret" aria-hidden>
                  ▾
                </span>
              </button>
              <div className="header__dropdown-menu">
                {group.items.map((item) => (
                  <a
                    key={item.href}
                    href={item.href}
                    className="header__dropdown-link"
                    onClick={() => setOpenDropdown(null)}
                  >
                    {item.label}
                  </a>
                ))}
              </div>
            </div>
          ))}
        </nav>

        <div className="header__actions">
          <button
            type="button"
            className="btn btn--outline btn--small header__game-btn"
            onClick={onOpenPigGame}
          >
            Хрюк-хватай 🐷
          </button>
          <button
            type="button"
            className="header__burger"
            aria-label={menuOpen ? "Закрыть меню" : "Открыть меню"}
            aria-expanded={menuOpen}
            onClick={() => setMenuOpen((open) => !open)}
          >
            <span />
            <span />
            <span />
          </button>
        </div>
      </header>

      <div className={`side-menu${menuOpen ? " side-menu--open" : ""}`} aria-hidden={!menuOpen}>
        <button
          type="button"
          className="side-menu__backdrop"
          aria-label="Закрыть меню"
          onClick={closeMenu}
        />
        <aside className="side-menu__panel" role="dialog" aria-modal="true" aria-label="Меню">
          <div className="side-menu__head">
            <span className="side-menu__title">Меню</span>
            <button
              type="button"
              className="side-menu__close"
              onClick={closeMenu}
              aria-label="Закрыть"
            >
              ✕
            </button>
          </div>

          <nav className="side-menu__nav">
            <a
              href="/"
              onClick={(e) => {
                onHomeNav?.(e);
                closeMenu();
              }}
            >
              Главная
            </a>
            {NAV_GROUPS.map((group) => (
              <div key={group.id} className="side-menu__section">
                <span className="side-menu__section-label">{group.label}</span>
                {group.items.map((item) => (
                  <a key={item.href} href={item.href} onClick={closeMenu}>
                    {item.label}
                  </a>
                ))}
              </div>
            ))}
          </nav>

          <div className="side-menu__section">
            <span className="side-menu__section-label">Документы</span>
            {LEGAL_LINKS.map((link) => (
              <a key={link.href} href={link.href} onClick={closeMenu}>
                {link.label}
              </a>
            ))}
          </div>

          <button
            type="button"
            className="btn btn--outline side-menu__game"
            onClick={() => {
              onOpenPigGame?.();
              closeMenu();
            }}
          >
            Хрюк-хватай 🐷
          </button>
        </aside>
      </div>
    </>
  );
}
