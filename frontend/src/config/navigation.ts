export interface NavItem {
  href: string;
  label: string;
}

export interface NavGroup {
  id: string;
  label: string;
  items: NavItem[];
}

export const NAV_GROUPS: NavGroup[] = [
  {
    id: "passwords",
    label: "Пароли",
    items: [
      { href: "/#pricing", label: "Все услуги" },
      { href: "/delivery", label: "Получение заказа" },
    ],
  },
  {
    id: "seller",
    label: "Продавцам",
    items: [{ href: "/sell", label: "Карточка маркетплейса" }],
  },
  {
    id: "logins",
    label: "Логины",
    items: [{ href: "/names", label: "Ники и псевдонимы" }],
  },
  {
    id: "security",
    label: "Безопасность",
    items: [
      { href: "/check", label: "Проверка пароля" },
      { href: "/watch", label: "Проверка утечек" },
    ],
  },
  {
    id: "qr",
    label: "QR",
    items: [{ href: "/qr", label: "QR-картинка" }],
  },
];
