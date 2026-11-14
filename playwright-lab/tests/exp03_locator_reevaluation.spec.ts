import { test, expect } from '@playwright/test';

/**
 * EXP-03 Comparative: Stale Element Reference Immunity.
 * Demonstrates the architectural difference between Selenium WebElement pointers
 * and Playwright's lazy re-evaluating Locators.
 */
test.describe('EXP-03 Comparative: Locator Re-evaluation vs Stale References', () => {
  test('Playwright locator remains valid across DOM node replacement', async ({ page }) => {
    await page.goto('/scenarios/stale-dom?recycle_ms=300');

    // Create a locator definition
    const victimLocator = page.locator('#victim-element');
    await expect(victimLocator).toBeVisible();

    // Trigger DOM replacement
    await victimLocator.click();

    // In Selenium, using the old reference throws StaleElementReferenceException.
    // In Playwright, the locator definition automatically re-queries the DOM!
    await expect(victimLocator).toHaveText('Recycled Button Node', { timeout: 5000 });
    await expect(victimLocator).toHaveClass(/recycled/);
  });
});
