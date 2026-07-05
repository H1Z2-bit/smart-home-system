# Alembic 数据库迁移说明

本项目已经接入 SQLAlchemy 模型和 Alembic 迁移框架。当前数据库可以继续使用 `smart_home.sql` 初始化；后续如果表结构继续变化，建议统一用 Alembic 生成和执行迁移脚本，避免每个人手动改表导致结构不一致。

## 使用前提

1. 确认 `backend/.env` 中 MySQL 配置正确：
   - `DATABASE_HOST`
   - `DATABASE_PORT`
   - `DATABASE_NAME`
   - `DATABASE_USER`
   - `DATABASE_PASSWORD`
   - `USE_MOCK_REPOSITORY=false`
2. 确认已安装依赖：

```powershell
cd "C:\Users\hanzhe\Desktop\software\smart home\backend"
pip install -r requirements.txt
```

## 常用命令

查看当前数据库迁移版本：

```powershell
cd "C:\Users\hanzhe\Desktop\software\smart home\backend"
alembic current
```

根据 SQLAlchemy 模型自动生成迁移脚本：

```powershell
cd "C:\Users\hanzhe\Desktop\software\smart home\backend"
alembic revision --autogenerate -m "add device layout fields"
```

执行所有未应用的迁移：

```powershell
cd "C:\Users\hanzhe\Desktop\software\smart home\backend"
alembic upgrade head
```

查看迁移历史：

```powershell
cd "C:\Users\hanzhe\Desktop\software\smart home\backend"
alembic history
```

回退上一个迁移：

```powershell
cd "C:\Users\hanzhe\Desktop\software\smart home\backend"
alembic downgrade -1
```

## 团队协作规则

1. 修改数据库字段时，先改 `backend/app/models/` 下的 SQLAlchemy 模型。
2. 再运行 `alembic revision --autogenerate -m "说明"` 生成迁移脚本。
3. 人工检查 `backend/migrations/versions/` 下新生成的脚本，确认字段类型、默认值、索引、外键是否正确。
4. 本地执行 `alembic upgrade head` 验证迁移能成功。
5. 提交代码时同时提交模型文件和迁移脚本。
6. 其他成员拉代码后只需要运行 `alembic upgrade head`，不要各自手动改表。

## 当前建议

当前阶段已经有完整的 `smart_home.sql`，可以继续作为课程设计演示的初始化脚本。Alembic 从下一次结构变化开始使用即可，例如后续新增设备图片、房间楼层、用户头像、更多传感器指标时，都应该生成对应迁移脚本。

项目中已经加入 `0001_initial_mysql_baseline` 作为当前 SQL 结构基线。第一次接入 Alembic 时，在已有数据库上执行：

```powershell
cd "C:\Users\hanzhe\Desktop\software\smart home\backend"
alembic upgrade head
```

这一步会创建 `alembic_version` 表并记录当前基线，之后新增字段就可以继续用 `alembic revision --autogenerate` 管理。
