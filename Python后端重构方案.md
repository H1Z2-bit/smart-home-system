# 智能家居综合管理系统 Python 后端重构方案

## 一、重构结论

本项目后端建议由原来的 C++ 后端调整为 Python 后端，推荐使用：

```text
Python 3.11 + FastAPI + SQLAlchemy + MySQL + JWT/RSA + RBAC + APScheduler
```

调整后的整体技术路线为：

| 部分 | 技术选型 | 说明 |
|---|---|---|
| 前端 | Vue3 + Element Plus | 保持不变，负责页面与交互 |
| 后端 | Python + FastAPI | 替代 C++ 后端，提供 RESTful API |
| 数据库 | MySQL | 保持不变，保存业务数据 |
| ORM | SQLAlchemy 2.x | Python 操作 MySQL 的主流方案 |
| 数据库迁移 | Alembic | 管理建表、字段变更、版本升级 |
| 接口文档 | FastAPI 自动 Swagger | 启动后自动生成 `/docs` 接口文档 |
| 登录认证 | JWT | 登录成功后返回 token |
| Token 签名 | RSA | 使用私钥签发 token，公钥验签 |
| 密码安全 | bcrypt 加盐哈希 | 不保存明文密码 |
| 权限控制 | RBAC | 按角色控制接口访问权限 |
| 设备模拟 | APScheduler 后台定时任务 | 周期更新设备状态、传感器数据、报警 |
| 部署方式 | 本地或局域网运行 | 前端调用后端 `http://127.0.0.1:8000/api` |

推荐框架选 FastAPI，而不是 Flask。原因是 FastAPI 自动生成接口文档，数据校验方便，异步能力好，和前端联调非常直观，适合课程设计快速做出完整可演示系统。

## 二、为什么从 C++ 换成 Python

### 2.1 开发效率更高

智能家居系统的重点不是底层性能，而是完整业务流程，包括用户、家庭、成员、设备、情景、报警、日志、数据库、前后端联调。Python 能更快完成这些业务模块。

### 2.2 生态更适合 Web 后端

FastAPI、SQLAlchemy、PyJWT、cryptography、APScheduler 都是成熟库，可以直接解决接口、数据库、认证、定时任务等问题，不需要自己写大量底层代码。

### 2.3 前后端联调更方便

FastAPI 启动后自带接口测试页面：

```text
http://127.0.0.1:8000/docs
```

前端和后端可以直接看接口参数、返回格式和错误码，减少沟通成本。

### 2.4 更适合课程设计交付

课程设计更看重系统完整性、需求覆盖、演示效果和文档质量。Python 后端更容易在有限时间内完成可运行软件。

## 三、后端整体架构

系统仍然采用：

```text
B/S 架构 + 前后端分离 + RESTful API + MVC/分层设计
```

后端内部分层为：

```text
Vue3 前端
    ↓ HTTP JSON
FastAPI Router 层
    ↓
Service 业务层
    ↓
Repository 数据访问层
    ↓
SQLAlchemy ORM
    ↓
MySQL 数据库
```

各层职责如下：

| 层级 | 目录建议 | 作用 |
|---|---|---|
| Router 层 | `app/api/v1/` | 接收 HTTP 请求，定义 RESTful API |
| Schema 层 | `app/schemas/` | 定义请求体和响应体，进行数据校验 |
| Service 层 | `app/services/` | 编写核心业务逻辑 |
| Repository 层 | `app/repositories/` | 封装数据库查询和 Mock 数据访问 |
| Model 层 | `app/models/` | 定义 SQLAlchemy 数据表模型 |
| Core 层 | `app/core/` | 配置、JWT、RSA、权限、异常处理 |
| Tasks 层 | `app/tasks/` | 后台定时任务和设备模拟 |
| Utils 层 | `app/utils/` | 时间、日志、通用工具函数 |

## 四、推荐项目目录结构

