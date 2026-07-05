<template>
  <view class="page">
    <view class="section page-head">
      <view>
        <text class="title">定时任务</text>
        <text class="subtitle">配置设备在指定时间自动执行动作</text>
      </view>
      <button class="head-button" @tap="openCreate">新增</button>
    </view>

    <view class="section auto-summary">
      <view>
        <view class="summary-number">{{ schedules.length }}</view>
        <view class="summary-label">任务总数</view>
      </view>
      <view>
        <view class="summary-number">{{ enabledCount }}</view>
        <view class="summary-label">启用中</view>
      </view>
    </view>

    <view v-if="schedules.length === 0" class="empty">暂无定时任务</view>

    <view v-for="task in schedules" :key="task.task_id" class="card task-card">
      <view class="row">
        <view>
          <view class="task-title">{{ task.task_name }}</view>
          <view class="muted">设备 #{{ task.device_id }} · {{ task.execute_time }}</view>
        </view>
        <view :class="['tag', task.status === 'enabled' ? '' : 'warn']">{{ task.status }}</view>
      </view>
      <view class="task-action">动作：{{ task.action }}</view>
      <view class="button-grid">
        <button class="small-button" @tap="toggleStatus(task)">
          {{ task.status === 'enabled' ? '停用' : '启用' }}
        </button>
        <button class="small-button" @tap="openEdit(task)">编辑</button>
        <button class="small-button danger" @tap="confirmDelete(task)">删除</button>
      </view>
    </view>

    <view v-if="showForm" class="mask" @tap="closeForm">
      <view class="form-panel" @tap.stop>
        <view class="form-title">{{ editingTask ? '编辑定时任务' : '新增定时任务' }}</view>
        <input class="input" v-model="form.task_name" placeholder="任务名称，例如 夜间关灯" />
        <view class="field-label">目标设备</view>
        <picker :range="deviceNames" :value="deviceIndex" @change="onDevicePick">
          <view class="picker-field">{{ selectedDeviceName }}</view>
        </picker>
        <input class="input" v-model="form.execute_time" placeholder="执行时间，例如 22:30 或 2026-07-04 22:30" />
        <input class="input" v-model="form.action" placeholder="执行动作，例如 off / on / switch" />
        <view class="field-label">任务状态</view>
        <picker :range="statusNames" :value="statusIndex" @change="onStatusPick">
          <view class="picker-field">{{ form.status }}</view>
        </picker>
        <view class="form-actions">
          <button class="form-button cancel" @tap="closeForm">取消</button>
          <button class="form-button save" @tap="submitForm">保存</button>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { listDevices } from '../../api/devices.js'
import { listHomes } from '../../api/homes.js'
import {
  createSchedule,
  deleteSchedule,
  listSchedules,
  updateSchedule,
  updateScheduleStatus
} from '../../api/schedules.js'

export default {
  data() {
    return {
      homeId: 1,
      devices: [],
      schedules: [],
      showForm: false,
      editingTask: null,
      form: {
        device_id: null,
        task_name: '',
        execute_time: '',
        action: 'off',
        status: 'enabled'
      },
      statuses: ['enabled', 'disabled']
    }
  },
  computed: {
    enabledCount() {
      return this.schedules.filter((item) => item.status === 'enabled').length
    },
    deviceNames() {
      return this.devices.map((item) => `${item.device_name} (#${item.device_id})`)
    },
    deviceIndex() {
      const index = this.devices.findIndex((item) => item.device_id === this.form.device_id)
      return index >= 0 ? index : 0
    },
    selectedDeviceName() {
      if (!this.devices.length) return '暂无设备'
      return this.deviceNames[this.deviceIndex]
    },
    statusNames() {
      return this.statuses
    },
    statusIndex() {
      return this.statuses.indexOf(this.form.status) >= 0 ? this.statuses.indexOf(this.form.status) : 0
    }
  },
  onShow() {
    this.init()
  },
  methods: {
    async init() {
      const homes = await listHomes()
      if (homes && homes.length > 0) this.homeId = homes[0].home_id
      const [devices, schedules] = await Promise.all([listDevices(this.homeId), listSchedules(this.homeId)])
      this.devices = devices || []
      this.schedules = schedules || []
    },
    openCreate() {
      this.editingTask = null
      this.form = {
        device_id: this.devices[0]?.device_id || null,
        task_name: '',
        execute_time: '22:30',
        action: 'off',
        status: 'enabled'
      }
      this.showForm = true
    },
    openEdit(task) {
      this.editingTask = task
      this.form = {
        device_id: task.device_id,
        task_name: task.task_name || '',
        execute_time: task.execute_time || '',
        action: task.action || 'off',
        status: task.status || 'enabled'
      }
      this.showForm = true
    },
    closeForm() {
      this.showForm = false
    },
    onDevicePick(event) {
      const device = this.devices[Number(event.detail.value)]
      if (device) this.form.device_id = device.device_id
    },
    onStatusPick(event) {
      this.form.status = this.statuses[Number(event.detail.value)]
    },
    async submitForm() {
      if (!this.form.device_id) {
        uni.showToast({ title: '请选择设备', icon: 'none' })
        return
      }
      if (!this.form.task_name.trim() || !this.form.execute_time.trim() || !this.form.action.trim()) {
        uni.showToast({ title: '请补全任务信息', icon: 'none' })
        return
      }
      const data = {
        device_id: Number(this.form.device_id),
        task_name: this.form.task_name.trim(),
        execute_time: this.form.execute_time.trim(),
        action: this.form.action.trim(),
        status: this.form.status
      }
      if (this.editingTask) {
        await updateSchedule(this.editingTask.task_id, data)
        uni.showToast({ title: '任务已更新', icon: 'success' })
      } else {
        await createSchedule(this.homeId, data)
        uni.showToast({ title: '任务已新增', icon: 'success' })
      }
      this.closeForm()
      await this.init()
    },
    async toggleStatus(task) {
      const status = task.status === 'enabled' ? 'disabled' : 'enabled'
      await updateScheduleStatus(task.task_id, status)
      uni.showToast({ title: status === 'enabled' ? '已启用' : '已停用', icon: 'success' })
      await this.init()
    },
    confirmDelete(task) {
      uni.showModal({
        title: '删除定时任务',
        content: `确认删除「${task.task_name}」吗？`,
        confirmColor: '#ef4444',
        success: async (res) => {
          if (res.confirm) {
            await deleteSchedule(task.task_id)
            uni.showToast({ title: '任务已删除', icon: 'success' })
            await this.init()
          }
        }
      })
    }
  }
}
</script>

