# FastAPI 后端接口快速联调说明

## 1. 启动方式

进入后端目录：

```powershell
cd "D:\coding\VScode\projects\smart home\backend"
.\.venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

访问：

```text
健康检查：http://127.0.0.1:8000/api/health
接口文档：http://127.0.0.1:8000/docs
```

## 2. 当前数据来源

当前阶段使用 MockRepository，不连接 MySQL。

默认数据：

- `home_id=1`
- 默认登录账号：
  - 业主：`13800000000` / `123456`
  - 普通成员：`13900000000` / `123456`
  - 访客：`13700000000` / `123456`
  - 维护人员：`13600000000` / `123456`
- 房间：客厅、主卧、厨房
- 设备：客厅灯、客厅插座、主卧温度传感器、厨房烟雾传感器、厨房燃气传感器、入户门磁
- 情景模式：离家模式
- 报警记录：厨房烟雾报警示例

## 3. 认证、家庭空间与成员接口

登录获取 token：

```powershell
curl -X POST "http://127.0.0.1:8000/api/auth/login" -H "Content-Type: application/json" -d "{\"phone\":\"13800000000\",\"password\":\"123456\"}"
```

后续需要登录的接口请带请求头：

```text
Authorization: Bearer 登录接口返回的token
```

查询当前用户：

```powershell
curl "http://127.0.0.1:8000/api/users/profile" -H "Authorization: Bearer 登录接口返回的token"
```

查询家庭空间：

```powershell
curl "http://127.0.0.1:8000/api/homes" -H "Authorization: Bearer 登录接口返回的token"
```

查询家庭成员：

```powershell
curl "http://127.0.0.1:8000/api/homes/1/members" -H "Authorization: Bearer 登录接口返回的token"
```

邀请成员：

```powershell
curl -X POST "http://127.0.0.1:8000/api/homes/1/members/invite" -H "Authorization: Bearer 登录接口返回的token" -H "Content-Type: application/json" -d "{\"phone\":\"13600000000\",\"role\":\"MAINTAINER\",\"expire_at\":null}"
```

## 4. 系统配置接口

查询系统配置：

```powershell
curl "http://127.0.0.1:8000/api/homes/1/system/config" -H "Authorization: Bearer 登录接口返回的token"
```

修改系统配置：

```powershell
curl -X PUT "http://127.0.0.1:8000/api/homes/1/system/config" -H "Authorization: Bearer 登录接口返回的token" -H "Content-Type: application/json" -d "{\"temperature_high_threshold\":36.5,\"simulation_enabled\":false}"
```

查询系统/成员日志：

```powershell
curl "http://127.0.0.1:8000/api/homes/1/system/logs" -H "Authorization: Bearer 登录接口返回的token"
```

说明：`/api/homes/1/logs` 保留给设备、房间、情景等操作日志；`/api/homes/1/system/logs` 用于登录、家庭、成员、系统配置相关日志。

## 5. 房间接口

查询房间：

```powershell
curl "http://127.0.0.1:8000/api/homes/1/rooms"
```

新增房间：

```powershell
curl -X POST "http://127.0.0.1:8000/api/homes/1/rooms" -H "Content-Type: application/json" -d "{\"room_name\":\"书房\",\"room_type\":\"study\",\"remark\":\"学习办公区域\"}"
```

修改房间：

```powershell
curl -X PUT "http://127.0.0.1:8000/api/rooms/2" -H "Content-Type: application/json" -d "{\"room_name\":\"主卧\",\"room_type\":\"bedroom\",\"remark\":\"主卧区域\"}"
```

删除房间：

```powershell
curl -X DELETE "http://127.0.0.1:8000/api/rooms/2"
```

如果房间下存在设备，会返回：

```json
{
  "code": 400,
  "message": "该房间下存在设备，不能删除",
  "data": null
}
```

## 6. 设备接口

查询设备：

```powershell
curl "http://127.0.0.1:8000/api/homes/1/devices"
```

按房间查询设备：

```powershell
curl "http://127.0.0.1:8000/api/homes/1/devices?room_id=1"
```

查询设备详情：

```powershell
curl "http://127.0.0.1:8000/api/devices/1"
```

新增设备：

```powershell
curl -X POST "http://127.0.0.1:8000/api/homes/1/devices" -H "Content-Type: application/json" -d "{\"room_id\":1,\"device_name\":\"书房灯\",\"device_type\":\"light\",\"device_status\":\"off\",\"is_key_device\":false}"
```

修改设备：

```powershell
curl -X PUT "http://127.0.0.1:8000/api/devices/1" -H "Content-Type: application/json" -d "{\"device_status\":\"on\"}"
```

控制设备开关：

```powershell
curl -X POST "http://127.0.0.1:8000/api/devices/1/control" -H "Content-Type: application/json" -d "{\"action\":\"switch\",\"target_state\":\"on\",\"param_value\":null}"
```

传感器类设备不允许控制，例如：

```powershell
curl -X POST "http://127.0.0.1:8000/api/devices/3/control" -H "Content-Type: application/json" -d "{\"action\":\"switch\",\"target_state\":\"off\",\"param_value\":null}"
```

会返回：

```json
{
  "code": 400,
  "message": "传感器类设备不允许控制",
  "data": null
}
```

删除设备：

```powershell
curl -X DELETE "http://127.0.0.1:8000/api/devices/1"
```

## 7. 操作日志接口

查询家庭空间操作日志：

```powershell
curl "http://127.0.0.1:8000/api/homes/1/logs"
```

设备控制、房间管理、设备管理成功后会写入 Mock 操作日志。当前还没有登录模块，`operator_id` 暂时固定为 `1`。

## 8. 情景模式接口

查询情景模式：

```powershell
curl "http://127.0.0.1:8000/api/homes/1/scenes"
```

新增情景模式：

```powershell
curl -X POST "http://127.0.0.1:8000/api/homes/1/scenes" -H "Content-Type: application/json" -d "{\"scene_name\":\"睡眠模式\",\"enabled\":true,\"actions\":[{\"device_id\":1,\"target_state\":\"off\",\"param_value\":null,\"sort_no\":1},{\"device_id\":2,\"target_state\":\"off\",\"param_value\":null,\"sort_no\":2}]}"
```

执行情景模式：

```powershell
curl -X POST "http://127.0.0.1:8000/api/scenes/1/execute"
```

## 9. 定时任务接口

查询定时任务：

```powershell
curl "http://127.0.0.1:8000/api/homes/1/schedules"
```

新增定时任务：

```powershell
curl -X POST "http://127.0.0.1:8000/api/homes/1/schedules" -H "Content-Type: application/json" -d "{\"device_id\":1,\"task_name\":\"晚上关灯\",\"execute_time\":\"2026-07-02 22:00:00\",\"action\":\"switch:off\",\"status\":\"enabled\"}"
```

停用定时任务：

```powershell
curl -X PUT "http://127.0.0.1:8000/api/schedules/1/status" -H "Content-Type: application/json" -d "{\"status\":\"disabled\"}"
```

## 10. 联动规则接口

查询联动规则：

```powershell
curl "http://127.0.0.1:8000/api/homes/1/linkages"
```

新增联动规则：

```powershell
curl -X POST "http://127.0.0.1:8000/api/homes/1/linkages" -H "Content-Type: application/json" -d "{\"rule_name\":\"烟雾报警联动\",\"trigger_condition\":{\"device_id\":4,\"metric\":\"smoke\",\"op\":\">\",\"value\":70},\"action_config\":{\"device_id\":1,\"action\":\"switch\",\"target_state\":\"on\"},\"enabled\":true}"
```

## 11. 报警处理接口

查询报警列表：

```powershell
curl "http://127.0.0.1:8000/api/homes/1/alarms"
```

查询报警详情：

```powershell
curl "http://127.0.0.1:8000/api/alarms/1"
```

确认报警：

```powershell
curl -X POST "http://127.0.0.1:8000/api/alarms/1/confirm" -H "Content-Type: application/json" -d "{\"process_desc\":\"已收到厨房烟雾报警\",\"process_result\":\"success\"}"
```

关闭报警：

```powershell
curl -X POST "http://127.0.0.1:8000/api/alarms/1/resolve" -H "Content-Type: application/json" -d "{\"process_desc\":\"现场已处理完成\",\"process_result\":\"success\"}"
```

## 12. 设备自检接口

发起设备自检：

```powershell
curl -X POST "http://127.0.0.1:8000/api/devices/1/self-check"
```

查询设备自检记录：

```powershell
curl "http://127.0.0.1:8000/api/devices/1/self-checks"
```

## 13. 设备模拟接口

模拟设备数据并触发报警：

```powershell
curl -X POST "http://127.0.0.1:8000/api/devices/4/simulate" -H "Content-Type: application/json" -d "{\"metric_name\":\"smoke\",\"metric_value\":90,\"device_status\":\"online\",\"trigger_alarm\":true,\"alarm_type\":\"smoke\",\"alarm_level\":\"serious\",\"simulation_type\":\"scenario\",\"scenario_name\":\"厨房烟雾升高演示\"}"
```

查询设备模拟记录：

```powershell
curl "http://127.0.0.1:8000/api/devices/4/simulations"
```

## 14. 前端配置

Vue 前端 `.env` 建议配置：

```text
VITE_API_BASE_URL=http://127.0.0.1:8000/api
```

请求头：

```text
Content-Type: application/json
```

设备、房间、情景、定时、联动、报警、自检等当前仍保留 Mock 演示接口，暂时不强制 `Authorization`；认证、家庭空间、成员、系统配置接口需要携带 `Authorization`。
