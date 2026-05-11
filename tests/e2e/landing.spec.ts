import { test, expect } from '@playwright/test';

test.describe('Landing page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('renders hero section', async ({ page }) => {
    await expect(page.locator('.hero h1')).toBeVisible();
    await expect(page.locator('.hero-subtitle')).toBeVisible();
    await expect(page.locator('.hero-actions .cta-btn').first()).toBeVisible();
  });

  test('Lucide SVG icons render in feature cards', async ({ page }) => {
    const icons = page.locator('.feature-card .feature-icon svg');
    await expect(icons).toHaveCount(6);
    for (const icon of await icons.all()) {
      await expect(icon).toBeVisible();
    }
  });

  test('feature cards visible after scroll', async ({ page }) => {
    await page.locator('.features-grid').scrollIntoViewIfNeeded();
    const cards = page.locator('.feature-card');
    await expect(cards).toHaveCount(6);
    await expect(cards.first()).toBeVisible();
  });

  test('navbar brand link present', async ({ page }) => {
    const brand = page.locator('.navbar-brand');
    await expect(brand).toHaveText('SECURO');
    await expect(brand).toHaveAttribute('href', '/');
  });

  test('steps section has 4 step cards', async ({ page }) => {
    await page.locator('.steps-grid').scrollIntoViewIfNeeded();
    await expect(page.locator('.step-card')).toHaveCount(4);
  });

  test('no console errors on load', async ({ page }) => {
    const errors: string[] = [];
    page.on('console', msg => {
      if (msg.type() === 'error') errors.push(msg.text());
    });
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    expect(errors).toHaveLength(0);
  });

  test('GSAP animations do not break layout', async ({ page }) => {
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1500);
    const subtitle = page.locator('.hero-subtitle');
    await expect(subtitle).toBeVisible();
    const box = await subtitle.boundingBox();
    expect(box?.width).toBeGreaterThan(0);
    expect(box?.height).toBeGreaterThan(0);
  });
});
