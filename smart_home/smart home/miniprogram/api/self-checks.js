import { request } from '../utils/request.js'

export function startSelfCheck(deviceId) {
  return request({
    url: `/api/devices/${deviceId}/self-check`,
    method: 'POST'
  })
}

export function listSelfChecks(deviceId) {
  return request({ url: `/api/devices/${deviceId}/self-checks` })
}
