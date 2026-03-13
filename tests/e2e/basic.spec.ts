import { test, expect } from '@playwright/test';

test.describe('Blue Plaques Map', () => {
  test('should load the homepage', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/Blue Plaques/);
  });

  test('should display map', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('.leaflet-container')).toBeVisible();
  });

  test('should search plaques', async ({ page }) => {
    await page.goto('/');
    await page.fill('input[type="search"]', 'Nelson Mandela');
    await page.waitForTimeout(500);
    // Add assertions based on your search results
  });
});
