# Python FastAPI 后端说明

本目录已加入 Python 版后端骨架，当前保留原 C++ 文件，Python 入口位于 `app/main.py`。

## 技术栈

```text
Python 3.12 + FastAPI + SQLAlchemy + MySQL + JWT/RSA + RBAC + MockRepository
```

## visgeom 环境启动

```powershell
conda activate visgeom
cd C:\Users\hanzhe\Desktop\software\backend
pip install -r requirements.txt
copy .env.example .env
D:\anaconda\envs\visgeom\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

启动后访问：

```text
健康检查：http://127.0.0.1:8000/api/health
接口文档：http://127.0.0.1:8000/docs
```

## RSA JWT 签名

开发环境已经支持正式 RSA 签名。生成密钥：

```powershell
D:\anaconda\envs\visgeom\python.exe scripts\generate_rsa_keys.py
```

生成文件：

```text
backend/keys/private_key.pem
backend/keys/public_key.pem
```

说明：

```text
private_key.pem 用于签发 JWT。
public_key.pem 用于验证 JWT。
这两个文件已被 .gitignore 忽略，不提交到 Git。
如果 key 文件存在，JWT 使用 RS256。
如果 key 文件不存在，开发环境会临时退回 HS256，方便首次启动。
```

## Mock 测试账号

| 角色 | 手机号 | 密码 |
|---|---|---|
| OWNER | `13800000000` | `123456` |
| MEMBER | `13900000000` | `123456` |
| GUEST | `13700000000` | `123456` |
| MAINTAINER | `13600000000` | `123456` |

Mock 阶段也使用 `SHA-256 预处理 + bcrypt` 保存密码哈希，不在内存中保存明文密码。后续接入 MySQL 时，对应字段为 `user_account.password_hash`。

## RBAC 权限矩阵

| 权限 | OWNER | MEMBER | GUEST | MAINTAINER |
|---|---|---|---|---|
| 查看家庭 | 是 | 是 | 是 | 是 |
| 修改/删除家庭 | 是 | 否 | 否 | 否 |
| 邀请/审批/移除成员 | 是 | 否 | 否 | 否 |
| 修改系统配置 | 是 | 否 | 否 | 否 |
| 查看日志 | 是 | 是 | 否 | 是 |

实现位置：

```text
app/core/permissions.py
app/services/permission_service.py
```

所有家庭资源接口都会先检查用户是否是该家庭成员，再根据家庭角色判断是否具备对应权限。

## 成员状态流转

```text
邀请成员：INVITED -> 用户接受 -> ACTIVE
申请加入：PENDING -> 户主审批通过 -> ACTIVE
申请加入：PENDING -> 户主拒绝 -> REJECTED
移除成员：ACTIVE/PENDING/INVITED -> REMOVED
```

邀请接口支持邀请已注册手机号，也支持先邀请未注册手机号。未注册用户后续注册同手机号后，可以接受邀请。

## Swagger 登录授权流程

1. 打开 `http://127.0.0.1:8000/docs`。
2. 执行 `POST /api/auth/login`。
3. 请求体填写：

```json
{
  "phone": "13800000000",
  "password": "123456"
}
```

4. 复制响应中的 `data.token`。
5. 点击 Swagger 页面右上角 `Authorize`。
6. 在 `HTTPBearer` 输入框里粘贴 token 本身，不需要手动输入 `Bearer`。
7. 点击授权后，再测试 `GET /api/users/profile`、`GET /api/homes` 等接口。

## 韩喆负责接口

| 方法 | 路径 | 功能 |
|---|---|---|
| GET | `/api/health` | 健康检查 |
| POST | `/api/auth/register` | 注册 |
| POST | `/api/auth/login` | 登录 |
| POST | `/api/auth/logout` | 退出 |
| GET | `/api/users/profile` | 个人信息 |
| PUT | `/api/users/password` | 修改密码 |
| POST | `/api/homes` | 创建家庭 |
| GET | `/api/homes` | 家庭列表 |
| GET | `/api/homes/{home_id}` | 家庭详情 |
| PUT | `/api/homes/{home_id}` | 修改家庭 |
| DELETE | `/api/homes/{home_id}` | 删除家庭 |
| POST | `/api/homes/{home_id}/members/invite` | 邀请成员，状态为 INVITED |
| POST | `/api/homes/{home_id}/members/apply` | 申请加入，状态为 PENDING |
| POST | `/api/homes/{home_id}/members/{member_id}/accept` | 被邀请用户接受邀请 |
| POST | `/api/homes/{home_id}/members/{member_id}/approve` | 户主审批申请 |
| GET | `/api/homes/{home_id}/members` | 成员列表 |
| PUT | `/api/homes/{home_id}/members/{member_id}/permission` | 修改成员权限 |
| DELETE | `/api/homes/{home_id}/members/{member_id}` | 移除成员 |
| GET | `/api/homes/{home_id}/system/config` | 系统配置 |
| PUT | `/api/homes/{home_id}/system/config` | 修改配置 |
| GET | `/api/homes/{home_id}/logs` | 操作日志 |

## 自动化测试

不需要启动 uvicorn，直接运行：

```powershell
cd C:\Users\hanzhe\Desktop\software\backend
D:\anaconda\envs\visgeom\python.exe -m pytest tests\test_hanzhe_api.py -q
```

## 冒烟测试

先启动后端，再运行：

```powershell
D:\anaconda\envs\visgeom\python.exe scripts\smoke_test.py
```

## MySQLRepository 预留

当前 `USE_MOCK_REPOSITORY=true`，接口走内存 Mock 数据。等王涵完成 `schema.sql` 后，再把 Repository 从 Mock 切换到 SQLAlchemy/MySQL。