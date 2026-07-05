<template>
  <view class="page visual-page">
    <view class="section">
      <text class="title">空间可视化</text>
      <text class="subtitle">用 2.5D 房屋视图展示房间、设备和安全状态</text>
    </view>

    <view class="section house-card">
      <view class="house-roof"></view>
      <view class="house-body">
        <view
          v-for="room in rooms"
          :key="room.room_id"
          :class="['room-cell', selectedRoomId === room.room_id ? 'active' : '']"
          @tap="selectRoom(room.room_id)"
        >
          <view class="room-title">{{ room.room_name }}</view>
          <view class="room-type">{{ room.room_type || 'room' }}</view>
          <view class="room-layout">{{ roomLayoutText(room) }}</view>
          <view class="device-dots">
            <view
              v-for="device in roomDevices(room.room_id)"
              :key="device.device_id"
              :class="['dot', device.is_key_device ? 'key' : '', isOnline(device) ? 'on' : '']"
              :style="dotStyle(device)"
            ></view>
          </view>
        </view>
      </view>
    </view>

    <view class="section card">
      <view class="row">
        <view>
          <view class="detail-title">{{ selectedRoomName }}</view>
          <view class="muted">当前房间设备分布</view>
        </view>
        <view class="tag">{{ selectedDevices.length }} 台设备</view>
      </view>
      <view v-if="selectedDevices.length === 0" class="empty small">该房间暂无设备</view>
      <view v-for="device in selectedDevices" :key="device.device_id" class="device-line" @tap="goDetail(device)">
        <view>
          <view class="device-name">{{ device.device_name }}</view>
          <view class="muted">{{ device.device_type }} · {{ deviceLayoutText(device) }}</view>
        </view>
        <view :class="['mini-status', isOnline(device) ? 'on' : '']">{{ device.device_status }}</view>
      </view>
    </view>

    <view class="section legend">
      <view class="legend-item"><view class="dot on"></view>在线/开启</view>
      <view class="legend-item"><view class="dot"></view>离线/关闭</view>
      <view class="legend-item"><view class="dot key"></view>安全关键设备</view>
    </view>
  </view>
</template>

<script>
import { listHomes } from '../../api/homes.js'
import { listDevices, listRooms } from '../../api/devices.js'

export default {
  data() {
    return {
      homeId: 1,
      rooms: [],
      devices: [],
      selectedRoomId: 0
    }
  },
  computed: {
    selectedRoomName() {
      const room = this.rooms.find((item) => item.room_id === this.selectedRoomId)
      return room ? room.room_name : '全部空间'
    },
    selectedDevices() {
      if (!this.selectedRoomId) return this.devices
      return this.devices.filter((device) => device.room_id === this.selectedRoomId)
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
      const [rooms, devices] = await Promise.all([listRooms(this.homeId), listDevices(this.homeId)])
      this.rooms = rooms || []
      this.devices = devices || []
      if (!this.selectedRoomId && this.rooms.length > 0) {
        this.selectedRoomId = this.rooms[0].room_id
      }
    },
    selectRoom(roomId) {
      this.selectedRoomId = roomId
    },
    roomDevices(roomId) {
      return this.devices.filter((device) => device.room_id === roomId)
    },
    isOnline(device) {
      return ['online', 'on'].includes(device.device_status)
    },
    roomLayoutText(room) {
      const layout = room.layout
      if (!layout) return '布局未设置'
      return `位置 ${layout.position_x}, ${layout.position_y} · ${layout.width}×${layout.height}`
    },
    deviceLayoutText(device) {
      const layout = device.layout
      if (!layout) return '坐标未设置'
      return `X${layout.position_x} Y${layout.position_y} Z${layout.position_z}`
    },
    dotStyle(device) {
      const layout = device.layout
      if (!layout) return ''
      const left = Math.max(8, Math.min(84, Number(layout.position_x || 0) * 16))
      const top = Math.max(8, Math.min(76, Number(layout.position_y || 0) * 18))
      return `left:${left}%;top:${top}%;`
    },
    goDetail(device) {
      uni.navigateTo({ url: `/pages/device-detail/device-detail?id=${device.device_id}` })
    }
  }
}
</script>

<style scoped>
.visual-page {
  background: linear-gradient(180deg, #f8fafc 0%, #eef2ff 100%);
}

.house-card {
  padding: 38rpx 28rpx 32rpx;
  border-radius: 24rpx;
  background: #ffffff;
  box-shadow: 0 24rpx 60rpx rgba(37, 99, 235, 0.14);
}

.house-roof {
  width: 70%;
  height: 74rpx;
  margin: 0 auto -6rpx;
  transform: skewX(-24deg);
  border-radius: 10rpx 18rpx 8rpx 8rpx;
  background: linear-gradient(135deg, #2563eb, #38bdf8);
}

.house-body {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16rpx;
  padding: 20rpx;
  border: 4rpx solid #dbeafe;
  border-radius: 20rpx;
  background: #eff6ff;
  transform: perspective(800rpx) rotateX(5deg);
  transform-origin: top center;
}

.room-cell {
  min-height: 170rpx;
  padding: 20rpx;
  border-radius: 16rpx;
  background: #ffffff;
  box-shadow: inset 0 0 0 2rpx #e5e7eb;
}

.room-cell.active {
  box-shadow: inset 0 0 0 4rpx #2563eb;
}

.room-title {
  font-size: 28rpx;
  font-weight: 800;
  color: #111827;
}

.room-type {
  margin-top: 8rpx;
  color: #94a3b8;
  font-size: 22rpx;
}

.room-layout {
  margin-top: 8rpx;
  color: #64748b;
  font-size: 20rpx;
}

.device-dots {
  position: relative;
  min-height: 62rpx;
  margin-top: 24rpx;
}

.dot {
  position: absolute;
  width: 18rpx;
  height: 18rpx;
  border-radius: 50%;
  background: #cbd5e1;
  transform: translate(-50%, -50%);
}

.dot.on {
  background: #22c55e;
}

.dot.key {
  width: 22rpx;
  height: 22rpx;
  background: #f97316;
}

.detail-title {
  font-size: 32rpx;
  font-weight: 800;
  color: #111827;
}

.device-line {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 22rpx 0;
  border-top: 2rpx solid #f1f5f9;
}

.device-name {
  font-size: 28rpx;
  font-weight: 700;
}

.mini-status {
  padding: 8rpx 14rpx;
  border-radius: 999rpx;
  background: #f1f5f9;
  color: #64748b;
  font-size: 22rpx;
}

.mini-status.on {
  background: #dcfce7;
  color: #15803d;
}

.legend {
  display: flex;
  flex-wrap: wrap;
  gap: 18rpx;
  color: #64748b;
  font-size: 23rpx;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 10rpx;
}

.empty.small {
  padding: 34rpx 0 10rpx;
}
</style>
