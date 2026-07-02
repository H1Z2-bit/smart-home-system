# Smart Home Backend

This directory contains the C++ backend skeleton for the Smart Home Management System.

## Tech Stack

- Language: C++17
- Current HTTP entry: lightweight built-in HTTP server based on sockets
- Future framework target: Drogon or Crow
- Database target: MySQL
- Current data access: MockRepository in memory
- Auth design: JWT token skeleton + mock RSA signature
- Permission design: RBAC + resource-level permission placeholders

## Directory Structure

```text
backend/
├── CMakeLists.txt
├── config.example.json
├── include/
│   ├── controllers/
│   ├── services/
│   ├── repositories/
│   ├── models/
│   ├── dto/
│   └── utils/
├── src/
│   ├── controllers/
│   ├── services/
│   ├── repositories/
│   ├── utils/
│   └── main.cpp
└── tests/
```

## Build

```powershell
cd backend
mkdir build
cd build
cmake ..
cmake --build .
```

## Run

After build, run the generated executable:

```powershell
.\Debug\smart_home_backend.exe
```

or, depending on your generator:

```powershell
.\smart_home_backend.exe
```

The server listens on:

```text
http://127.0.0.1:8080
```

Health check:

```text
GET http://127.0.0.1:8080/api/health
```

Expected response:

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "status": "ok"
  }
}
```

## Mock Test Accounts

| Role | Phone | Password |
|---|---|---|
| OWNER | `13800000000` | `123456` |
| MEMBER | `13900000000` | `123456` |
| GUEST | `13700000000` | `123456` |
| MAINTAINER | `13600000000` | `123456` |

## Current Implemented Modules

- Auth: register, login, logout
- User: profile, change password
- Home: create, list, get, update, delete
- Member: invite, apply, approve, list, update permission, remove
- SystemConfig: list, update
- OperationLog: write and list
- PermissionService: owner/member/role checks

## MySQL Switch Plan

Current services depend on repository interfaces:

- `UserRepository`
- `HomeRepository`
- `MemberRepository`
- `SystemConfigRepository`
- `OperationLogRepository`

The current implementation uses:

- `MockUserRepository`
- `MockHomeRepository`
- `MockMemberRepository`
- `MockSystemConfigRepository`
- `MockOperationLogRepository`

When Wang Han completes the MySQL schema, add corresponding implementations:

- `MySqlUserRepository`
- `MySqlHomeRepository`
- `MySqlMemberRepository`
- `MySqlSystemConfigRepository`
- `MySqlOperationLogRepository`

Then replace MockRepository creation in Service files with MySQLRepository creation, or introduce a repository factory / dependency injection container.

## Security Notes

The current JWT/RSA/password implementations are skeleton placeholders for early frontend and database integration.

TODO before final delivery:

- Replace mock JWT format with standard JWT.
- Replace mock RSA signature with real RS256.
- Replace simple password hash with BCrypt or SHA-256 + random salt.
- Add token expiration and optional logout token blacklist.

