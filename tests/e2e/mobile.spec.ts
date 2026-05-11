import { test, expect } from '@playwright/test';

test.use({
  viewport: { width: 375, height: 812 },
  userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
});

test.describe('Mobile 375px', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('hero stacks vertically — no horizontal scroll', async ({ page }) => {
    const scrollWidth = await page.evaluate(() => document.documentElement.scrollWidth);
    const clientWidth = await page.evaluate(() => document.documentElement.clientWidth);
    expect(scrollWidth).toBeLessThanOrEqual(clientWidth + 2);
  });

  test('hero-inner is single column on mobile', async ({ page }) => {
    const heroInner = page.locator('.hero-inner');
    const box = await heroInner.boundingBox();
    const viewport = page.viewportSize();
    expect(box!.width).toBeLessThanOrEqual(viewport!.width);
  });

  test('CTA buttons are visible and tappable', async ({ page }) => {
    const btn = page.locator('.hero-actions .cta-btn').first();
    await expect(btn).toBeVisible();
    const box = await btn.boundingBox();
    expect(box!.height).toBeGreaterThanOrEqual(44);
  });

  test('feature cards visible on scroll', async ({ page }) => {
    await page.locator('.features-grid').scrollIntoViewIfNeeded();
    await expect(page.locator('.feature-card').first()).toBeVisible();
  });

  test('terminal visible on mobile', async ({ page }) => {
    const terminal = page.locator('.hero-terminal');
    await expect(terminal).toBeVisible();
  });
});
