import { request } from '../utils/request.js'

export function listLinkages(homeId) {
  return request({ url: `/api/homes/${homeId}/linkages` })
}

export function createLinkage(homeId, data) {
  return request({
    url: `/api/homes/${homeId}/linkages`,
    method: 'POST',
    data
  })
}

export function updateLinkage(ruleId, data) {
  return request({
    url: `/api/linkages/${ruleId}`,
    method: 'PUT',
    data
  })
}

export function deleteLinkage(ruleId) {
  return request({
    url: `/api/linkages/${ruleId}`,
    method: 'DELETE'
  })
}
