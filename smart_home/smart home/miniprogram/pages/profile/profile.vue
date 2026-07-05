<template>
  <view class="page">
    <view class="section">
      <text class="title">个人中心</text>
      <text class="subtitle">账号信息、手机号绑定、系统管理和后端连接配置</text>
    </view>

    <view class="section card">
      <view class="profile-name">{{ profile.username || '未登录' }}</view>
      <view class="info-line">手机号：{{ profile.phone || '-' }}</view>
      <view class="info-line">角色：{{ profile.role || '-' }}</view>
      <view class="info-line">
        绑定状态：
        <text :class="profile.phone_bound ? 'green' : 'orange'">
          {{ profile.phone_bound ? '已绑定' : '未绑定' }}
        </text>
      </view>
    </view>

    <view class="section card">
      <view class="block-title">管理功能</view>
      <view class="menu-grid">
        <view class="menu-item" @tap="goPage('/pages/settings/settings')">系统配置</view>
        <view class="menu-item" @tap="goPage('/pages/logs/logs')">系统日志</view>
        <view class="menu-item" @tap="goPage('/pages/schedules/schedules')">定时任务</view>
        <view class="menu-item" @tap="goPage('/pages/linkages/linkages')">联动规则</view>
        <view class="menu-item wide" @tap="goPage('/pages/demo/demo')">演示模式</view>
      </view>
    </view>

    <view class="section card">
      <view class="block-title">绑定手机号</view>
      <input class="input" v-model="bindPhoneValue" placeholder="请输入手机号" type="number" />
      <view class="code-row">
        <input class="input code-input" v-model="bindCode" placeholder="验证码" type="number" />
        <button class="code-button" @tap="handleSendBindCode">获取验证码</button>
      </view>
      <view v-if="mockBindCode" class="mock-code">Mock 验证码：{{ mockBindCode }}</view>
      <button class="button submit" @tap="handleBindPhone">绑定手机号</button>
    </view>

    <view class="section card">
      <view class="block-title">后端连接</view>
      <view class="mode-grid">
        <button class="mode-button" @tap="setSimulatorUrl">模拟器</button>
        <button class="mode-button" @tap="setLanUrl">真机</button>
      </view>
      <input class="input" v-model="baseUrl" placeholder="例如 http://127.0.0.1:8000" />
      <view class="address-actions">
        <button class="small-button" @tap="saveBaseUrl">保存地址</button>
        <button class="small-button secondary" @tap="testConnection">测试连接</button>
      </view>
      <view class="muted tip">微信开发者工具模拟器通常使用 127.0.0.1；手机真机调试使用电脑局域网 IP。</view>
    </view>

    <button class="button danger" @tap="handleLogout">退出登录</button>
  </view>
</template>

<script>
import { bindPhone, getProfile, logout, sendBindPhoneCode } from '../../api/auth.js'
import { getBaseUrl, setBaseUrl } from '../../config/index.js'

export default {
  data() {
    return {
      profile: {},
      bindPhoneValue: '',
      bindCode: '',
      mockBindCode: '',
      baseUrl: ''
    }
  },
  onShow() {
    this.baseUrl = getBaseUrl()
    this.loadProfile()
  },
  methods: {
    async loadProfile() {
      this.profile = await getProfile()
      this.bindPhoneValue = this.profile.phone || ''
      uni.setStorageSync('user', this.profile)
    },
    goPage(url) {
      uni.navigateTo({ url })
    },
    async handleSendBindCode() {
      if (!this.bindPhoneValue) {
        uni.showToast({ title: '请输入手机号', icon: 'none' })
        return
      }
      const data = await sendBindPhoneCode(this.bindPhoneValue)
      this.mockBindCode = data.mock_code
      this.bindCode = data.mock_code
    },
    async handleBindPhone() {
      if (!this.bindPhoneValue || !this.bindCode) {
        uni.showToast({ title: '请输入手机号和验证码', icon: 'none' })
        return
      }
      await bindPhone(this.bindPhoneValue, this.bindCode)
      uni.showToast({ title: '绑定成功', icon: 'success' })
      await this.loadProfile()
    },
    setSimulatorUrl() {
      this.baseUrl = 'http://127.0.0.1:8000'
      this.saveBaseUrl()
    },
    setLanUrl() {
      this.baseUrl = 'http://10.126.19.85:8000'
      this.saveBaseUrl()
    },
    saveBaseUrl() {
      this.baseUrl = setBaseUrl(this.baseUrl)
      uni.showToast({ title: '已保存', icon: 'success' })
    },
    testConnection() {
      const url = this.baseUrl.replace(/\/$/, '') + '/api/health'
      uni.request({
        url,
        method: 'GET',
        success: (res) => {
          if (res.statusCode === 200 && res.data && res.data.code === 200) {
            uni.showToast({ title: '连接成功', icon: 'success' })
          } else {
            uni.showToast({ title: '连接异常', icon: 'none' })
          }
        },
        fail: () => {
          uni.showToast({ title: '连接失败', icon: 'none' })
        }
      })
    },
    async handleLogout() {
      try {
        await logout()
      } catch (error) {
      } finally {
        uni.removeStorageSync('token')
        uni.removeStorageSync('user')
        uni.reLaunch({ url: '/pages/login/login' })
      }
    }
  }
}
</script>

<style scoped>
.profile-name {
  font-size: 38rpx;
  font-weight: 800;
  color: #111827;
}

.info-line {
  margin-top: 16rpx;
  color: #4b5563;
  font-size: 28rpx;
}

.green {
  color: #15803d;
}

.orange {
  color: #c2410c;
}

.block-title {
  margin-bottom: 18rpx;
  font-size: 30rpx;
  font-weight: 800;
  color: #111827;
}

.menu-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16rpx;
}

.menu-item {
  padding: 22rpx;
  border-radius: 14rpx;
  background: #f8fafc;
  color: #111827;
  font-size: 26rpx;
  font-weight: 700;
}

.menu-item.wide {
  grid-column: span 2;
  background: #fff7ed;
  color: #c2410c;
}

.code-row {
  display: flex;
  gap: 16rpx;
  align-items: center;
}

.code-input {
  flex: 1;
}

.code-button {
  width: 210rpx;
  height: 88rpx;
  line-height: 88rpx;
  margin-top: 20rpx;
  border-radius: 12rpx;
  background: #eef2ff;
  color: #1d4ed8;
  font-size: 24rpx;
}

.mock-code {
  margin-top: 18rpx;
  padding: 18rpx 20rpx;
  border-radius: 12rpx;
  background: #fef3c7;
  color: #92400e;
  font-size: 24rpx;
}

.mode-grid,
.address-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16rpx;
}

.mode-button,
.small-button {
  height: 72rpx;
  line-height: 72rpx;
  border-radius: 12rpx;
  background: #eef2ff;
  color: #1d4ed8;
  font-size: 25rpx;
}

.small-button.secondary {
  background: #ecfdf5;
  color: #047857;
}

.submit,
.address-actions {
  margin-top: 24rpx;
}

.tip {
  margin-top: 18rpx;
  line-height: 1.6;
}
</style>
