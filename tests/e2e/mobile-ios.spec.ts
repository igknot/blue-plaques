import { test, expect } from '@playwright/test';

test.describe('Mobile iOS - Icons & Filters', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('.leaflet-container')).toBeVisible();
  });

  test('map marker icons are visible', async ({ page }) => {
    // Wait for markers to load
    await page.waitForSelector('.leaflet-marker-icon', { timeout: 10000 });
    const markers = page.locator('.leaflet-marker-icon');
    const count = await markers.count();
    expect(count).toBeGreaterThan(0);

    // Verify first marker icon actually loaded (has dimensions)
    const firstMarker = markers.first();
    const box = await firstMarker.boundingBox();
    expect(box).not.toBeNull();
    expect(box!.width).toBeGreaterThan(0);
    expect(box!.height).toBeGreaterThan(0);
  });

  test('filter panel opens and shows categories', async ({ page }) => {
    // Open filter panel
    const filterBtn = page.getByLabel('Toggle filters');
    await expect(filterBtn).toBeVisible();
    await filterBtn.click();

    // Verify categories are visible (not just select/clear buttons)
    await expect(page.getByText('Filter by Category')).toBeVisible();
    const categoryItems = page.locator('[class*="flex items-center justify-between p-2"]');
    await expect(categoryItems.first()).toBeVisible({ timeout: 5000 });
    const count = await categoryItems.count();
    expect(count).toBeGreaterThan(0);
  });

  test('filter checkboxes toggle on tap', async ({ page }) => {
    const filterBtn = page.getByLabel('Toggle filters');
    await filterBtn.click();

    // Tap first category
    const firstCategory = page.locator('[class*="flex items-center justify-between p-2"]').first();
    await firstCategory.click();

    // Check that the checkbox visual changed to selected (blue bg)
    const checkbox = firstCategory.locator('span').first();
    await expect(checkbox).toHaveCSS('background-color', 'rgb(37, 99, 235)');
  });

  test('search icon is visible', async ({ page }) => {
    const searchBtn = page.locator('form button[type="submit"]');
    await expect(searchBtn).toBeVisible();
    await expect(searchBtn).not.toBeEmpty();
  });

  test('close filter panel works', async ({ page }) => {
    await page.getByLabel('Toggle filters').click();
    await expect(page.getByText('Filter by Category')).toBeVisible();

    await page.getByLabel('Close filters').click();
    await expect(page.getByText('Filter by Category')).not.toBeVisible();
  });
});
