import { getBaseUrl } from '../config/index.js'

export function request(options) {
  const token = uni.getStorageSync('token')
  const baseUrl = getBaseUrl()

  return new Promise((resolve, reject) => {
    uni.request({
      url: baseUrl + options.url,
      method: options.method || 'GET',
      data: options.data || {},
      header: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: 'Bearer ' + token } : {}),
        ...(options.header || {})
      },
      success(res) {
        const body = res.data || {}
        if (res.statusCode === 200 && body.code === 200) {
          resolve(body.data)
          return
        }

        if (res.statusCode === 401 || body.code === 401) {
          uni.removeStorageSync('token')
          uni.removeStorageSync('user')
          uni.showToast({ title: '登录已失效', icon: 'none' })
          setTimeout(() => {
            uni.reLaunch({ url: '/pages/login/login' })
          }, 500)
        } else if (options.showError !== false) {
          uni.showToast({
            title: body.message || '请求失败',
            icon: 'none'
          })
        }
        reject(body)
      },
      fail(err) {
        if (options.showError !== false) {
          uni.showToast({
            title: '无法连接后端',
            icon: 'none'
          })
        }
        reject(err)
      }
    })
  })
}
