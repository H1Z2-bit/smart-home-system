# 智能家居综合管理系统 MySQL 完整字段补充说明

本文档用于同步当前 `smart_home.sql` 与后端、小程序功能之间的数据库缺口，便于数据库负责人补全最终 MySQL 表结构。

当前数据库已经包含用户、家庭、成员、房间、设备、场景、定时任务、联动规则、报警、自检、传感器数据、系统配置和日志等主体表，整体方向正确。

但是当前后端和小程序已经新增了手机号验证码登录、手机号绑定、设备模拟、日志详情、系统演示等功能，因此 MySQL 需要补充部分字段和表。

## 一、必须补充的字段和表

### 1. user_account 补充手机号验证字段

当前后端已经支持：

- 账号密码登录
- 手机号验证码登录
- 登录后绑定手机号
- 根据 `phone_verified` 判断手机号是否已验证
- 前端根据 `phone_bound` / `phone_verified` 判断是否提醒用户绑定手机号

因此 `user_account` 需要新增：

```sql
ALTER TABLE user_account
ADD COLUMN phone_verified TINYINT(1) NOT NULL DEFAULT 0 COMMENT '手机号是否已验证' AFTER phone;
```

如果已有演示账号手机号默认视为可登录，可以执行：

```sql
UPDATE user_account
SET phone_verified = 1
WHERE phone IS NOT NULL AND phone <> '';
```

建议同时保留手机号唯一约束：

```sql
UNIQUE INDEX `phone`(`phone`)
```

业务规则：

- 一个手机号只能绑定一个账号。
- `phone_verified = 1` 时，该手机号可以用于验证码登录。
- `phone_verified = 0` 时，该手机号只能作为未验证联系方式，不能直接作为已绑定手机号使用。

### 2. 新增 sms_code 表

当前 Mock 阶段验证码存在内存里，正式 MySQL 版本建议落库，便于验证码过期、重复验证、尝试次数限制。

```sql
CREATE TABLE `sms_code` (
  `sms_id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '短信验证码ID',
  `phone` VARCHAR(20) NOT NULL COMMENT '手机号',
  `scene` VARCHAR(20) NOT NULL COMMENT '验证码场景：login/bind',
  `code` VARCHAR(10) NOT NULL COMMENT '验证码',
  `expires_at` DATETIME NOT NULL COMMENT '过期时间',
  `used` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否已使用',
  `attempts` INT NOT NULL DEFAULT 0 COMMENT '验证尝试次数',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`sms_id`),
  INDEX `idx_sms_phone_scene` (`phone`, `scene`),
  INDEX `idx_sms_expires_at` (`expires_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='短信验证码表';
```

业务规则：

- 验证码有效期建议 5 分钟。
- 验证成功后 `used = 1`。
- 同一个验证码最多尝试 5 次。
- 正式环境不应把验证码返回给前端。

### 3. 新增 device_simulation 表

当前后端和小程序已支持：

- 提交设备模拟数据
- 查询设备模拟记录
- 模拟烟雾、燃气、温度等传感器数据
- 根据模拟数据触发报警

当前 SQL 中已有 `sensor_data`，但它更像真实采集数据表，不完全匹配当前接口：

```text
POST /api/devices/{device_id}/simulate
GET  /api/devices/{device_id}/simulations
```

建议新增专门的设备模拟表：

```sql
CREATE TABLE `device_simulation` (
  `simulation_id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '模拟记录ID',
  `device_id` BIGINT NOT NULL COMMENT '设备ID',
  `metric_name` VARCHAR(100) NOT NULL COMMENT '模拟指标名称，如 temperature/smoke/gas',
  `metric_value` VARCHAR(100) NOT NULL COMMENT '模拟指标值',
  `device_status` VARCHAR(30) NULL DEFAULT NULL COMMENT '可选设备状态',
  `trigger_alarm` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否触发报警',
  `alarm_type` VARCHAR(50) NULL DEFAULT NULL COMMENT '报警类型',
  `alarm_level` VARCHAR(30) NOT NULL DEFAULT 'warning' COMMENT '报警级别',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`simulation_id`),
  INDEX `idx_simulation_device` (`device_id`),
  INDEX `idx_simulation_time` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='设备模拟记录表';
