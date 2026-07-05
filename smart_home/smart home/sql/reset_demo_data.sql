/*
 Reset Smart Home demo data
 Generated from smart_home.sql.
*/
USE `smart_home`;

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

DELETE FROM `device_layout`;
DELETE FROM `room_layout`;
DELETE FROM `device_event`;
DELETE FROM `account_operation_log`;
DELETE FROM `device_simulation`;
DELETE FROM `self_check_record`;
DELETE FROM `operation_log`;
DELETE FROM `alarm_process_log`;
DELETE FROM `alarm_record`;
DELETE FROM `sensor_data`;
DELETE FROM `linkage_rule`;
DELETE FROM `schedule_task`;
DELETE FROM `scene_device_action`;
DELETE FROM `scene_mode`;
DELETE FROM `device`;
DELETE FROM `room_area`;
DELETE FROM `system_config`;
DELETE FROM `home_member`;
DELETE FROM `home_space`;
DELETE FROM `sms_code`;
DELETE FROM `user_account`;

ALTER TABLE `user_account` AUTO_INCREMENT = 1;
ALTER TABLE `sms_code` AUTO_INCREMENT = 1;
ALTER TABLE `home_space` AUTO_INCREMENT = 1;
ALTER TABLE `home_member` AUTO_INCREMENT = 1;
ALTER TABLE `system_config` AUTO_INCREMENT = 1;
ALTER TABLE `room_area` AUTO_INCREMENT = 1;
ALTER TABLE `device` AUTO_INCREMENT = 1;
ALTER TABLE `scene_mode` AUTO_INCREMENT = 1;
ALTER TABLE `scene_device_action` AUTO_INCREMENT = 1;
ALTER TABLE `schedule_task` AUTO_INCREMENT = 1;
ALTER TABLE `linkage_rule` AUTO_INCREMENT = 1;
ALTER TABLE `sensor_data` AUTO_INCREMENT = 1;
ALTER TABLE `alarm_record` AUTO_INCREMENT = 1;
ALTER TABLE `alarm_process_log` AUTO_INCREMENT = 1;
ALTER TABLE `operation_log` AUTO_INCREMENT = 1;
ALTER TABLE `self_check_record` AUTO_INCREMENT = 1;
ALTER TABLE `device_simulation` AUTO_INCREMENT = 1;
ALTER TABLE `account_operation_log` AUTO_INCREMENT = 1;
ALTER TABLE `device_event` AUTO_INCREMENT = 1;
ALTER TABLE `room_layout` AUTO_INCREMENT = 1;
ALTER TABLE `device_layout` AUTO_INCREMENT = 1;

INSERT INTO `user_account` (`user_id`, `username`, `phone`, `phone_verified`, `register_type`, `last_login_at`, `password_hash`, `role`, `status`, `created_at`, `updated_at`) VALUES
(1, 'han', '13800000000', 1, 'import', NULL, '$2b$12$zrDPbvIp.1FoZkzinQvMuuXZgLsvPR9dEb37i2B8Vm/27V7h1A6zm', 'OWNER', 'ACTIVE', '2026-07-03 22:45:04', NULL),
(2, 'member', '13900000000', 1, 'import', NULL, '$2b$12$zrDPbvIp.1FoZkzinQvMuuXZgLsvPR9dEb37i2B8Vm/27V7h1A6zm', 'MEMBER', 'ACTIVE', '2026-07-03 22:45:04', NULL),
(3, 'guest', '13700000000', 1, 'import', NULL, '$2b$12$zrDPbvIp.1FoZkzinQvMuuXZgLsvPR9dEb37i2B8Vm/27V7h1A6zm', 'GUEST', 'ACTIVE', '2026-07-03 22:45:04', NULL),
(4, 'maintainer', '13600000000', 1, 'import', NULL, '$2b$12$zrDPbvIp.1FoZkzinQvMuuXZgLsvPR9dEb37i2B8Vm/27V7h1A6zm', 'MAINTAINER', 'ACTIVE', '2026-07-03 22:45:04', NULL);

INSERT INTO `home_space` (`home_id`, `name`, `address`, `owner_id`, `cover_url`, `status`, `created_at`, `updated_at`) VALUES
(1, '演示家庭', '北京市朝阳区', 1, NULL, 'ACTIVE', '2026-07-03 22:45:04', NULL);

INSERT INTO `home_member` (`member_id`, `home_id`, `user_id`, `username`, `phone`, `role`, `status`, `expire_at`, `invited_by`, `apply_reason`, `created_at`, `updated_at`) VALUES
(1, 1, 1, 'han', '13800000000', 'OWNER', 'ACTIVE', NULL, NULL, NULL, '2026-07-04 15:39:12', NULL),
(2, 1, 2, 'member', '13900000000', 'MEMBER', 'ACTIVE', NULL, 1, NULL, '2026-07-04 15:39:12', NULL),
(3, 1, 3, 'guest', '13700000000', 'GUEST', 'ACTIVE', NULL, 1, NULL, '2026-07-04 15:39:12', NULL);

