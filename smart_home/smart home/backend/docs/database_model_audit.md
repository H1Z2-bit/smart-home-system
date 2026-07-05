# 数据库、后端模型与接口字段核对

本文档用于确认 MySQL 表结构、SQLAlchemy Model、Repository 返回字段和小程序展示字段是否一致。

## 1. 当前结论

当前后端已完成 MySQLRepository 接入，设备、房间、报警、场景、定时任务、联动规则、模拟、自检、日志等核心接口均可在 MySQL 模式下通过 pytest 集成测试。

验证命令：

```powershell
cd "C:\Users\hanzhe\Desktop\software\smart home\backend"
$env:RUN_MYSQL_TESTS='1'
$env:USE_MOCK_REPOSITORY='false'
python -B -m pytest tests\test_mysql_mode_flow.py
```

## 2. 重点表字段核对

### user_account

| 字段 | 后端模型 | 用途 |
| --- | --- | --- |
| `user_id` | `UserAccount.user_id` | 用户主键 |
| `username` | `UserAccount.username` | 用户名 |
| `phone` | `UserAccount.phone` | 手机号登录、绑定 |
| `phone_verified` | `UserAccount.phone_verified` | 手机号是否验证 |
| `register_type` | `UserAccount.register_type` | password/sms/import |
| `last_login_at` | `UserAccount.last_login_at` | 最近登录时间 |
| `password_hash` | `UserAccount.password_hash` | 密码哈希 |
| `role` | `UserAccount.role` | 全局默认角色 |
| `status` | `UserAccount.status` | 账号状态 |

### home_space / home_member

| 表 | 关键字段 | 用途 |
| --- | --- | --- |
| `home_space` | `home_id/name/address/owner_id/cover_url/status` | 家庭空间 |
| `home_member` | `member_id/home_id/user_id/phone/role/status/expire_at/invited_by/apply_reason` | 家庭成员、邀请、申请、审批 |

### room_area / room_layout

| 表 | 关键字段 | 用途 |
| --- | --- | --- |
| `room_area` | `room_id/home_id/room_name/room_type/remark/sort_no/status` | 房间信息 |
| `room_layout` | `position_x/position_y/width/height/floor_no/wall_color/floor_color` | 2.5D/3D 空间可视化 |

后端返回：

```json
{
  "room_id": 1,
  "room_name": "客厅",
  "layout": {
    "position_x": 0,
    "position_y": 0,
    "width": 5,
    "height": 4
  }
}
```

### device / device_layout

| 字段 | 用途 | 小程序展示 |
| --- | --- | --- |
| `manufacturer` | 厂商 | 设备列表、设备详情 |
| `model` | 型号 | 设备列表、设备详情 |
| `serial_no` | 序列号 | 设备详情 |
| `last_online_at` | 最后在线时间 | 设备列表、设备详情 |
| `last_offline_at` | 最后离线时间 | 设备详情 |
| `device_layout.position_x` | X 坐标 | 设备列表、设备详情、空间可视化 |
| `device_layout.position_y` | Y 坐标 | 设备列表、设备详情、空间可视化 |
| `device_layout.position_z` | Z 坐标 | 设备列表、设备详情、空间可视化 |
| `icon_name` | 设备图标 | 设备详情 |
| `model_name` | 3D 模型名称 | 设备详情 |

### automation

| 表 | 用途 |
| --- | --- |
| `scene_mode` | 情景模式 |
| `scene_device_action` | 场景下的设备动作 |
| `schedule_task` | 定时任务 |
| `linkage_rule` | 联动规则，支持 JSON 条件和动作配置 |

### alarm / telemetry / log

| 表 | 用途 |
| --- | --- |
| `sensor_data` | 真实或模拟传感器采集数据 |
| `alarm_record` | 报警主记录 |
| `alarm_process_log` | 报警确认、处理、关闭、误报过程 |
| `device_simulation` | 设备模拟记录 |
| `self_check_record` | 设备自检记录 |
| `operation_log` | 家庭空间内设备、房间、报警等操作审计 |
| `account_operation_log` | 登录、注册、成员、系统配置等账号级操作审计 |

## 3. 小程序已展示的新增字段

| 页面 | 字段 |
| --- | --- |
| 设备列表 | 厂商、型号、最后在线时间、3D 坐标 |
| 设备详情 | 厂商、型号、序列号、最后在线、最后离线、空间坐标、图标、模型 |
| 空间可视化 | 房间布局、设备坐标、设备点位 |

## 4. 后续新增字段流程

1. 修改 `smart_home.sql` 或新增 Alembic 迁移脚本。
2. 修改 `backend/app/models/` 中的 SQLAlchemy 模型。
3. 修改对应 `backend/app/repositories/mysql/` 返回字段。
4. 修改小程序页面展示或表单提交字段。
5. 新增 pytest 覆盖字段返回和业务流程。
6. 更新本文档。

