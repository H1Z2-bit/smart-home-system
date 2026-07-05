import { request } from '../utils/request.js'

export function loginByPassword(phone, password) {
  return request({
    url: '/api/auth/login',
    method: 'POST',
    data: { phone, password }
  })
}

export function sendLoginSmsCode(phone) {
  return request({
    url: '/api/auth/sms/send',
    method: 'POST',
    data: { phone, scene: 'login' }
  })
}

export function loginBySms(phone, code) {
  return request({
    url: '/api/auth/sms/login',
    method: 'POST',
    data: { phone, code }
  })
}

export function getProfile() {
  return request({ url: '/api/users/profile' })
}

export function sendBindPhoneCode(phone) {
  return request({
    url: '/api/users/phone/code',
    method: 'POST',
    data: { phone, scene: 'bind' }
  })
}

export function bindPhone(phone, code) {
  return request({
    url: '/api/users/phone/bind',
    method: 'POST',
    data: { phone, code }
  })
}

export function logout() {
  return request({
    url: '/api/auth/logout',
    method: 'POST',
    showError: false
  })
}
