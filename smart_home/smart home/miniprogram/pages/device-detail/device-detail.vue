<template>
  <view class="page">
    <view v-if="!device.device_id" class="empty">正在加载设备详情</view>

    <template v-else>
      <view class="detail-hero">
        <view>
          <text class="title">{{ device.device_name }}</text>
          <text class="subtitle">{{ device.device_type }} · 设备 #{{ device.device_id }}</text>
        </view>
        <view :class="['status-dot', isOnline ? 'on' : 'off']"></view>
      </view>

      <view class="section card status-card">
        <view>
          <view class="status-title">{{ device.device_status }}</view>
          <view class="muted">当前状态</view>
        </view>
        <view :class="['tag', device.is_key_device ? 'warn' : '']">
          {{ device.is_key_device ? '关键设备' : '普通设备' }}
        </view>
      </view>

      <view class="section metric-grid">
        <view class="metric-card">
          <view class="metric-value">{{ metricValue }}</view>
          <view class="metric-label">{{ metricLabel }}</view>
        </view>
        <view class="metric-card">
          <view class="metric-value">{{ isOnline ? '正常' : '待唤醒' }}</view>
          <view class="metric-label">通信状态</view>
        </view>
      </view>

      <view class="section card">
        <view class="block-title">设备信息</view>
        <view class="info-line">家庭编号：{{ device.home_id }}</view>
        <view class="info-line">房间编号：{{ device.room_id }}</view>
        <view class="info-line">设备厂商：{{ device.manufacturer || '未登记' }}</view>
        <view class="info-line">设备型号：{{ device.model || '未登记' }}</view>
        <view class="info-line">序列号：{{ device.serial_no || '未登记' }}</view>
        <view class="info-line">最后在线：{{ device.last_online_at || '暂无记录' }}</view>
        <view class="info-line">最后离线：{{ device.last_offline_at || '暂无记录' }}</view>
        <view class="info-line">创建时间：{{ device.created_at || '-' }}</view>
      </view>

      <view class="section card">
        <view class="block-title">空间坐标</view>
        <view class="layout-preview">
          <view class="axis-card">
            <view class="axis-value">{{ layoutValue('position_x') }}</view>
            <view class="axis-label">X 坐标</view>
          </view>
          <view class="axis-card">
            <view class="axis-value">{{ layoutValue('position_y') }}</view>
            <view class="axis-label">Y 坐标</view>
          </view>
          <view class="axis-card">
            <view class="axis-value">{{ layoutValue('position_z') }}</view>
            <view class="axis-label">Z 高度</view>
          </view>
        </view>
        <view class="info-line">图标：{{ layoutValue('icon_name') }}</view>
        <view class="info-line">模型：{{ layoutValue('model_name') }}</view>
      </view>

      <view class="section card">
        <view class="block-title">快速控制</view>
        <view class="control-grid">
          <button class="control-button on" @tap="switchDevice('on')">开启</button>
          <button class="control-button off" @tap="switchDevice('off')">关闭</button>
        </view>
      </view>

      <view class="section card">
        <view class="block-title">模拟数据</view>
        <input class="input" v-model="simulation.metric_name" placeholder="指标名称，例如 smoke / temperature" />
        <input class="input" v-model="simulation.metric_value" placeholder="指标值，例如 88" />
        <input class="input" v-model="simulation.device_status" placeholder="设备状态，可选，例如 online" />
        <view class="switch-row">
          <view>
            <view class="field-title">触发报警</view>
            <view class="muted">用于演示传感器异常到报警中心的闭环</view>
          </view>
          <switch :checked="simulation.trigger_alarm" @change="simulation.trigger_alarm = $event.detail.value" />
        </view>
        <input v-if="simulation.trigger_alarm" class="input" v-model="simulation.alarm_type" placeholder="报警类型，例如 smoke" />
        <input v-if="simulation.trigger_alarm" class="input" v-model="simulation.alarm_level" placeholder="报警级别，例如 warning" />
        <button class="button submit-button" @tap="submitSimulation">提交模拟数据</button>
      </view>

      <view class="section card">
        <view class="section-row">
          <view>
            <view class="block-title">模拟记录</view>
            <view class="muted">最近提交的传感器模拟数据</view>
          </view>
          <button class="mini-button" @tap="loadSimulationRecords">刷新</button>
        </view>
        <view v-if="simulationRecords.length === 0" class="empty small">暂无模拟记录</view>
        <view v-for="record in simulationRecords" :key="record.simulation_id || record.created_at" class="record-line">
          <view>
            <view class="record-title">{{ record.metric_name }} = {{ record.metric_value }}</view>
            <view class="muted">{{ record.created_at || '-' }}</view>
          </view>
          <view :class="['tag', record.trigger_alarm ? 'warn' : '']">
            {{ record.trigger_alarm ? '触发报警' : '普通记录' }}
          </view>
        </view>
      </view>

      <view class="section card">
        <view class="section-row">
          <view>
            <view class="block-title">设备自检</view>
            <view class="muted">发起设备自检并查看历史记录</view>
          </view>
          <button class="mini-button" @tap="handleSelfCheck">开始自检</button>
        </view>
        <view v-if="selfCheckRecords.length === 0" class="empty small">暂无自检记录</view>
        <view v-for="record in selfCheckRecords" :key="record.check_id || record.created_at" class="record-line">
          <view>
            <view class="record-title">{{ record.check_result || record.status || '自检记录' }}</view>
            <view class="muted">{{ record.created_at || '-' }}</view>
          </view>
          <view class="tag">{{ record.result_desc || record.device_status || '完成' }}</view>
        </view>
      </view>
    </template>
  </view>
