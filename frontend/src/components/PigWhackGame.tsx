import { useCallback, useEffect, useRef, useState } from "react";

const HOLE_COUNT = 9;
const ROUND_SECONDS = 30;
const MIN_VISIBLE_MS = 400;
const MAX_VISIBLE_MS = 1200;
const MIN_SPAWN_DELAY_MS = 30;
const MAX_SPAWN_DELAY_MS = 160;
const PASSWORD_PENALTY = 2;
const MISS_PENALTY = 1;
const GOLD_BONUS = 5;
const PASSWORD_TRAP_ICON = "🔒";

type Phase = "idle" | "playing" | "finished";
type TargetType = "pig" | "gold" | "password";

interface ActiveTarget {
  hole: number;
  type: TargetType;
}

function getRank(score: number): string {
  if (score >= 30) return "Легенда хрюши";
  if (score >= 20) return "Бекон Pro";
  if (score >= 10) return "Свиномат";
  return "Хряк-новичок";
}

function difficultyFactor(timeLeft: number): number {
  const elapsed = ROUND_SECONDS - timeLeft;
  const progress = elapsed / ROUND_SECONDS;
  return progress * progress;
}

function visibleDurationMs(timeLeft: number): number {
  const accel = difficultyFactor(timeLeft);
  return Math.round(MAX_VISIBLE_MS - (MAX_VISIBLE_MS - MIN_VISIBLE_MS) * accel);
}

function spawnDelayMs(timeLeft: number): number {
  const accel = difficultyFactor(timeLeft);
  return Math.round(MAX_SPAWN_DELAY_MS - (MAX_SPAWN_DELAY_MS - MIN_SPAWN_DELAY_MS) * accel);
}

function pickTargetType(): TargetType {
  const roll = Math.random();
  if (roll < 0.1) return "gold";
  if (roll < 0.35) return "password";
  return "pig";
}

function holeClassName(index: number, target: ActiveTarget | null): string {
  if (!target || target.hole !== index) return "pig-game__hole";
  if (target.type === "gold") return "pig-game__hole pig-game__hole--gold";
  if (target.type === "password") return "pig-game__hole pig-game__hole--trap";
  return "pig-game__hole pig-game__hole--active";
}

function holeAriaLabel(index: number, target: ActiveTarget | null): string {
  if (!target || target.hole !== index) return "Пустая лунка — промах, −1 очко";
  if (target.type === "gold") return "Золотая свинка! +5 очков";
  if (target.type === "password") return "Значок пароля! Не нажимайте";
  return "Свинка! Нажмите";
}

interface PigWhackGameProps {
  onClose: () => void;
}

