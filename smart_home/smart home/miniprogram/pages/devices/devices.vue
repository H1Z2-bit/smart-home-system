<template>
  <view class="page devices-page">
    <view class="section page-head">
      <view>
        <text class="title">设备控制</text>
        <text class="subtitle">支持设备查询、控制、新增、编辑和删除</text>
      </view>
      <button class="head-button" @tap="openCreateDevice">{{ canManage ? '新增' : '只读' }}</button>
    </view>

    <view class="section overview-card">
      <view class="overview-item">
        <view class="overview-number">{{ devices.length }}</view>
        <view class="overview-label">当前设备</view>
      </view>
      <view class="overview-item">
        <view class="overview-number">{{ onlineCount }}</view>
        <view class="overview-label">在线/开启</view>
      </view>
      <view class="overview-item" @tap="goRooms">
        <view class="overview-number">{{ rooms.length }}</view>
        <view class="overview-label">房间管理</view>
      </view>
    </view>

    <scroll-view class="room-scroll" scroll-x>
      <view class="room-tabs">
        <view :class="['room-tab', selectedRoomId === 0 ? 'active' : '']" @tap="selectRoom(0)">全部</view>
        <view
          v-for="room in rooms"
          :key="room.room_id"
          :class="['room-tab', selectedRoomId === room.room_id ? 'active' : '']"
          @tap="selectRoom(room.room_id)"
        >
          {{ room.room_name }}
        </view>
      </view>
    </scroll-view>

    <view v-if="devices.length === 0" class="empty">暂无设备，点击右上角新增</view>

    <view v-for="device in devices" :key="device.device_id" class="card device-card" @tap="goDetail(device)">
      <view class="row">
        <view class="device-left">
          <view :class="['device-type', typeClass(device.device_type)]">{{ typeShort(device.device_type) }}</view>
          <view>
            <view class="device-name">{{ device.device_name }}</view>
            <view class="muted">{{ device.device_type }} · {{ roomName(device.room_id) }}</view>
          </view>
        </view>
        <view :class="['tag', isOnline(device) ? '' : 'warn']">{{ device.device_status }}</view>
      </view>

      <view class="device-meta">
        <view>{{ device.is_key_device ? '关键安全设备' : '普通设备' }}</view>
        <view>#{{ device.device_id }}</view>
      </view>

      <view class="device-extra">
        <view class="extra-item">
          <text class="extra-label">厂商</text>
          <text class="extra-value">{{ device.manufacturer || '未登记' }}</text>
        </view>
        <view class="extra-item">
          <text class="extra-label">型号</text>
          <text class="extra-value">{{ device.model || '未登记' }}</text>
        </view>
        <view class="extra-item wide">
          <text class="extra-label">最后在线</text>
          <text class="extra-value">{{ device.last_online_at || '暂无记录' }}</text>
        </view>
        <view class="extra-item wide">
          <text class="extra-label">3D 坐标</text>
          <text class="extra-value">{{ layoutText(device) }}</text>
        </view>
      </view>

      <view class="device-actions" @tap.stop>
        <button class="action-button on" @tap="switchDevice(device, 'on')">开启</button>
        <button class="action-button off" @tap="switchDevice(device, 'off')">关闭</button>
      </view>

      <view v-if="canManage" class="manage-actions" @tap.stop>
        <button class="manage-button" @tap="openEditDevice(device)">编辑</button>
        <button class="manage-button danger" @tap="confirmDeleteDevice(device)">删除</button>
      </view>
    </view>

    <view v-if="showDeviceForm" class="mask" @tap="closeDeviceForm">
      <view class="form-panel" @tap.stop>
        <view class="form-title">{{ editingDevice ? '编辑设备' : '新增设备' }}</view>

        <view class="field-label">所属房间</view>
        <picker :range="roomPickerNames" :value="roomPickerIndex" @change="onRoomPick">
          <view class="picker-field">{{ selectedFormRoomName }}</view>
        </picker>

        <input class="input" v-model="deviceForm.device_name" placeholder="设备名称，例如 客厅灯" />

        <view class="field-label">设备类型</view>
        <picker :range="deviceTypeNames" :value="deviceTypeIndex" @change="onDeviceTypePick">
          <view class="picker-field">{{ deviceTypeLabel }}</view>
        </picker>

        <view class="field-label">设备状态</view>
        <picker :range="statusNames" :value="statusIndex" @change="onStatusPick">
          <view class="picker-field">{{ statusLabel }}</view>
        </picker>

        <view class="switch-row">
          <view>
            <view class="field-title">关键安全设备</view>
            <view class="muted">烟雾、燃气、门磁等建议开启</view>
          </view>
          <switch :checked="deviceForm.is_key_device" @change="onKeyDeviceChange" />
        </view>

        <view class="form-actions">
          <button class="form-button cancel" @tap="closeDeviceForm">取消</button>
          <button class="form-button save" @tap="submitDeviceForm">保存</button>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { listHomes } from '../../api/homes.js'
import {
  controlDevice,
  createDevice,
  deleteDevice,
  listDevices,
  listRooms,
  updateDevice
} from '../../api/devices.js'
import { canManageBaseData, showReadonlyToast } from '../../utils/permission.js'