</template>

<script>
import { controlDevice, getDevice } from '../../api/devices.js'
import { createDeviceSimulation, listDeviceSimulations } from '../../api/device-simulations.js'
import { listSelfChecks, startSelfCheck } from '../../api/self-checks.js'

export default {
  data() {
    return {
      deviceId: null,
      device: {},
      simulation: {
        metric_name: 'smoke',
        metric_value: '88',
        device_status: 'online',
        trigger_alarm: true,
        alarm_type: 'smoke',
        alarm_level: 'warning'
      },
      simulationRecords: [],
      selfCheckRecords: []
    }
  },
  computed: {
    isOnline() {
      return ['online', 'on'].includes(this.device.device_status)
    },
    metricLabel() {
      if (this.device.device_type === 'temperature_sensor') return '室内温度'
      if (this.device.device_type === 'smoke_sensor') return '烟雾浓度'
      if (this.device.device_type === 'gas_sensor') return '燃气浓度'
      if (this.device.device_type === 'light') return '照明状态'
      return '设备指标'
    },
    metricValue() {
      if (this.device.device_type === 'temperature_sensor') return '26.5℃'
      if (this.device.device_type === 'smoke_sensor') return '18 ppm'
      if (this.device.device_type === 'gas_sensor') return '12%'
      if (this.device.device_type === 'light') return this.device.device_status === 'on' ? '已亮起' : '已熄灭'
      return this.device.device_status || '-'
    }
  },
  onLoad(query) {
    this.deviceId = Number(query.id)
    this.loadAll()
  },
  methods: {
    async loadAll() {
      await this.loadDevice()
      await Promise.all([this.loadSimulationRecords(), this.loadSelfCheckRecords()])
    },
    async loadDevice() {
      this.device = await getDevice(this.deviceId)
      this.setDefaultSimulationByType()
    },
    setDefaultSimulationByType() {
      if (this.device.device_type === 'temperature_sensor') {
        this.simulation.metric_name = 'temperature'
        this.simulation.metric_value = '38'
        this.simulation.alarm_type = 'temperature'
      } else if (this.device.device_type === 'gas_sensor') {
        this.simulation.metric_name = 'gas'
        this.simulation.metric_value = '78'
        this.simulation.alarm_type = 'gas'
      } else if (this.device.device_type === 'smoke_sensor') {
        this.simulation.metric_name = 'smoke'
        this.simulation.metric_value = '88'
        this.simulation.alarm_type = 'smoke'
      }
    },
    async switchDevice(state) {
      await controlDevice(this.deviceId, state)
      uni.showToast({ title: state === 'on' ? '已开启' : '已关闭', icon: 'success' })
      await this.loadDevice()
    },
    async submitSimulation() {
      if (!this.simulation.metric_name || this.simulation.metric_value === '') {
        uni.showToast({ title: '请填写模拟指标', icon: 'none' })
        return
      }
      const data = {
        metric_name: this.simulation.metric_name.trim(),
        metric_value: this.normalizeMetricValue(this.simulation.metric_value),
        device_status: this.simulation.device_status.trim() || null,
        trigger_alarm: Boolean(this.simulation.trigger_alarm),
        alarm_type: this.simulation.trigger_alarm ? this.simulation.alarm_type.trim() || 'smoke' : null,
        alarm_level: this.simulation.alarm_level.trim() || 'warning'
      }
      await createDeviceSimulation(this.deviceId, data)
      uni.showToast({ title: data.trigger_alarm ? '已模拟报警' : '已提交模拟', icon: 'success' })
      await this.loadAll()
    },
    normalizeMetricValue(value) {
      const numberValue = Number(value)
      return Number.isNaN(numberValue) ? value : numberValue
    },
    layoutValue(key) {
      const layout = this.device.layout || {}
      const value = layout[key]
      return value === undefined || value === null || value === '' ? '未设置' : value
    },
    async loadSimulationRecords() {
      this.simulationRecords = await listDeviceSimulations(this.deviceId)
    },
    async handleSelfCheck() {
      await startSelfCheck(this.deviceId)
      uni.showToast({ title: '自检已完成', icon: 'success' })
      await this.loadSelfCheckRecords()
    },
    async loadSelfCheckRecords() {
      this.selfCheckRecords = await listSelfChecks(this.deviceId)
    }
  }
}
</script>

