# 智能家居综合管理系统

本项目是软件工程课程设计“智能家居系统”的完整可运行版本，包含 Python FastAPI 后端、MySQL 数据库、uni-app 微信小程序端，以及接口文档、自动化测试和演示数据。

## 技术栈

| 模块 | 技术 |
| --- | --- |
| 后端 | Python + FastAPI + SQLAlchemy |
| 数据库 | MySQL 8.0 |
| 小程序 | uni-app + Vue3 |
| 接口 | RESTful API |
| 权限 | JWT 登录认证 + RBAC 角色权限控制 |
| 模拟 | 后端设备模拟接口 + 传感器/报警数据 |
| 文档 | OpenAPI + Postman Collection + Markdown |
| 测试 | pytest，支持 Mock 模式和 MySQL 集成测试 |

## 目录结构

```text
smart home/
├── backend/                 # FastAPI 后端
├── miniprogram/             # uni-app 微信小程序
├── sql/                     # MySQL 建表、演示数据、重置脚本
├── scripts/                 # 项目级辅助脚本
├── smart_home.sql           # 完整初始化 SQL 来源文件在上级 software 目录
└── README.md                # 项目总说明
```

## 后端启动

```powershell
cd "C:\Users\hanzhe\Desktop\software\smart home\backend"
conda activate visgeom
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

访问：

```text
健康检查：http://127.0.0.1:8000/api/health
Swagger：http://127.0.0.1:8000/docs
OpenAPI：http://127.0.0.1:8000/openapi.json
```

## MySQL 初始化

完整初始化：

```powershell
mysql -uroot -p --default-character-set=utf8mb4 < "C:\Users\hanzhe\Desktop\software\smart_home.sql"
```

分步骤初始化：

```powershell
mysql -uroot -p --default-character-set=utf8mb4 < "C:\Users\hanzhe\Desktop\software\smart home\sql\init_schema.sql"
mysql -uroot -p --default-character-set=utf8mb4 < "C:\Users\hanzhe\Desktop\software\smart home\sql\init_data.sql"
```

答辩前重置演示数据：

```powershell
mysql -uroot -p --default-character-set=utf8mb4 < "C:\Users\hanzhe\Desktop\software\smart home\sql\reset_demo_data.sql"
```

## 小程序运行

1. 用 HBuilderX 打开：

```text
C:\Users\hanzhe\Desktop\software\smart home\miniprogram
```

2. 修改后端地址：

```text
miniprogram/config/index.js
```

模拟器可用：

```js
http://127.0.0.1:8000
```

真机或局域网设备使用电脑 WLAN IPv4：

```js
http://你的电脑局域网IP:8000
```

3. HBuilderX 运行到微信开发者工具。

4. 微信开发者工具打开：

```text
详情 -> 本地设置 -> 不校验合法域名、web-view、TLS 版本以及 HTTPS 证书
```

## 默认账号

| 角色 | 手机号 | 密码 | 说明 |
| --- | --- | --- | --- |
| OWNER | `13800000000` | `123456` | 户主，全权限 |
| MEMBER | `13900000000` | `123456` | 普通成员，可查看、控制设备、执行场景 |
| GUEST | `13700000000` | `123456` | 访客，只读查看 |
| MAINTAINER | `13600000000` | `123456` | 维护人员，可处理自动化和报警 |

## 测试命令

Mock 模式完整测试：

```powershell
cd "C:\Users\hanzhe\Desktop\software\smart home\backend"
$env:USE_MOCK_REPOSITORY='true'
python -B -m pytest
```

MySQL 集成测试：

```powershell
cd "C:\Users\hanzhe\Desktop\software\smart home\backend"
$env:RUN_MYSQL_TESTS='1'
$env:USE_MOCK_REPOSITORY='false'
python -B -m pytest tests\test_mysql_mode_flow.py
```

## 接口文档

| 文件 | 说明 |
| --- | --- |
| `backend/docs/openapi.json` | 最新 OpenAPI 文档 |
| `backend/docs/smart_home_api.postman_collection.json` | Postman/Apifox 接口集合 |
| `backend/docs/frontend_backend_integration.md` | 前后端联调说明 |
| `backend/docs/permission_matrix.md` | RBAC 权限矩阵 |
| `backend/docs/error_codes.md` | 统一错误码说明 |
| `backend/docs/database_model_audit.md` | 数据库、模型、接口字段核对 |
| `backend/docs/alembic_migration_guide.md` | Alembic 迁移管理说明 |

刷新接口文档：

```powershell
cd "C:\Users\hanzhe\Desktop\software\smart home\backend"
python -B scripts\export_api_docs.py
```

## 答辩演示流程

1. 启动 MySQL 并确认 `smart_home` 数据库存在。
2. 启动后端，打开 `/docs` 确认接口正常。
3. 打开小程序，使用 OWNER 账号登录。
4. 展示首页家庭空间、设备统计、报警统计。
5. 展示房间管理、设备管理、设备详情新增字段和 3D 坐标。
6. 执行情景模式、定时任务、联动规则。
7. 在设备详情提交烟雾模拟数据，触发报警。
8. 到报警中心确认、处理、关闭报警。
9. 到系统日志页展示操作审计记录。

