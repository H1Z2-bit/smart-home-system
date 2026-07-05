export function getCurrentRole() {
  const user = uni.getStorageSync('user') || {}
  return user.role || 'GUEST'
}

export function canManageBaseData() {
  return ['OWNER', 'MAINTAINER'].includes(getCurrentRole())
}

export function canManageSystem() {
  return getCurrentRole() === 'OWNER'
}

export function showReadonlyToast() {
  uni.showToast({
    title: '当前角色仅可查看',
    icon: 'none'
  })
}
