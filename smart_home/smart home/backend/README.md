# 智能家居综合管理系统 Python 后端

本目录是智能家居综合管理系统的 Python FastAPI 后端。当前支持 MockRepository 和 MySQLRepository 两种模式：Mock 模式便于快速演示和测试，MySQL 模式用于完整联调和最终答辩。

## 已完成能力

- 用户注册、登录、JWT 鉴权
- RSA/HS256 Token 签发与验证
- RBAC 角色权限控制
- 家庭空间管理
- 成员邀请、申请、审批、权限修改、移除
- 系统配置与系统操作日志
- 房间、设备、设备控制
- 情景模式、定时任务、联动规则
- 报警中心、报警处理、设备自检
- 设备模拟与传感器数据模拟
- Mock 数据重置接口
- Swagger、OpenAPI、Postman/Apifox 接口集合
- Alembic 数据库迁移基线
- 自动化测试

## 1. 进入后端目录

```powershell
cd "C:\Users\hanzhe\Desktop\software\smart home\backend"
```

## 2. 使用 visgeom 环境

如果已经有 `visgeom` 环境：

```powershell
conda activate visgeom
```

如果没有依赖：

```powershell
pip install -r requirements.txt
```

当前项目自带 `.venv` 可能指向旧 Python 路径，建议优先使用 `visgeom`。

## 3. 配置环境变量

第一次运行可复制示例配置：

```powershell
Copy-Item .env.example .env
```

Mock 模式保持：

```text
USE_MOCK_REPOSITORY=true
APP_ENV=dev
```

## 4. 启动后端

```powershell
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

访问：

```text
健康检查：http://127.0.0.1:8000/api/health
接口文档：http://127.0.0.1:8000/docs
OpenAPI：http://127.0.0.1:8000/openapi.json
```

## 5. 默认演示账号

| 角色 | 手机号 | 密码 |
| --- | --- | --- |
| OWNER | `13800000000` | `123456` |
| MEMBER | `13900000000` | `123456` |
| GUEST | `13700000000` | `123456` |
| MAINTAINER | `13600000000` | `123456` |

## 6. 重置演示数据

演示或测试前可以恢复默认 Mock 数据：

```powershell
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/api/debug/reset"
```

该接口只在 `APP_ENV=dev/test/local` 开放。

## 7. 运行测试

```powershell
$env:USE_MOCK_REPOSITORY='true'
python -B -m pytest
```

MySQL 集成测试：

```powershell
$env:RUN_MYSQL_TESTS='1'
$env:USE_MOCK_REPOSITORY='false'
python -B -m pytest tests\test_mysql_mode_flow.py
```

当前测试覆盖健康检查、CRUD、认证、RBAC、成员邀请/申请流程、MySQL 模式核心流程、Mock 数据重置。

## 8. 运行演示脚本

先启动后端，然后另开一个 PowerShell：

```powershell
python scripts/demo_flow.py
```

脚本会自动完成：健康检查、重置数据、户主登录、邀请成员、成员接受邀请、修改成员权限、修改系统配置、控制设备、模拟报警、查询日志。

## 9. 接口文档和集合

| 文件 | 说明 |
| --- | --- |
| `docs/api_usage.md` | 核心接口使用说明 |
| `docs/permission_matrix.md` | RBAC 权限矩阵 |
| `docs/error_codes.md` | 错误码说明 |
| `docs/frontend_backend_integration.md` | 前后端联调说明 |
| `docs/database_model_audit.md` | 数据库、模型、接口字段核对 |
| `docs/alembic_migration_guide.md` | Alembic 迁移说明 |
| `docs/mysql_repository_plan.md` | MySQLRepository 对接计划 |
| `docs/openapi.json` | OpenAPI 文件 |
| `docs/smart_home_api.postman_collection.json` | Postman/Apifox 接口集合 |

导入 Postman/Apifox 后，先调用登录接口，再把返回的 `token` 填到集合变量 `token` 中。

刷新 OpenAPI 和 Postman 集合：

```powershell
python -B scripts\export_api_docs.py
```

## 10. MySQL 与迁移

MySQL 模式需要 `.env`：

```text
USE_MOCK_REPOSITORY=false
DATABASE_HOST=127.0.0.1
DATABASE_PORT=3306
DATABASE_NAME=smart_home
DATABASE_USER=root
DATABASE_PASSWORD=你的数据库密码
```

当前已有 Alembic 基线迁移，后续表结构变化按 `docs/alembic_migration_guide.md` 执行。