```

业务规则：

- 用于课程演示和设备模拟。
- 如果 `trigger_alarm = 1`，后端可以同时生成 `alarm_record`。
- 后续如果接真实设备，真实采集数据可以继续写入 `sensor_data`。

### 4. operation_log 补充 operation_desc 字段

当前后端写日志时包含：

```text
operation_desc
```

小程序日志页也会优先展示：

```text
operation_desc
```

但当前 `operation_log` 表没有这个字段，建议补充：

```sql
ALTER TABLE operation_log
ADD COLUMN operation_desc VARCHAR(500) NULL COMMENT '操作描述' AFTER operation_result;
```

建议日志字段最终为：

```text
log_id
home_id
operator_id
operation_type
operation_object
operation_result
operation_desc
created_at
```

### 5. schedule_task 的 execute_time 格式要统一

当前表中：

```sql
execute_time DATETIME NOT NULL
```

后端 schema 当前接收字符串：

```text
execute_time: str
```

小程序表单中可能输入：

```text
22:30
2026-07-04 22:30
```

建议二选一：

方案 A：保持 `DATETIME`，前端必须传完整时间。

```text
2026-07-04 22:30:00
```

方案 B：支持周期任务，补充任务类型字段。

```sql
ALTER TABLE schedule_task
ADD COLUMN schedule_type VARCHAR(20) NOT NULL DEFAULT 'once' COMMENT 'once/daily/weekly/cron' AFTER task_name,
ADD COLUMN cron_expr VARCHAR(100) NULL COMMENT 'cron表达式，可选' AFTER execute_time;
```

课程设计建议采用方案 B，更能体现智能家居定时自动化能力。

## 二、建议优化的字段和约束

### 1. linkage_rule 的 JSON 字段建议改为 JSON 类型

当前表中：

```sql
trigger_condition TEXT NOT NULL
action_config TEXT NOT NULL
```

建议 MySQL 8 使用 JSON 类型：

```sql
ALTER TABLE linkage_rule
MODIFY COLUMN trigger_condition JSON NOT NULL COMMENT '触发条件JSON',
MODIFY COLUMN action_config JSON NOT NULL COMMENT '动作配置JSON';
```

如果担心兼容性，也可以继续使用 `TEXT`，但要由后端保证写入合法 JSON。

### 2. room_area 建议增加索引

当前 `room_area` 只有主键，建议补：

```sql
ALTER TABLE room_area
ADD INDEX idx_room_home (`home_id`),
ADD UNIQUE INDEX uk_room_home_name (`home_id`, `room_name`);
```

原因：

- 查询某个家庭下房间列表需要 `home_id`。
- 同一家庭下房间名不建议重复。

### 3. device 建议增加唯一约束

当前已有：

```sql
idx_device_room_id
idx_device_type
idx_device_status
```

建议补：

```sql
ALTER TABLE device
ADD UNIQUE INDEX uk_device_room_name (`room_id`, `device_name`);
```

原因：

- 后端业务规则要求同一房间下设备名称不能重复。

### 4. home_member 建议增加唯一约束

建议补：

```sql
ALTER TABLE home_member
ADD UNIQUE INDEX uk_member_home_phone (`home_id`, `phone`);
```

原因：

- 同一个家庭空间中，同一手机号不应重复邀请/申请。

### 5. alarm_record 建议补 home_id

当前 `alarm_record` 通过 `device_id` 间接找到家庭。

为了查询某个家庭下报警列表更方便，建议补：

```sql
ALTER TABLE alarm_record
ADD COLUMN home_id BIGINT NULL COMMENT '家庭ID' AFTER alarm_id,
ADD INDEX idx_alarm_home (`home_id`);
```

后端创建报警时直接写入 `home_id`。

### 6. self_check_record 建议统一时间字段命名

当前表使用：

```text
check_time
```

Mock 后端返回字段中常见：

```text
created_at
```

建议二选一：

方案 A：后端 MySQLRepository 映射时把 `check_time` 转成 `created_at` 返回。

方案 B：数据库新增 `created_at`，保留 `check_time`。

建议采用方案 A，避免表结构重复。

## 三、建议补充外键

当前 SQL 大多只有索引，没有外键。课程设计可以不强制，但完整 MySQL 版本建议至少补充以下关系。

```sql
ALTER TABLE home_space
ADD CONSTRAINT fk_home_owner
FOREIGN KEY (owner_id) REFERENCES user_account(user_id);

