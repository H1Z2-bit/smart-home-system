/*
 Smart Home System MySQL Schema
 Updated according to backend database requirements and FastAPI mock schema.
 Date: 2026-07-04
*/

CREATE DATABASE IF NOT EXISTS `smart_home` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
USE `smart_home`;

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS `device_layout`;
DROP TABLE IF EXISTS `room_layout`;
DROP TABLE IF EXISTS `device_event`;
DROP TABLE IF EXISTS `account_operation_log`;
DROP TABLE IF EXISTS `device_simulation`;
DROP TABLE IF EXISTS `self_check_record`;
DROP TABLE IF EXISTS `operation_log`;
DROP TABLE IF EXISTS `alarm_process_log`;
DROP TABLE IF EXISTS `alarm_record`;
DROP TABLE IF EXISTS `sensor_data`;
DROP TABLE IF EXISTS `linkage_rule`;
DROP TABLE IF EXISTS `schedule_task`;
DROP TABLE IF EXISTS `scene_device_action`;
DROP TABLE IF EXISTS `scene_mode`;
DROP TABLE IF EXISTS `device`;
DROP TABLE IF EXISTS `room_area`;
DROP TABLE IF EXISTS `system_config`;
DROP TABLE IF EXISTS `home_member`;
DROP TABLE IF EXISTS `home_space`;
DROP TABLE IF EXISTS `sms_code`;
DROP TABLE IF EXISTS `user_account`;