export default function PigWhackGame({ onClose }: PigWhackGameProps) {
  const [phase, setPhase] = useState<Phase>("idle");
  const [score, setScore] = useState(0);
  const [timeLeft, setTimeLeft] = useState(ROUND_SECONDS);
  const [activeTarget, setActiveTarget] = useState<ActiveTarget | null>(null);

  const hideTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const spawnTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const countdownRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const timeLeftRef = useRef(ROUND_SECONDS);
  const phaseRef = useRef<Phase>("idle");

  const clearTimers = useCallback(() => {
    if (hideTimeoutRef.current) {
      clearTimeout(hideTimeoutRef.current);
      hideTimeoutRef.current = null;
    }
    if (spawnTimeoutRef.current) {
      clearTimeout(spawnTimeoutRef.current);
      spawnTimeoutRef.current = null;
    }
    if (countdownRef.current) {
      clearInterval(countdownRef.current);
      countdownRef.current = null;
    }
  }, []);

  const spawnTarget = useCallback(() => {
    if (phaseRef.current !== "playing") return;

    const hole = Math.floor(Math.random() * HOLE_COUNT);
    const type = pickTargetType();
    const target: ActiveTarget = { hole, type };

    setActiveTarget(target);

    const duration = visibleDurationMs(timeLeftRef.current);
    hideTimeoutRef.current = setTimeout(() => {
      setActiveTarget(null);
      spawnTimeoutRef.current = setTimeout(spawnTarget, spawnDelayMs(timeLeftRef.current));
    }, duration);
  }, []);

  const startGame = useCallback(() => {
    clearTimers();
    setScore(0);
    setTimeLeft(ROUND_SECONDS);
    timeLeftRef.current = ROUND_SECONDS;
    setActiveTarget(null);
    phaseRef.current = "playing";
    setPhase("playing");

    countdownRef.current = setInterval(() => {
      timeLeftRef.current -= 1;
      setTimeLeft(timeLeftRef.current);

      if (timeLeftRef.current <= 0) {
        clearTimers();
        phaseRef.current = "finished";
        setPhase("finished");
        setActiveTarget(null);
      }
    }, 1000);

    spawnTarget();
  }, [clearTimers, spawnTarget]);

  const resolveTarget = (target: ActiveTarget) => {
    if (hideTimeoutRef.current) {
      clearTimeout(hideTimeoutRef.current);
      hideTimeoutRef.current = null;
    }
    if (spawnTimeoutRef.current) {
      clearTimeout(spawnTimeoutRef.current);
      spawnTimeoutRef.current = null;
    }

    if (target.type === "gold") {
      setScore((s) => s + GOLD_BONUS);
    } else if (target.type === "password") {
      setScore((s) => Math.max(0, s - PASSWORD_PENALTY));
    } else {
      setScore((s) => s + 1);
    }

    setActiveTarget(null);
    spawnTimeoutRef.current = setTimeout(spawnTarget, spawnDelayMs(timeLeftRef.current));
  };

  const handleHoleClick = (index: number) => {
    if (phase !== "playing") return;

    if (activeTarget && activeTarget.hole === index) {
      resolveTarget(activeTarget);
      return;
    }

    setScore((s) => Math.max(0, s - MISS_PENALTY));
  };

  useEffect(() => {
    phaseRef.current = phase;
  }, [phase]);

  useEffect(() => () => clearTimers(), [clearTimers]);

  return (
    <div className="pig-game">
      <h2 id="pig-game-title" className="pig-game__title">
        Хрюк-хватай
      </h2>

      {phase === "idle" && (
        <div className="pig-game__start">
          <p className="pig-game__rules">
            Ловите свинок 🐷 (+1), золотых свинок ✨ (+5). Не кликайте по значку пароля 🔒 (−2) и
            мимо пустых лунок (−1). К концу раунда темп ускоряется — держитесь 30 секунд!
          </p>
          <button type="button" className="btn btn--primary btn--large" onClick={startGame}>
            Начать
          </button>
        </div>
      )}

      {phase === "playing" && (
        <>
          <div className="pig-game__hud">
            <span className="pig-game__timer">
              Время: <strong>{timeLeft}</strong> сек
            </span>
            <span className="pig-game__score">
              Счёт: <strong>{score}</strong>
            </span>
          </div>
          <div className="pig-game__board" role="group" aria-label="Игровое поле">
            {Array.from({ length: HOLE_COUNT }, (_, index) => {
              const isActive = activeTarget?.hole === index;
              return (
                <button
                  key={index}
                  type="button"
                  className={holeClassName(index, activeTarget)}
                  onClick={() => handleHoleClick(index)}
                  aria-label={holeAriaLabel(index, activeTarget)}
                >
                  {isActive && activeTarget.type === "pig" && (
                    <span className="pig-game__pig" aria-hidden="true">
                      🐷
                    </span>
                  )}
                  {isActive && activeTarget.type === "gold" && (
                    <span className="pig-game__pig pig-game__pig--gold" aria-hidden="true">
                      🐷
                    </span>
                  )}
                  {isActive && activeTarget.type === "password" && (
                    <span className="pig-game__trap" aria-hidden="true">
                      {PASSWORD_TRAP_ICON}
                    </span>
                  )}
                </button>
              );
            })}
          </div>
        </>
      )}

      {phase === "finished" && (
        <div className="pig-game__result">
          <p className="pig-game__result-score">
            Ваш счёт: <strong>{score}</strong>
          </p>
          <p className="pig-game__result-rank">{getRank(score)}</p>
          <div className="pig-game__result-actions">
            <button type="button" className="btn btn--primary" onClick={startGame}>
              Ещё раз
            </button>
            <button type="button" className="btn btn--outline" onClick={onClose}>
              Закрыть
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