<style scoped>
.page-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 20rpx;
}

.page-head > view:first-child {
  flex: 1;
  min-width: 0;
}

.head-button {
  flex-shrink: 0;
  width: 132rpx;
  height: 68rpx;
  line-height: 68rpx;
  border-radius: 12rpx;
  background: #2563eb;
  color: #ffffff;
  font-size: 24rpx;
}

.auto-summary {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 2rpx;
  overflow: hidden;
  border-radius: 18rpx;
  background: #e5e7eb;
}

.auto-summary > view {
  padding: 26rpx;
  background: #ffffff;
  text-align: center;
}

.summary-number {
  font-size: 42rpx;
  font-weight: 800;
  color: #111827;
}

.summary-label {
  margin-top: 8rpx;
  color: #6b7280;
  font-size: 22rpx;
}

.task-card {
  margin-bottom: 20rpx;
}

.task-title {
  font-size: 32rpx;
  font-weight: 800;
}

.task-action {
  margin-top: 20rpx;
  padding: 18rpx 20rpx;
  border-radius: 14rpx;
  background: #f8fafc;
  color: #475569;
  font-size: 24rpx;
}

.button-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12rpx;
  margin-top: 22rpx;
}

.small-button {
  height: 68rpx;
  line-height: 68rpx;
  border-radius: 10rpx;
  background: #eef2ff;
  color: #1d4ed8;
  font-size: 24rpx;
}

.small-button.danger {
  background: #fee2e2;
  color: #b91c1c;
}

.mask {
  position: fixed;
  inset: 0;
  z-index: 99;
  display: flex;
  align-items: flex-end;
  background: rgba(15, 23, 42, 0.42);
}

.form-panel {
  width: 100%;
  box-sizing: border-box;
  max-height: 88vh;
  overflow-y: auto;
  padding: 34rpx 28rpx 48rpx;
  border-radius: 28rpx 28rpx 0 0;
  background: #ffffff;
}

.form-title {
  font-size: 34rpx;
  font-weight: 800;
}

.field-label {
  margin-top: 22rpx;
  color: #111827;
  font-size: 26rpx;
  font-weight: 700;
}

.picker-field {
  height: 88rpx;
  line-height: 88rpx;
  box-sizing: border-box;
  margin-top: 12rpx;
  padding: 0 24rpx;
  border: 2rpx solid #e5e7eb;
  border-radius: 12rpx;
  background: #ffffff;
  color: #334155;
  font-size: 28rpx;
}

.form-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18rpx;
  margin-top: 30rpx;
}

.form-button {
  height: 82rpx;
  line-height: 82rpx;
  border-radius: 12rpx;
  font-size: 28rpx;
}

.form-button.cancel {
  background: #f1f5f9;
  color: #334155;
}

.form-button.save {
  background: #2563eb;
  color: #ffffff;
}
</style>
