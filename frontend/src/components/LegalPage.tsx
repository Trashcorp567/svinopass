import type { ReactNode } from "react";
import { SITE } from "../config/site";

interface LegalPageProps {
  title: string;
  children: ReactNode;
}

export default function LegalPage({ title, children }: LegalPageProps) {
  return (
    <article className="legal">
      <h1 className="legal__title">{title}</h1>
      <p className="legal__updated">Редакция от {SITE.updatedAt}</p>
      <div className="legal__body">{children}</div>
    </article>
  );
}
