import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  timeout: 90000,
  retries: 0,
  use: {
    baseURL: "http://localhost:5173",
    trace: "on-first-retry",
    screenshot: "only-on-failure",
  },
  projects: [{
    name: "chromium",
    use: {
      ...devices["Desktop Chrome"],
      permissions: ["clipboard-read", "clipboard-write"],
    },
  }],
  webServer: [
    {
      command: "cd ../backend && .venv\\Scripts\\uvicorn app.main:app --port 8000",
      url: "http://127.0.0.1:8000/api/health",
      reuseExistingServer: false,
      timeout: 120000,
      env: {
        YOOKASSA_MOCK: "true",
        REDIS_URL: "redis://localhost:6379/0",
        DATABASE_URL: "postgresql://svinopass:svinopass@localhost:5432/svinopass",
      },
    },
    {
      command: "npm run dev",
      url: "http://localhost:5173",
      reuseExistingServer: false,
      timeout: 120000,
    },
  ],
});
