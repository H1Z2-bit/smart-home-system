# 韩喆负责后端模块答辩讲解稿

## 1. 我负责的模块

我负责智能家居综合管理系统后端中的用户与权限相关模块，主要包括：

```text
用户注册、登录、退出
JWT/RSA 身份认证
RBAC 角色权限控制
家庭空间管理
家庭成员邀请、申请、审批、移除
系统配置管理
操作日志记录
统一接口返回格式
自动化测试
```

这些模块属于系统的基础支撑能力。前端页面、设备控制、报警处理等功能都需要先通过登录认证和家庭权限判断，才能安全访问对应资源。

## 2. 后端技术选择

后端使用 Python FastAPI 实现，原因是：

```text
1. FastAPI 开发效率高，适合课程设计快速完成完整系统。
2. 自动生成 Swagger 接口文档，方便前端联调。
3. Python 生态中 JWT、RSA、bcrypt、SQLAlchemy 等库成熟。
4. 后端结构清晰，后续接 MySQL 和扩展设备模块比较方便。
```

## 3. 后端分层结构

项目采用分层设计：

```text
API Router 层：接收前端 HTTP 请求
Schema 层：校验请求体和响应数据
Service 层：处理业务逻辑
Repository 层：访问数据，目前使用 MockRepository
Model 层：预留 SQLAlchemy 数据库模型
Core 层：认证、安全、权限、配置
```

这样设计的好处是，后续从 MockRepository 切换到 MySQLRepository 时，Service 层业务逻辑不需要大改。

## 4. JWT/RSA 认证流程

登录流程如下：

```text
用户输入手机号和密码
后端根据手机号查询用户
使用 bcrypt 校验密码哈希
校验通过后生成 JWT payload
使用 RSA 私钥进行 RS256 签名
返回 token 给前端
前端后续请求携带 Authorization: Bearer token
后端使用 RSA 公钥验证 token
解析出 user_id、username、role
```

安全点：

```text
1. 密码不明文保存，使用 SHA-256 预处理 + bcrypt 哈希。
2. token 使用 RSA 签名，私钥签发，公钥验签。
3. 私钥文件不提交到 Git 仓库。
4. 未携带 token 或 token 无效时，接口返回 401。
```

## 5. RBAC 权限控制

系统设计了四类用户角色：

| 角色 | 说明 |
|---|---|
| OWNER | 户主，拥有家庭最高权限 |
| MEMBER | 常住成员，可查看家庭和部分日志 |
| GUEST | 临时访客，只能查看有限家庭信息 |
| MAINTAINER | 维护人员，可查看家庭和日志，便于维修处理 |

权限判断不是只看用户全局角色，而是看用户在某个家庭中的成员角色。比如同一个用户可以在 A 家庭是 OWNER，在 B 家庭是 MEMBER。

权限控制流程：

```text
先判断是否登录
再判断是否属于该家庭
最后判断该家庭角色是否拥有对应权限
```

示例：

```text
修改系统配置需要 SYSTEM_CONFIG 权限，目前只有 OWNER 具备。
邀请成员需要 MEMBER_MANAGE 权限，目前只有 OWNER 具备。
查看日志需要 LOG_VIEW 权限，OWNER、MEMBER、MAINTAINER 具备，GUEST 不具备。
```

## 6. 家庭成员流程

成员管理支持两种加入方式。

第一种：户主邀请成员。

```text
OWNER 邀请手机号
系统生成 INVITED 成员记录
被邀请用户登录后接受邀请
成员状态变为 ACTIVE
```

第二种：用户申请加入家庭。

```text
用户提交加入申请
成员状态为 PENDING
OWNER 审批通过
成员状态变为 ACTIVE
OWNER 拒绝
成员状态变为 REJECTED
```

移除成员时，状态变为 REMOVED。

## 7. 操作日志

系统会记录关键操作，例如：

```text
用户注册
用户登录
修改密码
创建家庭
修改家庭
邀请成员
接受邀请
审批成员
修改成员权限
移除成员
修改系统配置
```

日志可以用于答辩演示系统的可追溯性，也方便后续排查问题。

## 8. 当前完成情况

当前完成的是 MockRepository 版本，也就是后端接口和业务逻辑已经跑通，但数据暂时保存在内存中。

已经完成：

```text
认证接口可用
JWT/RSA 可用
RBAC 权限可用
家庭空间接口可用
成员流程接口可用
系统配置接口可用
日志接口可用
Swagger 文档可用
自动化测试通过
```

待后续完成：

```text
等数据库表结构确定后，接入 MySQLRepository
与前端页面联调
与设备、报警模块联动
```

## 9. 测试说明

我为负责模块编写了自动化测试，覆盖：

```text
健康检查
登录和个人信息
未登录访问拦截
RS256 token 签名
家庭、成员、配置、日志主流程
普通成员权限不足
邀请并接受邀请流程
重复申请拦截
```

运行命令：

```powershell
D:\anaconda\envs\visgeom\python.exe -m pytest tests\test_hanzhe_api.py -q
```

当前测试结果为：

```text
7 passed
```

## 10. 答辩总结

我负责的模块主要解决系统中的身份认证、权限控制和家庭成员管理问题。通过 JWT/RSA 保证用户身份可信，通过 RBAC 保证不同角色只能访问允许的资源，通过操作日志保证关键行为可追踪。当前模块已经实现 Mock 版完整业务闭环，后续只需要替换 Repository 即可接入 MySQL 数据库。