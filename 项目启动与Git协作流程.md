# 智能家居综合管理系统启动流程与 Git 协作流程

## 一、项目整体启动顺序

本项目采用前后端分离结构，启动顺序建议为：

```text
1. 启动 MySQL 数据库
2. 导入数据库建表 SQL 和初始化数据
3. 启动 C++ 后端服务
4. 启动 Vue3 前端服务
5. 浏览器访问前端页面
6. 前端通过 RESTful API 调用后端接口
7. 后端访问 MySQL 并返回数据
```

整体关系如下：

```text
浏览器
-> Vue3 + Element Plus 前端
-> RESTful API
-> C++ 后端服务
-> MySQL 数据库
```

## 二、推荐项目目录结构

建议后续代码按下面结构整理：

```text
smart-home-system/
├── frontend/                  # 邓延霄负责，Vue3 + Element Plus 前端
├── backend/                   # 韩喆、周敬琦负责，C++ 后端
├── database/                  # 王涵负责，MySQL 建表和初始化数据
│   ├── schema.sql             # 建表 SQL
│   ├── init_data.sql          # 初始化数据
│   └── data_dictionary.md     # 数据字典
├── docs/                      # 项目文档
│   ├── api.md                 # 接口文档
│   ├── deploy.md              # 部署说明
│   └── test_cases.md          # 测试用例
├── README.md                  # 项目总说明
└── .gitignore                 # Git 忽略规则
```

## 三、数据库启动流程

数据库由王涵主要负责。

### 3.1 启动 MySQL

如果本机已经安装 MySQL，先启动 MySQL 服务。

Windows 可以在服务管理器中启动，也可以使用命令：

```powershell
net start mysql
```

如果服务名不是 `mysql`，可能是：

```powershell
net start MySQL80
```

### 3.2 创建数据库

登录 MySQL：

```powershell
mysql -u root -p
```

创建数据库：

```sql
CREATE DATABASE smart_home DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
```

使用数据库：

```sql
USE smart_home;
```

### 3.3 导入建表 SQL

如果建表文件放在 `database/schema.sql`：

```powershell
mysql -u root -p smart_home < database/schema.sql
```

如果有初始化数据：

```powershell
mysql -u root -p smart_home < database/init_data.sql
```

## 四、后端启动流程

后端由韩喆和周敬琦负责，建议使用 C++ Drogon。

### 4.1 后端准备内容

后端至少需要包含：

```text
1. C++ Web 框架 Drogon / Crow
2. MySQL 连接配置
3. JWT 生成和解析
4. RSA 签名验证
5. RESTful API 路由
6. 设备模拟定时任务
```

### 4.2 后端配置文件

建议后端使用配置文件保存数据库连接信息，例如：

```text
backend/config.json
```

示例内容：

```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 8080
  },
  "database": {
    "host": "127.0.0.1",
    "port": 3306,
    "name": "smart_home",
    "user": "root",
    "password": "your_password"
  },
  "jwt": {
    "expire_seconds": 7200
  }
}
```

注意：真实密码不要提交到 Git 仓库，可以提交 `config.example.json`，每个人本地复制成 `config.json` 后自行填写。

### 4.3 编译后端

如果后端使用 CMake，推荐命令：

```powershell
cd backend
mkdir build
cd build
cmake ..
cmake --build .
```

### 4.4 启动后端

编译完成后运行后端程序，例如：

```powershell
.\smart_home_backend.exe
```

后端启动成功后应显示类似：

```text
Server started at http://127.0.0.1:8080
```

可先测试登录或健康检查接口：

```text
GET http://127.0.0.1:8080/api/health
```

## 五、前端启动流程

前端由邓延霄负责，采用 Vue3 + Element Plus。

### 5.1 安装依赖

进入前端目录：

```powershell
cd frontend
```

安装依赖：

```powershell
npm install
```

### 5.2 配置后端接口地址

建议在前端 `.env.development` 中配置后端地址：

```text
VITE_API_BASE_URL=http://127.0.0.1:8080/api
```

### 5.3 启动前端

```powershell
npm run dev
```

启动成功后访问：

```text
http://127.0.0.1:5173
```

如果 Vite 使用其他端口，以终端显示为准。

## 六、完整联调流程

推荐每次联调按下面顺序进行：

```text
1. 王涵确认 MySQL 已启动
2. 王涵导入最新 schema.sql 和 init_data.sql
3. 韩喆、周敬琦启动 C++ 后端
4. 邓延霄启动 Vue3 前端
5. 浏览器打开前端页面
6. 使用测试账号登录
7. 测试设备列表、设备控制、报警记录等接口
8. 发现问题后先定位是前端、后端还是数据库问题
```

## 七、Git 协作目标

使用 Git 的目的：

