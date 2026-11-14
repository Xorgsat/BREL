import { test, expect } from '@playwright/test';

/**
 * EXP-02 Comparative: Synchronization and Auto-waiting.
 * Demonstrates that Playwright performs actionability checks (visible, stable, enabled)
 * before dispatching click events without manual polling logic.
 */
test.describe('EXP-02 Comparative: Auto-waiting and Web-first Assertions', () => {
  test('Auto-wait on delayed actionability in dynamic controls', async ({ page }) => {
    await page.goto('https://the-internet.herokuapp.com/dynamic_controls');

    const input = page.locator('#input-example input');
    const enableBtn = page.getByRole('button', { name: 'Enable' });

    await expect(input).toBeDisabled();
    await enableBtn.click();

    // In Playwright, fill() automatically waits for input to become enabled
    await input.fill('Playwright Auto-Wait In Action', { timeout: 10000 });
    await expect(input).toHaveValue('Playwright Auto-Wait In Action');
  });
});
