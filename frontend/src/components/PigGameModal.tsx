import { useEffect, useRef, type MouseEvent } from "react";
import PigWhackGame from "./PigWhackGame";

interface PigGameModalProps {
  open: boolean;
  onClose: () => void;
}

export default function PigGameModal({ open, onClose }: PigGameModalProps) {
  const dialogRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;

    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") onClose();
    };

    window.addEventListener("keydown", handleKeyDown);
    dialogRef.current?.focus();

    return () => {
      document.body.style.overflow = previousOverflow;
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [open, onClose]);

  if (!open) return null;

  const handleOverlayClick = (event: MouseEvent<HTMLDivElement>) => {
    if (event.target === event.currentTarget) onClose();
  };

  return (
    <div
      className="pig-modal__overlay"
      onClick={handleOverlayClick}
      role="presentation"
    >
      <div
        ref={dialogRef}
        className="pig-modal__dialog"
        role="dialog"
        aria-modal="true"
        aria-labelledby="pig-game-title"
        tabIndex={-1}
      >
        <button
          type="button"
          className="pig-modal__close"
          onClick={onClose}
          aria-label="Закрыть игру"
        >
          ✕
        </button>
        <PigWhackGame onClose={onClose} />
      </div>
    </div>
  );
}
