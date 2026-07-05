<template>
  <view class="login-page">
    <view class="hero">
      <text class="title">智能家居</text>
      <text class="subtitle">统一账号登录，管理家庭设备与安全报警</text>
    </view>

    <view class="panel">
      <view class="tabs">
        <view :class="['tab', mode === 'password' ? 'active' : '']" @tap="mode = 'password'">密码登录</view>
        <view :class="['tab', mode === 'sms' ? 'active' : '']" @tap="mode = 'sms'">验证码登录</view>
      </view>

      <input class="input" v-model="phone" placeholder="手机号" type="number" maxlength="20" />

      <template v-if="mode === 'password'">
        <input class="input" v-model="password" placeholder="密码" password maxlength="64" />
        <button class="button submit" :loading="loading" @tap="handlePasswordLogin">登录</button>
      </template>

      <template v-else>
        <view class="code-row">
          <input class="input code-input" v-model="code" placeholder="验证码" type="number" maxlength="8" />
          <button class="code-button" :disabled="sending" @tap="handleSendCode">
            {{ sending ? countdown + 's' : '获取验证码' }}
          </button>
        </view>
        <view v-if="mockCode" class="mock-code">Mock 验证码：{{ mockCode }}</view>
        <button class="button submit" :loading="loading" @tap="handleSmsLogin">验证码登录</button>
      </template>

      <view class="hint">默认账号：13800000000 / 123456</view>
    </view>
  </view>
</template>

<script>
import { loginByPassword, loginBySms, sendLoginSmsCode } from '../../api/auth.js'

export default {
  data() {
    return {
      mode: 'password',
      phone: '13800000000',
      password: '123456',
      code: '',
      mockCode: '',
      loading: false,
      sending: false,
      countdown: 0,
      timer: null
    }
  },
  onUnload() {
    if (this.timer) {
      clearInterval(this.timer)
    }
  },
  methods: {
    saveLogin(data) {
      uni.setStorageSync('token', data.token)
      uni.setStorageSync('user', data.user)
      uni.reLaunch({ url: '/pages/home/home' })
    },
    validatePhone() {
      if (!this.phone || this.phone.length < 6) {
        uni.showToast({ title: '请输入手机号', icon: 'none' })
        return false
      }
      return true
    },
    async handlePasswordLogin() {
      if (!this.validatePhone()) return
      if (!this.password) {
        uni.showToast({ title: '请输入密码', icon: 'none' })
        return
      }
      this.loading = true
      try {
        const data = await loginByPassword(this.phone, this.password)
        this.saveLogin(data)
      } finally {
        this.loading = false
      }
    },
    async handleSendCode() {
      if (!this.validatePhone() || this.sending) return
      try {
        const data = await sendLoginSmsCode(this.phone)
        this.mockCode = data.mock_code
        this.code = data.mock_code
        this.startCountdown()
      } catch (error) {
        this.sending = false
      }
    },
    async handleSmsLogin() {
      if (!this.validatePhone()) return
      if (!this.code) {
        uni.showToast({ title: '请输入验证码', icon: 'none' })
        return
      }
      this.loading = true
      try {
        const data = await loginBySms(this.phone, this.code)
        this.saveLogin(data)
      } finally {
        this.loading = false
      }
    },
    startCountdown() {
      this.sending = true
      this.countdown = 60
      if (this.timer) clearInterval(this.timer)
      this.timer = setInterval(() => {
        this.countdown -= 1
        if (this.countdown <= 0) {
          clearInterval(this.timer)
          this.timer = null
          this.sending = false
        }
      }, 1000)
    }
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  padding: 88rpx 32rpx 32rpx;
  box-sizing: border-box;
  background: linear-gradient(180deg, #dbeafe 0%, #f8fafc 46%, #f5f7fb 100%);
}

.hero {
  margin: 40rpx 0 52rpx;
}

.title {
  display: block;
  font-size: 58rpx;
  font-weight: 800;
  color: #111827;
}

.subtitle {
  display: block;
  margin-top: 16rpx;
  color: #4b5563;
  font-size: 28rpx;
  line-height: 1.6;
}

.panel {
  padding: 32rpx;
  border-radius: 24rpx;
  background: #ffffff;
  box-shadow: 0 24rpx 60rpx rgba(37, 99, 235, 0.14);
}

.tabs {
  display: grid;
  grid-template-columns: 1fr 1fr;
  padding: 6rpx;
  border-radius: 14rpx;
  background: #f1f5f9;
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
  font-weight: 700;
}

.submit {
  margin-top: 28rpx;
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

.hint {
  margin-top: 26rpx;
  text-align: center;
  color: #94a3b8;
  font-size: 24rpx;
}
</style>
