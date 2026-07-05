<template>
  <view class="page">
    <view class="section page-head">
      <view>
        <text class="title">房间管理</text>
        <text class="subtitle">维护家庭空间下的房间信息</text>
      </view>
      <button class="head-button" @tap="openCreate">{{ canManage ? '新增' : '只读' }}</button>
    </view>

    <view class="section summary-card">
      <view>
        <view class="summary-number">{{ rooms.length }}</view>
        <view class="summary-label">房间数量</view>
      </view>
      <view>
        <view class="summary-number">{{ currentHomeName }}</view>
        <view class="summary-label">当前家庭</view>
      </view>
    </view>

    <view v-if="loading" class="empty">正在加载房间...</view>
    <view v-else-if="rooms.length === 0" class="empty">暂无房间，点击右上角新增</view>

    <block v-else>
      <view v-for="room in rooms" :key="room.room_id" class="card room-card">
        <view class="row">
          <view>
            <view class="room-name">{{ room.room_name }}</view>
            <view class="muted">{{ room.room_type || '未设置类型' }}</view>
          </view>
          <view class="room-id">#{{ room.room_id }}</view>
        </view>
        <view class="remark">{{ room.remark || '暂无备注' }}</view>
        <view v-if="canManage" class="actions">
          <button class="small-button" @tap="openEdit(room)">编辑</button>
          <button class="small-button danger" @tap="confirmDelete(room)">删除</button>
        </view>
      </view>
    </block>

    <view v-if="showForm" class="mask" @tap="closeForm">
      <view class="form-panel" @tap.stop>
        <view class="form-title">{{ editingRoom ? '编辑房间' : '新增房间' }}</view>
        <input class="input" v-model="form.room_name" placeholder="房间名称，例如 客厅" />
        <input class="input" v-model="form.room_type" placeholder="房间类型，例如 living_room" />
        <textarea class="textarea" v-model="form.remark" placeholder="备注，可选" />
        <view class="form-actions">
          <button class="form-button cancel" @tap="closeForm">取消</button>
          <button class="form-button save" @tap="submitForm">保存</button>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { listHomes } from '../../api/homes.js'
import { createRoom, deleteRoom, listRooms, updateRoom } from '../../api/devices.js'
import { canManageBaseData, showReadonlyToast } from '../../utils/permission.js'

export default {
  data() {
    return {
      homeId: 1,
      homes: [],
      rooms: [],
      showForm: false,
      editingRoom: null,
      form: {
        room_name: '',
        room_type: '',
        remark: ''
      },
      canManage: true,
      loading: false
    }
  },
  computed: {
    currentHomeName() {
      return this.homes && this.homes.length > 0 ? this.homes[0].name : '默认家庭'
    }
  },
  onShow() {
    this.init()
  },
  methods: {
    async init() {
      this.loading = true
      this.canManage = canManageBaseData()
      this.homes = await listHomes()
      if (this.homes && this.homes.length > 0) {
        this.homeId = this.homes[0].home_id
      }
      await this.loadRooms()
      this.loading = false
    },
    async loadRooms() {
      this.rooms = await listRooms(this.homeId)
    },
    openCreate() {
      if (!this.canManage) {
        showReadonlyToast()
        return
      }
      this.editingRoom = null
      this.form = { room_name: '', room_type: '', remark: '' }
      this.showForm = true
    },
    openEdit(room) {
      this.editingRoom = room
      this.form = {
        room_name: room.room_name || '',
        room_type: room.room_type || '',
        remark: room.remark || ''
      }
      this.showForm = true
    },
    closeForm() {
      this.showForm = false
    },
    async submitForm() {
      if (!this.form.room_name.trim()) {
        uni.showToast({ title: '请输入房间名称', icon: 'none' })
        return
      }
      const data = {
        room_name: this.form.room_name.trim(),
        room_type: this.form.room_type.trim() || null,
        remark: this.form.remark.trim() || null
      }
      if (this.editingRoom) {
        await updateRoom(this.editingRoom.room_id, data)
        uni.showToast({ title: '房间已更新', icon: 'success' })
      } else {
        await createRoom(this.homeId, data)
        uni.showToast({ title: '房间已新增', icon: 'success' })
      }
      this.closeForm()
      await this.loadRooms()
    },
    confirmDelete(room) {
      uni.showModal({
        title: '删除房间',
        content: `确认删除「${room.room_name}」吗？如果房间下存在设备，后端会拒绝删除。`,
        confirmColor: '#ef4444',
        success: async (res) => {
          if (res.confirm) {
            await deleteRoom(room.room_id)
            uni.showToast({ title: '房间已删除', icon: 'success' })
            await this.loadRooms()
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

.summary-card {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 2rpx;
  overflow: hidden;
  border-radius: 18rpx;
  background: #e5e7eb;
}

.summary-card > view {
  padding: 24rpx;
  background: #ffffff;
}

.summary-number {
  font-size: 34rpx;
  font-weight: 800;
  color: #111827;
}

.summary-label {
  margin-top: 8rpx;
  color: #6b7280;
  font-size: 22rpx;
}

.room-card {
  margin-bottom: 20rpx;
}

.room-name {
  font-size: 32rpx;
  font-weight: 800;
  color: #111827;
}

.room-id {
  padding: 10rpx 16rpx;
  border-radius: 999rpx;
  background: #eff6ff;
  color: #1d4ed8;
  font-size: 22rpx;
  font-weight: 700;
}

.remark {
  margin-top: 18rpx;
  color: #64748b;
  font-size: 24rpx;
}

.actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16rpx;
  margin-top: 24rpx;
}

.small-button {
  height: 70rpx;
  line-height: 70rpx;
  border-radius: 12rpx;
  background: #eef2ff;
  color: #1d4ed8;
  font-size: 25rpx;
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
  padding: 34rpx 28rpx 48rpx;
  border-radius: 28rpx 28rpx 0 0;
  background: #ffffff;
}

.form-title {
  font-size: 34rpx;
  font-weight: 800;
  color: #111827;
}

.textarea {
  width: 100%;
  min-height: 150rpx;
  box-sizing: border-box;
  margin-top: 20rpx;
  padding: 20rpx 24rpx;
  border: 2rpx solid #e5e7eb;
  border-radius: 12rpx;
  background: #ffffff;
  font-size: 28rpx;
}

.form-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18rpx;
  margin-top: 26rpx;
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
