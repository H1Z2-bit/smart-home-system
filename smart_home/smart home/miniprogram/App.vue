<script>
export default {
  onLaunch() {
    const token = uni.getStorageSync('token')
    if (!token) {
      uni.reLaunch({ url: '/pages/login/login' })
    }
  }
}
</script>

<style>
page {
  min-height: 100%;
  background: #f5f7fb;
  color: #1f2937;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

.page {
  min-height: 100vh;
  box-sizing: border-box;
  padding: 28rpx;
}

.section {
  margin-bottom: 24rpx;
}

.card {
  padding: 28rpx;
  border-radius: 16rpx;
  background: #ffffff;
  box-shadow: 0 10rpx 28rpx rgba(17, 24, 39, 0.06);
}

.title {
  display: block;
  font-size: 42rpx;
  line-height: 1.22;
  font-weight: 700;
  color: #111827;
  letter-spacing: 0;
}

.subtitle {
  display: block;
  margin-top: 8rpx;
  font-size: 26rpx;
  line-height: 1.55;
  color: #6b7280;
  letter-spacing: 0;
}

.row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20rpx;
}

.muted {
  color: #6b7280;
  font-size: 24rpx;
}

.input {
  width: 100%;
  height: 88rpx;
  box-sizing: border-box;
  margin-top: 20rpx;
  padding: 0 24rpx;
  border: 2rpx solid #e5e7eb;
  border-radius: 12rpx;
  background: #ffffff;
  font-size: 28rpx;
}

.button {
  height: 88rpx;
  line-height: 88rpx;
  border-radius: 12rpx;
  background: #2563eb;
  color: #ffffff;
  font-size: 28rpx;
  font-weight: 600;
}

.button.secondary {
  background: #eef2ff;
  color: #1d4ed8;
}

.button.danger {
  background: #ef4444;
}

.tag {
  display: inline-flex;
  align-items: center;
  padding: 8rpx 16rpx;
  border-radius: 999rpx;
  background: #ecfdf5;
  color: #047857;
  font-size: 22rpx;
}

.tag.warn {
  background: #fff7ed;
  color: #c2410c;
}

.empty {
  padding: 60rpx 20rpx;
  text-align: center;
  color: #9ca3af;
  font-size: 26rpx;
}
</style>
