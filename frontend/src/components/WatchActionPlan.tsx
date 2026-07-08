import {
  getWatchActionDisclaimer,
  getWatchActionSteps,
} from "../config/watchActionPlan";

interface WatchActionPlanProps {
  breachCount: number;
  /** Скрыть CTA на подписку сторожа (уже подключён). */
  hideWatchCta?: boolean;
}

export default function WatchActionPlan({ breachCount, hideWatchCta = false }: WatchActionPlanProps) {
  const steps = getWatchActionSteps(breachCount).filter(
    (step) => !(hideWatchCta && step.link?.href === "/watch"),
  );

  return (
    <aside className="watch-plan" aria-labelledby="watch-plan-title">
      <h2 id="watch-plan-title" className="watch-plan__title">
        {breachCount > 0 ? "Что делать после утечки" : "Как оставаться в безопасности"}
      </h2>
      <ol className="watch-plan__steps">
        {steps.map((step, index) => (
          <li key={index}>
            {step.text}
            {step.link && (
              <>
                {" "}
                <a href={step.link.href}>{step.link.label}</a>
              </>
            )}
          </li>
        ))}
      </ol>
      <p className="watch-plan__disclaimer">{getWatchActionDisclaimer()}</p>
    </aside>
  );
}
