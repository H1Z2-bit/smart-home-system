<template>
  <view class="page home-page">
    <view class="hero">
      <view>
        <text class="eyebrow">Smart Home</text>
        <text class="title">智能家居控制台</text>
        <text class="subtitle">统一查看家庭空间、设备状态与安全报警</text>
      </view>
      <view :class="['status-pill', profile.phone_bound ? 'ok' : 'warn']">
        {{ profile.phone_bound ? '手机号已绑定' : '待绑定手机号' }}
      </view>
    </view>

    <view class="section card user-card">
      <view class="avatar">{{ avatarText }}</view>
      <view class="user-main">
        <view class="username">{{ profile.username || '未登录' }}</view>
        <view class="muted">{{ profile.phone || '暂无手机号' }}</view>
      </view>
      <view class="role">{{ profile.role || '-' }}</view>
    </view>

    <view class="section stats-grid">
      <view class="stat-card">
        <view class="stat-number">{{ homes.length }}</view>
        <view class="stat-label">家庭空间</view>
      </view>
      <view class="stat-card">
        <view class="stat-number">{{ devices.length }}</view>
        <view class="stat-label">设备数量</view>
      </view>
      <view class="stat-card danger">
        <view class="stat-number">{{ activeAlarmCount }}</view>
        <view class="stat-label">待处理报警</view>
      </view>
    </view>

    <view class="section action-grid">
      <view class="action-card device" @tap="goDevices">
        <view class="action-icon">D</view>
        <view class="action-title">设备控制</view>
        <view class="muted">开关、插座、传感器</view>
      </view>
      <view class="action-card room" @tap="goRooms">
        <view class="action-icon">R</view>
        <view class="action-title">房间管理</view>
        <view class="muted">新增、编辑、删除房间</view>
      </view>
      <view class="action-card scene" @tap="goScenes">
        <view class="action-icon">S</view>
        <view class="action-title">场景模式</view>
        <view class="muted">离家、回家、一键执行</view>
      </view>
      <view class="action-card schedule" @tap="goSchedules">
        <view class="action-icon">T</view>
        <view class="action-title">定时任务</view>
        <view class="muted">定时开关、自动执行</view>
      </view>
      <view class="action-card linkage" @tap="goLinkages">
        <view class="action-icon">L</view>
        <view class="action-title">联动规则</view>
        <view class="muted">条件触发、自动报警</view>
      </view>
      <view class="action-card visual" @tap="goVisualization">
        <view class="action-icon">3D</view>
        <view class="action-title">空间可视化</view>
        <view class="muted">房间与设备分布</view>
      </view>
      <view class="action-card alarm" @tap="goAlarms">
        <view class="action-icon">A</view>
        <view class="action-title">报警中心</view>
        <view class="muted">烟雾、燃气、异常</view>
      </view>
      <view class="action-card demo" @tap="goDemo">
        <view class="action-icon">M</view>
        <view class="action-title">演示模式</view>
        <view class="muted">重置数据、答辩流程</view>
      </view>
    </view>

    <view class="section card bind-card" v-if="!profile.phone_bound">
      <view>
        <view class="bind-title">建议绑定手机号</view>
        <view class="muted">用于安全验证和验证码登录</view>
      </view>
      <button class="mini-button" @tap="goProfile">去绑定</button>
    </view>

    <view class="section">
      <view class="section-head">
        <view class="section-title">家庭空间</view>
        <view class="muted">默认展示第一个家庭</view>
      </view>
      <view v-if="homes.length === 0" class="empty">暂无家庭空间</view>
      <view v-for="home in homes" :key="home.home_id" class="card home-card">
        <view>
          <view class="home-name">{{ home.name }}</view>
          <view class="muted">{{ home.address || '未填写地址' }}</view>
        </view>
        <view class="home-badge">#{{ home.home_id }}</view>
      </view>
    </view>
  </view>
</template>

<script>
import { getProfile } from '../../api/auth.js'
import { listHomes } from '../../api/homes.js'
import { listDevices } from '../../api/devices.js'
import { listAlarms } from '../../api/alarms.js'

