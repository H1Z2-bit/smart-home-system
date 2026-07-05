# RBAC 权限矩阵

后端采用 JWT + RBAC。JWT 负责识别当前用户，RBAC 根据用户在家庭空间中的成员角色判断能否访问接口。

## 1. 角色定义

| 角色 | 含义 | 典型用户 |
| --- | --- | --- |
| OWNER | 户主 | 创建家庭空间的人 |
| MEMBER | 普通成员 | 家庭常住成员 |
| GUEST | 临时访客 | 临时查看家庭状态的人 |
| MAINTAINER | 维护人员 | 设备维护或物业人员 |
| SYSTEM | 系统内部角色 | 预留给后台任务或系统自动操作 |

## 2. 权限点定义

| 权限点 | 含义 |
| --- | --- |
| HOME_VIEW | 查看家庭空间信息 |
| HOME_MANAGE | 管理家庭空间信息 |
| DEVICE_MANAGE | 新增、修改、删除房间和设备，发起设备自检 |
| DEVICE_CONTROL | 控制设备、执行情景模式 |
| AUTOMATION_MANAGE | 管理情景模式、定时任务、联动规则 |
| ALARM_MANAGE | 处理、关闭、标记报警，提交演示模拟数据 |
| MEMBER_MANAGE | 邀请、审批、修改、移除成员 |
| SYSTEM_CONFIG | 修改系统配置 |
| LOG_VIEW | 查看系统日志 |

## 3. 角色权限矩阵

| 角色 | HOME_VIEW | HOME_MANAGE | DEVICE_MANAGE | DEVICE_CONTROL | AUTOMATION_MANAGE | ALARM_MANAGE | MEMBER_MANAGE | SYSTEM_CONFIG | LOG_VIEW |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| OWNER | 是 | 是 | 是 | 是 | 是 | 是 | 是 | 是 | 是 |
| MEMBER | 是 | 否 | 否 | 是 | 否 | 否 | 否 | 否 | 是 |
| GUEST | 是 | 否 | 否 | 否 | 否 | 否 | 否 | 否 | 否 |
| MAINTAINER | 是 | 否 | 否 | 是 | 是 | 是 | 否 | 否 | 是 |
| SYSTEM | 是 | 是 | 是 | 是 | 是 | 是 | 是 | 是 | 是 |

## 4. 当前测试覆盖

已覆盖：

- OWNER 可以修改系统配置。
- MEMBER 不能修改系统配置。
- GUEST 可以查看系统配置，但不能邀请成员。
- GUEST 可以查看设备列表，但不能控制设备或新增设备。
- 未登录用户不能访问设备、房间、日志等受保护接口。
- MEMBER 可以控制设备和执行情景模式。
- OWNER 可以管理房间、设备、情景模式、定时任务、联动规则、报警。
- 非家庭成员不能查看家庭详情。
- 成员邀请、接受、权限修改、移除流程。
- 成员申请、审批通过、审批拒绝流程。

测试文件：

```text
backend/tests/test_rbac_and_member_flow.py
backend/tests/test_health_and_crud.py
```
