import { request } from '../utils/request.js'

export function listHomes() {
  return request({ url: '/api/homes' })
}