export default {
  data() {
    return {
      homeId: 1,
      rooms: [],
      devices: [],
      selectedRoomId: 0,
      showDeviceForm: false,
      editingDevice: null,
      deviceForm: {
        room_id: null,
        device_name: '',
        device_type: 'light',
        device_status: 'offline',
        is_key_device: false
      },
      canManage: true,
      deviceTypes: [
        { label: '灯光 light', value: 'light' },
        { label: '插座 socket', value: 'socket' },
        { label: '温度传感器', value: 'temperature_sensor' },
        { label: '烟雾传感器', value: 'smoke_sensor' },
        { label: '燃气传感器', value: 'gas_sensor' },
        { label: '门磁传感器', value: 'door_sensor' }
      ],
      statuses: [
        { label: '离线 offline', value: 'offline' },
        { label: '在线 online', value: 'online' },
        { label: '开启 on', value: 'on' },
        { label: '关闭 off', value: 'off' }
      ]
    }
  },
  computed: {
    onlineCount() {
      return this.devices.filter((device) => this.isOnline(device)).length
    },
    roomPickerNames() {
      return this.rooms.map((room) => room.room_name)
    },
    roomPickerIndex() {
      const index = this.rooms.findIndex((room) => room.room_id === this.deviceForm.room_id)
      return index >= 0 ? index : 0
    },
    selectedFormRoomName() {
      if (!this.rooms.length) return '请先新增房间'
      return this.rooms[this.roomPickerIndex]?.room_name || '请选择房间'
    },
    deviceTypeNames() {
      return this.deviceTypes.map((item) => item.label)
    },
    deviceTypeIndex() {
      const index = this.deviceTypes.findIndex((item) => item.value === this.deviceForm.device_type)
      return index >= 0 ? index : 0
    },
    deviceTypeLabel() {
      return this.deviceTypes[this.deviceTypeIndex]?.label || '请选择设备类型'
    },
    statusNames() {
      return this.statuses.map((item) => item.label)
    },
    statusIndex() {
      const index = this.statuses.findIndex((item) => item.value === this.deviceForm.device_status)
      return index >= 0 ? index : 0
    },
    statusLabel() {
      return this.statuses[this.statusIndex]?.label || '请选择设备状态'
    }
  },
  onShow() {
    this.init()
  },
  methods: {
    async init() {
      this.canManage = canManageBaseData()
      const homes = await listHomes()
      if (homes && homes.length > 0) {
        this.homeId = homes[0].home_id
      }
      await this.loadRooms()
      await this.loadDevices()
    },
    async loadRooms() {
      this.rooms = await listRooms(this.homeId)
    },
    async loadDevices() {
      this.devices = await listDevices(this.homeId, this.selectedRoomId || undefined)
    },
    selectRoom(roomId) {
      this.selectedRoomId = roomId
      this.loadDevices()
    },
    roomName(roomId) {
      const room = this.rooms.find((item) => item.room_id === roomId)
      return room ? room.room_name : `房间 #${roomId}`
    },
    isOnline(device) {
      return ['online', 'on'].includes(device.device_status)
    },
    typeShort(type) {
      const map = {
        light: '灯',
        socket: '插',
        temperature_sensor: '温',
        smoke_sensor: '烟',
        gas_sensor: '气',
        door_sensor: '门'
      }
      return map[type] || '设'
    },
    typeClass(type) {
      if (type && type.includes('sensor')) return 'sensor'
      if (type === 'light') return 'light'
      if (type === 'socket') return 'socket'
      return ''
    },
    layoutText(device) {
      const layout = device.layout
      if (!layout) return '未设置'
      return `X ${layout.position_x}, Y ${layout.position_y}, Z ${layout.position_z}`
    },
    async switchDevice(device, state) {
      await controlDevice(device.device_id, state)
      uni.showToast({ title: state === 'on' ? '已开启' : '已关闭', icon: 'success' })
      await this.loadDevices()
    },
    goDetail(device) {
      uni.navigateTo({ url: `/pages/device-detail/device-detail?id=${device.device_id}` })
    },
    goRooms() {
      uni.navigateTo({ url: '/pages/rooms/rooms' })
    },
    openCreateDevice() {
      if (!this.canManage) {
        showReadonlyToast()
        return
      }
      if (!this.rooms.length) {
        uni.showModal({
          title: '需要房间',
          content: '新增设备前需要先创建房间。',
          confirmText: '去创建',
          success: (res) => {
            if (res.confirm) this.goRooms()
          }
        })
        return
      }
      this.editingDevice = null
      this.deviceForm = {
        room_id: this.selectedRoomId || this.rooms[0].room_id,
        device_name: '',
        device_type: 'light',
        device_status: 'offline',
        is_key_device: false
      }
      this.showDeviceForm = true
    },
    openEditDevice(device) {
      this.editingDevice = device
      this.deviceForm = {
        room_id: device.room_id,
        device_name: device.device_name || '',
        device_type: device.device_type || 'light',
        device_status: device.device_status || 'offline',
        is_key_device: Boolean(device.is_key_device)
      }
      this.showDeviceForm = true
    },
    closeDeviceForm() {
      this.showDeviceForm = false
    },
    onRoomPick(event) {
      const room = this.rooms[Number(event.detail.value)]
      if (room) this.deviceForm.room_id = room.room_id
    },
    onDeviceTypePick(event) {
      const item = this.deviceTypes[Number(event.detail.value)]
      if (item) this.deviceForm.device_type = item.value
    },
    onStatusPick(event) {
      const item = this.statuses[Number(event.detail.value)]
      if (item) this.deviceForm.device_status = item.value
    },
    onKeyDeviceChange(event) {
      this.deviceForm.is_key_device = event.detail.value
    },
    async submitDeviceForm() {
      if (!this.deviceForm.room_id) {
        uni.showToast({ title: '请选择房间', icon: 'none' })
        return
      }
      if (!this.deviceForm.device_name.trim()) {
        uni.showToast({ title: '请输入设备名称', icon: 'none' })
        return
      }
      const data = {
        room_id: Number(this.deviceForm.room_id),
        device_name: this.deviceForm.device_name.trim(),
        device_type: this.deviceForm.device_type,
        device_status: this.deviceForm.device_status,
        is_key_device: Boolean(this.deviceForm.is_key_device)
      }
      if (this.editingDevice) {
        await updateDevice(this.editingDevice.device_id, data)
        uni.showToast({ title: '设备已更新', icon: 'success' })
      } else {
        await createDevice(this.homeId, data)
        uni.showToast({ title: '设备已新增', icon: 'success' })
      }
      this.closeDeviceForm()
      await this.loadDevices()
    },
    confirmDeleteDevice(device) {
      uni.showModal({
        title: '删除设备',
        content: `确认删除「${device.device_name}」吗？`,
        confirmColor: '#ef4444',
        success: async (res) => {
          if (res.confirm) {
            await deleteDevice(device.device_id)
            uni.showToast({ title: '设备已删除', icon: 'success' })
            await this.loadDevices()
          }
        }
      })
    }
  }
}
</script>

