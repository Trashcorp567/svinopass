interface ImageViewPageProps {
  token: string;
}

export default function ImageViewPage({ token }: ImageViewPageProps) {
  const src = `/api/public/images/${encodeURIComponent(token)}`;

  return (
    <section className="image-view">
      <img src={src} alt="Картинка по QR" className="image-view__img" />
      <p className="image-view__note">
        Хостинг Svinopass · только изображения · срок ограничен
      </p>
    </section>
  );
}
