<template>
  <view class="page alarms-page">
    <view class="section">
      <text class="title">报警中心</text>
      <text class="subtitle">查看并处理烟雾、燃气和设备异常</text>
    </view>

    <view class="section alarm-summary">
      <view>
        <view class="summary-number">{{ activeCount }}</view>
        <view class="summary-label">待处理报警</view>
      </view>
      <view class="summary-line"></view>
      <view>
        <view class="summary-number">{{ alarms.length }}</view>
        <view class="summary-label">总记录</view>
      </view>
    </view>

    <view v-if="alarms.length === 0" class="empty">暂无报警记录</view>

    <view v-for="alarm in alarms" :key="alarm.alarm_id" class="card alarm-card">
      <view class="row">
        <view>
          <view class="alarm-title">{{ typeName(alarm.alarm_type) }}</view>
          <view class="muted">设备 #{{ alarm.device_id }} · {{ alarm.trigger_time }}</view>
        </view>
        <view :class="['alarm-level', alarm.alarm_level === 'warning' ? 'warn' : '']">
          {{ alarm.alarm_level || 'notice' }}
        </view>
      </view>

      <view class="alarm-body">
        <view>
          <view class="alarm-value">{{ alarm.trigger_value || '-' }}</view>
          <view class="muted">触发值</view>
        </view>
        <view>
          <view class="alarm-value">{{ alarm.alarm_status }}</view>
          <view class="muted">状态</view>
        </view>
      </view>

      <view class="alarm-actions">
        <button class="small-button" @tap="handleConfirm(alarm.alarm_id)">确认</button>
        <button class="small-button blue" @tap="handleProcess(alarm.alarm_id)">处理</button>
        <button class="small-button green" @tap="handleResolve(alarm.alarm_id)">关闭</button>
        <button class="small-button gray" @tap="handleFalse(alarm.alarm_id)">误报</button>
      </view>
    </view>
  </view>
</template>

<script>
import { listHomes } from '../../api/homes.js'
import { confirmAlarm, listAlarms, markFalseAlarm, processAlarm, resolveAlarm } from '../../api/alarms.js'

export default {
  data() {
    return {
      homeId: 1,
      alarms: []
    }
  },
  computed: {
    activeCount() {
      return this.alarms.filter((alarm) => !['resolved', 'false_alarm'].includes(alarm.alarm_status)).length
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
      await this.loadAlarms()
    },
    async loadAlarms() {
      this.alarms = await listAlarms(this.homeId)
    },
    typeName(type) {
      const map = {
        smoke: '烟雾报警',
        gas: '燃气报警',
        temperature: '温度异常'
      }
      return map[type] || '设备报警'
    },
    async handleConfirm(id) {
      await confirmAlarm(id)
      uni.showToast({ title: '已确认', icon: 'success' })
      this.loadAlarms()
    },
    async handleProcess(id) {
      await processAlarm(id)
      uni.showToast({ title: '已处理', icon: 'success' })
      this.loadAlarms()
    },
    async handleResolve(id) {
      await resolveAlarm(id)
      uni.showToast({ title: '已关闭', icon: 'success' })
      this.loadAlarms()
    },
    async handleFalse(id) {
      await markFalseAlarm(id)
      uni.showToast({ title: '已标记', icon: 'success' })
      this.loadAlarms()
    }
  }
}
</script>

<style scoped>
.alarm-summary {
  display: flex;
  align-items: center;
  justify-content: space-around;
  padding: 30rpx;
  border-radius: 20rpx;
  background: #111827;
  color: #ffffff;
}

.summary-number {
  text-align: center;
  font-size: 48rpx;
  font-weight: 800;
}

.summary-label {
  margin-top: 8rpx;
  color: #cbd5e1;
  font-size: 24rpx;
}

.summary-line {
  width: 2rpx;
  height: 72rpx;
  background: rgba(255, 255, 255, 0.22);
}

.alarm-card {
  margin-bottom: 20rpx;
}

.alarm-title {
  font-size: 32rpx;
  font-weight: 800;
  color: #111827;
}

.alarm-level {
  padding: 10rpx 16rpx;
  border-radius: 999rpx;
  background: #f1f5f9;
  color: #64748b;
  font-size: 22rpx;
}

.alarm-level.warn {
  background: #ffedd5;
  color: #c2410c;
}

.alarm-body {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16rpx;
  margin-top: 24rpx;
}

.alarm-body > view {
  padding: 22rpx;
  border-radius: 14rpx;
  background: #f8fafc;
}

.alarm-value {
  font-size: 30rpx;
  font-weight: 800;
  color: #111827;
}

.alarm-actions {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12rpx;
  margin-top: 24rpx;
}

.small-button {
  height: 66rpx;
  line-height: 66rpx;
  border-radius: 10rpx;
  background: #ffedd5;
  color: #c2410c;
  font-size: 23rpx;
}

.small-button.blue {
  background: #dbeafe;
  color: #1d4ed8;
}

.small-button.green {
  background: #dcfce7;
  color: #15803d;
}

.small-button.gray {
  background: #f1f5f9;
  color: #475569;
}
</style>
