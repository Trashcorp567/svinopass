export type ServiceCategoryId = "passwords" | "logins" | "seller" | "security";

export interface ServiceCategory {
  id: ServiceCategoryId;
  label: string;
  icon: string;
  description: string;
  accent: string;
}

export const SERVICE_CATEGORIES: ServiceCategory[] = [
  {
    id: "passwords",
    label: "Пароли",
    icon: "🔐",
    description: "Генератор и backup-коды",
    accent: "#ff6b9d",
  },
  {
    id: "logins",
    label: "Логины",
    icon: "🎮",
    description: "Ники и псевдонимы",
    accent: "#5ec8ff",
  },
  {
    id: "seller",
    label: "Продавцам",
    icon: "🛒",
    description: "Карточки маркетплейсов",
    accent: "#7ee787",
  },
  {
    id: "security",
    label: "Безопасность",
    icon: "🛡️",
    description: "Проверки и мониторинг",
    accent: "#b8a0ff",
  },
];

export const FREE_SECURITY_TOOLS = [
  {
    href: "/check",
    name: "Проверка пароля",
    description: "Сила пароля и поиск в базах утечек. Бесплатно в браузере.",
    badge: "Бесплатно",
  },
  {
    href: "/watch",
    name: "Снимок утечек email",
    description: "Бесплатная проверка email в публичных базах прямо сейчас.",
    badge: "Бесплатно",
  },
] as const;

export function tierPageHref(category: ServiceCategoryId, tierId: string): string {
  if (category === "logins") return `/names?tier=${tierId}`;
  if (category === "seller") return `/sell?tier=${tierId}`;
  if (category === "security") {
    if (tierId === "storozh") return "/watch";
    if (tierId === "qr_pic") return "/qr";
  }
  return "/";
}
