import { request } from '../utils/request.js'

export function getSystemConfig(homeId) {
  return request({ url: `/api/homes/${homeId}/system/config` })
}

export function updateSystemConfig(homeId, data) {
  return request({
    url: `/api/homes/${homeId}/system/config`,
    method: 'PUT',
    data
  })
}

export function listSystemLogs(homeId) {
  return request({ url: `/api/homes/${homeId}/system/logs` })
}

export function listOperationLogs(homeId) {
  return request({ url: `/api/homes/${homeId}/logs` })
}

export function resetMockData() {
  return request({
    url: '/api/debug/reset',
    method: 'POST'
  })
}