```text
backend/
├── app/
│   ├── main.py                         # FastAPI 应用入口
│   ├── api/
│   │   └── v1/
│   │       ├── api_router.py            # 汇总所有路由
│   │       ├── auth.py                  # 登录、注册、退出
│   │       ├── users.py                 # 用户信息、修改密码
│   │       ├── homes.py                 # 家庭空间
│   │       ├── members.py               # 成员管理
│   │       ├── rooms.py                 # 房间管理
│   │       ├── devices.py               # 设备管理与控制
│   │       ├── scenes.py                # 情景模式
│   │       ├── schedules.py             # 定时任务
│   │       ├── linkages.py              # 联动规则
│   │       ├── alarms.py                # 报警中心
│   │       ├── self_checks.py           # 设备自检
│   │       ├── system_config.py         # 系统配置
│   │       └── logs.py                  # 操作日志
│   ├── core/
│   │   ├── config.py                    # 读取 .env 配置
│   │   ├── security.py                  # 密码哈希、JWT、RSA
│   │   ├── permissions.py               # RBAC 权限判断
│   │   ├── deps.py                      # 获取当前用户、数据库会话
│   │   └── exceptions.py                # 统一异常处理
│   ├── db/
│   │   ├── session.py                   # 数据库连接
│   │   ├── base.py                      # ORM 基类
│   │   └── init_db.py                   # 初始化数据
│   ├── models/
│   │   ├── user.py
│   │   ├── home.py
│   │   ├── member.py
│   │   ├── room.py
│   │   ├── device.py
│   │   ├── scene.py
│   │   ├── schedule.py
│   │   ├── linkage.py
│   │   ├── alarm.py
│   │   ├── self_check.py
│   │   ├── system_config.py
│   │   └── operation_log.py
│   ├── schemas/
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── home.py
│   │   ├── member.py
│   │   ├── device.py
│   │   ├── scene.py
│   │   ├── alarm.py
│   │   └── common.py
│   ├── repositories/
│   │   ├── mock/
│   │   │   ├── user_mock.py
│   │   │   ├── home_mock.py
│   │   │   └── device_mock.py
│   │   ├── user_repository.py
│   │   ├── home_repository.py
│   │   ├── device_repository.py
│   │   └── alarm_repository.py
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── user_service.py
│   │   ├── home_service.py
│   │   ├── member_service.py
│   │   ├── device_service.py
│   │   ├── scene_service.py
│   │   ├── schedule_service.py
│   │   ├── linkage_service.py
│   │   ├── alarm_service.py
│   │   ├── self_check_service.py
│   │   ├── system_config_service.py
│   │   └── operation_log_service.py
│   ├── tasks/
│   │   ├── scheduler.py                 # APScheduler 启停
│   │   ├── device_simulator.py          # 模拟设备状态
│   │   ├── sensor_simulator.py          # 模拟传感器数据
│   │   └── alarm_detector.py            # 报警检测任务
│   └── utils/
│       ├── response.py                  # 统一返回格式
│       └── time.py
├── alembic/                             # 数据库迁移目录
├── tests/                               # 后端接口测试
├── .env.example                         # 配置示例，不放真实密码
├── requirements.txt                     # Python 依赖
├── README.md                            # 后端说明
└── alembic.ini
```

## 五、后端依赖建议

`requirements.txt` 建议包含：

```text
fastapi
uvicorn[standard]
pydantic
pydantic-settings
sqlalchemy
pymysql
alembic
python-jose[cryptography]
passlib[bcrypt]
python-multipart
apscheduler
python-dotenv
pytest
httpx
```

各依赖作用：

| 依赖 | 作用 |
|---|---|
| `fastapi` | Web 后端框架 |
| `uvicorn` | FastAPI 运行服务器 |
| `pydantic` | 请求体和响应体数据校验 |
| `pydantic-settings` | 读取 `.env` 配置 |
| `sqlalchemy` | ORM，操作 MySQL |
| `pymysql` | Python 连接 MySQL 的驱动 |
| `alembic` | 数据库迁移管理 |
| `python-jose[cryptography]` | JWT 生成、解析、RSA 签名验签 |
| `passlib[bcrypt]` | 密码加盐哈希 |
| `apscheduler` | 定时任务，设备模拟和报警检测 |
| `pytest` | 自动化测试 |
| `httpx` | 测试 HTTP 接口 |

## 六、统一接口返回格式

所有接口统一返回：

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

错误示例：

```json
{
  "code": 401,
  "message": "unauthorized",
  "data": null
}
```

建议错误码：

| code | 含义 |
|---|---|
| 200 | 成功 |
| 400 | 参数错误 |
| 401 | 未登录或 token 无效 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 409 | 数据冲突，例如手机号已注册 |
| 500 | 服务器内部错误 |

## 七、核心配置文件

`.env.example` 示例：

```text
APP_NAME=smart-home-backend
APP_ENV=dev
APP_HOST=0.0.0.0
APP_PORT=8000

DATABASE_HOST=127.0.0.1
DATABASE_PORT=3306
DATABASE_NAME=smart_home
DATABASE_USER=root
DATABASE_PASSWORD=your_password

JWT_ALGORITHM=RS256
JWT_EXPIRE_MINUTES=120
JWT_PRIVATE_KEY_PATH=keys/private_key.pem
JWT_PUBLIC_KEY_PATH=keys/public_key.pem

CORS_ORIGINS=http://127.0.0.1:5173,http://localhost:5173
USE_MOCK_REPOSITORY=true
```

