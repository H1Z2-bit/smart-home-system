# 智能家居后端接口使用说明

本文档给前端联调、后端自测和课程答辩使用。当前后端运行在 MockRepository 模式，不依赖 MySQL。

## 1. 启动地址

默认地址：

```text
http://127.0.0.1:8000
```

Swagger 文档：

```text
http://127.0.0.1:8000/docs
```

## 2. 统一响应格式

成功：

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

失败：

```json
{
  "code": 403,
  "message": "permission denied",
  "data": null
}
```

## 3. 登录与 Token

### 登录

```http
POST /api/auth/login
```

```json
{
  "phone": "13800000000",
  "password": "123456"
}
```

返回 `data.token` 后，后续需要鉴权的接口在请求头携带：

```text
Authorization: Bearer <token>
```

## 4. 默认演示账号

| 角色 | 手机号 | 密码 | 说明 |
| --- | --- | --- | --- |
| OWNER | `13800000000` | `123456` | 户主，可管理家庭、成员、配置、日志 |
| MEMBER | `13900000000` | `123456` | 普通成员，可查看家庭和日志 |
| GUEST | `13700000000` | `123456` | 访客，只能查看家庭基础信息 |
| MAINTAINER | `13600000000` | `123456` | 维护人员，可查看家庭和日志 |

## 5. 演示数据重置

```http
POST /api/debug/reset
```

说明：该接口仅用于开发和答辩演示，默认在 `APP_ENV=dev/test/local` 时可用。调用后会恢复默认用户、家庭、成员、房间、设备、场景、报警数据。

## 6. 核心流程接口

| 模块 | 方法 | 路径 | 是否需要 Token |
| --- | --- | --- | --- |
| 健康检查 | GET | `/api/health` | 否 |
| 注册 | POST | `/api/auth/register` | 否 |
| 登录 | POST | `/api/auth/login` | 否 |
| 个人资料 | GET | `/api/users/profile` | 是 |
| 创建家庭 | POST | `/api/homes` | 是 |
| 查询家庭列表 | GET | `/api/homes` | 是 |
| 查询家庭详情 | GET | `/api/homes/{home_id}` | 是 |
| 邀请成员 | POST | `/api/homes/{home_id}/members/invite` | 是 |
| 成员申请加入 | POST | `/api/homes/{home_id}/members/apply` | 是 |
| 接受邀请 | POST | `/api/homes/{home_id}/members/{member_id}/accept` | 是 |
| 审批成员 | POST | `/api/homes/{home_id}/members/{member_id}/approve` | 是 |
| 修改成员权限 | PUT | `/api/homes/{home_id}/members/{member_id}/permission` | 是 |
| 系统配置 | GET | `/api/homes/{home_id}/system/config` | 是 |
| 修改系统配置 | PUT | `/api/homes/{home_id}/system/config` | 是 |
| 系统日志 | GET | `/api/homes/{home_id}/system/logs` | 是 |

## 7. 导入 Apifox/Postman

已生成接口集合：

```text
backend/docs/smart_home_api.postman_collection.json
backend/docs/openapi.json
```

导入后先调用登录接口，再把返回的 `token` 填到集合变量 `token` 中。
