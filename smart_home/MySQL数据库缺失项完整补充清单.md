# 智能家居综合管理系统 MySQL 数据库缺失项完整补充清单

本文档用于交接给数据库负责人，基于当前文件：

`C:\Users\hanzhe\Desktop\software\smart_home.sql`

结合当前后端 FastAPI、小程序端、3D 可视化、短信验证码登录、手机号绑定、成员管理、设备模拟、自检、报警、定时任务、联动规则等功能，对数据库进行完整核对后整理。

## 1. 当前数据库已覆盖的内容

当前 `smart_home.sql` 已经包含以下核心业务表：

| 表名 | 作用 | 当前状态 |
| --- | --- | --- |
| `user_account` | 用户账号、手机号、密码、角色 | 已有 |
| `sms_code` | Mock 短信验证码 | 已有 |
| `home_space` | 家庭空间 | 已有 |
| `home_member` | 家庭成员、邀请、申请、权限 | 已有 |
| `system_config` | 系统配置、报警阈值、模拟开关 | 已有 |
| `room_area` | 房间管理 | 已有 |
| `device` | 设备管理 | 已有 |
| `scene_mode` | 情景模式 | 已有 |
| `scene_device_action` | 情景模式设备动作 | 已有 |
| `schedule_task` | 定时任务 | 已有 |
| `linkage_rule` | 联动规则 | 已有 |
| `sensor_data` | 传感器采集数据 | 已有 |
| `alarm_record` | 报警记录 | 已有 |
| `alarm_process_log` | 报警处理日志 | 已有 |
| `operation_log` | 业务操作日志 | 已有 |
| `self_check_record` | 设备自检记录 | 已有 |
| `device_simulation` | 设备模拟数据 | 已有 |

结论：从“表数量”来看，数据库主体已经比较完整，不是缺少大模块，而是需要补齐字段、修正初始化数据、统一后端字段命名，并增强 3D 可视化和答辩演示所需字段。

## 2. 必须修复项

以下内容属于必须修复，否则可能导致 SQL 导入失败、后端 MySQL 对接失败或业务逻辑不完整。

### 2.1 初始化数据中文乱码

当前 SQL 文件后半部分 `INSERT INTO` 初始数据中存在中文乱码，例如：

- `婕旂ず瀹跺涵`
- `瀹㈠巺`
- `鐑熼浘`
- `涓诲崸`
- `鍘ㄦ埧`

这些内容应该改为正常中文。

建议替换为：

| 当前乱码含义 | 建议中文 |
| --- | --- |
| `婕旂ず瀹跺涵` | 演示家庭 |
| `鍖椾含甯傛湞闃冲尯` | 北京市朝阳区 |
| `瀹㈠巺` | 客厅 |
| `涓诲崸` | 主卧 |
| `鍘ㄦ埧` | 厨房 |
| `瀹㈠巺鐏?` | 客厅灯 |
| `瀹㈠巺鎻掑骇` | 客厅插座 |
| `涓诲崸娓╁害浼犳劅鍣?` | 主卧温度传感器 |
| `鍘ㄦ埧鐑熼浘浼犳劅鍣?` | 厨房烟雾传感器 |
| `鍘ㄦ埧鐕冩皵浼犳劅鍣?` | 厨房燃气传感器 |
| `鍏ユ埛闂ㄧ` | 入户门磁 |
| `绂诲妯″紡` | 离家模式 |
| `娓呮櫒寮€鐏?` | 清晨开灯 |
| `鐑熼浘鎶ヨ鑱斿姩` | 烟雾报警联动 |

### 2.2 初始化数据疑似存在字符串引号错误

当前 SQL 中有几处由于乱码导致字符串疑似没有正常闭合，可能直接导致 MySQL 执行失败。

重点检查位置：

```sql
INSERT INTO `room_area`
INSERT INTO `device`
INSERT INTO `schedule_task`
INSERT INTO `alarm_process_log`
```

建议不要继续使用乱码版本的 `INSERT`，应整体重写一份干净的初始化数据。

### 2.3 `user_account.phone` 是否允许为空需要确认

当前设计：

