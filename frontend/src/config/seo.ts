import { SITE } from "./site";

export type PageMeta = {
  title: string;
  description: string;
  noindex?: boolean;
};

export const DEFAULT_META: PageMeta = {
  title: "Svinopass — генератор криптографически стойких паролей",
  description:
    "Разовая услуга: выберите тариф, оплатите картой — надёжный пароль появится на экране и придёт на email. Пароли на сервере не храним.",
};

export const PAGE_META: Record<string, PageMeta> = {
  "/": DEFAULT_META,
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
  "/check": {
    title: "Проверка надёжности пароля",
    description:
      "Бесплатный хрюк-чек: оценка силы пароля и проверка утечек в браузере. Пароль не отправляется на сервер Svinopass.",
  },
  "/watch": {
    title: "Свиной сторож — мониторинг утечек email",
    description:
      "Подписка 199₽/мес: проверка email в публичных базах утечек и уведомления раз в неделю.",
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

export const SITEMAP_PATHS = ["/", "/check", "/watch", "/offer", "/privacy", "/delivery", "/contacts"] as const;
