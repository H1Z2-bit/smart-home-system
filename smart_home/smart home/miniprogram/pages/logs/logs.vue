<template>
  <view class="page">
    <view class="section">
      <text class="title">系统日志</text>
      <text class="subtitle">查看设备操作、系统配置和报警处理记录</text>
    </view>

    <view class="section tabs">
      <view :class="['tab', mode === 'operation' ? 'active' : '']" @tap="mode = 'operation'; loadLogs()">操作日志</view>
      <view :class="['tab', mode === 'system' ? 'active' : '']" @tap="mode = 'system'; loadLogs()">系统日志</view>
    </view>

    <view v-if="logs.length === 0" class="empty">暂无日志</view>

    <view v-for="log in logs" :key="log.log_id || log.created_at" class="card log-card">
      <view class="row">
        <view>
          <view class="log-title">{{ log.operation_type || log.action || '日志记录' }}</view>
          <view class="muted">{{ log.created_at || '-' }}</view>
        </view>
        <view class="tag">{{ log.operation_result || log.target_type || 'success' }}</view>
      </view>
      <view class="log-desc">{{ log.operation_desc || log.description || '-' }}</view>
    </view>
  </view>
</template>

<script>
import { listHomes } from '../../api/homes.js'
import { listOperationLogs, listSystemLogs } from '../../api/system.js'

export default {
  data() {
    return {
      homeId: 1,
      mode: 'operation',
      logs: []
    }
  },
  onShow() {
    this.init()
  },
  methods: {
    async init() {
      const homes = await listHomes()
      if (homes && homes.length > 0) this.homeId = homes[0].home_id
      await this.loadLogs()
    },
    async loadLogs() {
      this.logs = this.mode === 'system' ? await listSystemLogs(this.homeId) : await listOperationLogs(this.homeId)
    }
  }
}
</script>

<style scoped>
.tabs {
  display: grid;
  grid-template-columns: 1fr 1fr;
  padding: 6rpx;
  border-radius: 14rpx;
  background: #e5e7eb;
}

.tab {
  height: 72rpx;
  line-height: 72rpx;
  text-align: center;
  border-radius: 10rpx;
  color: #64748b;
  font-size: 26rpx;
}

.tab.active {
  background: #ffffff;
  color: #1d4ed8;
  font-weight: 800;
}

.log-card {
  margin-bottom: 20rpx;
}

.log-title {
  font-size: 30rpx;
  font-weight: 800;
  color: #111827;
}

.log-desc {
  margin-top: 18rpx;
  color: #475569;
  font-size: 24rpx;
  line-height: 1.6;
}
</style>
