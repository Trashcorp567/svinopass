import { SITE } from "./site";

export type PageMeta = {
  title: string;
  description: string;
  noindex?: boolean;
};

/** Главная: ключ «генератор паролей онлайн» в title и description. */
export const DEFAULT_META: PageMeta = {
  title: "Генератор паролей онлайн — криптостойкий пароль на email",
  description:
    "Генератор паролей онлайн с доставкой на email после оплаты. Бесплатно: проверка пароля и проверка утечек email. Пароли на сервере не храним.",
};

export const PAGE_META: Record<string, PageMeta> = {
  "/": DEFAULT_META,
  "/check": {
    title: "Проверка пароля и утечек онлайн",
    description:
      "Бесплатная проверка пароля: оценка силы, энтропия и поиск в базах утечек (HIBP k-anonymity). Пароль не отправляется на сервер Svinopass.",
  },
  "/watch": {
    title: "Проверка утечек email — мониторинг баз",
    description:
      "Бесплатная проверка утечек email в публичных базах. Подписка 199₽/мес: еженедельный мониторинг и уведомления о новых утечках.",
  },
  "/names": {
    title: "Генератор ников и псевдонимов онлайн",
    description:
      "Платный набор English-ников, псевдонимов и био для соцсетей и игр.",
  },
  "/names/success": {
    title: "Набор готов",
    description: "Страница выдачи ников и псевдонимов после оплаты.",
    noindex: true,
  },
  "/offer": {
    title: "Публичная оферта",
    description: `Условия оказания услуги генерации паролей на ${SITE.domain}. Тарифы, оплата, возврат, ответственность сторон.`,
  },
  "/privacy": {
    title: "Политика конфиденциальности",
    description: `Как ${SITE.name} обрабатывает персональные данные при заказе услуги генерации паролей на ${SITE.domain}.`,
  },
  "/delivery": {
    title: "Получение заказа",
    description:
      "Как получить пароль после оплаты: отображение на сайте, доставка на email, сроки и поддержка.",
  },
  "/contacts": {
    title: "Контакты и реквизиты",
    description: `Контакты продавца ${SITE.sellerName}, ИНН ${SITE.inn}, email и телефон поддержки ${SITE.name}.`,
  },
  "/watch/success": {
    title: "Сторож подключён",
    description: "Подтверждение подписки на мониторинг утечек email.",
    noindex: true,
  },
  "/payment/success": {
    title: "Заказ оформлен",
    description: "Страница выдачи пароля после оплаты.",
    noindex: true,
  },
};

export const SITEMAP_PATHS = [
  "/",
  "/check",
  "/names",
  "/watch",
  "/offer",
  "/privacy",
  "/delivery",
  "/contacts",
] as const;
