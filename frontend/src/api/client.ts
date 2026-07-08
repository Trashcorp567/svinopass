export interface Tier {
  id: string;
  name: string;
  price: number;
  price_label: string;
  description: string;
  length: number;
  features: string[];
  product_type?: "password" | "backup_codes" | "watch" | "creative";
}

export interface CreativeCategory {
  id: string;
  label: string;
  description: string;
  requires_seeds: boolean;
  optional_seeds: boolean;
}

export interface BreachSummary {
  name: string;
  title: string;
  domain: string;
  breach_date: string;
  pwn_count?: number | null;
}

export interface OrderResult {
  order_id: string;
  tier: string;
  tier_name: string;
  product_type?: "password" | "backup_codes" | "watch" | "creative";
  password?: string | null;
  backup_codes?: string[] | null;
  entropy_bits?: number | null;
  monitored_email?: string | null;
  expires_at?: string | null;
  breach_count?: number | null;
  breaches?: BreachSummary[] | null;
  creative_items?: string[] | null;
  creative_bios?: string[] | null;
  creative_category?: string | null;
  creative_kind?: string | null;
  creative_source?: string | null;
  email_sent: boolean;
  paid_at: string | null;
  warning: string;
}

export interface CheckoutResult {
  order_id: string;
  confirmation_url: string;
}

export interface OrderPending {
  status: "pending";
  order_id: string;
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options?.headers as Record<string, string> | undefined),
    },
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    const detail = body.detail;
    const message = typeof detail === "string" ? detail : `HTTP ${response.status}`;
    throw new Error(message);
  }
  return response.json();
}

export function fetchTiers(): Promise<Tier[]> {
  return request<Tier[]>("/api/tiers");
}

export type GenerationMode = "random" | "passphrase";

export function createCheckout(
  tier: string,
  email: string,
  mode: GenerationMode = "random",
): Promise<CheckoutResult> {
  return request<CheckoutResult>("/api/checkout", {
    method: "POST",
    body: JSON.stringify({ tier, email, mode }),
  });
}

export function fetchCreativeCategories(): Promise<CreativeCategory[]> {
  return request<CreativeCategory[]>("/api/creative/categories");
}

export function createCreativeCheckout(
  tier: string,
  email: string,
  category: string,
  seedWords: string[],
): Promise<CheckoutResult> {
  return request<CheckoutResult>("/api/checkout", {
    method: "POST",
    body: JSON.stringify({
      tier,
      email,
      category,
      seed_words: seedWords,
    }),
  });
}

export function previewWatchEmail(email: string): Promise<{
  email: string;
  breach_count: number;
  breaches: BreachSummary[];
}> {
  return request("/api/watch/preview", {
    method: "POST",
    body: JSON.stringify({ email }),
  });
}

export async function fetchOrderResult(
  orderId: string,
): Promise<OrderResult | OrderPending> {
  const response = await fetch(`/api/orders/${orderId}/result`);
  if (response.status === 410) {
    throw new Error("Result already shown. Check your email.");
  }
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    const detail = body.detail;
    throw new Error(typeof detail === "string" ? detail : `HTTP ${response.status}`);
  }
  return response.json();
}
