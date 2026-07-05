# MySQLRepository 对接计划

当前项目使用 MockRepository，后续数据库完成后可以按本计划切换为 MySQLRepository。

## 1. 已预留目录

```text
backend/app/repositories/mysql/
```

已预留文件：

| 文件 | 负责模块 |
| --- | --- |
| `user_mysql.py` | 用户账号 |
| `home_mysql.py` | 家庭空间 |
| `member_mysql.py` | 成员管理 |
| `system_config_mysql.py` | 系统配置 |
| `account_operation_log_mysql.py` | 账号与系统操作日志 |

## 2. 当前占位策略

这些类已经保留了和 MockRepository 对应的方法签名，但调用时会抛出 `MySQLRepositoryNotReady`。这样可以先让团队明确接口边界，等 SQLAlchemy Model 和数据库表完成后逐个实现。

## 3. 对接步骤

1. 王同学完成 MySQL 建表 SQL 和数据字典。
2. 后端新增 SQLAlchemy Model。
3. 在 `repositories/mysql/` 中实现查询、插入、更新、删除逻辑。
4. 修改 `repositories/factory.py`，根据 `USE_MOCK_REPOSITORY` 返回 Mock 或 MySQL 实现。
5. 将现有测试分为 Mock 测试和 MySQL 集成测试。
