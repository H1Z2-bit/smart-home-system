export const BASE_URL = 'http://10.126.19.85:8000'

export function getBaseUrl() {
  return uni.getStorageSync('baseUrl') || BASE_URL
}

export function setBaseUrl(url) {
  const value = String(url || '').trim().replace(/\/$/, '')
  if (!value) {
    uni.removeStorageSync('baseUrl')
    return BASE_URL
  }
  uni.setStorageSync('baseUrl', value)
  return value
}
