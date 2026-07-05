import { request } from '../utils/request.js'

export function listSchedules(homeId) {
  return request({ url: `/api/homes/${homeId}/schedules` })
}

export function createSchedule(homeId, data) {
  return request({
    url: `/api/homes/${homeId}/schedules`,
    method: 'POST',
    data
  })
}

export function updateSchedule(taskId, data) {
  return request({
    url: `/api/schedules/${taskId}`,
    method: 'PUT',
    data
  })
}

export function updateScheduleStatus(taskId, status) {
  return request({
    url: `/api/schedules/${taskId}/status`,
    method: 'PUT',
    data: { status }
  })
}

export function deleteSchedule(taskId) {
  return request({
    url: `/api/schedules/${taskId}`,
    method: 'DELETE'
  })
}