INSERT INTO `system_config` (`config_id`, `home_id`, `alarm_smoke_threshold`, `alarm_gas_threshold`, `temperature_high_threshold`, `auto_alarm_enabled`, `simulation_enabled`, `created_at`, `updated_at`) VALUES
(1, 1, 80.00, 70.00, 35.00, 1, 1, '2026-07-03 22:45:04', NULL);

INSERT INTO `room_area` (`room_id`, `home_id`, `room_name`, `room_type`, `remark`, `sort_no`, `status`, `created_at`, `updated_at`) VALUES
(1, 1, '客厅', 'living_room', '用于智能灯、插座、门磁演示', 1, 'ACTIVE', '2026-07-03 22:47:33', NULL),
(2, 1, '主卧', 'bedroom', '用于温度传感器演示', 2, 'ACTIVE', '2026-07-03 22:47:33', NULL),
(3, 1, '厨房', 'kitchen', '用于烟雾和燃气报警演示', 3, 'ACTIVE', '2026-07-03 22:47:33', NULL);

INSERT INTO `device` (`device_id`, `home_id`, `room_id`, `device_name`, `device_type`, `device_status`, `is_key_device`, `manufacturer`, `model`, `serial_no`, `last_online_at`, `last_offline_at`, `remark`, `created_at`, `updated_at`) VALUES
(1, 1, 1, '客厅灯', 'light', 'off', 0, 'DemoSmart', 'LIGHT-A1', 'SH-DEV-0001', NULL, NULL, 'Living room light demo device', '2026-07-03 22:47:33', NULL),
(2, 1, 1, '客厅插座', 'socket', 'off', 0, 'DemoSmart', 'SOCKET-A1', 'SH-DEV-0002', NULL, NULL, 'Living room socket demo device', '2026-07-03 22:47:33', NULL),
(3, 1, 2, '主卧温度传感器', 'temperature_sensor', 'online', 0, 'DemoSmart', 'TEMP-S1', 'SH-DEV-0003', '2026-07-04 15:39:12', NULL, 'Bedroom temperature sensor', '2026-07-03 22:47:33', NULL),
(4, 1, 3, '厨房烟雾传感器', 'smoke_sensor', 'online', 1, 'DemoSmart', 'SMOKE-S1', 'SH-DEV-0004', '2026-07-04 15:39:12', NULL, 'Kitchen smoke alarm sensor', '2026-07-03 22:47:33', NULL),
(5, 1, 3, '厨房燃气传感器', 'gas_sensor', 'online', 1, 'DemoSmart', 'GAS-S1', 'SH-DEV-0005', '2026-07-04 15:39:12', NULL, 'Kitchen gas alarm sensor', '2026-07-03 22:47:33', NULL),
(6, 1, 1, '入户门磁', 'door_sensor', 'online', 1, 'DemoSmart', 'DOOR-S1', 'SH-DEV-0006', '2026-07-04 15:39:12', NULL, 'Door sensor demo device', '2026-07-03 22:47:33', NULL);

INSERT INTO `room_layout` (`layout_id`, `room_id`, `position_x`, `position_y`, `width`, `height`, `floor_no`, `wall_color`, `floor_color`, `created_at`, `updated_at`) VALUES
(1, 1, 0.00, 0.00, 5.00, 4.00, 1, '#dbeafe', '#f8fafc', '2026-07-04 15:44:10', NULL),
(2, 2, 0.00, 4.00, 4.00, 3.50, 1, '#ede9fe', '#faf5ff', '2026-07-04 15:44:10', NULL),
(3, 3, 5.00, 0.00, 3.50, 3.50, 1, '#ffedd5', '#fff7ed', '2026-07-04 15:44:10', NULL);

INSERT INTO `device_layout` (`layout_id`, `device_id`, `position_x`, `position_y`, `position_z`, `rotation_x`, `rotation_y`, `rotation_z`, `icon_name`, `model_name`, `created_at`, `updated_at`) VALUES
(1, 1, 1.20, 1.00, 2.40, 0, 0, 0, 'light', 'ceiling-light', '2026-07-04 15:44:10', NULL),
(2, 2, 2.50, 0.40, 0.20, 0, 0, 0, 'socket', 'wall-socket', '2026-07-04 15:44:10', NULL),
(3, 3, 1.20, 0.80, 1.20, 0, 0, 0, 'thermometer', 'temperature-sensor', '2026-07-04 15:44:10', NULL),
(4, 4, 1.00, 0.80, 1.80, 0, 0, 0, 'smoke', 'smoke-sensor', '2026-07-04 15:44:10', NULL),
(5, 5, 2.00, 0.80, 1.20, 0, 0, 0, 'gas', 'gas-sensor', '2026-07-04 15:44:10', NULL),
(6, 6, 0.20, 0.80, 0.20, 0, 0, 0, 'door', 'door-sensor', '2026-07-04 15:44:10', NULL);

