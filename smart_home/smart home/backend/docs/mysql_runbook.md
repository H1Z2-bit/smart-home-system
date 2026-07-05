# MySQL 接入运行说明

当前后端已经支持通过 `USE_MOCK_REPOSITORY` 在 Mock 和 MySQL 之间切换。

## 1. 导入数据库

PowerShell 中执行：

```powershell
cd "C:\Users\hanzhe\Desktop\software\smart home\backend"
.\scripts\import_mysql_schema.ps1
```

脚本会提示输入 MySQL `root` 密码，并导入：

```text
C:\Users\hanzhe\Desktop\software\smart_home.sql
```

## 2. 配置后端

编辑：

```text
C:\Users\hanzhe\Desktop\software\smart home\backend\.env
```

把：

```env
DATABASE_PASSWORD=your_mysql_password
```

改成你的 MySQL 密码。

确认：

```env
USE_MOCK_REPOSITORY=false
```

## 3. 启动后端

```powershell
cd "C:\Users\hanzhe\Desktop\software\smart home\backend"
conda activate visgeom
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 4. 运行 MySQL 接入冒烟测试

```powershell
cd "C:\Users\hanzhe\Desktop\software\smart home\backend"
conda activate visgeom
python scripts\mysql_smoke_test.py
```

看到：

```text
MySQL smoke test passed.
```

说明后端已经真正通过 MySQLRepository 读取数据库。

## 5. 切回 Mock 模式

如果想临时使用 Mock 数据，把 `.env` 改成：

```env
USE_MOCK_REPOSITORY=true
```

然后重启后端。
