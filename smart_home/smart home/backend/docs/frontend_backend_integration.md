# 前后端联调说明

本文档用于后端、小程序、数据库三方联调。

## 1. 启动后端

```powershell
cd "C:\Users\hanzhe\Desktop\software\smart home\backend"
conda activate visgeom
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

本机浏览器检查：

```text
http://127.0.0.1:8000/api/health
```

返回：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "status": "ok"
  }
}
```

## 2. 小程序配置后端地址

文件：

```text
miniprogram/config/index.js
```

微信开发者工具模拟器可用：

```js
const BASE_URL = "http://127.0.0.1:8000"
```

真机或局域网访问时，后端必须用 `--host 0.0.0.0` 启动，并把地址改为电脑 WLAN IPv4：

```js
const BASE_URL = "http://10.126.19.85:8000"
```

如果 IP 变化，重新执行：

```powershell
ipconfig
```

查看 `无线局域网适配器 WLAN` 下的 `IPv4 地址`。

## 3. 微信开发者工具设置

开发阶段需要打开：

```text
详情 -> 本地设置 -> 不校验合法域名、web-view、TLS 版本以及 HTTPS 证书
```

否则 HTTP 局域网接口可能无法请求。

## 4. 登录与 Token

默认登录接口：

```http
POST /api/auth/login
```

请求体：

```json
{
  "phone": "13800000000",
  "password": "123456"
}
```

返回的 `data.token` 是 JWT。小程序已在 `utils/request.js` 中统一携带：

```http
Authorization: Bearer <token>
```

没有 token 的受保护接口会返回：

```json
{
  "code": 401,
  "message": "unauthorized",
  "data": null
}
```

## 5. 推荐联调顺序

1. `GET /api/health`：确认后端可访问。
2. `POST /api/auth/login`：确认账号登录。
3. `GET /api/homes`：确认 token 生效。
4. `GET /api/homes/1/rooms`：确认房间数据。
5. `GET /api/homes/1/devices`：确认设备列表。
6. `POST /api/devices/1/control`：确认设备控制。
7. `GET /api/homes/1/scenes`：确认场景模式。
8. `POST /api/devices/4/simulate`：提交烟雾模拟数据。
9. `GET /api/homes/1/alarms`：确认报警触发。
10. `GET /api/homes/1/logs`：确认操作日志。

## 6. Postman / Apifox

导入：

```text
backend/docs/smart_home_api.postman_collection.json
```

集合变量：

| 变量 | 示例 |
| --- | --- |
| `base_url` | `http://127.0.0.1:8000` |
| `token` | 登录接口返回的 JWT |

## 7. 常见问题

| 问题 | 处理方式 |
| --- | --- |
| 小程序提示无法连接后端 | 检查后端是否用 `--host 0.0.0.0` 启动 |
| 模拟器能访问，真机不能访问 | 把 `127.0.0.1` 改成电脑 WLAN IPv4 |
| 返回 `401 unauthorized` | 重新登录，确认请求头带 `Authorization` |
| 返回 `403 permission denied` | 当前角色没有该操作权限，换 OWNER 账号测试 |
| 返回 `not home member` | 当前用户不是该家庭空间成员 |