说明：

```text
.env.example 可以提交到 Git。
.env 不能提交到 Git，因为里面可能有数据库密码和私钥路径。
```

## 八、认证与权限方案

### 8.1 登录流程

```text
用户输入手机号和密码
-> 前端调用 POST /api/auth/login
-> 后端查询用户
-> bcrypt 验证密码
-> 生成 JWT payload
-> 使用 RSA 私钥签名 token
-> 返回 token 和用户信息
-> 前端保存 token
-> 后续请求在 Header 中携带 Authorization: Bearer token
-> 后端使用 RSA 公钥验签并解析用户身份
-> RBAC 判断是否允许访问该接口
```

### 8.2 JWT 内容建议

```json
{
  "sub": "1",
  "username": "han",
  "role": "OWNER",
  "home_id": 1,
  "exp": 1710000000
}
```

### 8.3 角色设计

| 角色 | 说明 | 权限 |
|---|---|---|
| OWNER | 户主 | 家庭、成员、设备、报警、系统设置最高权限 |
| MEMBER | 常住成员 | 查看家庭、控制授权设备、使用情景模式 |
| GUEST | 临时成员 | 在限定时间、限定范围内控制设备 |
| MAINTAINER | 维护人员 | 查看故障、自检、提交维护结果 |
| SYSTEM | 系统任务 | 执行定时任务、传感器模拟、报警检测 |

### 8.4 权限控制方式

后端使用依赖函数控制权限，例如：

```text
require_roles("OWNER")
require_roles("OWNER", "MEMBER")
require_home_permission(home_id, "DEVICE_CONTROL")
```

权限判断分两层：

```text
第一层：是否登录，token 是否有效。
第二层：是否有角色权限或家庭资源权限。
```

## 九、数据访问方案

### 9.1 第一阶段：MockRepository

为了让前端先联调，后端第一阶段使用 MockRepository，不依赖 MySQL。

优点：

```text
1. 后端可以快速启动。
2. 前端可以提前调用接口。
3. 数据库表还没完全确定时，不阻塞开发。
4. 接口格式先稳定下来。
```

### 9.2 第二阶段：MySQLRepository

数据库表结构完成后，把 Repository 从 Mock 切换到 MySQL。

推荐方式：

```text
Service 层不直接操作数据库。
Service 只调用 Repository 接口。
MockRepository 和 MySQLRepository 提供相同方法。
通过配置 USE_MOCK_REPOSITORY 控制使用哪一种。
```

示例：

```text
USE_MOCK_REPOSITORY=true   使用内存模拟数据
USE_MOCK_REPOSITORY=false  使用 MySQL 数据库
```

## 十、韩喆负责模块 Python 方案

韩喆负责后端一，主要方向仍然是用户、安全、权限、家庭成员、系统管理。

### 10.1 用户认证模块

接口：

| 方法 | 路径 | 功能 |
|---|---|---|
| POST | `/api/auth/register` | 用户注册 |
| POST | `/api/auth/login` | 用户登录 |
| POST | `/api/auth/logout` | 用户退出 |
| GET | `/api/users/profile` | 查看个人信息 |
| PUT | `/api/users/password` | 修改密码 |

实现内容：

```text
1. 注册时校验手机号唯一。
2. 密码使用 bcrypt 加盐哈希。
3. 登录成功后签发 JWT。
4. 所有需要登录的接口解析 token。
5. 登录、退出、修改密码写入操作日志。
```

### 10.2 JWT/RSA 模块

文件建议：

```text
app/core/security.py
```

职责：

```text
1. 加载 RSA 私钥和公钥。
2. 使用私钥生成 JWT。
3. 使用公钥验证 JWT。
4. 校验 token 是否过期。
5. 从 token 中提取 user_id、role、home_id。
```

### 10.3 RBAC 权限模块

文件建议：

```text
app/core/permissions.py
```

职责：

```text
1. 定义角色枚举 OWNER、MEMBER、GUEST、MAINTAINER、SYSTEM。
2. 定义权限枚举，例如 HOME_MANAGE、DEVICE_CONTROL、ALARM_PROCESS。
3. 判断用户是否拥有某个家庭空间的操作权限。
4. 给 Router 提供权限依赖函数。
```

### 10.4 家庭空间模块

接口：