```text
1. 代码统一保存到远程仓库
2. 组员可以随时拉取最新代码
3. 每个人负责自己的模块，减少文件互相覆盖
4. 出问题时可以回退到历史版本
5. 方便最终提交课程设计代码
```

## 八、第一次创建 Git 仓库流程

当前目录下如果还没有有效 Git 仓库，先执行：

```powershell
git init
```

设置默认分支为 `main`：

```powershell
git branch -M main
```

查看状态：

```powershell
git status
```

## 九、添加远程仓库

先在 GitHub / Gitee 上新建一个仓库，例如：

```text
smart-home-system
```

然后复制远程仓库地址。

如果使用 HTTPS 地址：

```powershell
git remote add origin https://github.com/你的用户名/smart-home-system.git
```

如果使用 Gitee：

```powershell
git remote add origin https://gitee.com/你的用户名/smart-home-system.git
```

查看远程仓库：

```powershell
git remote -v
```

## 十、第一次提交代码

建议不要直接 `git add .`，因为当前目录里有很多课程 PDF、Word、大文件。应该只提交项目代码和必要文档。

推荐：

```powershell
git add README.md .gitignore
git add frontend backend database docs
git add 智能家居系统完整方案与分工.md 项目启动与Git协作流程.md
git commit -m "init smart home system project"
```

如果暂时还没有代码目录，可以先提交文档：

```powershell
git add .gitignore 智能家居系统完整方案与分工.md 项目启动与Git协作流程.md
git commit -m "add project plan and collaboration workflow"
```

推送到远程仓库：

```powershell
git push -u origin main
```

## 十一、组员第一次拉取代码

组员在自己的电脑上执行：

```powershell
git clone https://github.com/你的用户名/smart-home-system.git
```

进入项目目录：

```powershell
cd smart-home-system
```

查看分支：

```powershell
git branch
```

## 十二、日常开发流程

每次开始写代码前，先拉取最新代码：

```powershell
git pull origin main
```

修改代码后查看状态：

```powershell
git status
```

提交自己的修改：

```powershell
git add 修改过的文件或目录
git commit -m "说明本次修改内容"
git push origin main
```

示例：

```powershell
git add backend/controllers/AuthController.cpp backend/services/AuthService.cpp
git commit -m "add login and jwt auth api"
git push origin main
```

## 十三、推荐分支管理方式

如果小组成员对 Git 不熟悉，可以先都提交到 `main`，但每次提交前必须先 `git pull`。

如果想更规范，可以每个人使用自己的分支：

| 成员 | 分支名 | 负责内容 |
|---|---|---|
| 韩喆 | `backend-auth` | 登录、JWT、权限、家庭成员 |
| 周敬琦 | `backend-device` | 设备、情景、报警、自检、模拟 |
| 邓延霄 | `frontend` | Vue3 前端页面 |
| 王涵 | `database` | MySQL 表结构和测试数据 |

创建分支：

```powershell
git checkout -b backend-auth
```

推送分支：

```powershell
git push -u origin backend-auth
```

切回主分支：

```powershell
git checkout main
```

拉取主分支：

```powershell
git pull origin main
```

## 十四、避免冲突的规则

建议小组约定：

```text
1. 韩喆主要修改 backend/auth、backend/member、backend/system
2. 周敬琦主要修改 backend/device、backend/alarm、backend/simulation
3. 邓延霄主要修改 frontend
4. 王涵主要修改 database
5. 修改公共接口前先在群里说一声
6. 每天开发前先 pull，开发后及时 push
7. 不要提交 node_modules、build、config.json、数据库密码和临时文件
```

## 十五、建议提交信息格式

推荐格式：

```text
类型: 简短说明
```

示例：

```text
feat: add user login api
feat: add device control page
fix: fix alarm status update
docs: update database dictionary
test: add login test data
```

常用类型：

| 类型 | 含义 |
|---|---|
| `feat` | 新功能 |
| `fix` | 修复问题 |
| `docs` | 文档修改 |
| `style` | 样式修改 |
| `refactor` | 代码重构 |
| `test` | 测试相关 |
| `chore` | 构建、配置、杂项 |

## 十六、最终交付前检查

最终提交前检查：

```text
1. 前端可以正常启动
2. 后端可以正常启动
3. MySQL 可以成功导入建表 SQL
4. 登录、设备控制、报警处理主流程可演示
5. README.md 写清楚启动步骤
6. .gitignore 已排除 node_modules、build、config.json 等文件
7. Git 远程仓库中包含 frontend、backend、database、docs
```

## 十七、推荐 README.md 内容

后续可以在项目根目录创建 `README.md`，包含：

```text
1. 项目名称
2. 项目简介
3. 技术栈
4. 小组分工
5. 目录结构
6. 数据库启动方式
7. 后端启动方式
8. 前端启动方式
9. 测试账号
10. 演示流程
```

