<template>
  <view class="page">
    <view class="section">
      <text class="title">演示模式</text>
      <text class="subtitle">用于课程答辩的一键演示和 Mock 数据管理</text>
    </view>

    <view class="section card">
      <view class="block-title">Mock 数据重置</view>
      <view class="muted">恢复默认用户、家庭、房间、设备、场景和报警数据。</view>
      <button class="button danger action-button" @tap="handleReset">重置 Mock 数据</button>
    </view>

    <view class="section card">
      <view class="block-title">演示建议</view>
      <view class="demo-line">1. 重置 Mock 数据</view>
      <view class="demo-line">2. 打开设备详情，提交烟雾模拟数据</view>
      <view class="demo-line">3. 进入报警中心，确认并处理报警</view>
      <view class="demo-line">4. 执行离家场景，查看日志记录</view>
    </view>
  </view>
</template>

<script>
import { resetMockData } from '../../api/system.js'

export default {
  methods: {
    handleReset() {
      uni.showModal({
        title: '重置 Mock 数据',
        content: '确认恢复默认演示数据吗？当前 Mock 修改会被覆盖。',
        confirmColor: '#ef4444',
        success: async (res) => {
          if (res.confirm) {
            await resetMockData()
            uni.showToast({ title: '已重置', icon: 'success' })
          }
        }
      })
    }
  }
}
</script>

<style scoped>
.block-title {
  margin-bottom: 12rpx;
  font-size: 30rpx;
  font-weight: 800;
  color: #111827;
}

.action-button {
  margin-top: 24rpx;
}

.demo-line {
  padding: 18rpx 0;
  border-top: 2rpx solid #f1f5f9;
  color: #475569;
  font-size: 26rpx;
}
</style>
