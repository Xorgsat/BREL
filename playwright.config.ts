import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './playwright-lab/tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  workers: 2,
  reporter: [
    ['list'],
    ['json', { outputFile: 'reports/playwright-results.json' }],
    ['html', { outputFolder: 'reports/playwright-report', open: 'never' }],
  ],
  use: {
    baseURL: process.env.CONTROLLED_APP_URL || 'http://127.0.0.1:8000',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    ignoreHTTPSErrors: true,
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  webServer: {
    command: '.venv/bin/python -m uvicorn controlled_app.app.main:app --host 127.0.0.1 --port 8000',
    port: 8000,
    reuseExistingServer: true,
    timeout: 10000,
  },
});
