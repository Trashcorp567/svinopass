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
      { href: "/#pricing", label: "Тарифы и оплата" },
      { href: "/delivery", label: "Получение заказа" },
    ],
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
];
