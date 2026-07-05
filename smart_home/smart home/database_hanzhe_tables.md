# 韩喆负责模块数据库表字段建议

本文档用于给数据库负责人设计 MySQL 表结构。当前后端是 MockRepository，后续切换 MySQLRepository 时建议按以下表结构落库。

## 1. user_account 用户账号表

用途：保存用户账号、登录信息和全局角色。

| 字段名 | 类型建议 | 约束 | 说明 |
|---|---|---|---|
| user_id | BIGINT | PK, AUTO_INCREMENT | 用户 ID |
| username | VARCHAR(50) | NOT NULL | 用户名 |
| phone | VARCHAR(20) | UNIQUE, NOT NULL | 手机号，登录账号 |
| password_hash | VARCHAR(255) | NOT NULL | 密码哈希，后端使用 SHA-256 预处理 + bcrypt |
| role | VARCHAR(30) | NOT NULL | 默认角色，OWNER/MEMBER/GUEST/MAINTAINER |
| status | VARCHAR(20) | NOT NULL | ACTIVE/DISABLED |
| created_at | DATETIME | NOT NULL | 创建时间 |
| updated_at | DATETIME | NOT NULL | 更新时间 |

建议索引：

```sql
UNIQUE KEY uk_user_phone (phone)
```

## 2. home_space 家庭空间表

用途：保存家庭空间基本信息。

| 字段名 | 类型建议 | 约束 | 说明 |
|---|---|---|---|
| home_id | BIGINT | PK, AUTO_INCREMENT | 家庭 ID |
| name | VARCHAR(80) | NOT NULL | 家庭名称 |
| address | VARCHAR(255) | NULL | 家庭地址 |
| owner_id | BIGINT | FK, NOT NULL | 户主用户 ID，关联 user_account.user_id |
| created_at | DATETIME | NOT NULL | 创建时间 |
| updated_at | DATETIME | NOT NULL | 更新时间 |

建议索引：

```sql
KEY idx_home_owner (owner_id)
```

## 3. home_member 家庭成员表

用途：保存用户在某个家庭空间中的角色、状态和有效期。

| 字段名 | 类型建议 | 约束 | 说明 |
|---|---|---|---|
| member_id | BIGINT | PK, AUTO_INCREMENT | 成员关系 ID |
| home_id | BIGINT | FK, NOT NULL | 家庭 ID |
| user_id | BIGINT | FK, NULL | 用户 ID。邀请未注册手机号时可暂时为空 |
| username | VARCHAR(50) | NULL | 冗余用户名，方便展示 |
| phone | VARCHAR(20) | NOT NULL | 成员手机号或被邀请手机号 |
| role | VARCHAR(30) | NOT NULL | OWNER/MEMBER/GUEST/MAINTAINER |
| status | VARCHAR(30) | NOT NULL | INVITED/PENDING/ACTIVE/REJECTED/REMOVED/EXPIRED |
| expire_at | DATETIME | NULL | 临时成员有效期 |
| invited_by | BIGINT | NULL | 邀请人用户 ID |
| apply_reason | VARCHAR(255) | NULL | 申请加入理由 |
| created_at | DATETIME | NOT NULL | 创建时间 |
| updated_at | DATETIME | NOT NULL | 更新时间 |

建议索引：

```sql
KEY idx_member_home (home_id),
KEY idx_member_user (user_id),
KEY idx_member_phone (phone),
UNIQUE KEY uk_home_phone_active (home_id, phone, status)
```

成员状态流转：

```text
邀请：INVITED -> ACCEPT -> ACTIVE
申请：PENDING -> APPROVE -> ACTIVE
申请：PENDING -> REJECT -> REJECTED
移除：ACTIVE/PENDING/INVITED -> REMOVED
过期：ACTIVE -> EXPIRED
```

## 4. system_config 系统配置表

用途：保存每个家庭空间的报警阈值、模拟开关等系统配置。

| 字段名 | 类型建议 | 约束 | 说明 |
|---|---|---|---|
| config_id | BIGINT | PK, AUTO_INCREMENT | 配置 ID |
| home_id | BIGINT | UNIQUE, FK, NOT NULL | 家庭 ID |
| alarm_smoke_threshold | DECIMAL(8,2) | NOT NULL | 烟雾报警阈值 |
| alarm_gas_threshold | DECIMAL(8,2) | NOT NULL | 燃气报警阈值 |
| temperature_high_threshold | DECIMAL(8,2) | NOT NULL | 高温阈值 |
| auto_alarm_enabled | TINYINT(1) | NOT NULL | 是否开启自动报警 |
| simulation_enabled | TINYINT(1) | NOT NULL | 是否开启设备模拟 |
| created_at | DATETIME | NOT NULL | 创建时间 |
| updated_at | DATETIME | NOT NULL | 更新时间 |

建议索引：

```sql
UNIQUE KEY uk_config_home (home_id)
```

## 5. operation_log 操作日志表

用途：记录登录、成员管理、系统配置修改等敏感操作。

| 字段名 | 类型建议 | 约束 | 说明 |
|---|---|---|---|
| log_id | BIGINT | PK, AUTO_INCREMENT | 日志 ID |
| user_id | BIGINT | NOT NULL | 操作人用户 ID |
| home_id | BIGINT | NULL | 所属家庭 ID，登录类日志可为空 |
| action | VARCHAR(80) | NOT NULL | 操作类型 |
| description | TEXT | NOT NULL | 操作说明 |
| target_type | VARCHAR(80) | NULL | 操作对象类型，如 USER/HOME/MEMBER/SYSTEM_CONFIG |
| target_id | BIGINT | NULL | 操作对象 ID |
| ip_address | VARCHAR(64) | NULL | 预留：请求 IP |
| user_agent | VARCHAR(255) | NULL | 预留：客户端信息 |
| created_at | DATETIME | NOT NULL | 创建时间 |

建议索引：

```sql
KEY idx_log_home_created (home_id, created_at),
KEY idx_log_user_created (user_id, created_at),
KEY idx_log_action (action)
```

## 6. 后端当前用到的 action 值

| action | 说明 |
|---|---|
| REGISTER | 用户注册 |
| LOGIN | 用户登录 |
| LOGOUT | 用户退出 |
| CHANGE_PASSWORD | 修改密码 |
| CREATE_HOME | 创建家庭 |
| UPDATE_HOME | 修改家庭 |
| DELETE_HOME | 删除家庭 |
| INVITE_MEMBER | 邀请成员 |
| ACCEPT_INVITATION | 接受邀请 |
| APPLY_MEMBER | 申请加入家庭 |
| APPROVE_MEMBER | 审批成员 |
| UPDATE_MEMBER_PERMISSION | 修改成员权限 |
| REMOVE_MEMBER | 移除成员 |
| UPDATE_SYSTEM_CONFIG | 修改系统配置 |

## 7. MySQLRepository 对接建议

后端 Service 层已经不直接操作数据库，后续替换数据源时建议：

```text
1. 保留 app/services/ 业务逻辑不变。
2. 在 app/repositories/mysql/ 下实现 MySQL 版本 Repository。
3. 根据 USE_MOCK_REPOSITORY 配置选择 MockRepository 或 MySQLRepository。
4. 用 SQLAlchemy Model 映射上述表结构。
5. 用 Alembic 管理表结构迁移。
```