export default {
  data() {
    return {
      profile: {},
      homes: [],
      devices: [],
      alarms: []
    }
  },
  computed: {
    avatarText() {
      return (this.profile.username || 'U').slice(0, 1).toUpperCase()
    },
    activeAlarmCount() {
      return this.alarms.filter((alarm) => !['resolved', 'false_alarm'].includes(alarm.alarm_status)).length
    }
  },
  onShow() {
    this.loadData()
  },
  methods: {
    async loadData() {
      const profile = await getProfile()
      const homes = await listHomes()
      this.profile = profile
      this.homes = homes || []
      uni.setStorageSync('user', profile)

      const homeId = this.homes[0]?.home_id
      if (homeId) {
        const [devices, alarms] = await Promise.all([listDevices(homeId), listAlarms(homeId)])
        this.devices = devices || []
        this.alarms = alarms || []
      }
    },
    goProfile() {
      uni.switchTab({ url: '/pages/profile/profile' })
    },
    goDevices() {
      uni.switchTab({ url: '/pages/devices/devices' })
    },
    goRooms() {
      uni.navigateTo({ url: '/pages/rooms/rooms' })
    },
    goAlarms() {
      uni.switchTab({ url: '/pages/alarms/alarms' })
    },
    goScenes() {
      uni.navigateTo({ url: '/pages/scenes/scenes' })
    },
    goSchedules() {
      uni.navigateTo({ url: '/pages/schedules/schedules' })
    },
    goLinkages() {
      uni.navigateTo({ url: '/pages/linkages/linkages' })
    },
    goVisualization() {
      uni.navigateTo({ url: '/pages/visualization/visualization' })
    },
    goDemo() {
      uni.navigateTo({ url: '/pages/demo/demo' })
    }
  }
}
</script>

<style scoped>
.home-page {
  background: linear-gradient(180deg, #eef6ff 0%, #f5f7fb 42%, #f5f7fb 100%);
}

.hero {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 20rpx;
  padding: 20rpx 0 10rpx;
}

.hero > view:first-child {
  flex: 1;
  min-width: 0;
}

.eyebrow {
  display: block;
  margin-bottom: 8rpx;
  color: #2563eb;
  font-size: 22rpx;
  font-weight: 700;
}

.status-pill {
  flex-shrink: 0;
  padding: 12rpx 18rpx;
  border-radius: 999rpx;
  font-size: 22rpx;
  font-weight: 700;
}

.status-pill.ok {
  background: #dcfce7;
  color: #15803d;
}

.status-pill.warn {
  background: #ffedd5;
  color: #c2410c;
}

.user-card,
.bind-card,
.home-card,
.section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20rpx;
}

.avatar {
  width: 88rpx;
  height: 88rpx;
  line-height: 88rpx;
  border-radius: 22rpx;
  text-align: center;
  background: #2563eb;
  color: #ffffff;
  font-weight: 800;
  font-size: 36rpx;
}

.user-main {
  flex: 1;
}

.username {
  font-size: 34rpx;
  font-weight: 800;
}

.role,
.home-badge {
  padding: 12rpx 18rpx;
  border-radius: 10rpx;
  background: #eff6ff;
  color: #1d4ed8;
  font-size: 24rpx;
  font-weight: 700;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16rpx;
}

.stat-card {
  padding: 24rpx 18rpx;
  border-radius: 16rpx;
  background: #ffffff;
  text-align: center;
}

.stat-card.danger {
  background: #fff1f2;
}

.stat-number {
  font-size: 42rpx;
  font-weight: 800;
  color: #111827;
}

.stat-label {
  margin-top: 6rpx;
  color: #6b7280;
  font-size: 22rpx;
}

.action-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 18rpx;
}

.action-card {
  min-height: 172rpx;
  padding: 24rpx;
  border-radius: 18rpx;
  background: #ffffff;
  box-sizing: border-box;
}

.action-card.device {
  background: #e0f2fe;
}

.action-card.room {
  background: #f1f5f9;
}

.action-card.scene {
  background: #ecfdf5;
}

.action-card.schedule {
  background: #fef3c7;
}

.action-card.linkage {
  background: #ede9fe;
}

.action-card.visual {
  background: #fef9c3;
}

.action-card.alarm {
  background: #fee2e2;
}

.action-card.demo {
  background: #ffedd5;
}

.action-icon {
  width: 56rpx;
  height: 56rpx;
  line-height: 56rpx;
  margin-bottom: 18rpx;
  border-radius: 14rpx;
  background: rgba(255, 255, 255, 0.72);
  color: #111827;
  text-align: center;
  font-size: 22rpx;
  font-weight: 800;
}

.action-title,
.bind-title,
.section-title,
.home-name {
  font-size: 30rpx;
  font-weight: 800;
  color: #111827;
}

.mini-button {
  width: 150rpx;
  height: 64rpx;
  line-height: 64rpx;
  border-radius: 10rpx;
  background: #2563eb;
  color: #ffffff;
  font-size: 24rpx;
}

.home-card {
  margin-top: 18rpx;
}
</style>