<style scoped>
.devices-page {
  background: #f5f7fb;
}

.page-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
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

.overview-card {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 2rpx;
  overflow: hidden;
  border-radius: 18rpx;
  background: #e5e7eb;
}

.overview-item {
  padding: 24rpx 12rpx;
  text-align: center;
  background: #ffffff;
}

.overview-number {
  font-size: 40rpx;
  font-weight: 800;
  color: #111827;
}

.overview-label {
  margin-top: 6rpx;
  color: #6b7280;
  font-size: 22rpx;
}

.room-scroll {
  white-space: nowrap;
  margin-bottom: 22rpx;
}

.room-tabs {
  display: flex;
  gap: 14rpx;
}

.room-tab {
  padding: 16rpx 24rpx;
  border-radius: 999rpx;
  background: #ffffff;
  color: #64748b;
  font-size: 24rpx;
}

.room-tab.active {
  background: #2563eb;
  color: #ffffff;
  font-weight: 700;
}

.device-card {
  margin-bottom: 20rpx;
}

.device-left {
  display: flex;
  align-items: center;
  gap: 18rpx;
}

.device-type {
  width: 72rpx;
  height: 72rpx;
  line-height: 72rpx;
  border-radius: 18rpx;
  background: #eef2ff;
  color: #3730a3;
  text-align: center;
  font-size: 28rpx;
  font-weight: 800;
}

.device-type.sensor {
  background: #fef3c7;
  color: #92400e;
}

.device-type.light {
  background: #dcfce7;
  color: #15803d;
}

.device-type.socket {
  background: #e0f2fe;
  color: #0369a1;
}

.device-name {
  font-size: 32rpx;
  font-weight: 800;
  color: #111827;
}

.device-meta {
  display: flex;
  justify-content: space-between;
  margin-top: 18rpx;
  color: #94a3b8;
  font-size: 22rpx;
}

.device-extra {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12rpx;
  margin-top: 18rpx;
  padding: 18rpx;
  border-radius: 14rpx;
  background: #f8fafc;
}

.extra-item {
  min-width: 0;
}

.extra-item.wide {
  grid-column: span 2;
}

.extra-label,
.extra-value {
  display: block;
}

.extra-label {
  color: #94a3b8;
  font-size: 20rpx;
}

.extra-value {
  margin-top: 4rpx;
  color: #334155;
  font-size: 23rpx;
  word-break: break-all;
}

.device-actions,
.manage-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16rpx;
  margin-top: 22rpx;
}

.action-button,
.manage-button {
  height: 72rpx;
  line-height: 72rpx;
  border-radius: 12rpx;
  font-size: 26rpx;
}

.action-button.on {
  background: #dcfce7;
  color: #15803d;
}

.action-button.off {
  background: #f1f5f9;
  color: #334155;
}

.manage-button {
  background: #eef2ff;
  color: #1d4ed8;
}

.manage-button.danger {
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
  color: #111827;
}

.field-label,
.field-title {
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

.switch-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20rpx;
  margin-top: 22rpx;
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
