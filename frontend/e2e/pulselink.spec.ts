import { expect, test } from '@playwright/test'

test('creates a link through the frontend and verifies the persisted redirect', async ({ page, request }) => {
  const alias = `e2e-${Date.now()}`
  await page.goto('/')
  await page.getByLabel('Destination URL').fill('https://example.com/end-to-end')
  await page.getByLabel('Custom alias').fill(alias)
  await page.getByRole('button', { name: /shorten url/i }).click()

  const shortLink = page.getByRole('link', { name: new RegExp(alias) })
  await expect(shortLink).toBeVisible()

  const apiResponse = await request.get(`http://127.0.0.1:8000/api/urls`, { headers: { 'X-User-ID': 'demo-user' } })
  expect(apiResponse.ok()).toBeTruthy()
  const urls = await apiResponse.json()
  expect(urls.some((url: { short_code: string; original_url: string }) => url.short_code === alias && url.original_url === 'https://example.com/end-to-end')).toBeTruthy()

  const redirect = await request.get(`http://127.0.0.1:8000/${alias}`, { maxRedirects: 0 })
  expect(redirect.status()).toBe(302)
  expect(redirect.headers()['location']).toBe('https://example.com/end-to-end')
})
