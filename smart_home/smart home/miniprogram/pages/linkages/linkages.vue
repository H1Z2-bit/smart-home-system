<template>
  <view class="page">
    <view class="section page-head">
      <view>
        <text class="title">联动规则</text>
        <text class="subtitle">配置触发条件与动作，实现自动化联动</text>
      </view>
      <button class="head-button" @tap="openCreate">新增</button>
    </view>

    <view class="section rule-summary">
      <view>
        <view class="summary-number">{{ rules.length }}</view>
        <view class="summary-label">规则总数</view>
      </view>
      <view>
        <view class="summary-number">{{ enabledCount }}</view>
        <view class="summary-label">启用中</view>
      </view>
    </view>

    <view v-if="rules.length === 0" class="empty">暂无联动规则</view>

    <view v-for="rule in rules" :key="rule.rule_id" class="card rule-card">
      <view class="row">
        <view>
          <view class="rule-title">{{ rule.rule_name }}</view>
          <view class="muted">规则 #{{ rule.rule_id }}</view>
        </view>
        <switch :checked="rule.enabled" @change="toggleEnabled(rule, $event)" />
      </view>

      <view class="json-box">
        <view class="json-title">触发条件</view>
        <view class="json-text">{{ stringify(rule.trigger_condition) }}</view>
      </view>
      <view class="json-box">
        <view class="json-title">动作配置</view>
        <view class="json-text">{{ stringify(rule.action_config) }}</view>
      </view>

      <view class="button-grid">
        <button class="small-button" @tap="openEdit(rule)">编辑</button>
        <button class="small-button danger" @tap="confirmDelete(rule)">删除</button>
      </view>
    </view>

    <view v-if="showForm" class="mask" @tap="closeForm">
      <view class="form-panel" @tap.stop>
        <view class="form-title">{{ editingRule ? '编辑联动规则' : '新增联动规则' }}</view>
        <input class="input" v-model="form.rule_name" placeholder="规则名称，例如 烟雾报警联动" />
        <view class="field-label">触发条件 JSON</view>
        <textarea class="textarea" v-model="form.trigger_condition" />
        <view class="field-label">动作配置 JSON</view>
        <textarea class="textarea" v-model="form.action_config" />
        <view class="switch-row">
          <view>
            <view class="field-title">启用规则</view>
            <view class="muted">关闭后规则仍保留但不参与联动</view>
          </view>
          <switch :checked="form.enabled" @change="form.enabled = $event.detail.value" />
        </view>
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
import { createLinkage, deleteLinkage, listLinkages, updateLinkage } from '../../api/linkages.js'

const defaultTrigger = {
  device_type: 'smoke_sensor',
  metric_name: 'smoke',
  operator: '>',
  value: 80
}

const defaultAction = {
  action: 'create_alarm',
  alarm_type: 'smoke',
  alarm_level: 'warning'
}

export default {
  data() {
    return {
      homeId: 1,
      rules: [],
      showForm: false,
      editingRule: null,
      form: {
        rule_name: '',
        trigger_condition: JSON.stringify(defaultTrigger, null, 2),
        action_config: JSON.stringify(defaultAction, null, 2),
        enabled: true
      }
    }
  },
  computed: {
    enabledCount() {
      return this.rules.filter((item) => item.enabled).length
    }
  },
  onShow() {
    this.init()
  },
  methods: {
    async init() {
      const homes = await listHomes()
      if (homes && homes.length > 0) this.homeId = homes[0].home_id
      this.rules = await listLinkages(this.homeId)
    },
    stringify(value) {
      try {
        return JSON.stringify(value || {}, null, 2)
      } catch (error) {
        return String(value || '')
      }
    },
    openCreate() {
      this.editingRule = null
      this.form = {
        rule_name: '',
        trigger_condition: JSON.stringify(defaultTrigger, null, 2),
        action_config: JSON.stringify(defaultAction, null, 2),
        enabled: true
      }
      this.showForm = true
    },
    openEdit(rule) {
      this.editingRule = rule
      this.form = {
        rule_name: rule.rule_name || '',
        trigger_condition: this.stringify(rule.trigger_condition),
        action_config: this.stringify(rule.action_config),
        enabled: Boolean(rule.enabled)
      }
      this.showForm = true
    },
    closeForm() {
      this.showForm = false
    },
    parseJson(text, label) {
      try {
        return JSON.parse(text)
      } catch (error) {
        uni.showToast({ title: `${label}不是有效 JSON`, icon: 'none' })
        throw error
      }
    },
    async submitForm() {
      if (!this.form.rule_name.trim()) {
        uni.showToast({ title: '请输入规则名称', icon: 'none' })
        return
      }
      let triggerCondition
      let actionConfig
      try {
        triggerCondition = this.parseJson(this.form.trigger_condition, '触发条件')
        actionConfig = this.parseJson(this.form.action_config, '动作配置')
      } catch (error) {
        return
      }

      const data = {
        rule_name: this.form.rule_name.trim(),
        trigger_condition: triggerCondition,
        action_config: actionConfig,
        enabled: Boolean(this.form.enabled),
        created_by: 1
      }

      if (this.editingRule) {
        await updateLinkage(this.editingRule.rule_id, data)
        uni.showToast({ title: '规则已更新', icon: 'success' })
      } else {
        await createLinkage(this.homeId, data)
        uni.showToast({ title: '规则已新增', icon: 'success' })
      }
      this.closeForm()
      await this.init()
    },
    async toggleEnabled(rule, event) {
      await updateLinkage(rule.rule_id, { enabled: event.detail.value })
      uni.showToast({ title: event.detail.value ? '已启用' : '已停用', icon: 'success' })
      await this.init()
    },
    confirmDelete(rule) {
      uni.showModal({
        title: '删除联动规则',
        content: `确认删除「${rule.rule_name}」吗？`,
        confirmColor: '#ef4444',
        success: async (res) => {
          if (res.confirm) {
            await deleteLinkage(rule.rule_id)
            uni.showToast({ title: '规则已删除', icon: 'success' })
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

.rule-summary {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 2rpx;
  overflow: hidden;
  border-radius: 18rpx;
  background: #e5e7eb;
}

.rule-summary > view {
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

.rule-card {
  margin-bottom: 20rpx;
}

.rule-title {
  font-size: 32rpx;
  font-weight: 800;
}

.json-box {
  margin-top: 18rpx;
  padding: 18rpx;
  border-radius: 14rpx;
  background: #f8fafc;
}

.json-title {
  margin-bottom: 8rpx;
  color: #111827;
  font-size: 24rpx;
  font-weight: 700;
}

.json-text {
  white-space: pre-wrap;
  color: #475569;
  font-size: 22rpx;
  line-height: 1.5;
}

.button-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14rpx;
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

.field-label,
.field-title {
  margin-top: 22rpx;
  color: #111827;
  font-size: 26rpx;
  font-weight: 700;
}

.textarea {
  width: 100%;
  min-height: 220rpx;
  box-sizing: border-box;
  margin-top: 12rpx;
  padding: 20rpx 24rpx;
  border: 2rpx solid #e5e7eb;
  border-radius: 12rpx;
  background: #ffffff;
  font-size: 24rpx;
  line-height: 1.5;
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