ALTER TABLE home_member
ADD CONSTRAINT fk_member_home
FOREIGN KEY (home_id) REFERENCES home_space(home_id);

ALTER TABLE room_area
ADD CONSTRAINT fk_room_home
FOREIGN KEY (home_id) REFERENCES home_space(home_id);

ALTER TABLE device
ADD CONSTRAINT fk_device_room
FOREIGN KEY (room_id) REFERENCES room_area(room_id);

ALTER TABLE alarm_record
ADD CONSTRAINT fk_alarm_device
FOREIGN KEY (device_id) REFERENCES device(device_id);

ALTER TABLE alarm_process_log
ADD CONSTRAINT fk_alarm_process_alarm
FOREIGN KEY (alarm_id) REFERENCES alarm_record(alarm_id);

ALTER TABLE scene_mode
ADD CONSTRAINT fk_scene_home
FOREIGN KEY (home_id) REFERENCES home_space(home_id);

ALTER TABLE scene_device_action
ADD CONSTRAINT fk_scene_action_scene
FOREIGN KEY (scene_id) REFERENCES scene_mode(scene_id);

ALTER TABLE scene_device_action
ADD CONSTRAINT fk_scene_action_device
FOREIGN KEY (device_id) REFERENCES device(device_id);

ALTER TABLE schedule_task
ADD CONSTRAINT fk_schedule_home
FOREIGN KEY (home_id) REFERENCES home_space(home_id);

ALTER TABLE schedule_task
ADD CONSTRAINT fk_schedule_device
FOREIGN KEY (device_id) REFERENCES device(device_id);

ALTER TABLE linkage_rule
ADD CONSTRAINT fk_linkage_home
FOREIGN KEY (home_id) REFERENCES home_space(home_id);

ALTER TABLE system_config
ADD CONSTRAINT fk_config_home
FOREIGN KEY (home_id) REFERENCES home_space(home_id);
```

注意：

- 如果演示数据插入顺序不规范，添加外键前需要先清洗数据。
- 如果担心删除冲突，外键可以先不加，只保留索引和业务层校验。

## 四、当前 smart_home.sql 已有表覆盖情况

| 功能模块 | 当前是否已有表 | 说明 |
| --- | --- | --- |
| 用户账号 | 有 | `user_account`，需补 `phone_verified` |
| 短信验证码 | 缺 | 需新增 `sms_code` |
| 家庭空间 | 有 | `home_space` |
| 家庭成员 | 有 | `home_member` |
| 房间管理 | 有 | `room_area`，建议补索引和唯一约束 |
| 设备管理 | 有 | `device`，建议补唯一约束 |
| 设备控制日志 | 有 | `operation_log`，需补 `operation_desc` |
| 场景模式 | 有 | `scene_mode`、`scene_device_action` |
| 定时任务 | 有 | `schedule_task`，建议补周期字段 |
| 联动规则 | 有 | `linkage_rule`，建议 JSON 类型 |
| 设备模拟 | 缺 | 需新增 `device_simulation` |
| 真实传感器数据 | 有 | `sensor_data` |
| 报警记录 | 有 | `alarm_record`，建议补 `home_id` |
| 报警处理日志 | 有 | `alarm_process_log` |
| 设备自检 | 有 | `self_check_record` |
| 系统配置 | 有 | `system_config` |

## 五、建议最终新增/修改 SQL 汇总

可以把下面这段作为补丁 SQL 交给数据库负责人执行。

```sql
-- 1. 用户手机号验证状态
ALTER TABLE user_account
ADD COLUMN phone_verified TINYINT(1) NOT NULL DEFAULT 0 COMMENT '手机号是否已验证' AFTER phone;

