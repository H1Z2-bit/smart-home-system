# Smart Home Backend API

Base URL:

```text
http://127.0.0.1:8080/api
```

## Unified Response

Success:

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

Failure:

```json
{
  "code": 400,
  "message": "parameter error",
  "data": null
}
```

## Error Codes

| Code | Meaning |
|---|---|
| 200 | success |
| 400 | bad request / parameter error |
| 401 | unauthorized / invalid token |
| 403 | forbidden / permission denied |
| 404 | resource not found |
| 409 | conflict |
| 500 | internal server error |

## Auth Header

Protected endpoints require:

```http
Authorization: Bearer <token>
```

## Mock Accounts

| Role | Phone | Password |
|---|---|---|
| OWNER | `13800000000` | `123456` |
| MEMBER | `13900000000` | `123456` |
| GUEST | `13700000000` | `123456` |
| MAINTAINER | `13600000000` | `123456` |

## Health

### GET `/api/health`

Response:

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "status": "ok"
  }
}
```

## Auth APIs

### POST `/api/auth/register`

Request:

```json
{
  "username": "han",
  "phone": "13810000000",
  "password": "123456"
}
```

### POST `/api/auth/login`

Request:

```json
{
  "phone": "13800000000",
  "password": "123456"
}
```

Response:

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "token": "mockjwt....",
    "user": {
      "userId": 1,
      "username": "han",
      "role": "OWNER"
    }
  }
}
```

### POST `/api/auth/logout`

Current implementation returns success. Token blacklist is reserved.

## User APIs

### GET `/api/users/profile`

Requires token.

### PUT `/api/users/password`

Requires token.

Request:

```json
{
  "oldPassword": "123456",
  "newPassword": "abcdef"
}
```

## Home APIs

### POST `/api/homes`

Requires token.

Request:

```json
{
  "homeName": "My Home",
  "address": "Beijing"
}
```

### GET `/api/homes`

Requires token. Returns home spaces joined by current user.

### GET `/api/homes/{homeId}`

Requires token and home membership.

### PUT `/api/homes/{homeId}`

Requires owner permission.

Request:

```json
{
  "homeName": "New Home Name",
  "address": "New Address"
}
```

### DELETE `/api/homes/{homeId}`

Requires owner permission.

## Member APIs

### POST `/api/homes/{homeId}/members/invite`

Requires owner permission.

Request:

```json
{
  "phone": "13900000000",
  "role": "MEMBER",
  "validTo": ""
}
```

### POST `/api/homes/{homeId}/members/apply`

Requires token.

Request:

```json
{
  "applyReason": "I am a family member"
}
```

### POST `/api/homes/{homeId}/members/{memberId}/approve`

Requires owner permission.

Request:

```json
{
  "approved": true,
  "role": "MEMBER"
}
```

### GET `/api/homes/{homeId}/members`

Requires home membership.

### PUT `/api/homes/{homeId}/members/{memberId}/permission`

Requires owner permission.

Request:

```json
{
  "role": "GUEST",
  "permissionScope": "ROOM:1,DEVICE:2",
  "validTo": "2026-07-10 23:59:59"
}
```

### DELETE `/api/homes/{homeId}/members/{memberId}`

Requires owner permission.

## System Config APIs

### GET `/api/homes/{homeId}/system/config`

Requires home membership.

### PUT `/api/homes/{homeId}/system/config`

Requires owner permission or maintainer permission.

Request:

```json
{
  "configKey": "smoke_threshold",
  "configValue": "80",
  "description": "Smoke alarm threshold"
}
```

## Operation Log APIs

### GET `/api/homes/{homeId}/logs`

Requires owner permission.

## Notes for Frontend

The frontend can first integrate:

1. `GET /api/health`
2. `POST /api/auth/login`
3. `GET /api/users/profile`
4. `GET /api/homes`
5. `GET /api/homes/1/members`
6. `GET /api/homes/1/system/config`

## Notes for Database

Current data is stored in MockRepository. MySQL tables should align with these model files:

- `models/User.h`
- `models/Home.h`
- `models/HomeMember.h`
- `models/SystemConfig.h`
- `models/OperationLog.h`

