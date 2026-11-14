import { test, expect } from '@playwright/test';

/**
 * EXP-01 Comparative: Dynamic DOM & Asynchronous Rendering.
 * Investigates Playwright locator auto-waiting vs Selenium explicit condition polling.
 */
test.describe('EXP-01 Comparative: Dynamic DOM', () => {
  test('Playwright auto-waiting on dynamically injected element', async ({ page }) => {
    await page.goto('/scenarios/dynamic-render?delay_ms=800');

    const triggerBtn = page.locator('#trigger-btn');
    const targetElement = page.locator('#target-element');

    await triggerBtn.click();

    // Playwright web-first assertion automatically retries until condition is met
    const startTime = Date.now();
    await expect(targetElement).toBeVisible({ timeout: 5000 });
    const elapsed = Date.now() - startTime;

    await expect(targetElement).toHaveText('Target Loaded Successfully!');
    expect(elapsed).toBeGreaterThanOrEqual(700);
    expect(elapsed).toBeLessThan(3000);
  });

  test('Public App: Dynamic Loading absent DOM element auto-waiting', async ({ page }) => {
    await page.goto('https://the-internet.herokuapp.com/dynamic_loading/2');

    const startBtn = page.getByRole('button', { name: 'Start' });
    const finishText = page.locator('#finish h4');

    await startBtn.click();

    // Playwright auto-waits for element insertion and visibility
    await expect(finishText).toBeVisible({ timeout: 10000 });
    await expect(finishText).toHaveText('Hello World!');
  });
});
