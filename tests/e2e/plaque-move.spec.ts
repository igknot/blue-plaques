import { test, expect, Page } from '@playwright/test';

const TEST_MARKER_TITLE = 'E2E Test Marker';
const ORIGINAL_LAT = -26.2041;
const ORIGINAL_LNG = 28.0473;
const API_URL = process.env.E2E_API_URL || 'http://localhost:8000/api/v1';

async function loginAndGetToken(): Promise<string> {
  const email = process.env.E2E_ADMIN_EMAIL;
  const password = process.env.E2E_ADMIN_PASSWORD;
  if (!email || !password) throw new Error('Set E2E_ADMIN_EMAIL and E2E_ADMIN_PASSWORD env vars');
  const res = await fetch(`${API_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) throw new Error(`Login failed: ${res.status}`);
  const { access_token } = await res.json();
  return access_token;
}

async function resetTestMarker(token: string) {
  await fetch(`${API_URL}/plaques/389`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
    body: JSON.stringify({ latitude: ORIGINAL_LAT, longitude: ORIGINAL_LNG }),
  });
}

async function setupAuthenticatedPage(page: Page, token: string) {
  await page.addInitScript((t) => localStorage.setItem('token', t), token);
}

async function searchForTestMarker(page: Page) {
  await page.fill('input[type="search"]', TEST_MARKER_TITLE);
  await page.waitForTimeout(600);
  await page.waitForSelector('.leaflet-marker-icon');
}

test.describe('Plaque Location Correction (Admin)', () => {
  let token: string;

  test.beforeAll(async () => {
    token = await loginAndGetToken();
  });

  test.afterEach(async () => {
    await resetTestMarker(token);
  });

  test('drag marker shows confirmation and saves on confirm', async ({ page }) => {
    await setupAuthenticatedPage(page, token);
    await page.goto('/');
    await searchForTestMarker(page);

    const marker = page.locator('.leaflet-marker-icon').first();
    const box = (await marker.boundingBox())!;
    const cx = box.x + box.width / 2;
    const cy = box.y + box.height / 2;

    await page.mouse.move(cx, cy);
    await page.mouse.down();
    await page.mouse.move(cx + 80, cy + 60, { steps: 10 });
    await page.mouse.up();

    await expect(page.getByText('Move Plaque?')).toBeVisible();
    await expect(page.getByText(`"${TEST_MARKER_TITLE}"`)).toBeVisible();

    const updatePromise = page.waitForRequest(
      (req) => req.url().includes('/plaques/389') && req.method() === 'PUT'
    );
    await page.getByRole('button', { name: 'Confirm' }).click();

    const req = await updatePromise;
    const body = req.postDataJSON();
    expect(body.latitude).toBeDefined();
    expect(body.longitude).toBeDefined();
    expect(body.latitude).not.toBe(ORIGINAL_LAT);

    await expect(page.getByText('Move Plaque?')).not.toBeVisible();
  });

  test('drag marker cancel reverts position and does not save', async ({ page }) => {
    await setupAuthenticatedPage(page, token);
    await page.goto('/');
    await searchForTestMarker(page);

    const marker = page.locator('.leaflet-marker-icon').first();
    const box = (await marker.boundingBox())!;
    const cx = box.x + box.width / 2;
    const cy = box.y + box.height / 2;

    await page.mouse.move(cx, cy);
    await page.mouse.down();
    await page.mouse.move(cx + 80, cy + 60, { steps: 10 });
    await page.mouse.up();

    await expect(page.getByText('Move Plaque?')).toBeVisible();

    let apiCalled = false;
    page.on('request', (req) => {
      if (req.url().includes('/plaques/389') && req.method() === 'PUT') apiCalled = true;
    });

    await page.getByRole('button', { name: 'Cancel' }).click();

    await expect(page.getByText('Move Plaque?')).not.toBeVisible();
    expect(apiCalled).toBe(false);
  });

  test('Move Here moves plaque to user location with confirmation', async ({ context, page }) => {
    const fakeLocation = { latitude: -26.21, longitude: 28.05 };
    await context.grantPermissions(['geolocation']);
    await context.setGeolocation(fakeLocation);

    await setupAuthenticatedPage(page, token);
    await page.goto('/');
    await searchForTestMarker(page);

    const marker = page.locator('.leaflet-marker-icon').first();
    await marker.click();
    await expect(page.locator('.leaflet-popup')).toBeVisible();

    await page.getByText('Move Here ↗').click();

    await expect(page.getByText('Move Plaque?')).toBeVisible();
    await expect(page.getByText(new RegExp(fakeLocation.latitude.toFixed(6)))).toBeVisible();

    const updatePromise = page.waitForRequest(
      (req) => req.url().includes('/plaques/389') && req.method() === 'PUT'
    );
    await page.getByRole('button', { name: 'Confirm' }).click();

    const req = await updatePromise;
    const body = req.postDataJSON();
    expect(body.latitude).toBeCloseTo(fakeLocation.latitude, 2);
    expect(body.longitude).toBeCloseTo(fakeLocation.longitude, 2);
  });

  test('Move Here is hidden without geolocation', async ({ page }) => {
    await setupAuthenticatedPage(page, token);
    // Block geolocation
    await page.addInitScript(() => {
      navigator.geolocation.watchPosition = (_s, err) => { err?.({ code: 1, message: 'denied', PERMISSION_DENIED: 1, POSITION_UNAVAILABLE: 2, TIMEOUT: 3 } as GeolocationPositionError); return 0; };
    });
    await page.goto('/');
    await searchForTestMarker(page);

    const marker = page.locator('.leaflet-marker-icon').first();
    await marker.click();
    await expect(page.locator('.leaflet-popup')).toBeVisible();
    await expect(page.getByText('Move Here ↗')).not.toBeVisible();
  });

  test('markers are not draggable for unauthenticated users', async ({ page }) => {
    await page.goto('/');
    await searchForTestMarker(page);

    const marker = page.locator('.leaflet-marker-icon').first();
    const draggable = await marker.evaluate((el) =>
      el.classList.contains('leaflet-marker-draggable')
    );
    expect(draggable).toBe(false);
  });
});
