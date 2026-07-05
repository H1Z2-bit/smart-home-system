<template>
  <view class="page">
    <view class="section">
      <text class="title">系统配置</text>
      <text class="subtitle">配置报警阈值、模拟开关和自动报警策略</text>
    </view>

    <view class="section card">
      <view class="block-title">报警阈值</view>
      <input class="input" v-model="form.alarm_smoke_threshold" type="digit" placeholder="烟雾报警阈值" />
      <input class="input" v-model="form.alarm_gas_threshold" type="digit" placeholder="燃气报警阈值" />
      <input class="input" v-model="form.temperature_high_threshold" type="digit" placeholder="高温报警阈值" />
    </view>

    <view class="section card">
      <view class="block-title">系统开关</view>
      <view class="switch-row">
        <view>
          <view class="field-title">自动报警</view>
          <view class="muted">设备模拟或联动触发后自动生成报警</view>
        </view>
        <switch :checked="form.auto_alarm_enabled" @change="form.auto_alarm_enabled = $event.detail.value" />
      </view>
      <view class="switch-row">
        <view>
          <view class="field-title">设备模拟</view>
          <view class="muted">允许提交传感器模拟数据</view>
        </view>
        <switch :checked="form.simulation_enabled" @change="form.simulation_enabled = $event.detail.value" />
      </view>
    </view>

    <button class="button" @tap="saveConfig">保存配置</button>
  </view>
</template>

<script>
import { listHomes } from '../../api/homes.js'
import { getSystemConfig, updateSystemConfig } from '../../api/system.js'

export default {
  data() {
    return {
      homeId: 1,
      form: {
        alarm_smoke_threshold: '',
        alarm_gas_threshold: '',
        temperature_high_threshold: '',
        auto_alarm_enabled: true,
        simulation_enabled: true
      }
    }
  },
  onShow() {
    this.init()
  },
  methods: {
    async init() {
      const homes = await listHomes()
      if (homes && homes.length > 0) this.homeId = homes[0].home_id
      const config = await getSystemConfig(this.homeId)
      this.form = {
        alarm_smoke_threshold: String(config.alarm_smoke_threshold),
        alarm_gas_threshold: String(config.alarm_gas_threshold),
        temperature_high_threshold: String(config.temperature_high_threshold),
        auto_alarm_enabled: Boolean(config.auto_alarm_enabled),
        simulation_enabled: Boolean(config.simulation_enabled)
      }
    },
    async saveConfig() {
      const data = {
        alarm_smoke_threshold: Number(this.form.alarm_smoke_threshold),
        alarm_gas_threshold: Number(this.form.alarm_gas_threshold),
        temperature_high_threshold: Number(this.form.temperature_high_threshold),
        auto_alarm_enabled: Boolean(this.form.auto_alarm_enabled),
        simulation_enabled: Boolean(this.form.simulation_enabled)
      }
      await updateSystemConfig(this.homeId, data)
      uni.showToast({ title: '配置已保存', icon: 'success' })
    }
  }
}
</script>

<style scoped>
.block-title {
  margin-bottom: 10rpx;
  font-size: 30rpx;
  font-weight: 800;
  color: #111827;
}

.switch-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20rpx;
  padding: 22rpx 0;
  border-top: 2rpx solid #f1f5f9;
}

.switch-row:first-of-type {
  border-top: 0;
}

.field-title {
  font-size: 27rpx;
  font-weight: 700;
  color: #111827;
}
</style>
