<template>
  <view class="page scenes-page">
    <view class="section">
      <text class="title">场景模式</text>
      <text class="subtitle">一键执行预设动作，适合课程演示联动效果</text>
    </view>

    <view class="section scene-hero">
      <view class="scene-rings">
        <view class="ring ring-a"></view>
        <view class="ring ring-b"></view>
        <view class="ring-center">Scene</view>
      </view>
      <view>
        <view class="hero-title">{{ scenes.length }} 个场景</view>
        <view class="hero-text">执行后由后端统一写入操作日志，并改变相关设备状态。</view>
      </view>
    </view>

    <view v-if="scenes.length === 0" class="empty">暂无场景模式</view>

    <view v-for="scene in scenes" :key="scene.scene_id" class="card scene-card">
      <view class="row">
        <view>
          <view class="scene-name">{{ scene.scene_name }}</view>
          <view class="muted">动作数量：{{ scene.actions ? scene.actions.length : 0 }}</view>
        </view>
        <view :class="['tag', scene.enabled ? '' : 'warn']">{{ scene.enabled ? '启用' : '停用' }}</view>
      </view>

      <view class="action-list" v-if="scene.actions && scene.actions.length">
        <view v-for="action in scene.actions" :key="action.sort_no" class="action-line">
          <text>设备 #{{ action.device_id }}</text>
          <text>{{ action.target_state }}</text>
        </view>
      </view>

      <button class="button execute-button" :disabled="!scene.enabled" @tap="handleExecute(scene)">
        执行场景
      </button>
    </view>
  </view>
</template>

<script>
import { listHomes } from '../../api/homes.js'
import { executeScene, listScenes } from '../../api/scenes.js'

export default {
  data() {
    return {
      homeId: 1,
      scenes: []
    }
  },
  onShow() {
    this.init()
  },
  methods: {
    async init() {
      const homes = await listHomes()
      if (homes && homes.length > 0) {
        this.homeId = homes[0].home_id
      }
      this.scenes = await listScenes(this.homeId)
    },
    async handleExecute(scene) {
      await executeScene(scene.scene_id)
      uni.showToast({ title: '场景已执行', icon: 'success' })
    }
  }
}
</script>

<style scoped>
.scene-hero {
  display: flex;
  align-items: center;
  gap: 28rpx;
  padding: 30rpx;
  border-radius: 22rpx;
  background: #111827;
  color: #ffffff;
}

.scene-rings {
  position: relative;
  width: 148rpx;
  height: 148rpx;
  flex-shrink: 0;
}

.ring {
  position: absolute;
  border-radius: 50%;
}

.ring-a {
  inset: 0;
  border: 4rpx solid rgba(96, 165, 250, 0.6);
}

.ring-b {
  inset: 20rpx;
  border: 4rpx solid rgba(52, 211, 153, 0.64);
}

.ring-center {
  position: absolute;
  left: 38rpx;
  top: 50rpx;
  font-size: 24rpx;
  font-weight: 800;
}

.hero-title {
  font-size: 34rpx;
  font-weight: 800;
}

.hero-text {
  margin-top: 10rpx;
  color: #cbd5e1;
  font-size: 24rpx;
  line-height: 1.6;
}

.scene-card {
  margin-bottom: 20rpx;
}

.scene-name {
  font-size: 32rpx;
  font-weight: 800;
}

.action-list {
  margin-top: 22rpx;
  border-radius: 14rpx;
  background: #f8fafc;
  overflow: hidden;
}

.action-line {
  display: flex;
  justify-content: space-between;
  padding: 18rpx 20rpx;
  border-bottom: 2rpx solid #eef2f7;
  color: #475569;
  font-size: 24rpx;
}

.action-line:last-child {
  border-bottom: 0;
}

.execute-button {
  margin-top: 24rpx;
}
</style>