<style scoped>
.detail-hero {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 20rpx;
  padding: 26rpx 0 12rpx;
}

.detail-hero > view:first-child {
  flex: 1;
  min-width: 0;
}

.status-dot {
  flex-shrink: 0;
  width: 28rpx;
  height: 28rpx;
  margin-top: 14rpx;
  border-radius: 50%;
  background: #94a3b8;
  box-shadow: 0 0 0 10rpx rgba(148, 163, 184, 0.16);
}

.status-dot.on {
  background: #22c55e;
  box-shadow: 0 0 0 10rpx rgba(34, 197, 94, 0.16);
}

.status-card,
.section-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20rpx;
}

.status-title {
  font-size: 42rpx;
  font-weight: 800;
  color: #111827;
}

.metric-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 18rpx;
}

.layout-preview {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14rpx;
  margin: 18rpx 0;
}

.axis-card {
  min-width: 0;
  padding: 20rpx 10rpx;
  border-radius: 14rpx;
  background: #f8fafc;
  text-align: center;
}

.axis-value {
  color: #1d4ed8;
  font-size: 30rpx;
  font-weight: 800;
  word-break: break-all;
}

.axis-label {
  margin-top: 6rpx;
  color: #64748b;
  font-size: 21rpx;
}

.metric-card {
  padding: 28rpx;
  border-radius: 18rpx;
  background: #ffffff;
}

.metric-value {
  font-size: 38rpx;
  font-weight: 800;
  color: #111827;
}

.metric-label,
.info-line {
  margin-top: 12rpx;
  color: #6b7280;
  font-size: 24rpx;
}

.block-title {
  margin-bottom: 10rpx;
  font-size: 30rpx;
  font-weight: 800;
}

.control-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18rpx;
  margin-top: 22rpx;
}

.control-button {
  height: 80rpx;
  line-height: 80rpx;
  border-radius: 12rpx;
  font-size: 28rpx;
}

.control-button.on {
  background: #dcfce7;
  color: #15803d;
}

.control-button.off {
  background: #f1f5f9;
  color: #334155;
}

.switch-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20rpx;
  margin-top: 22rpx;
}

.field-title {
  color: #111827;
  font-size: 26rpx;
  font-weight: 700;
}

.submit-button {
  margin-top: 24rpx;
}

.mini-button {
  flex-shrink: 0;
  width: 132rpx;
  height: 64rpx;
  line-height: 64rpx;
  border-radius: 10rpx;
  background: #eef2ff;
  color: #1d4ed8;
  font-size: 24rpx;
}

.record-line {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18rpx;
  padding: 20rpx 0;
  border-top: 2rpx solid #f1f5f9;
}

.record-title {
  font-size: 27rpx;
  font-weight: 700;
  color: #111827;
}

.empty.small {
  padding: 34rpx 0 10rpx;
}
</style>
