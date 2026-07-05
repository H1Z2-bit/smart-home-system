# 韩喆负责模块接口文档

## 1. 基本约定

后端基础地址：

```text
http://127.0.0.1:8000/api
```

接口文档地址：

```text
http://127.0.0.1:8000/docs
```

统一返回格式：

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

常用错误码：

| code | 含义 |
|---|---|
| 200 | 成功 |
| 400 | 参数错误或业务状态不允许 |
| 401 | 未登录或 token 无效 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 409 | 数据冲突 |
| 500 | 服务器内部错误 |

除注册、登录、健康检查外，其余接口都需要请求头：

```text
Authorization: Bearer <token>
Content-Type: application/json
```

## 2. 测试账号

| 角色 | 手机号 | 密码 |
|---|---|---|
| 户主 OWNER | `13800000000` | `123456` |
| 常住成员 MEMBER | `13900000000` | `123456` |
| 访客 GUEST | `13700000000` | `123456` |
| 维护人员 MAINTAINER | `13600000000` | `123456` |

## 3. 认证接口

### 3.1 健康检查

```text
GET /api/health
```

响应示例：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "status": "ok",
    "service": "smart-home-python-backend"
  }
}
```

### 3.2 用户注册

```text
POST /api/auth/register
```

请求体：

```json
{
  "username": "zhangsan",
  "phone": "13500000000",
  "password": "123456"
}
```

响应示例：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "user_id": 5,
    "username": "zhangsan"
  }
}
```

### 3.3 用户登录

```text
POST /api/auth/login
```

请求体：

```json
{
  "phone": "13800000000",
  "password": "123456"
}
```

响应示例：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "token": "jwt-token-string",
    "user": {
      "user_id": 1,
      "username": "han",
      "phone": "13800000000",
      "role": "OWNER"
    }
  }
}
```

### 3.4 用户退出

```text
POST /api/auth/logout
```

需要 token。

响应示例：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "status": "logout_ok"
  }
}
```

## 4. 用户接口

### 4.1 查看个人信息

```text
GET /api/users/profile
```

需要 token。

响应示例：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "user_id": 1,
    "username": "han",
    "phone": "13800000000",
    "role": "OWNER"
  }
}
```

### 4.2 修改密码

```text
PUT /api/users/password
```

需要 token。

请求体：

```json
{
  "old_password": "123456",
  "new_password": "654321"
}
```

响应示例：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "status": "password_updated"
  }
}
```

## 5. 家庭空间接口

### 5.1 创建家庭

```text
POST /api/homes
```

需要 token。

请求体：

```json
{
  "name": "我的家庭",
  "address": "北京市朝阳区"
}
```

### 5.2 查询我的家庭列表

```text
GET /api/homes
```

需要 token。

### 5.3 查询家庭详情

```text
GET /api/homes/{home_id}
```

需要 token，且用户必须是该家庭成员。

### 5.4 修改家庭

```text
PUT /api/homes/{home_id}
```

需要 token，且需要 OWNER 权限。

请求体：

```json
{
  "name": "新家庭名称",
  "address": "新地址"
}
```

### 5.5 删除家庭

```text
DELETE /api/homes/{home_id}
```

需要 token，且需要 OWNER 权限。

## 6. 成员管理接口

### 6.1 邀请成员

```text
POST /api/homes/{home_id}/members/invite
```

需要 token，且需要 OWNER 权限。

请求体：

```json
{
  "phone": "13600000000",
  "role": "MAINTAINER",
  "expire_at": null
}
```

响应中成员状态为：

```text
INVITED
```

### 6.2 被邀请用户接受邀请

```text
POST /api/homes/{home_id}/members/{member_id}/accept
```

需要 token，且当前登录用户手机号必须与邀请手机号一致。

成功后成员状态变为：

```text
ACTIVE
```

### 6.3 申请加入家庭

```text
POST /api/homes/{home_id}/members/apply
```

需要 token。

请求体：

```json
{
  "reason": "我是家庭成员"
}
```

响应中成员状态为：

```text
PENDING
```

### 6.4 审批成员

```text
POST /api/homes/{home_id}/members/{member_id}/approve
```

需要 token，且需要 OWNER 权限。

请求体：

```json
{
  "approved": true,
  "role": "MEMBER"
}
```

### 6.5 查询成员列表

```text
GET /api/homes/{home_id}/members
```

需要 token，且用户必须是该家庭成员。

### 6.6 修改成员权限

```text
PUT /api/homes/{home_id}/members/{member_id}/permission
```

需要 token，且需要 OWNER 权限。

请求体：

```json
{
  "role": "GUEST",
  "expire_at": "2026-08-01 00:00:00"
}
```

### 6.7 移除成员

```text
DELETE /api/homes/{home_id}/members/{member_id}
```

需要 token，且需要 OWNER 权限。

## 7. 系统配置接口

### 7.1 查询系统配置

```text
GET /api/homes/{home_id}/system/config
```

需要 token，且用户必须是该家庭成员。

### 7.2 修改系统配置

```text
PUT /api/homes/{home_id}/system/config
```

需要 token，且需要 OWNER 权限。

请求体：

```json
{
  "alarm_smoke_threshold": 80.0,
  "alarm_gas_threshold": 70.0,
  "temperature_high_threshold": 35.0,
  "auto_alarm_enabled": true,
  "simulation_enabled": true
}
```

## 8. 操作日志接口

```text
GET /api/homes/{home_id}/logs
```

需要 token。OWNER、MEMBER、MAINTAINER 可以查看，GUEST 不允许查看。

## 9. Swagger 授权说明

1. 执行 `POST /api/auth/login`。
2. 复制响应中的 `data.token`。
3. 点击 Swagger 页面右上角 `Authorize`。
4. 在 `HTTPBearer` 输入框中粘贴 token 本身。
5. 点击授权后，再测试需要登录的接口。