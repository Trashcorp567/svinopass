/** Реквизиты продавца для страниц сайта и модерации ЮKassa. */
export const SITE = {
  name: "Svinopass",
  /** Короткий слоган для hero и SEO — не только пароли. */
  tagline: "Пароли, безопасность и полезные инструменты онлайн",
  domain: "svinopass.ru",
  url: "https://svinopass.ru",
  sellerName: "Глинский Владислав Иванович",
  inn: "710607988002",
  email: "supersvinopass@yandex.ru",
  phone: "+7 (910) 556-59-62",
  postalAddress: "Российская Федерация (адрес по запросу на email)",
  supportHours: "Пн–Вс, 10:00–20:00 (МСК)",
  updatedAt: "7 июля 2026 г.",
} as const;

export const LEGAL_LINKS = [
  { href: "/offer", label: "Публичная оферта" },
  { href: "/privacy", label: "Политика конфиденциальности" },
  { href: "/delivery", label: "Получение заказа" },
  { href: "/contacts", label: "Контакты и реквизиты" },
] as const;
