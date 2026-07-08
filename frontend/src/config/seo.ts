import { SITE } from "./site";

export type PageMeta = {
  title: string;
  description: string;
  noindex?: boolean;
};

/** Главная: бренд + пароли в description для SEO, без узкого «только генератор». */
export const DEFAULT_META: PageMeta = {
  title: `${SITE.name} — пароли, проверка утечек и онлайн-инструменты`,
  description:
    "Генератор паролей с доставкой на email, бесплатная проверка утечек, ники, карточки для Ozon и Wildberries, QR-картинки. Пароли на сервере не храним.",
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
  "/sell": {
    title: "Описание товара для Ozon, Wildberries и Avito по фото",
    description:
      "Загрузите фото товара — получите заголовки и SEO-описание для маркетплейса. Ozon, WB, Avito или полный пакет.",
  },
  "/sell/success": {
    title: "Тексты для маркетплейса готовы",
    description: "Страница выдачи описаний товара после оплаты.",
    noindex: true,
  },
  "/qr": {
    title: "QR-картинка — ссылка на фото по QR",
    description:
      "Загрузите изображение и получите QR со ссылкой. Только JPEG, PNG, WebP. Хостинг 30 дней. Без видео и аудио.",
  },
  "/qr/success": {
    title: "QR готов",
    description: "Страница выдачи QR-картинки после оплаты.",
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
  "/sell",
  "/qr",
  "/watch",
  "/offer",
  "/privacy",
  "/delivery",
  "/contacts",
] as const;
