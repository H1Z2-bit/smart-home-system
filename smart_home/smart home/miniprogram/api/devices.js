import { request } from '../utils/request.js'

export function listRooms(homeId) {
  return request({ url: `/api/homes/${homeId}/rooms` })
}

export function createRoom(homeId, data) {
  return request({
    url: `/api/homes/${homeId}/rooms`,
    method: 'POST',
    data
  })
}

export function updateRoom(roomId, data) {
  return request({
    url: `/api/rooms/${roomId}`,
    method: 'PUT',
    data
  })
}

export function deleteRoom(roomId) {
  return request({
    url: `/api/rooms/${roomId}`,
    method: 'DELETE'
  })
}

export function listDevices(homeId, roomId) {
  const query = roomId ? `?room_id=${roomId}` : ''
  return request({ url: `/api/homes/${homeId}/devices${query}` })
}

export function getDevice(deviceId) {
  return request({ url: `/api/devices/${deviceId}` })
}

export function createDevice(homeId, data) {
  return request({
    url: `/api/homes/${homeId}/devices`,
    method: 'POST',
    data
  })
}

export function updateDevice(deviceId, data) {
  return request({
    url: `/api/devices/${deviceId}`,
    method: 'PUT',
    data
  })
}

export function deleteDevice(deviceId) {
  return request({
    url: `/api/devices/${deviceId}`,
    method: 'DELETE'
  })
}

export function controlDevice(deviceId, targetState) {
  return request({
    url: `/api/devices/${deviceId}/control`,
    method: 'POST',
    data: {
      action: 'switch',
      target_state: targetState
    }
  })
}