INSERT INTO `scene_mode` (`scene_id`, `home_id`, `scene_name`, `scene_desc`, `icon_name`, `sort_no`, `created_by`, `enabled`, `created_at`, `updated_at`) VALUES
(1, 1, '离家模式', 'Turn off major powered devices and keep safety sensors online', 'scene-leave', 1, 1, 1, '2026-07-04 15:44:10', NULL);

INSERT INTO `scene_device_action` (`action_id`, `scene_id`, `device_id`, `action`, `target_state`, `param_value`, `sort_no`) VALUES
(1, 1, 1, 'switch', 'off', NULL, 1),
(2, 1, 2, 'switch', 'off', NULL, 2);

INSERT INTO `schedule_task` (`task_id`, `home_id`, `device_id`, `task_name`, `schedule_type`, `execute_time`, `cron_expr`, `action`, `status`, `last_run_at`, `next_run_at`, `run_count`, `fail_reason`, `created_at`, `updated_at`) VALUES
(1, 1, 1, '清晨开灯', 'daily', '2026-07-05 07:30:00', NULL, 'on', 'enabled', NULL, '2026-07-05 07:30:00', 0, NULL, '2026-07-04 15:44:10', NULL);

INSERT INTO `linkage_rule` (`rule_id`, `home_id`, `rule_name`, `trigger_condition`, `action_config`, `enabled`, `created_by`, `last_triggered_at`, `trigger_count`, `rule_desc`, `created_at`, `updated_at`) VALUES
(1, 1, '烟雾报警联动', JSON_OBJECT('device_id', 4, 'data_type', 'smoke', 'operator', '>', 'threshold', 50), JSON_OBJECT('device_id', 1, 'target_state', 'on'), 1, 1, NULL, 0, '厨房烟雾浓度超阈值时自动打开客厅灯', '2026-07-04 15:44:10', NULL);

INSERT INTO `sensor_data` (`data_id`, `home_id`, `room_id`, `device_id`, `data_type`, `data_value`, `unit`, `collect_time`) VALUES
(1, 1, 2, 3, 'temperature', 26.00, 'C', '2026-07-04 15:39:12'),
(2, 1, 3, 4, 'smoke', 10.00, '%', '2026-07-04 15:39:12'),
(3, 1, 3, 5, 'gas', 100.00, 'ppm', '2026-07-04 15:39:12');

INSERT INTO `alarm_record` (`alarm_id`, `home_id`, `device_id`, `alarm_type`, `alarm_level`, `trigger_value`, `alarm_status`, `alarm_desc`, `confirmed_by`, `confirmed_at`, `processed_by`, `processed_at`, `trigger_time`, `closed_time`) VALUES
(1, 1, 4, 'smoke', 'serious', '85.00', 'new', '厨房烟雾浓度超过阈值', NULL, NULL, NULL, NULL, '2026-07-04 15:42:35', NULL);

INSERT INTO `alarm_process_log` (`log_id`, `alarm_id`, `handler_id`, `action_type`, `process_desc`, `process_result`, `created_at`) VALUES
(1, 1, NULL, 'notify', '系统检测到烟雾浓度超过阈值，已自动生成报警', 'success', '2026-07-04 15:42:35');

INSERT INTO `operation_log` (`log_id`, `home_id`, `operator_id`, `operation_type`, `operation_object`, `operation_result`, `operation_desc`, `created_at`) VALUES
(1, 1, 1, 'device_control', 'device:1', 'success', '控制设备 客厅灯，目标状态：on', '2026-07-04 15:42:35');

INSERT INTO `account_operation_log` (`log_id`, `user_id`, `home_id`, `action`, `description`, `target_type`, `target_id`, `ip_address`, `user_agent`, `created_at`) VALUES
(1, 1, 1, 'LOGIN', 'user login', 'USER', 1, NULL, NULL, '2026-07-04 15:39:12');

INSERT INTO `device_event` (`event_id`, `home_id`, `device_id`, `event_type`, `old_status`, `new_status`, `event_desc`, `operator_id`, `created_at`) VALUES
(1, 1, 1, 'control', 'off', 'on', '控制设备 客厅灯，目标状态：on', 1, '2026-07-04 15:42:35');

INSERT INTO `self_check_record` (`check_id`, `device_id`, `check_type`, `check_result`, `error_info`, `check_time`, `operator_id`, `check_items`, `duration_ms`) VALUES
(1, 4, 'manual', 'normal', NULL, '2026-07-04 15:44:10', 1, JSON_ARRAY('sensor', 'network', 'power'), 1200);

INSERT INTO `device_simulation` (`simulation_id`, `home_id`, `device_id`, `metric_name`, `metric_value`, `device_status`, `trigger_alarm`, `alarm_type`, `alarm_level`, `alarm_id`, `simulation_type`, `scenario_name`, `created_at`) VALUES
(1, 1, 4, 'smoke', '85', 'online', 1, 'smoke', 'serious', 1, 'manual', '厨房烟雾浓度升高', '2026-07-04 15:42:35');

SET FOREIGN_KEY_CHECKS = 1;
