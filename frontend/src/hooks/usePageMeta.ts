import { useEffect } from "react";
import { DEFAULT_META, PAGE_META, type PageMeta } from "../config/seo";
import { SITE } from "../config/site";

function upsertMeta(selector: string, create: () => HTMLElement, content: string) {
  let el = document.head.querySelector(selector);
  if (!el) {
    el = create();
    document.head.appendChild(el);
  }
  el.setAttribute("content", content);
}

function upsertLink(rel: string, href: string) {
  let el = document.head.querySelector(`link[rel="${rel}"]`);
  if (!el) {
    el = document.createElement("link");
    el.setAttribute("rel", rel);
    document.head.appendChild(el);
  }
  el.setAttribute("href", href);
}

export function usePageMeta(pathname: string) {
  useEffect(() => {
    const meta: PageMeta = PAGE_META[pathname] ?? DEFAULT_META;
    const canonicalPath = pathname === "/" ? "" : pathname;
    const url = `${SITE.url}${canonicalPath}`;
    const documentTitle =
      pathname === "/" ? `${meta.title} | ${SITE.name}` : `${meta.title} — ${SITE.name}`;

    document.title = documentTitle;

    upsertMeta(
      'meta[name="description"]',
      () => {
        const tag = document.createElement("meta");
        tag.setAttribute("name", "description");
        return tag;
      },
      meta.description,
    );

    upsertMeta(
      'meta[name="robots"]',
      () => {
        const tag = document.createElement("meta");
        tag.setAttribute("name", "robots");
        return tag;
      },
      meta.noindex ? "noindex, nofollow" : "index, follow",
    );

    upsertLink("canonical", url);

    for (const [property, content] of [
      ["og:title", documentTitle],
      ["og:description", meta.description],
      ["og:url", url],
      ["og:type", "website"],
      ["og:locale", "ru_RU"],
      ["og:site_name", SITE.name],
    ] as const) {
      upsertMeta(
        `meta[property="${property}"]`,
        () => {
          const tag = document.createElement("meta");
          tag.setAttribute("property", property);
          return tag;
        },
        content,
      );
    }
  }, [pathname]);
}
