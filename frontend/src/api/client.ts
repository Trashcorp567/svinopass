export interface Tier {
  id: string;
  name: string;
  price: number;
  price_label: string;
  description: string;
  length: number;
  features: string[];
}

export interface OrderResult {
  order_id: string;
  tier: string;
  tier_name: string;
  password: string;
  entropy_bits: number;
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

export function createCheckout(tier: string, email: string): Promise<CheckoutResult> {
  return request<CheckoutResult>("/api/checkout", {
    method: "POST",
    body: JSON.stringify({ tier, email }),
  });
}

export async function fetchOrderResult(
  orderId: string,
): Promise<OrderResult | OrderPending> {
  const response = await fetch(`/api/orders/${orderId}/result`);
  if (response.status === 410) {
    throw new Error("Password already shown. Check your email.");
  }
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    const detail = body.detail;
    throw new Error(typeof detail === "string" ? detail : `HTTP ${response.status}`);
  }
  return response.json();
}