| 方法 | 路径 | 功能 |
|---|---|---|
| POST | `/api/homes` | 创建家庭空间 |
| GET | `/api/homes` | 查询当前用户加入的家庭 |
| GET | `/api/homes/{home_id}` | 查看家庭详情 |
| PUT | `/api/homes/{home_id}` | 修改家庭信息 |
| DELETE | `/api/homes/{home_id}` | 删除家庭空间 |

权限：

```text
创建家庭：登录用户即可。
查看家庭：家庭成员即可。
修改家庭：OWNER。
删除家庭：OWNER。
```

### 10.5 成员管理模块

接口：

| 方法 | 路径 | 功能 |
|---|---|---|
| POST | `/api/homes/{home_id}/members/invite` | 邀请成员 |
| POST | `/api/homes/{home_id}/members/apply` | 申请加入家庭 |
| POST | `/api/homes/{home_id}/members/{member_id}/approve` | 审批成员 |
| GET | `/api/homes/{home_id}/members` | 成员列表 |
| PUT | `/api/homes/{home_id}/members/{member_id}/permission` | 修改成员权限 |
| DELETE | `/api/homes/{home_id}/members/{member_id}` | 移除成员 |

成员状态：

```text
PENDING   待审批
ACTIVE    正常
REJECTED  已拒绝
REMOVED   已移除
EXPIRED   临时权限过期
```

### 10.6 系统配置模块

接口：

| 方法 | 路径 | 功能 |
|---|---|---|
| GET | `/api/homes/{home_id}/system/config` | 查询系统配置 |
| PUT | `/api/homes/{home_id}/system/config` | 修改系统配置 |

配置内容示例：

```text
alarm_smoke_threshold
alarm_gas_threshold
temperature_high_threshold
auto_alarm_enabled
simulation_enabled
```

### 10.7 操作日志模块

接口：

| 方法 | 路径 | 功能 |
|---|---|---|
| GET | `/api/homes/{home_id}/logs` | 查询操作日志 |

日志写入场景：

```text
1. 登录成功、登录失败。
2. 创建家庭空间。
3. 邀请、审批、移除成员。
4. 修改成员权限。
5. 修改系统配置。
6. 控制设备。
7. 处理报警。
```

## 十一、周敬琦负责模块 Python 方案

周敬琦负责后端二，主要方向是设备、房间、情景、定时任务、联动、报警、自检、设备模拟。

### 11.1 房间管理

| 方法 | 路径 | 功能 |
|---|---|---|
| POST | `/api/homes/{home_id}/rooms` | 新增房间 |
| GET | `/api/homes/{home_id}/rooms` | 房间列表 |
| PUT | `/api/rooms/{room_id}` | 修改房间 |
| DELETE | `/api/rooms/{room_id}` | 删除房间 |

### 11.2 设备管理与控制

| 方法 | 路径 | 功能 |
|---|---|---|
| POST | `/api/homes/{home_id}/devices` | 添加设备 |
| GET | `/api/homes/{home_id}/devices` | 设备列表 |
| GET | `/api/devices/{device_id}` | 设备详情 |
| PUT | `/api/devices/{device_id}` | 修改设备 |
| DELETE | `/api/devices/{device_id}` | 删除设备 |
| POST | `/api/devices/{device_id}/control` | 控制设备 |

### 11.3 设备模拟

使用 APScheduler 启动后台任务：

```text
每 5 秒更新一次设备在线状态。
每 5 秒生成一次温度、烟雾、燃气等传感器数据。
每 10 秒检测一次报警条件。
每 30 秒执行一次定时任务扫描。
```

模拟设备类型：

| 类型 | 状态字段 |
|---|---|
| 智能灯 | on/off、brightness |
| 智能插座 | on/off、power |
| 温度传感器 | temperature |
| 烟雾传感器 | smoke_value、status |
| 燃气传感器 | gas_value、status |
| 门磁传感器 | opened/closed |
| 摄像头 | online/offline |

### 11.4 情景模式

| 方法 | 路径 | 功能 |
|---|---|---|
| POST | `/api/homes/{home_id}/scenes` | 创建情景 |
| GET | `/api/homes/{home_id}/scenes` | 情景列表 |
| PUT | `/api/scenes/{scene_id}` | 修改情景 |
| DELETE | `/api/scenes/{scene_id}` | 删除情景 |
| POST | `/api/scenes/{scene_id}/execute` | 执行情景 |

### 11.5 定时任务

| 方法 | 路径 | 功能 |
|---|---|---|
| POST | `/api/homes/{home_id}/schedules` | 创建定时任务 |
| GET | `/api/homes/{home_id}/schedules` | 查询定时任务 |
| PUT | `/api/schedules/{schedule_id}` | 修改定时任务 |
| PUT | `/api/schedules/{schedule_id}/status` | 启用或停用 |
| DELETE | `/api/schedules/{schedule_id}` | 删除定时任务 |