UPDATE user_account
SET phone_verified = 1
WHERE phone IS NOT NULL AND phone <> '';

-- 2. 短信验证码表
CREATE TABLE IF NOT EXISTS sms_code (
  sms_id BIGINT NOT NULL AUTO_INCREMENT COMMENT '短信验证码ID',
  phone VARCHAR(20) NOT NULL COMMENT '手机号',
  scene VARCHAR(20) NOT NULL COMMENT '验证码场景：login/bind',
  code VARCHAR(10) NOT NULL COMMENT '验证码',
  expires_at DATETIME NOT NULL COMMENT '过期时间',
  used TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否已使用',
  attempts INT NOT NULL DEFAULT 0 COMMENT '验证尝试次数',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (sms_id),
  INDEX idx_sms_phone_scene (phone, scene),
  INDEX idx_sms_expires_at (expires_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='短信验证码表';

-- 3. 设备模拟记录表
CREATE TABLE IF NOT EXISTS device_simulation (
  simulation_id BIGINT NOT NULL AUTO_INCREMENT COMMENT '模拟记录ID',
  device_id BIGINT NOT NULL COMMENT '设备ID',
  metric_name VARCHAR(100) NOT NULL COMMENT '模拟指标名称',
  metric_value VARCHAR(100) NOT NULL COMMENT '模拟指标值',
  device_status VARCHAR(30) NULL DEFAULT NULL COMMENT '可选设备状态',
  trigger_alarm TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否触发报警',
  alarm_type VARCHAR(50) NULL DEFAULT NULL COMMENT '报警类型',
  alarm_level VARCHAR(30) NOT NULL DEFAULT 'warning' COMMENT '报警级别',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (simulation_id),
  INDEX idx_simulation_device (device_id),
  INDEX idx_simulation_time (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='设备模拟记录表';

-- 4. 操作日志描述
ALTER TABLE operation_log
ADD COLUMN operation_desc VARCHAR(500) NULL COMMENT '操作描述' AFTER operation_result;

-- 5. 房间索引和唯一约束
ALTER TABLE room_area
ADD INDEX idx_room_home (home_id),
ADD UNIQUE INDEX uk_room_home_name (home_id, room_name);

-- 6. 设备唯一约束
ALTER TABLE device
ADD UNIQUE INDEX uk_device_room_name (room_id, device_name);

-- 7. 家庭成员唯一约束
ALTER TABLE home_member
ADD UNIQUE INDEX uk_member_home_phone (home_id, phone);

-- 8. 报警记录补 home_id
ALTER TABLE alarm_record
ADD COLUMN home_id BIGINT NULL COMMENT '家庭ID' AFTER alarm_id,
ADD INDEX idx_alarm_home (home_id);

-- 9. 定时任务周期字段，可选但建议加
ALTER TABLE schedule_task
ADD COLUMN schedule_type VARCHAR(20) NOT NULL DEFAULT 'once' COMMENT 'once/daily/weekly/cron' AFTER task_name,
ADD COLUMN cron_expr VARCHAR(100) NULL COMMENT 'cron表达式，可选' AFTER execute_time;
```

## 六、交接说明

数据库负责人补表后，需要和后端负责人确认：

1. MySQLRepository 是否已经实现对应表的读写。
2. `user_account.phone_verified` 是否参与登录判断。
3. `sms_code` 是否替代当前 Mock 内存验证码。
4. `device_simulation` 是否接入设备详情页模拟记录。
5. `operation_log.operation_desc` 是否能在日志页正常显示。
6. `schedule_task.execute_time` 前后端格式是否统一。

如果暂时不切 MySQL，以上改动不影响当前 MockRepository 演示。
