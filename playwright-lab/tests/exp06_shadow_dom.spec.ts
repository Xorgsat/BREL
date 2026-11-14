import { test, expect } from '@playwright/test';

/**
 * EXP-06 Comparative: Shadow DOM Traversal.
 * Demonstrates Playwright's default shadow-piercing CSS selector engine
 * compared to Selenium's explicit shadow_root access.
 */
test.describe('EXP-06 Comparative: Shadow DOM', () => {
  test('Playwright CSS locators pierce open shadow roots transparently', async ({ page }) => {
    await page.goto('/scenarios/shadow-dom');

    // In Playwright, standard CSS selectors automatically pierce open shadow roots!
    const shadowText = page.locator('#shadow-content');
    await expect(shadowText).toBeVisible();
    await expect(shadowText).toHaveText('Inside Open Shadow Root');

    const shadowBtn = page.locator('#shadow-btn');
    await expect(shadowBtn).toBeVisible();
  });

  test('Public App: UITAP Shadow DOM piercing without manual root navigation', async ({ page }) => {
    await page.goto('https://uitestingplayground.com/shadowdom');

    // Pierces guid-generator shadow root directly
    const generateBtn = page.locator('button#buttonGenerate');
    await generateBtn.click();

    const editField = page.locator('input#editField');
    await expect(editField).not.toHaveValue('');
  });
});
