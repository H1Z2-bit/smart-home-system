# 手机号验证码登录与账号绑定方案

## 1. 设计原则

本系统采用“一个用户主体，多种登录方式”的模式：

- `user_id` 是系统内唯一用户身份。
- 账号密码登录、手机号验证码登录只是不同登录凭据。
- 一个手机号只能绑定一个账号。
- 账号绑定手机号后，无论使用账号密码登录还是手机号验证码登录，进入的都是同一个 `user_id`。
- 未绑定或未验证手机号的账号，密码登录后由前端根据 `phone_bound=false` 弹出绑定提醒。

## 2. 当前 Mock 版能力

当前版本不接真实短信平台，验证码由后端 Mock 生成，并直接返回给调用方，方便课程设计联调和演示。

正式上线时，`mock_code` 不应返回给前端，应改为调用阿里云短信、腾讯云短信、Twilio 等短信服务。

## 3. 接口流程

### 3.1 账号密码登录

```http
POST /api/auth/login
```

```json
{
  "phone": "13800000000",
  "password": "123456"
}
```

返回中的 `phone_verified` 和 `phone_bound` 用于前端判断是否提醒绑定手机号：

```json
{
  "token": "...",
  "user": {
    "user_id": 1,
    "username": "han",
    "phone": "13800000000",
    "role": "OWNER",
    "phone_verified": true,
    "phone_bound": true
  }
}
```

### 3.2 发送手机号登录验证码

```http
POST /api/auth/sms/send
```

```json
{
  "phone": "15500001111",
  "scene": "login"
}
```

Mock 返回：

```json
{
  "phone": "15500001111",
  "scene": "login",
  "expires_in": 300,
  "mock_code": "123456",
  "mock_notice": "Mock mode returns the SMS code directly. Real SMS provider must not return it."
}
```

### 3.3 手机号验证码登录

```http
POST /api/auth/sms/login
```

```json
{
  "phone": "15500001111",
  "code": "123456"
}
```

处理规则：

- 手机号已绑定已验证账号：直接登录该账号。
- 手机号存在但未验证：验证码正确后，将该账号手机号标记为已验证并登录该账号。
- 手机号不存在：自动创建新账号并登录，用户名默认为 `user_手机号后4位`。

### 3.4 登录后发送绑定手机号验证码

需要携带 JWT：

```http
POST /api/users/phone/code
Authorization: Bearer <token>
```

```json
{
  "phone": "15600002222",
  "scene": "bind"
}
```

### 3.5 绑定手机号

需要携带 JWT：

```http
POST /api/users/phone/bind
Authorization: Bearer <token>
```

```json
{
  "phone": "15600002222",
  "code": "123456"
}
```

处理规则：

- 当前手机号已被其他已验证账号绑定：拒绝绑定，返回 `409`。
- 当前手机号属于当前账号但未验证：验证成功后标记为已绑定。
- 当前账号更换为一个未被占用手机号：验证成功后绑定新手机号。

## 4. 前端提示逻辑

账号密码登录成功后，前端读取：

```js
response.data.user.phone_bound
```

如果为 `false`，弹出提示：

```text
建议绑定手机号，用于安全验证和下次验证码登录。
```

用户可以选择：

- 立即绑定：进入手机号绑定流程。
- 暂不绑定：关闭弹窗，继续使用账号密码登录。

## 5. 安全规则

当前 Mock 版已经包含：

- 验证码 6 位数字。
- 验证码有效期 300 秒。
- 验证码使用后失效。
- 同一验证码最多允许 5 次尝试。
- 绑定手机号时检查手机号是否已被其他账号占用。

正式短信版建议继续补充：

- 同手机号同场景 60 秒内限制重复发送。
- 同 IP、同手机号每日发送次数限制。
- 接入图形验证码或滑块验证防刷。
- 生产环境强制 HTTPS。
- 验证码不写入明文日志。
