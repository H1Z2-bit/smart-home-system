import { request } from '../utils/request.js'

export function createDeviceSimulation(deviceId, data) {
  return request({
    url: `/api/devices/${deviceId}/simulate`,
    method: 'POST',
    data
  })
}

export function listDeviceSimulations(deviceId) {
  return request({ url: `/api/devices/${deviceId}/simulations` })
}
