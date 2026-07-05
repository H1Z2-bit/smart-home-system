# 韩喆模块 Mock 初始化数据说明

当前 Python 后端默认使用 MockRepository，数据保存在内存中。服务重启后，Mock 数据会恢复到初始状态。

## 1. 初始化账号

| user_id | username | phone | password | role | status |
|---|---|---|---|---|---|
| 1 | han | 13800000000 | 123456 | OWNER | ACTIVE |
| 2 | member | 13900000000 | 123456 | MEMBER | ACTIVE |
| 3 | guest | 13700000000 | 123456 | GUEST | ACTIVE |
| 4 | maintainer | 13600000000 | 123456 | MAINTAINER | ACTIVE |

说明：

```text
代码中不保存明文密码，启动时会把 123456 转成 bcrypt 哈希。
```

## 2. 初始化家庭空间

| home_id | name | address | owner_id |
|---|---|---|---|
| 1 | 演示家庭 | 北京市朝阳区 | 1 |

## 3. 初始化家庭成员

| member_id | home_id | user_id | username | phone | role | status |
|---|---|---|---|---|---|---|
| 1 | 1 | 1 | han | 13800000000 | OWNER | ACTIVE |
| 2 | 1 | 2 | member | 13900000000 | MEMBER | ACTIVE |
| 3 | 1 | 3 | guest | 13700000000 | GUEST | ACTIVE |

维护人员账号 `13600000000` 默认还不是家庭成员，可以用于测试邀请流程。

## 4. 初始化系统配置

| 配置项 | 默认值 | 说明 |
|---|---|---|
| alarm_smoke_threshold | 80.0 | 烟雾报警阈值 |
| alarm_gas_threshold | 70.0 | 燃气报警阈值 |
| temperature_high_threshold | 35.0 | 高温阈值 |
| auto_alarm_enabled | true | 是否启用自动报警 |
| simulation_enabled | true | 是否启用设备模拟 |

## 5. 推荐测试流程

### 5.1 户主登录

```json
{
  "phone": "13800000000",
  "password": "123456"
}
```

可测试：

```text
查看个人信息
查看家庭列表
查看成员列表
修改系统配置
邀请成员
审批成员
查看日志
```

### 5.2 普通成员登录

```json
{
  "phone": "13900000000",
  "password": "123456"
}
```

可测试：

```text
查看家庭
查看日志
不能修改系统配置
不能邀请成员
```

### 5.3 访客登录

```json
{
  "phone": "13700000000",
  "password": "123456"
}
```

可测试：

```text
查看家庭
不能查看日志
不能修改配置
不能邀请成员
```

### 5.4 维护人员登录

```json
{
  "phone": "13600000000",
  "password": "123456"
}
```

可测试：

```text
先由户主邀请
维护人员接受邀请
接受后成为家庭成员
```

## 6. 数据重置方式

Mock 数据保存在 Python 进程内存中。如果想恢复初始状态：

```text
停止 uvicorn
重新启动 uvicorn
```