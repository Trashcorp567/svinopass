import { USE_CASE_PRESETS, type UseCaseId } from "../config/useCases";

interface UseCasePickerProps {
  activeUseCase: UseCaseId | null;
  onSelect: (useCaseId: UseCaseId, tierId: string) => void;
}

export default function UseCasePicker({ activeUseCase, onSelect }: UseCasePickerProps) {
  return (
    <section className="use-cases" id="use-cases">
      <h2 className="section-title">Под задачу</h2>
      <p className="use-cases__intro">Выберите сценарий — подсветим подходящий тариф.</p>
      <div className="use-cases__grid">
        {USE_CASE_PRESETS.map((preset) => (
          <button
            key={preset.id}
            type="button"
            className={`use-cases__card ${activeUseCase === preset.id ? "use-cases__card--active" : ""}`}
            onClick={() => onSelect(preset.id, preset.recommendedTier)}
          >
            <span className="use-cases__title">{preset.title}</span>
            <span className="use-cases__hint">{preset.hint}</span>
          </button>
        ))}
      </div>
    </section>
  );
}