```sql
`phone` VARCHAR(20) NOT NULL COMMENT 'Login phone number',
UNIQUE KEY `uk_user_phone` (`phone`)
```

如果系统只允许手机号注册和手机号登录，这样可以。

但你们目前设计过“账号登录后可选择绑定手机号，未绑定手机号也可以继续使用账号登录”，因此建议改成：

```sql
`phone` VARCHAR(20) NULL DEFAULT NULL COMMENT 'Bound phone number',
`phone_verified` TINYINT(1) NOT NULL DEFAULT 0 COMMENT 'Whether phone number is verified',
UNIQUE KEY `uk_user_phone` (`phone`)
```

说明：

- MySQL 的 `UNIQUE` 允许多个 `NULL`。
- 未绑定手机号的账号可以 `phone = NULL`。
- 绑定手机号后，`phone_verified = 1`。
- 短信验证码登录时，只允许查找 `phone_verified = 1` 的账号。

### 2.4 登录方式字段缺失

当前 `user_account` 没有明确记录用户是通过哪种方式注册的。

建议补充：

```sql
ALTER TABLE `user_account`
ADD COLUMN `register_type` VARCHAR(30) NOT NULL DEFAULT 'password'
COMMENT 'Register type: password/sms/import';
```

用途：

- `password`：账号密码注册。
- `sms`：手机号验证码注册。
- `import`：系统初始化或管理员导入。

### 2.5 账号最后登录时间缺失

建议补充：

```sql
ALTER TABLE `user_account`
ADD COLUMN `last_login_at` DATETIME NULL DEFAULT NULL COMMENT 'Last login time';
```

用途：

- 个人中心展示最近登录。
- 管理员判断账号是否长期未使用。
- 操作日志和安全审计更完整。

### 2.6 操作日志字段命名与后端存在不一致风险

当前 SQL 的 `operation_log` 字段是：

```sql
operator_id
operation_type
operation_object
operation_result
operation_desc
```

但后端另一个日志模型字段是：

```python
user_id
action
description
target_type
target_id
```

这两套含义接近，但命名不同。后续真正接入 MySQLRepository 时必须统一。

建议方案一：保留当前 `operation_log` 作为业务操作日志，同时新增 `account_operation_log` 用于账号、安全、登录类日志。

建议方案二：只保留一张 `operation_log`，但后端所有日志模型都改为 SQL 当前字段。

更推荐方案一，因为业务日志和账号安全日志关注点不同。

## 3. 建议新增表

### 3.1 新增账号安全日志表 `account_operation_log`

当前业务中存在以下账号安全行为：

- 用户注册。
- 用户登录。
- 短信验证码登录。
- 修改密码。
- 绑定手机号。
- 发送验证码。
- 成员邀请。
- 成员申请。
- 权限变更。

这些不完全适合放在设备、房间、报警类业务日志中，建议单独建表。

```sql
CREATE TABLE `account_operation_log` (
  `log_id` BIGINT NOT NULL AUTO_INCREMENT COMMENT 'Log ID',
  `user_id` BIGINT NULL DEFAULT NULL COMMENT 'User ID, nullable before login',
  `home_id` BIGINT NULL DEFAULT NULL COMMENT 'Related home ID',
  `action` VARCHAR(80) NOT NULL COMMENT 'Action such as login/register/bind_phone/change_password',
  `description` VARCHAR(500) NOT NULL COMMENT 'Operation description',
  `target_type` VARCHAR(80) NULL DEFAULT NULL COMMENT 'Target type such as user/home/member',
  `target_id` BIGINT NULL DEFAULT NULL COMMENT 'Target ID',
  `ip_address` VARCHAR(64) NULL DEFAULT NULL COMMENT 'Client IP address',
  `user_agent` VARCHAR(255) NULL DEFAULT NULL COMMENT 'Client user agent',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Created time',
  PRIMARY KEY (`log_id`),
  KEY `idx_account_log_user` (`user_id`),
  KEY `idx_account_log_home` (`home_id`),
  KEY `idx_account_log_action` (`action`),
  KEY `idx_account_log_time` (`created_at`),
  CONSTRAINT `fk_account_log_user` FOREIGN KEY (`user_id`) REFERENCES `user_account` (`user_id`) ON DELETE SET NULL,
  CONSTRAINT `fk_account_log_home` FOREIGN KEY (`home_id`) REFERENCES `home_space` (`home_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Account and security operation log';
