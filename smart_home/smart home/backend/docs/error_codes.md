# 后端错误码说明

后端 HTTP 状态码和响应体中的 `code` 保持一致，前端可优先根据 `code` 做统一提示。

统一响应格式：

```json
{
  "code": 400,
  "message": "错误说明",
  "data": null
}
```

成功响应格式：

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

| code | 含义 | 常见原因 | 前端建议 |
| --- | --- | --- | --- |
| 200 | 成功 | 请求处理成功 | 正常渲染 `data` |
| 400 | 请求参数或业务状态错误 | 参数校验失败、状态不允许流转 | 提示用户检查输入 |
| 401 | 未登录或 token 无效 | 未携带 token、token 过期、token 解析失败 | 跳转登录页 |
| 403 | 权限不足 | 不是家庭成员、角色无权限 | 提示无权限 |
| 404 | 资源不存在 | 用户、家庭、成员、设备、报警等不存在 | 提示数据不存在并刷新列表 |
| 409 | 数据冲突 | 手机号重复、成员已存在、名称重复 | 提示冲突原因 |
| 500 | 服务端错误 | 未捕获异常 | 提示稍后重试并记录日志 |

## 常见错误消息

| message | 场景 |
| --- | --- |
| `unauthorized` | 未登录或 token 无效 |
| `permission denied` | 当前角色没有权限 |
| `not home member` | 当前用户不是该家庭成员 |
| `phone or password incorrect` | 登录账号或密码错误 |
| `phone already registered` | 注册手机号已存在 |
| `member already exists or pending` | 成员已存在或邀请/申请待处理 |
| `invitation does not belong to current user` | 当前用户不能接受别人的邀请 |
| `cannot remove yourself` | 成员管理中不能移除自己 |
| `设备不存在` | 设备详情、控制、模拟、自检时设备编号无效 |
| `房间不存在` | 修改或删除房间时房间编号无效 |
| `报警记录不存在` | 查询或处理报警时报警编号无效 |

## 已验证场景

- 未携带 Token 访问受保护接口返回 `401 unauthorized`。
- GUEST 控制设备或新增设备返回 `403 permission denied`。
- 查询不存在设备返回 `404 设备不存在`。
- 参数缺失或格式错误返回 `400`，响应体仍保持统一格式。
