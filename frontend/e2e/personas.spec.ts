import { test, expect, type Page } from "@playwright/test";

function uniqueEmail(tag: string) {
  return `${tag}_${Date.now()}@example.com`;
}

async function buyTier(page: Page, tierText: string, email: string) {
  await expect(page.locator(".pricing__card").first()).toBeVisible({ timeout: 30000 });
  await page.locator(".pricing__card").filter({ hasText: tierText }).click();
  await page.locator(".checkout__input").fill(email);
  await page.getByRole("button", { name: /Оплатить/i }).click();
  await page.waitForURL(/payment\/success/, { timeout: 30000 });
}

test.describe("Persona: Impatient Grisha", () => {
  test("tries to pay without email", async ({ page }) => {
    await page.goto("/");
    await expect(page.locator(".pricing__card").first()).toBeVisible({ timeout: 30000 });
    await page.locator(".pricing__card").first().click();
    const payBtn = page.getByRole("button", { name: /Оплатить/i });
    await expect(payBtn).toBeDisabled();
  });
});

test.describe("Persona: Careful Maria", () => {
  test("buys svinomat and sees password", async ({ page }) => {
    const email = uniqueEmail("maria");
    await page.goto("/");
    await buyTier(page, "Свиномат", email);
    await expect(page.locator(".generator__password")).toBeVisible({ timeout: 30000 });
    const pwd = await page.locator(".generator__password").textContent();
    expect(pwd?.length).toBe(20);
    await expect(page.locator(".generator__warning")).toBeVisible();
  });
});

test.describe("Persona: Returning Petya", () => {
  test("buys bacon twice with same email", async ({ page }) => {
    const email = uniqueEmail("petya");
    await page.goto("/");
    await buyTier(page, "Бекон", email);
    await expect(page.locator(".generator__password")).toBeVisible({ timeout: 30000 });
    await page.goto("/");
    await buyTier(page, "Бекон", email);
    await expect(page.locator(".generator__password")).toBeVisible({ timeout: 30000 });
  });
});

test.describe("Persona: Chaotic Dasha", () => {
  test("rapid tier switching then buys", async ({ page }) => {
    const email = uniqueEmail("dasha");
    await page.goto("/");
    await expect(page.locator(".pricing__card").first()).toBeVisible({ timeout: 30000 });
    await page.locator(".pricing__card").nth(0).click();
    await page.locator(".pricing__card").nth(1).click();
    await page.locator(".pricing__card").nth(0).click();
    await page.locator(".checkout__input").fill(email);
    await page.getByRole("button", { name: /Оплатить/i }).click();
    await page.waitForURL(/payment\/success/, { timeout: 30000 });
    await expect(page.locator(".generator__password")).toBeVisible({ timeout: 30000 });
  });
});

test.describe("Persona: Premium Oleg", () => {
  test("buys legend and copies password", async ({ page }) => {
    const email = uniqueEmail("oleg");
    await page.goto("/");
    await buyTier(page, "Легенда", email);
    await expect(page.locator(".generator__password")).toBeVisible({ timeout: 30000 });
    const pwd = await page.locator(".generator__password").textContent();
    expect(pwd?.length).toBe(32);
    await page.getByRole("button", { name: /копир/i }).click();
    await expect(page.getByRole("button", { name: /Скопировано/i })).toBeVisible();
  });
});