```

### 3.2 新增设备事件表 `device_event`

当前已有 `sensor_data` 和 `device_simulation`，但缺少设备状态变化事件记录。

建议新增：

```sql
CREATE TABLE `device_event` (
  `event_id` BIGINT NOT NULL AUTO_INCREMENT COMMENT 'Event ID',
  `home_id` BIGINT NOT NULL COMMENT 'Home ID',
  `device_id` BIGINT NOT NULL COMMENT 'Device ID',
  `event_type` VARCHAR(50) NOT NULL COMMENT 'online/offline/status_change/control/fault/recover',
  `old_status` VARCHAR(30) NULL DEFAULT NULL COMMENT 'Old device status',
  `new_status` VARCHAR(30) NULL DEFAULT NULL COMMENT 'New device status',
  `event_desc` VARCHAR(500) NULL DEFAULT NULL COMMENT 'Event description',
  `operator_id` BIGINT NULL DEFAULT NULL COMMENT 'Operator user ID, null means system',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Created time',
  PRIMARY KEY (`event_id`),
  KEY `idx_device_event_home` (`home_id`),
  KEY `idx_device_event_device` (`device_id`),
  KEY `idx_device_event_type` (`event_type`),
  KEY `idx_device_event_time` (`created_at`),
  CONSTRAINT `fk_device_event_home` FOREIGN KEY (`home_id`) REFERENCES `home_space` (`home_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_device_event_device` FOREIGN KEY (`device_id`) REFERENCES `device` (`device_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_device_event_operator` FOREIGN KEY (`operator_id`) REFERENCES `user_account` (`user_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Device status and control event';
```

用途：

- 记录设备开关变化。
- 记录设备上线、离线。
- 记录故障和恢复。
- 方便设备详情页展示“设备动态”。

### 3.3 新增 3D 房间布局表 `room_layout`

如果后续要做更细致的 3D 或 2.5D 空间可视化，建议不要把所有布局字段都塞进 `room_area`。

```sql
CREATE TABLE `room_layout` (
  `layout_id` BIGINT NOT NULL AUTO_INCREMENT COMMENT 'Layout ID',
  `room_id` BIGINT NOT NULL COMMENT 'Room ID',
  `position_x` DECIMAL(10,2) NOT NULL DEFAULT 0 COMMENT 'Room X position',
  `position_y` DECIMAL(10,2) NOT NULL DEFAULT 0 COMMENT 'Room Y position',
  `width` DECIMAL(10,2) NOT NULL DEFAULT 4 COMMENT 'Room width',
  `height` DECIMAL(10,2) NOT NULL DEFAULT 3 COMMENT 'Room height',
  `floor_no` INT NOT NULL DEFAULT 1 COMMENT 'Floor number',
  `wall_color` VARCHAR(30) NULL DEFAULT NULL COMMENT 'Wall color',
  `floor_color` VARCHAR(30) NULL DEFAULT NULL COMMENT 'Floor color',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Created time',
  `updated_at` DATETIME NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT 'Updated time',
  PRIMARY KEY (`layout_id`),
  UNIQUE KEY `uk_layout_room` (`room_id`),
  CONSTRAINT `fk_layout_room` FOREIGN KEY (`room_id`) REFERENCES `room_area` (`room_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Room layout for 2.5D or 3D visualization';
```

### 3.4 新增 3D 设备布局表 `device_layout`

用于记录设备在房间或 3D 场景中的位置、朝向、图标、模型等。

```sql
CREATE TABLE `device_layout` (
  `layout_id` BIGINT NOT NULL AUTO_INCREMENT COMMENT 'Layout ID',
  `device_id` BIGINT NOT NULL COMMENT 'Device ID',
  `position_x` DECIMAL(10,2) NOT NULL DEFAULT 0 COMMENT 'Device X position',
  `position_y` DECIMAL(10,2) NOT NULL DEFAULT 0 COMMENT 'Device Y position',
  `position_z` DECIMAL(10,2) NOT NULL DEFAULT 0 COMMENT 'Device Z position',
  `rotation_x` DECIMAL(10,2) NOT NULL DEFAULT 0 COMMENT 'Device X rotation',
  `rotation_y` DECIMAL(10,2) NOT NULL DEFAULT 0 COMMENT 'Device Y rotation',
  `rotation_z` DECIMAL(10,2) NOT NULL DEFAULT 0 COMMENT 'Device Z rotation',
  `icon_name` VARCHAR(80) NULL DEFAULT NULL COMMENT 'Icon name for mini program',
  `model_name` VARCHAR(100) NULL DEFAULT NULL COMMENT '3D model name',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Created time',
  `updated_at` DATETIME NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT 'Updated time',
  PRIMARY KEY (`layout_id`),
  UNIQUE KEY `uk_device_layout_device` (`device_id`),
  CONSTRAINT `fk_device_layout_device` FOREIGN KEY (`device_id`) REFERENCES `device` (`device_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Device layout for 2.5D or 3D visualization';
```

## 4. 建议补充字段

### 4.1 `user_account` 建议补充字段

```sql
ALTER TABLE `user_account`
MODIFY COLUMN `phone` VARCHAR(20) NULL DEFAULT NULL COMMENT 'Bound phone number',
ADD COLUMN `register_type` VARCHAR(30) NOT NULL DEFAULT 'password' COMMENT 'password/sms/import',
ADD COLUMN `last_login_at` DATETIME NULL DEFAULT NULL COMMENT 'Last login time';
```

如果不支持未绑定手机号账号，可以不修改 `phone` 的 `NOT NULL`。

### 4.2 `home_space` 建议补充字段

```sql
ALTER TABLE `home_space`
ADD COLUMN `cover_url` VARCHAR(255) NULL DEFAULT NULL COMMENT 'Home cover image',
ADD COLUMN `status` VARCHAR(20) NOT NULL DEFAULT 'ACTIVE' COMMENT 'ACTIVE/DISABLED';
```

用途：

- 小程序首页展示家庭封面。
- 软删除或禁用家庭空间。

### 4.3 `room_area` 建议补充字段

```sql
ALTER TABLE `room_area`
ADD COLUMN `sort_no` INT NOT NULL DEFAULT 1 COMMENT 'Room display order',
ADD COLUMN `status` VARCHAR(20) NOT NULL DEFAULT 'ACTIVE' COMMENT 'ACTIVE/DISABLED';
```

用途：

- 小程序房间列表排序。
- 删除房间时可做逻辑删除。

### 4.4 `device` 建议补充字段

```sql
ALTER TABLE `device`
ADD COLUMN `manufacturer` VARCHAR(100) NULL DEFAULT NULL COMMENT 'Device manufacturer',
ADD COLUMN `model` VARCHAR(100) NULL DEFAULT NULL COMMENT 'Device model',
ADD COLUMN `serial_no` VARCHAR(100) NULL DEFAULT NULL COMMENT 'Device serial number',
ADD COLUMN `last_online_at` DATETIME NULL DEFAULT NULL COMMENT 'Last online time',
ADD COLUMN `last_offline_at` DATETIME NULL DEFAULT NULL COMMENT 'Last offline time',
ADD COLUMN `remark` VARCHAR(255) NULL DEFAULT NULL COMMENT 'Device remark',
ADD UNIQUE KEY `uk_device_serial_no` (`serial_no`);
```

用途：

- 设备详情页更完整。
- 支持设备厂商、型号、编号展示。
- 设备离线报警更合理。

### 4.5 `scene_mode` 建议补充字段

```sql
ALTER TABLE `scene_mode`
ADD COLUMN `scene_desc` VARCHAR(255) NULL DEFAULT NULL COMMENT 'Scene description',
ADD COLUMN `icon_name` VARCHAR(80) NULL DEFAULT NULL COMMENT 'Scene icon name',
ADD COLUMN `sort_no` INT NOT NULL DEFAULT 1 COMMENT 'Scene display order';
```

用途：

- 小程序场景模式页展示更细致。
- 答辩时展示“回家模式、离家模式、睡眠模式”等更完整。

### 4.6 `scene_device_action` 建议补充字段

当前只有：

```sql
target_state
param_value
```

建议补充：

```sql
ALTER TABLE `scene_device_action`
ADD COLUMN `action` VARCHAR(50) NOT NULL DEFAULT 'switch' COMMENT 'Action type such as switch/set_temperature/set_brightness';
```

用途：

- 和设备控制接口保持一致。
- 不仅支持开关，还能支持亮度、温度、模式等。

### 4.7 `schedule_task` 建议补充字段

当前已有 `schedule_type` 和 `cron_expr`，建议再补：

```sql
ALTER TABLE `schedule_task`
ADD COLUMN `last_run_at` DATETIME NULL DEFAULT NULL COMMENT 'Last run time',
ADD COLUMN `next_run_at` DATETIME NULL DEFAULT NULL COMMENT 'Next run time',
ADD COLUMN `run_count` INT NOT NULL DEFAULT 0 COMMENT 'Run count',
ADD COLUMN `fail_reason` VARCHAR(500) NULL DEFAULT NULL COMMENT 'Last fail reason';
```

用途：

- 定时任务列表展示“上次执行/下次执行”。
- 后端定时任务调度更完整。
- 失败时可记录原因。

### 4.8 `linkage_rule` 建议补充字段

```sql
ALTER TABLE `linkage_rule`
ADD COLUMN `last_triggered_at` DATETIME NULL DEFAULT NULL COMMENT 'Last triggered time',
ADD COLUMN `trigger_count` INT NOT NULL DEFAULT 0 COMMENT 'Triggered count',
ADD COLUMN `rule_desc` VARCHAR(255) NULL DEFAULT NULL COMMENT 'Rule description';
```

用途：

- 展示联动规则执行次数。
- 判断规则是否真的被触发过。

### 4.9 `alarm_record` 建议补充字段

```sql
ALTER TABLE `alarm_record`
ADD COLUMN `alarm_desc` VARCHAR(500) NULL DEFAULT NULL COMMENT 'Alarm description',
ADD COLUMN `confirmed_by` BIGINT NULL DEFAULT NULL COMMENT 'Confirm user ID',
ADD COLUMN `confirmed_at` DATETIME NULL DEFAULT NULL COMMENT 'Confirm time',
ADD COLUMN `processed_by` BIGINT NULL DEFAULT NULL COMMENT 'Process user ID',
ADD COLUMN `processed_at` DATETIME NULL DEFAULT NULL COMMENT 'Process time',
ADD CONSTRAINT `fk_alarm_confirmed_by` FOREIGN KEY (`confirmed_by`) REFERENCES `user_account` (`user_id`) ON DELETE SET NULL,
ADD CONSTRAINT `fk_alarm_processed_by` FOREIGN KEY (`processed_by`) REFERENCES `user_account` (`user_id`) ON DELETE SET NULL;
```

用途：

- 报警详情页展示确认人、处理人。
- 报警流程更符合实际系统。

### 4.10 `self_check_record` 建议补充字段

```sql
ALTER TABLE `self_check_record`
ADD COLUMN `check_items` JSON NULL COMMENT 'Self check items JSON',
ADD COLUMN `duration_ms` INT NULL DEFAULT NULL COMMENT 'Check duration milliseconds';
```

用途：

- 展示检查项，例如传感器、网络、电源、通信。
- 更适合答辩演示设备自检。

### 4.11 `device_simulation` 建议补充字段

```sql
ALTER TABLE `device_simulation`
ADD COLUMN `simulation_type` VARCHAR(50) NOT NULL DEFAULT 'manual' COMMENT 'manual/auto/scenario',
ADD COLUMN `scenario_name` VARCHAR(100) NULL DEFAULT NULL COMMENT 'Simulation scenario name';
```

用途：

- 区分手动模拟、自动模拟、场景模拟。
- 支持“烟雾浓度升高”“燃气泄漏”“设备离线”等演示场景。

### 4.12 `sensor_data` 建议补充字段

```sql
ALTER TABLE `sensor_data`
ADD COLUMN `home_id` BIGINT NULL DEFAULT NULL COMMENT 'Home ID for faster query',
ADD COLUMN `room_id` BIGINT NULL DEFAULT NULL COMMENT 'Room ID for faster query',
ADD KEY `idx_sensor_home_time` (`home_id`, `collect_time`),
ADD KEY `idx_sensor_room_time` (`room_id`, `collect_time`),
ADD CONSTRAINT `fk_sensor_home` FOREIGN KEY (`home_id`) REFERENCES `home_space` (`home_id`) ON DELETE CASCADE,
ADD CONSTRAINT `fk_sensor_room` FOREIGN KEY (`room_id`) REFERENCES `room_area` (`room_id`) ON DELETE SET NULL;
```

用途：

- 查询某个家庭的传感器趋势更快。
- 查询某个房间的温度、烟雾、燃气历史更方便。

## 5. 建议补充索引

### 5.1 报警查询索引

```sql
ALTER TABLE `alarm_record`
ADD KEY `idx_alarm_home_status_time` (`home_id`, `alarm_status`, `trigger_time`);
```

用途：

- 小程序报警中心按家庭、状态、时间查询。

### 5.2 设备查询索引

```sql
ALTER TABLE `device`
ADD KEY `idx_device_home_room` (`home_id`, `room_id`);
```

用途：

- 设备页按家庭和房间筛选。

### 5.3 定时任务查询索引

```sql
ALTER TABLE `schedule_task`
ADD KEY `idx_task_home_status_time` (`home_id`, `status`, `execute_time`);
```

用途：

- 后端定时任务轮询。
- 小程序查询启用任务。

### 5.4 成员查询索引

```sql
ALTER TABLE `home_member`
ADD KEY `idx_member_home_status` (`home_id`, `status`);
```

用途：

- 成员列表按状态筛选。
- 查询待审批、已邀请、已加入成员。

### 5.5 短信验证码查询索引

当前已有：

```sql
KEY `idx_sms_phone_scene` (`phone`, `scene`)
```

建议增强为：

```sql
ALTER TABLE `sms_code`
ADD KEY `idx_sms_phone_scene_used_expires` (`phone`, `scene`, `used`, `expires_at`);
```

用途：

- 快速查找指定手机号、指定场景、未使用、未过期的验证码。

## 6. 字段枚举建议统一

建议在后端和数据库文档中统一以下枚举值。

### 6.1 用户角色

```text
OWNER
MEMBER
GUEST
MAINTAINER
```

### 6.2 用户状态

```text
ACTIVE
DISABLED
```

### 6.3 成员状态

```text
INVITED
PENDING
ACTIVE
REJECTED
REMOVED
EXPIRED
```

### 6.4 设备状态

```text
online
offline
on
off
fault
```

### 6.5 报警状态

```text
new
confirmed
processing
recheck
closed
false_alarm
```

### 6.6 报警等级

```text
notice
warning
serious
```

### 6.7 定时任务状态

```text
enabled
disabled
done
failed
```

### 6.8 定时任务类型

```text
once
daily
weekly
cron
```

### 6.9 短信验证码场景

```text
login
bind
reset_password
```

当前代码已有 `login` 和 `bind`，如果后续支持忘记密码，建议预留 `reset_password`。

## 7. 建议修正后的初始化数据示例

以下示例用于替换当前乱码初始化数据。

```sql
INSERT INTO `home_space` (`home_id`, `name`, `address`, `owner_id`, `created_at`, `updated_at`) VALUES
(1, '演示家庭', '北京市朝阳区', 1, '2026-07-03 22:45:04', NULL);

INSERT INTO `room_area` (`room_id`, `home_id`, `room_name`, `room_type`, `remark`, `created_at`, `updated_at`) VALUES
(1, 1, '客厅', 'living_room', '用于智能灯、插座、门磁演示', '2026-07-03 22:47:33', NULL),
(2, 1, '主卧', 'bedroom', '用于温度传感器演示', '2026-07-03 22:47:33', NULL),
(3, 1, '厨房', 'kitchen', '用于烟雾和燃气报警演示', '2026-07-03 22:47:33', NULL);

INSERT INTO `device` (`device_id`, `home_id`, `room_id`, `device_name`, `device_type`, `device_status`, `is_key_device`, `created_at`, `updated_at`) VALUES
(1, 1, 1, '客厅灯', 'light', 'off', 0, '2026-07-03 22:47:33', NULL),
(2, 1, 1, '客厅插座', 'socket', 'off', 0, '2026-07-03 22:47:33', NULL),
(3, 1, 2, '主卧温度传感器', 'temperature_sensor', 'online', 0, '2026-07-03 22:47:33', NULL),
(4, 1, 3, '厨房烟雾传感器', 'smoke_sensor', 'online', 1, '2026-07-03 22:47:33', NULL),
(5, 1, 3, '厨房燃气传感器', 'gas_sensor', 'online', 1, '2026-07-03 22:47:33', NULL),
(6, 1, 1, '入户门磁', 'door_sensor', 'online', 1, '2026-07-03 22:47:33', NULL);

INSERT INTO `scene_mode` (`scene_id`, `home_id`, `scene_name`, `created_by`, `enabled`, `created_at`, `updated_at`) VALUES
(1, 1, '离家模式', 1, 1, '2026-07-04 15:44:10', NULL);

INSERT INTO `schedule_task` (`task_id`, `home_id`, `device_id`, `task_name`, `schedule_type`, `execute_time`, `cron_expr`, `action`, `status`, `created_at`, `updated_at`) VALUES
(1, 1, 1, '清晨开灯', 'daily', '2026-07-05 07:30:00', NULL, 'on', 'enabled', '2026-07-04 15:44:10', NULL);

INSERT INTO `linkage_rule` (`rule_id`, `home_id`, `rule_name`, `trigger_condition`, `action_config`, `enabled`, `created_by`, `created_at`, `updated_at`) VALUES
(1, 1, '烟雾报警联动', JSON_OBJECT('device_id', 4, 'data_type', 'smoke', 'operator', '>', 'threshold', 50), JSON_OBJECT('device_id', 1, 'target_state', 'on'), 1, 1, '2026-07-04 15:44:10', NULL);
```

## 8. 推荐最终数据库执行顺序

如果要重新整理完整数据库，建议顺序如下：

1. 先修正 `smart_home.sql` 的乱码和错误引号。
2. 决定 `user_account.phone` 是否允许为空。
3. 新增 `account_operation_log`。
4. 新增 `device_event`。
5. 新增 `room_layout`。
6. 新增 `device_layout`。
7. 补充 `user_account`、`device`、`scene_mode`、`schedule_task`、`linkage_rule`、`alarm_record` 等字段。
8. 补充组合索引。
9. 重写初始化数据。
10. 用 MySQL 执行完整 SQL，确认无语法错误。
11. 后端 MySQLRepository 按最终字段实现。

## 9. 最小必做清单

如果时间紧，至少完成以下内容：

1. 修复全部中文乱码和字符串引号错误。
2. 明确 `user_account.phone` 是否允许为空。
3. 新增 `account_operation_log`。
4. 补充 `device` 的 `manufacturer/model/serial_no/last_online_at/last_offline_at/remark`。
5. 补充 `scene_device_action.action`。
6. 补充 `alarm_record.alarm_desc/confirmed_by/confirmed_at/processed_by/processed_at`。
7. 新增 `room_layout` 和 `device_layout`，支撑 3D 可视化。
8. 增加核心组合索引。

## 10. 给数据库负责人的交接说明

当前数据库主体已经能覆盖系统功能，但仍需做以下完善：

- 先修复 SQL 文件中的中文乱码和初始化数据语法问题。
- 按项目最终登录策略决定手机号是否允许为空。
- 账号安全日志建议独立成 `account_operation_log`。
- 设备、房间、报警、定时、联动建议补充展示和追踪字段。
- 为 3D 可视化新增 `room_layout` 和 `device_layout`。
- 统一后端字段命名，尤其是操作日志相关字段。
- 补充组合索引，保证小程序查询和后端定时任务查询效率。

完成以上内容后，数据库就可以支撑：

- Web 前端。
- 微信小程序。
- 后端 MySQLRepository。
- 设备模拟。
- 报警演示。
- 设备自检。
- 情景模式。
- 定时任务。
- 联动规则。
- 2.5D/3D 空间可视化。

