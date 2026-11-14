import { test, expect } from '@playwright/test';

/**
 * EXP-04 Comparative: Actionability Checks & Interception.
 * Demonstrates Playwright's built-in actionability verification
 * and contrasts normal vs forced interaction.
 */
test.describe('EXP-04 Comparative: Actionability & Overlays', () => {
  test('Playwright auto-waits for overlay to disappear before clicking', async ({ page }) => {
    await page.goto('/scenarios/click-interception?overlay_ms=1200');

    const targetBtn = page.locator('#target-action-btn');
    const feedback = page.locator('#click-feedback');

    // Playwright automatically waits for #blocking-overlay to detach before dispatching click
    await targetBtn.click({ timeout: 5000 });
    await expect(feedback).toHaveText('Action Button Successfully Clicked!');
  });

  test('Diagnostic contrast: force click vs DOM evaluate click', async ({ page }) => {
    await page.goto('/scenarios/click-interception?overlay_ms=4000');

    const targetBtn = page.locator('#target-action-btn');
    const feedback = page.locator('#click-feedback');

    // Force click bypasses Playwright actionability checks, but dispatches mouse event at coordinates.
    // Because the overlay is physically in front, the overlay absorbs the pointer event!
    await targetBtn.click({ force: true });
    await expect(feedback).toHaveText('Awaiting Click');

    // In contrast, direct DOM evaluate click bypasses physical coordinate hit-testing completely:
    await targetBtn.evaluate((el: HTMLElement) => el.click());
    await expect(feedback).toHaveText('Action Button Successfully Clicked!');
  });
});