CREATE TABLE `user_account` (
  `user_id` BIGINT NOT NULL AUTO_INCREMENT COMMENT 'User ID',
  `username` VARCHAR(50) NOT NULL COMMENT 'Username',
  `phone` VARCHAR(20) NULL DEFAULT NULL COMMENT 'Bound phone number',
  `phone_verified` TINYINT(1) NOT NULL DEFAULT 0 COMMENT 'Whether phone number is verified',
  `register_type` VARCHAR(30) NOT NULL DEFAULT 'password' COMMENT 'password/sms/import',
  `last_login_at` DATETIME NULL DEFAULT NULL COMMENT 'Last login time',
  `password_hash` VARCHAR(255) NOT NULL COMMENT 'Password hash',
  `role` VARCHAR(30) NOT NULL DEFAULT 'MEMBER' COMMENT 'Global role: OWNER/MEMBER/GUEST/MAINTAINER',
  `status` VARCHAR(20) NOT NULL DEFAULT 'ACTIVE' COMMENT 'ACTIVE/DISABLED',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Created time',
  `updated_at` DATETIME NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT 'Updated time',
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `uk_user_phone` (`phone`),
  KEY `idx_user_role` (`role`),
  KEY `idx_user_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='User account';

CREATE TABLE `sms_code` (
  `sms_id` BIGINT NOT NULL AUTO_INCREMENT COMMENT 'SMS code ID',
  `phone` VARCHAR(20) NOT NULL COMMENT 'Phone number',
  `scene` VARCHAR(20) NOT NULL COMMENT 'Code scene: login/bind',
  `code` VARCHAR(10) NOT NULL COMMENT 'SMS code',
  `expires_at` DATETIME NOT NULL COMMENT 'Expires at',
  `used` TINYINT(1) NOT NULL DEFAULT 0 COMMENT 'Whether code is used',
  `attempts` INT NOT NULL DEFAULT 0 COMMENT 'Verify attempts',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Created time',
  PRIMARY KEY (`sms_id`),
  KEY `idx_sms_phone_scene` (`phone`, `scene`),
  KEY `idx_sms_phone_scene_used_expires` (`phone`, `scene`, `used`, `expires_at`),
  KEY `idx_sms_expires_at` (`expires_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='SMS verification code';

CREATE TABLE `home_space` (
  `home_id` BIGINT NOT NULL AUTO_INCREMENT COMMENT 'Home ID',
  `name` VARCHAR(80) NOT NULL COMMENT 'Home name',
  `address` VARCHAR(255) NULL DEFAULT NULL COMMENT 'Home address',
  `owner_id` BIGINT NOT NULL COMMENT 'Owner user ID',
  `cover_url` VARCHAR(255) NULL DEFAULT NULL COMMENT 'Home cover image',
  `status` VARCHAR(20) NOT NULL DEFAULT 'ACTIVE' COMMENT 'ACTIVE/DISABLED',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Created time',
  `updated_at` DATETIME NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT 'Updated time',
  PRIMARY KEY (`home_id`),
  KEY `idx_home_owner` (`owner_id`),
  CONSTRAINT `fk_home_owner` FOREIGN KEY (`owner_id`) REFERENCES `user_account` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Home space';

CREATE TABLE `home_member` (
  `member_id` BIGINT NOT NULL AUTO_INCREMENT COMMENT 'Member ID',
  `home_id` BIGINT NOT NULL COMMENT 'Home ID',
  `user_id` BIGINT NULL DEFAULT NULL COMMENT 'User ID, nullable before invited user registers',
  `username` VARCHAR(50) NULL DEFAULT NULL COMMENT 'Cached username',
  `phone` VARCHAR(20) NOT NULL COMMENT 'Phone number',
  `role` VARCHAR(30) NOT NULL DEFAULT 'MEMBER' COMMENT 'OWNER/MEMBER/GUEST/MAINTAINER',
  `status` VARCHAR(30) NOT NULL DEFAULT 'INVITED' COMMENT 'INVITED/PENDING/ACTIVE/REJECTED/REMOVED/EXPIRED',
  `expire_at` DATETIME NULL DEFAULT NULL COMMENT 'Temporary member expiry',
  `invited_by` BIGINT NULL DEFAULT NULL COMMENT 'Inviter user ID',
  `apply_reason` VARCHAR(255) NULL DEFAULT NULL COMMENT 'Application reason',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Created time',
  `updated_at` DATETIME NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT 'Updated time',
  PRIMARY KEY (`member_id`),
  UNIQUE KEY `uk_member_home_phone` (`home_id`, `phone`),
  KEY `idx_member_home` (`home_id`),
  KEY `idx_member_user` (`user_id`),
  KEY `idx_member_phone` (`phone`),
  KEY `idx_member_status` (`status`),
  KEY `idx_member_home_status` (`home_id`, `status`),
  CONSTRAINT `fk_member_home` FOREIGN KEY (`home_id`) REFERENCES `home_space` (`home_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_member_user` FOREIGN KEY (`user_id`) REFERENCES `user_account` (`user_id`) ON DELETE SET NULL,
  CONSTRAINT `fk_member_inviter` FOREIGN KEY (`invited_by`) REFERENCES `user_account` (`user_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Home member';

CREATE TABLE `system_config` (
  `config_id` BIGINT NOT NULL AUTO_INCREMENT COMMENT 'Config ID',
  `home_id` BIGINT NOT NULL COMMENT 'Home ID',
  `alarm_smoke_threshold` DECIMAL(8,2) NOT NULL DEFAULT 80.00 COMMENT 'Smoke alarm threshold',
  `alarm_gas_threshold` DECIMAL(8,2) NOT NULL DEFAULT 70.00 COMMENT 'Gas alarm threshold',
  `temperature_high_threshold` DECIMAL(8,2) NOT NULL DEFAULT 35.00 COMMENT 'High temperature threshold',
  `auto_alarm_enabled` TINYINT(1) NOT NULL DEFAULT 1 COMMENT 'Whether auto alarm is enabled',
  `simulation_enabled` TINYINT(1) NOT NULL DEFAULT 1 COMMENT 'Whether simulation is enabled',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Created time',
  `updated_at` DATETIME NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT 'Updated time',
  PRIMARY KEY (`config_id`),
  UNIQUE KEY `uk_config_home` (`home_id`),
  CONSTRAINT `fk_config_home` FOREIGN KEY (`home_id`) REFERENCES `home_space` (`home_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='System config';

CREATE TABLE `room_area` (
  `room_id` BIGINT NOT NULL AUTO_INCREMENT COMMENT 'Room ID',
  `home_id` BIGINT NOT NULL COMMENT 'Home ID',
  `room_name` VARCHAR(100) NOT NULL COMMENT 'Room name',
  `room_type` VARCHAR(50) NULL DEFAULT NULL COMMENT 'Room type',
  `remark` VARCHAR(255) NULL DEFAULT NULL COMMENT 'Remark',
  `sort_no` INT NOT NULL DEFAULT 1 COMMENT 'Room display order',
  `status` VARCHAR(20) NOT NULL DEFAULT 'ACTIVE' COMMENT 'ACTIVE/DISABLED',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Created time',
  `updated_at` DATETIME NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT 'Updated time',
  PRIMARY KEY (`room_id`),
  UNIQUE KEY `uk_room_home_name` (`home_id`, `room_name`),
  KEY `idx_room_home` (`home_id`),
  CONSTRAINT `fk_room_home` FOREIGN KEY (`home_id`) REFERENCES `home_space` (`home_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Room area';

CREATE TABLE `room_layout` (
  `layout_id` BIGINT NOT NULL AUTO_INCREMENT COMMENT 'Layout ID',
  `room_id` BIGINT NOT NULL COMMENT 'Room ID',
  `position_x` DECIMAL(10,2) NOT NULL DEFAULT 0 COMMENT 'Room X position',
  `position_y` DECIMAL(10,2) NOT NULL DEFAULT 0 COMMENT 'Room Y position',
  `width` DECIMAL(10,2) NOT NULL DEFAULT 4 COMMENT 'Room width',
  `height` DECIMAL(10,2) NOT NULL DEFAULT 3 COMMENT 'Room height',
  `floor_no` INT NOT NULL DEFAULT 1 COMMENT 'Floor number',
  `wall_color` VARCHAR(30) NULL DEFAULT NULL COMMENT 'Wall color',
  `floor_color` VARCHAR(30) NULL DEFAULT NULL COMMENT 'Floor color',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Created time',
  `updated_at` DATETIME NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT 'Updated time',
  PRIMARY KEY (`layout_id`),
  UNIQUE KEY `uk_layout_room` (`room_id`),
  CONSTRAINT `fk_layout_room` FOREIGN KEY (`room_id`) REFERENCES `room_area` (`room_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Room layout for 2.5D or 3D visualization';

CREATE TABLE `device` (
  `device_id` BIGINT NOT NULL AUTO_INCREMENT COMMENT 'Device ID',
  `home_id` BIGINT NOT NULL COMMENT 'Home ID for efficient home-level device query',
  `room_id` BIGINT NOT NULL COMMENT 'Room ID',
  `device_name` VARCHAR(100) NOT NULL COMMENT 'Device name',
  `device_type` VARCHAR(50) NOT NULL COMMENT 'Device type: light/socket/temperature_sensor/etc.',
  `device_status` VARCHAR(30) NOT NULL DEFAULT 'offline' COMMENT 'online/offline/on/off/fault',
  `is_key_device` TINYINT(1) NOT NULL DEFAULT 0 COMMENT 'Whether it is a key security device',
  `manufacturer` VARCHAR(100) NULL DEFAULT NULL COMMENT 'Device manufacturer',
  `model` VARCHAR(100) NULL DEFAULT NULL COMMENT 'Device model',
  `serial_no` VARCHAR(100) NULL DEFAULT NULL COMMENT 'Device serial number',
  `last_online_at` DATETIME NULL DEFAULT NULL COMMENT 'Last online time',
  `last_offline_at` DATETIME NULL DEFAULT NULL COMMENT 'Last offline time',
  `remark` VARCHAR(255) NULL DEFAULT NULL COMMENT 'Device remark',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Created time',
  `updated_at` DATETIME NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT 'Updated time',
  PRIMARY KEY (`device_id`),
  UNIQUE KEY `uk_device_room_name` (`room_id`, `device_name`),
  UNIQUE KEY `uk_device_serial_no` (`serial_no`),
  KEY `idx_device_home` (`home_id`),
  KEY `idx_device_home_room` (`home_id`, `room_id`),
  KEY `idx_device_room_id` (`room_id`),
  KEY `idx_device_type` (`device_type`),
  KEY `idx_device_status` (`device_status`),
  CONSTRAINT `fk_device_home` FOREIGN KEY (`home_id`) REFERENCES `home_space` (`home_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_device_room` FOREIGN KEY (`room_id`) REFERENCES `room_area` (`room_id`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Device';

CREATE TABLE `device_layout` (
  `layout_id` BIGINT NOT NULL AUTO_INCREMENT COMMENT 'Layout ID',
  `device_id` BIGINT NOT NULL COMMENT 'Device ID',
  `position_x` DECIMAL(10,2) NOT NULL DEFAULT 0 COMMENT 'Device X position',
  `position_y` DECIMAL(10,2) NOT NULL DEFAULT 0 COMMENT 'Device Y position',
  `position_z` DECIMAL(10,2) NOT NULL DEFAULT 0 COMMENT 'Device Z position',
  `rotation_x` DECIMAL(10,2) NOT NULL DEFAULT 0 COMMENT 'Device X rotation',
  `rotation_y` DECIMAL(10,2) NOT NULL DEFAULT 0 COMMENT 'Device Y rotation',
  `rotation_z` DECIMAL(10,2) NOT NULL DEFAULT 0 COMMENT 'Device Z rotation',
  `icon_name` VARCHAR(80) NULL DEFAULT NULL COMMENT 'Icon name for mini program',
  `model_name` VARCHAR(100) NULL DEFAULT NULL COMMENT '3D model name',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Created time',
  `updated_at` DATETIME NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT 'Updated time',
  PRIMARY KEY (`layout_id`),
  UNIQUE KEY `uk_device_layout_device` (`device_id`),
  CONSTRAINT `fk_device_layout_device` FOREIGN KEY (`device_id`) REFERENCES `device` (`device_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Device layout for 2.5D or 3D visualization';

CREATE TABLE `device_event` (
  `event_id` BIGINT NOT NULL AUTO_INCREMENT COMMENT 'Event ID',
  `home_id` BIGINT NOT NULL COMMENT 'Home ID',
  `device_id` BIGINT NOT NULL COMMENT 'Device ID',
  `event_type` VARCHAR(50) NOT NULL COMMENT 'online/offline/status_change/control/fault/recover',
  `old_status` VARCHAR(30) NULL DEFAULT NULL COMMENT 'Old device status',
  `new_status` VARCHAR(30) NULL DEFAULT NULL COMMENT 'New device status',
  `event_desc` VARCHAR(500) NULL DEFAULT NULL COMMENT 'Event description',
  `operator_id` BIGINT NULL DEFAULT NULL COMMENT 'Operator user ID, null means system',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Created time',
  PRIMARY KEY (`event_id`),
  KEY `idx_device_event_home` (`home_id`),
  KEY `idx_device_event_device` (`device_id`),
  KEY `idx_device_event_type` (`event_type`),
  KEY `idx_device_event_time` (`created_at`),
  CONSTRAINT `fk_device_event_home` FOREIGN KEY (`home_id`) REFERENCES `home_space` (`home_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_device_event_device` FOREIGN KEY (`device_id`) REFERENCES `device` (`device_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_device_event_operator` FOREIGN KEY (`operator_id`) REFERENCES `user_account` (`user_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Device status and control event';

CREATE TABLE `scene_mode` (
  `scene_id` BIGINT NOT NULL AUTO_INCREMENT COMMENT 'Scene ID',
  `home_id` BIGINT NOT NULL COMMENT 'Home ID',
  `scene_name` VARCHAR(100) NOT NULL COMMENT 'Scene name',
  `scene_desc` VARCHAR(255) NULL DEFAULT NULL COMMENT 'Scene description',
  `icon_name` VARCHAR(80) NULL DEFAULT NULL COMMENT 'Scene icon name',
  `sort_no` INT NOT NULL DEFAULT 1 COMMENT 'Scene display order',
  `created_by` BIGINT NOT NULL COMMENT 'Creator user ID',
  `enabled` TINYINT(1) NOT NULL DEFAULT 1 COMMENT 'Whether enabled',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Created time',
  `updated_at` DATETIME NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT 'Updated time',
  PRIMARY KEY (`scene_id`),
  UNIQUE KEY `uk_scene_home_name` (`home_id`, `scene_name`),
  KEY `idx_scene_home` (`home_id`),
  CONSTRAINT `fk_scene_home` FOREIGN KEY (`home_id`) REFERENCES `home_space` (`home_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_scene_creator` FOREIGN KEY (`created_by`) REFERENCES `user_account` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Scene mode';

CREATE TABLE `scene_device_action` (
  `action_id` BIGINT NOT NULL AUTO_INCREMENT COMMENT 'Action ID',
  `scene_id` BIGINT NOT NULL COMMENT 'Scene ID',
  `device_id` BIGINT NOT NULL COMMENT 'Target device ID',
  `action` VARCHAR(50) NOT NULL DEFAULT 'switch' COMMENT 'Action type such as switch/set_temperature/set_brightness',
  `target_state` VARCHAR(50) NOT NULL COMMENT 'Target state such as on/off',
  `param_value` VARCHAR(100) NULL DEFAULT NULL COMMENT 'Optional parameter such as brightness',
  `sort_no` INT NOT NULL DEFAULT 1 COMMENT 'Execution order',
  PRIMARY KEY (`action_id`),
  KEY `idx_action_scene` (`scene_id`),
  KEY `idx_action_device` (`device_id`),
  CONSTRAINT `fk_scene_action_scene` FOREIGN KEY (`scene_id`) REFERENCES `scene_mode` (`scene_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_scene_action_device` FOREIGN KEY (`device_id`) REFERENCES `device` (`device_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Scene device action';

CREATE TABLE `schedule_task` (
  `task_id` BIGINT NOT NULL AUTO_INCREMENT COMMENT 'Task ID',
  `home_id` BIGINT NOT NULL COMMENT 'Home ID',
  `device_id` BIGINT NOT NULL COMMENT 'Target device ID',
  `task_name` VARCHAR(100) NOT NULL COMMENT 'Task name',
  `schedule_type` VARCHAR(20) NOT NULL DEFAULT 'once' COMMENT 'once/daily/weekly/cron',
  `execute_time` DATETIME NOT NULL COMMENT 'Execution time',
  `cron_expr` VARCHAR(100) NULL DEFAULT NULL COMMENT 'Optional cron expression',
  `action` VARCHAR(100) NOT NULL COMMENT 'Action such as on/off',
  `status` VARCHAR(20) NOT NULL DEFAULT 'enabled' COMMENT 'enabled/disabled/done/failed',
  `last_run_at` DATETIME NULL DEFAULT NULL COMMENT 'Last run time',
  `next_run_at` DATETIME NULL DEFAULT NULL COMMENT 'Next run time',
  `run_count` INT NOT NULL DEFAULT 0 COMMENT 'Run count',
  `fail_reason` VARCHAR(500) NULL DEFAULT NULL COMMENT 'Last fail reason',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Created time',
  `updated_at` DATETIME NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT 'Updated time',
  PRIMARY KEY (`task_id`),
  KEY `idx_task_home` (`home_id`),
  KEY `idx_task_device` (`device_id`),
  KEY `idx_task_time` (`execute_time`),
  KEY `idx_task_status` (`status`),
  KEY `idx_task_home_status_time` (`home_id`, `status`, `execute_time`),
  CONSTRAINT `fk_schedule_home` FOREIGN KEY (`home_id`) REFERENCES `home_space` (`home_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_schedule_device` FOREIGN KEY (`device_id`) REFERENCES `device` (`device_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Schedule task';

CREATE TABLE `linkage_rule` (
  `rule_id` BIGINT NOT NULL AUTO_INCREMENT COMMENT 'Rule ID',
  `home_id` BIGINT NOT NULL COMMENT 'Home ID',
  `rule_name` VARCHAR(100) NOT NULL COMMENT 'Rule name',
  `trigger_condition` JSON NOT NULL COMMENT 'Trigger condition JSON',
  `action_config` JSON NOT NULL COMMENT 'Action config JSON',
  `enabled` TINYINT(1) NOT NULL DEFAULT 1 COMMENT 'Whether enabled',
  `created_by` BIGINT NOT NULL COMMENT 'Creator user ID',
  `last_triggered_at` DATETIME NULL DEFAULT NULL COMMENT 'Last triggered time',
  `trigger_count` INT NOT NULL DEFAULT 0 COMMENT 'Triggered count',
  `rule_desc` VARCHAR(255) NULL DEFAULT NULL COMMENT 'Rule description',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Created time',
  `updated_at` DATETIME NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT 'Updated time',
  PRIMARY KEY (`rule_id`),
  UNIQUE KEY `uk_linkage_home_name` (`home_id`, `rule_name`),
  KEY `idx_linkage_home` (`home_id`),
  KEY `idx_linkage_enabled` (`enabled`),
  CONSTRAINT `fk_linkage_home` FOREIGN KEY (`home_id`) REFERENCES `home_space` (`home_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_linkage_creator` FOREIGN KEY (`created_by`) REFERENCES `user_account` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Linkage rule';

CREATE TABLE `sensor_data` (
  `data_id` BIGINT NOT NULL AUTO_INCREMENT COMMENT 'Data ID',
  `home_id` BIGINT NULL DEFAULT NULL COMMENT 'Home ID for faster query',
  `room_id` BIGINT NULL DEFAULT NULL COMMENT 'Room ID for faster query',
  `device_id` BIGINT NOT NULL COMMENT 'Device ID',
  `data_type` VARCHAR(50) NOT NULL COMMENT 'temperature/smoke/gas/door/power',
  `data_value` DECIMAL(10,2) NOT NULL COMMENT 'Collected value',
  `unit` VARCHAR(20) NULL DEFAULT NULL COMMENT 'Unit',
  `collect_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Collect time',
  PRIMARY KEY (`data_id`),
  KEY `idx_sensor_device_time` (`device_id`, `collect_time`),
  KEY `idx_sensor_type_time` (`data_type`, `collect_time`),
  KEY `idx_sensor_home_time` (`home_id`, `collect_time`),
  KEY `idx_sensor_room_time` (`room_id`, `collect_time`),
  CONSTRAINT `fk_sensor_home` FOREIGN KEY (`home_id`) REFERENCES `home_space` (`home_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_sensor_room` FOREIGN KEY (`room_id`) REFERENCES `room_area` (`room_id`) ON DELETE SET NULL,
  CONSTRAINT `fk_sensor_device` FOREIGN KEY (`device_id`) REFERENCES `device` (`device_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Real sensor data';

CREATE TABLE `alarm_record` (
  `alarm_id` BIGINT NOT NULL AUTO_INCREMENT COMMENT 'Alarm ID',
  `home_id` BIGINT NOT NULL COMMENT 'Home ID for efficient home-level alarm query',
  `device_id` BIGINT NOT NULL COMMENT 'Trigger device ID',
  `alarm_type` VARCHAR(50) NOT NULL COMMENT 'temperature/smoke/gas/intrusion/device_fault/device_offline',
  `alarm_level` VARCHAR(20) NOT NULL COMMENT 'notice/warning/serious',
  `trigger_value` VARCHAR(100) NOT NULL COMMENT 'Trigger value',
  `alarm_status` VARCHAR(20) NOT NULL DEFAULT 'new' COMMENT 'new/confirmed/processing/recheck/closed/false_alarm',
  `alarm_desc` VARCHAR(500) NULL DEFAULT NULL COMMENT 'Alarm description',
  `confirmed_by` BIGINT NULL DEFAULT NULL COMMENT 'Confirm user ID',
  `confirmed_at` DATETIME NULL DEFAULT NULL COMMENT 'Confirm time',
  `processed_by` BIGINT NULL DEFAULT NULL COMMENT 'Process user ID',
  `processed_at` DATETIME NULL DEFAULT NULL COMMENT 'Process time',
  `trigger_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Trigger time',
  `closed_time` DATETIME NULL DEFAULT NULL COMMENT 'Closed time',
  PRIMARY KEY (`alarm_id`),
  KEY `idx_alarm_home` (`home_id`),
  KEY `idx_alarm_device` (`device_id`),
  KEY `idx_alarm_status` (`alarm_status`),
  KEY `idx_alarm_time` (`trigger_time`),
  KEY `idx_alarm_home_status_time` (`home_id`, `alarm_status`, `trigger_time`),
  KEY `idx_alarm_confirmed_by` (`confirmed_by`),
  KEY `idx_alarm_processed_by` (`processed_by`),
  CONSTRAINT `fk_alarm_home` FOREIGN KEY (`home_id`) REFERENCES `home_space` (`home_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_alarm_device` FOREIGN KEY (`device_id`) REFERENCES `device` (`device_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_alarm_confirmed_by` FOREIGN KEY (`confirmed_by`) REFERENCES `user_account` (`user_id`) ON DELETE SET NULL,
  CONSTRAINT `fk_alarm_processed_by` FOREIGN KEY (`processed_by`) REFERENCES `user_account` (`user_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Alarm record';

CREATE TABLE `alarm_process_log` (
  `log_id` BIGINT NOT NULL AUTO_INCREMENT COMMENT 'Log ID',
  `alarm_id` BIGINT NOT NULL COMMENT 'Alarm ID',
  `handler_id` BIGINT NULL DEFAULT NULL COMMENT 'Handler user ID, nullable for system actions',
  `action_type` VARCHAR(50) NOT NULL COMMENT 'notify/linkage/confirm/process/recheck/close/mark_false_alarm',
  `process_desc` VARCHAR(500) NULL DEFAULT NULL COMMENT 'Process description',
  `process_result` VARCHAR(100) NULL DEFAULT NULL COMMENT 'Process result',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Created time',
  PRIMARY KEY (`log_id`),
  KEY `idx_process_alarm` (`alarm_id`),
  KEY `idx_process_handler` (`handler_id`),
  CONSTRAINT `fk_alarm_process_alarm` FOREIGN KEY (`alarm_id`) REFERENCES `alarm_record` (`alarm_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_alarm_process_handler` FOREIGN KEY (`handler_id`) REFERENCES `user_account` (`user_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Alarm process log';

CREATE TABLE `operation_log` (
  `log_id` BIGINT NOT NULL AUTO_INCREMENT COMMENT 'Log ID',
  `home_id` BIGINT NULL DEFAULT NULL COMMENT 'Home ID',
  `operator_id` BIGINT NOT NULL COMMENT 'Operator user ID',
  `operation_type` VARCHAR(50) NOT NULL COMMENT 'Operation type such as room_create/device_control',
  `operation_object` VARCHAR(100) NOT NULL COMMENT 'Operation object such as device:1',
  `operation_result` VARCHAR(50) NOT NULL COMMENT 'success/fail',
  `operation_desc` VARCHAR(500) NULL DEFAULT NULL COMMENT 'Operation description',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Created time',
  PRIMARY KEY (`log_id`),
  KEY `idx_log_home` (`home_id`),
  KEY `idx_log_user` (`operator_id`),
  KEY `idx_log_type` (`operation_type`),
  KEY `idx_log_time` (`created_at`),
  CONSTRAINT `fk_operation_home` FOREIGN KEY (`home_id`) REFERENCES `home_space` (`home_id`) ON DELETE SET NULL,
  CONSTRAINT `fk_operation_user` FOREIGN KEY (`operator_id`) REFERENCES `user_account` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Business operation log';

CREATE TABLE `account_operation_log` (
  `log_id` BIGINT NOT NULL AUTO_INCREMENT COMMENT 'Log ID',
  `user_id` BIGINT NULL DEFAULT NULL COMMENT 'User ID, nullable before login',
  `home_id` BIGINT NULL DEFAULT NULL COMMENT 'Related home ID',
  `action` VARCHAR(80) NOT NULL COMMENT 'Action such as login/register/bind_phone/change_password',
  `description` VARCHAR(500) NOT NULL COMMENT 'Operation description',
  `target_type` VARCHAR(80) NULL DEFAULT NULL COMMENT 'Target type such as user/home/member',
  `target_id` BIGINT NULL DEFAULT NULL COMMENT 'Target ID',
  `ip_address` VARCHAR(64) NULL DEFAULT NULL COMMENT 'Client IP address',
  `user_agent` VARCHAR(255) NULL DEFAULT NULL COMMENT 'Client user agent',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Created time',
  PRIMARY KEY (`log_id`),
  KEY `idx_account_log_user` (`user_id`),
  KEY `idx_account_log_home` (`home_id`),
  KEY `idx_account_log_action` (`action`),
  KEY `idx_account_log_time` (`created_at`),
  CONSTRAINT `fk_account_log_user` FOREIGN KEY (`user_id`) REFERENCES `user_account` (`user_id`) ON DELETE SET NULL,
  CONSTRAINT `fk_account_log_home` FOREIGN KEY (`home_id`) REFERENCES `home_space` (`home_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Account and security operation log';

CREATE TABLE `self_check_record` (
  `check_id` BIGINT NOT NULL AUTO_INCREMENT COMMENT 'Check ID',
  `device_id` BIGINT NOT NULL COMMENT 'Device ID',
  `check_type` VARCHAR(30) NOT NULL DEFAULT 'manual' COMMENT 'manual/auto',
  `check_result` VARCHAR(30) NOT NULL COMMENT 'normal/fault/offline',
  `error_info` VARCHAR(500) NULL DEFAULT NULL COMMENT 'Error info',
  `check_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Check time, can be mapped to created_at by repository',
  `operator_id` BIGINT NULL DEFAULT NULL COMMENT 'Operator user ID, nullable for auto checks',
  `check_items` JSON NULL COMMENT 'Self check items JSON',
  `duration_ms` INT NULL DEFAULT NULL COMMENT 'Check duration milliseconds',
  PRIMARY KEY (`check_id`),
  KEY `idx_check_device` (`device_id`),
  KEY `idx_check_time` (`check_time`),
  CONSTRAINT `fk_self_check_device` FOREIGN KEY (`device_id`) REFERENCES `device` (`device_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_self_check_operator` FOREIGN KEY (`operator_id`) REFERENCES `user_account` (`user_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Device self check record';

CREATE TABLE `device_simulation` (
  `simulation_id` BIGINT NOT NULL AUTO_INCREMENT COMMENT 'Simulation ID',
  `home_id` BIGINT NOT NULL COMMENT 'Home ID, matches backend response field',
  `device_id` BIGINT NOT NULL COMMENT 'Device ID',
  `metric_name` VARCHAR(100) NOT NULL COMMENT 'Metric name such as temperature/smoke/gas',
  `metric_value` VARCHAR(100) NOT NULL COMMENT 'Metric value',
  `device_status` VARCHAR(30) NULL DEFAULT NULL COMMENT 'Optional device status',
  `trigger_alarm` TINYINT(1) NOT NULL DEFAULT 0 COMMENT 'Whether alarm is triggered',
  `alarm_type` VARCHAR(50) NULL DEFAULT NULL COMMENT 'Alarm type',
  `alarm_level` VARCHAR(30) NOT NULL DEFAULT 'warning' COMMENT 'Alarm level',
  `alarm_id` BIGINT NULL DEFAULT NULL COMMENT 'Related alarm ID if triggered',
  `simulation_type` VARCHAR(50) NOT NULL DEFAULT 'manual' COMMENT 'manual/auto/scenario',
  `scenario_name` VARCHAR(100) NULL DEFAULT NULL COMMENT 'Simulation scenario name',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Created time',
  PRIMARY KEY (`simulation_id`),
  KEY `idx_simulation_home` (`home_id`),
  KEY `idx_simulation_device` (`device_id`),
  KEY `idx_simulation_alarm` (`alarm_id`),
  KEY `idx_simulation_time` (`created_at`),
  CONSTRAINT `fk_simulation_home` FOREIGN KEY (`home_id`) REFERENCES `home_space` (`home_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_simulation_device` FOREIGN KEY (`device_id`) REFERENCES `device` (`device_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_simulation_alarm` FOREIGN KEY (`alarm_id`) REFERENCES `alarm_record` (`alarm_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Device simulation record';

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
