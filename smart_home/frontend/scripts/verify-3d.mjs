import { mkdir } from 'node:fs/promises'
import { fileURLToPath } from 'node:url'
import { chromium } from 'playwright'

const edgePath = 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'
const url = process.env.VIS_URL || 'http://127.0.0.1:5173/'
const outDir = new URL('../test-results/', import.meta.url)

async function inspectPage(page, name) {
  await page.goto(url, { waitUntil: 'networkidle' })
  await page.waitForSelector('canvas')
  await page.waitForTimeout(800)
  const screenshotPath = fileURLToPath(new URL(name + '.png', outDir))
  await page.screenshot({ path: screenshotPath, fullPage: true })
  const stats = await page.evaluate(() => {
    const canvas = document.querySelector('canvas')
    if (!canvas) return { ok: false, reason: 'missing canvas' }
    const sample = document.createElement('canvas')
    sample.width = 96
    sample.height = 96
    const ctx = sample.getContext('2d', { willReadFrequently: true })
    if (!ctx) return { ok: false, reason: 'missing 2d context' }
    ctx.drawImage(canvas, 0, 0, sample.width, sample.height)
    const pixels = ctx.getImageData(0, 0, sample.width, sample.height).data
    const colors = new Set()
    let nonTransparent = 0
    let nonWhite = 0
    for (let i = 0; i < pixels.length; i += 4) {
      const r = pixels[i]
      const g = pixels[i + 1]
      const b = pixels[i + 2]
      const a = pixels[i + 3]
      if (a > 0) nonTransparent += 1
      if (!(r > 238 && g > 238 && b > 238)) nonWhite += 1
      if (i % 16 === 0) colors.add(r + ',' + g + ',' + b + ',' + a)
    }
    return {
      ok: nonTransparent > 2000 && nonWhite > 600 && colors.size > 20,
      width: canvas.width,
      height: canvas.height,
      nonTransparent,
      nonWhite,
      colors: colors.size,
    }
  })
  if (!stats.ok) {
    throw new Error(name + ' canvas check failed: ' + JSON.stringify(stats))
  }
  console.log('[OK] ' + name, stats)
}

await mkdir(outDir, { recursive: true })
const browser = await chromium.launch({ executablePath: edgePath, headless: true })
try {
  const desktop = await browser.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 })
  await inspectPage(desktop, 'desktop-3d')
  await desktop.close()

  const mobile = await browser.newPage({ viewport: { width: 390, height: 844 }, isMobile: true, deviceScaleFactor: 2 })
  await inspectPage(mobile, 'mobile-3d')
  await mobile.close()
} finally {
  await browser.close()
}