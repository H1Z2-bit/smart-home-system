import { request } from '../utils/request.js'

export function listScenes(homeId) {
  return request({ url: `/api/homes/${homeId}/scenes` })
}

export function executeScene(sceneId) {
  return request({
    url: `/api/scenes/${sceneId}/execute`,
    method: 'POST'
  })
}
