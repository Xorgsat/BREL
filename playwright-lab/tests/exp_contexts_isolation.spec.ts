import { test, expect } from '@playwright/test';

/**
 * Comparative Isolation Benchmark:
 * Measures the creation duration of ephemeral BrowserContext instances
 * vs WebDriver full process initialization.
 */
test.describe('Comparative Architecture: Browser Context Isolation', () => {
  test('BrowserContext ephemeral isolation speed benchmark', async ({ browser }) => {
    const iterations = 5;
    const durations: number[] = [];

    for (let i = 0; i < iterations; i++) {
      const startTime = Date.now();
      const context = await browser.newContext();
      const page = await context.newPage();
      await page.goto('/api/health');
      const elapsed = Date.now() - startTime;
      durations.push(elapsed);

      await expect(page.locator('body')).toContainText('"status":"ok"');
      await context.close();
    }

    const averageDuration = durations.reduce((a, b) => a + b, 0) / durations.length;
    console.log(`Average BrowserContext creation + navigation time: ${averageDuration.toFixed(1)}ms`);

    // BrowserContext creation is typically an order of magnitude faster than full WebDriver process startup
    expect(averageDuration).toBeLessThan(1000);
  });
});
