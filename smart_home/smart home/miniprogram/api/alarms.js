import { request } from '../utils/request.js'

export function listAlarms(homeId) {
  return request({ url: `/api/homes/${homeId}/alarms` })
}

export function confirmAlarm(alarmId) {
  return request({
    url: `/api/alarms/${alarmId}/confirm`,
    method: 'POST',
    data: { process_desc: '小程序端确认报警', process_result: 'confirmed' }
  })
}

export function processAlarm(alarmId) {
  return request({
    url: `/api/alarms/${alarmId}/process`,
    method: 'POST',
    data: { process_desc: '小程序端处理报警', process_result: 'processing' }
  })
}

export function resolveAlarm(alarmId) {
  return request({
    url: `/api/alarms/${alarmId}/resolve`,
    method: 'POST',
    data: { process_desc: '小程序端关闭报警', process_result: 'resolved' }
  })
}

export function markFalseAlarm(alarmId) {
  return request({
    url: `/api/alarms/${alarmId}/false-alarm`,
    method: 'POST',
    data: { process_desc: '小程序端标记误报', process_result: 'false_alarm' }
  })
}
