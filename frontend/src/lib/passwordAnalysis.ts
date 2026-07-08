const AMBIGUOUS = new Set("0OIl1|");
const LOWER = "abcdefghijklmnopqrstuvwxyz".split("").filter((c) => !AMBIGUOUS.has(c)).join("");
const UPPER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("").filter((c) => !AMBIGUOUS.has(c)).join("");
const DIGITS = "23456789";
const SYMBOLS = "!@#$%^&*-_=+?";
const FULL = LOWER + UPPER + DIGITS + SYMBOLS;

const WEAK_PATTERNS: { pattern: RegExp; message: string }[] = [
  { pattern: /12345|123456|1234567|12345678/, message: "Последовательность цифр (123…)" },
  { pattern: /qwerty|asdfgh|zxcvbn/i, message: "Раскладка клавиатуры (qwerty и т.п.)" },
  { pattern: /password|пароль|passw0rd|admin|letmein|welcome|login/i, message: "Типичное слово из словаря атак" },
  { pattern: /20(1\d|2[0-6])/, message: "Год в пароле (легко подобрать)" },
  { pattern: /(.)\1{2,}/, message: "Повторяющиеся символы подряд" },
];

export type HealthScore = "weak" | "fair" | "strong" | "legend";

export type HealthResult = {
  score: HealthScore;
  entropyBits: number;
  length: number;
  hasLower: boolean;
  hasUpper: boolean;
  hasDigit: boolean;
  hasSymbol: boolean;
  warnings: string[];
  breachCount: number | null;
  breachCheckFailed: boolean;
};

export function estimateEntropyBits(password: string): number {
  let pool = 0;
  if ([...password].some((c) => LOWER.includes(c))) pool += LOWER.length;
  if ([...password].some((c) => UPPER.includes(c))) pool += UPPER.length;
  if ([...password].some((c) => DIGITS.includes(c))) pool += DIGITS.length;
  if ([...password].some((c) => SYMBOLS.includes(c))) pool += SYMBOLS.length;
  if (pool <= 1) pool = FULL.length;
  return Math.round(password.length * Math.log2(pool) * 10) / 10;
}

function collectWarnings(password: string): string[] {
  const warnings: string[] = [];
  if (password.length < 8) warnings.push("Слишком короткий — меньше 8 символов");
  if (password.length < 12) warnings.push("Рекомендуем минимум 12 символов для важных аккаунтов");
  if (![...password].some((c) => LOWER.includes(c))) warnings.push("Нет строчных букв");
  if (![...password].some((c) => UPPER.includes(c))) warnings.push("Нет заглавных букв");
  if (![...password].some((c) => DIGITS.includes(c))) warnings.push("Нет цифр");
  if (![...password].some((c) => SYMBOLS.includes(c))) warnings.push("Нет спецсимволов");
  for (const { pattern, message } of WEAK_PATTERNS) {
    if (pattern.test(password) && !warnings.includes(message)) warnings.push(message);
  }
  return warnings;
}

function scoreFromMetrics(entropyBits: number, length: number, warnings: string[]): HealthScore {
  if (length < 8 || entropyBits < 28 || warnings.length >= 4) return "weak";
  if (entropyBits < 50 || length < 12) return "fair";
  if (entropyBits < 72) return "strong";
  return "legend";
}

export function analyzePassword(password: string): Omit<HealthResult, "breachCount" | "breachCheckFailed"> {
  const entropyBits = estimateEntropyBits(password);
  const warnings = collectWarnings(password);
  return {
    score: scoreFromMetrics(entropyBits, password.length, warnings),
    entropyBits,
    length: password.length,
    hasLower: [...password].some((c) => LOWER.includes(c)),
    hasUpper: [...password].some((c) => UPPER.includes(c)),
    hasDigit: [...password].some((c) => DIGITS.includes(c)),
    hasSymbol: [...password].some((c) => SYMBOLS.includes(c)),
    warnings,
  };
}

async function sha1HexUpper(text: string): Promise<string> {
  const data = new TextEncoder().encode(text);
  const hash = await crypto.subtle.digest("SHA-1", data);
  return [...new Uint8Array(hash)].map((b) => b.toString(16).padStart(2, "0")).join("").toUpperCase();
}

export async function checkBreachCount(password: string): Promise<{ count: number | null; failed: boolean }> {
  if (!password) return { count: null, failed: false };
  try {
    const hash = await sha1HexUpper(password);
    const prefix = hash.slice(0, 5);
    const suffix = hash.slice(5);
    const response = await fetch(`https://api.pwnedpasswords.com/range/${prefix}`, {
      headers: { "Add-Padding": "true" },
    });
    if (!response.ok) return { count: null, failed: true };
    const body = await response.text();
    for (const line of body.split("\n")) {
      const [lineSuffix, countStr] = line.trim().split(":");
      if (lineSuffix === suffix) return { count: parseInt(countStr, 10), failed: false };
    }
    return { count: 0, failed: false };
  } catch {
    return { count: null, failed: true };
  }
}

export async function analyzePasswordFull(password: string): Promise<HealthResult> {
  const base = analyzePassword(password);
  const { count, failed } = await checkBreachCount(password);
  return { ...base, breachCount: count, breachCheckFailed: failed };
}

export const SCORE_LABELS: Record<HealthScore, string> = {
  weak: "Слабый",
  fair: "Норм",
  strong: "Крепкий",
  legend: "Легенда хлева",
};