### 11.6 联动规则

| 方法 | 路径 | 功能 |
|---|---|---|
| POST | `/api/homes/{home_id}/linkages` | 创建联动规则 |
| GET | `/api/homes/{home_id}/linkages` | 查询联动规则 |
| PUT | `/api/linkages/{rule_id}` | 修改规则 |
| DELETE | `/api/linkages/{rule_id}` | 删除规则 |

联动示例：

```text
如果烟雾浓度 > 阈值
-> 自动打开报警器
-> 自动生成报警记录
-> 前端报警中心显示未确认报警
```

### 11.7 报警与自检

| 方法 | 路径 | 功能 |
|---|---|---|
| GET | `/api/homes/{home_id}/alarms` | 报警列表 |
| GET | `/api/alarms/{alarm_id}` | 报警详情 |
| POST | `/api/alarms/{alarm_id}/confirm` | 确认报警 |
| POST | `/api/alarms/{alarm_id}/process` | 处理报警 |
| POST | `/api/alarms/{alarm_id}/resolve` | 消警 |
| POST | `/api/devices/{device_id}/self-check` | 设备自检 |
| GET | `/api/devices/{device_id}/self-checks` | 自检记录 |

## 十二、数据库表保持不变但映射到 Python Model

数据库仍然由王涵负责，表结构基本沿用原方案：

```text
user_account
home_space
home_member
room_area
device
sensor_data
scene_mode
scene_device_action
schedule_task
linkage_rule
alarm_record
alarm_process_log
self_check_record
operation_log
system_config
```

Python 后端中的 `models/` 与这些表一一对应。

建议数据库协作方式：

```text
王涵先设计 schema.sql。
后端根据 schema.sql 编写 SQLAlchemy models。
然后使用 Alembic 对比和迁移。
最终数据库建表 SQL 和 Alembic 迁移文件都提交到 Git。
```

## 十三、前后端接口约定

前端请求地址建议：

```text
VITE_API_BASE_URL=http://127.0.0.1:8000/api
```

前端请求头：

```text
Authorization: Bearer <token>
Content-Type: application/json
```

登录响应示例：

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

## 十四、迭代开发计划

| 迭代 | 内容 | 负责人 |
|---|---|---|
| 第 1 版 | Python 后端项目骨架、健康检查、统一返回格式、Swagger | 韩喆、周敬琦 |
| 第 2 版 | 注册、登录、JWT/RSA、用户信息、MockRepository | 韩喆 |
| 第 3 版 | 家庭空间、成员管理、RBAC 权限 | 韩喆 |
| 第 4 版 | 房间、设备、设备控制、设备状态 Mock | 周敬琦 |
| 第 5 版 | MySQL 接入、SQLAlchemy Model、Alembic 迁移 | 韩喆、周敬琦、王涵 |
| 第 6 版 | 情景模式、定时任务、联动规则 | 周敬琦 |
| 第 7 版 | 报警、自检、操作日志、系统配置 | 韩喆、周敬琦 |
| 第 8 版 | 前后端联调、测试、答辩演示流程 | 全体 |

## 十五、启动流程调整

### 15.1 创建虚拟环境

```powershell
cd C:\Users\hanzhe\Desktop\software\backend
python -m venv .venv
.\.venv\Scripts\activate
```

### 15.2 安装依赖

```powershell
pip install -r requirements.txt
```

### 15.3 配置环境变量

```powershell
copy .env.example .env
```

然后修改 `.env` 中的数据库账号密码。

### 15.4 启动后端

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

启动成功后访问：

```text
健康检查：http://127.0.0.1:8000/api/health
接口文档：http://127.0.0.1:8000/docs
```

## 十六、Git 调整建议

后端改成 Python 后，`.gitignore` 需要加入：

```text
backend/.venv/
backend/__pycache__/
backend/.pytest_cache/
backend/.env
backend/*.db
backend/keys/private_key.pem
```

建议不要删除旧 C++ 后端，先保留备份或移动到：

```text
backend_cpp_backup/
```

等 Python 后端跑通后，再决定是否删除旧版本。

## 十七、最终推荐方案一句话总结

本项目后端建议改为 Python FastAPI 实现，保留原有 RESTful API、JWT/RSA、RBAC、MySQL、设备模拟和前后端分离架构。Python 版本能显著降低后端开发难度，提高接口联调效率，更适合在课程设计周期内完成一套可以完整演示和实际使用的软件系统。
