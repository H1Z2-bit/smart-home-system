CREATE DATABASE IF NOT EXISTS smart_home
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE smart_home;

CREATE TABLE IF NOT EXISTS room_area (
  room_id BIGINT PRIMARY KEY AUTO_INCREMENT,
  home_id BIGINT NOT NULL,
  room_name VARCHAR(100) NOT NULL,
  room_type VARCHAR(50) NULL,
  remark VARCHAR(255) NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uk_room_home_name (home_id, room_name),
  KEY idx_room_home_id (home_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS device (
  device_id BIGINT PRIMARY KEY AUTO_INCREMENT,
  room_id BIGINT NOT NULL,
  device_name VARCHAR(100) NOT NULL,
  device_type VARCHAR(50) NOT NULL,
  device_status VARCHAR(30) NOT NULL DEFAULT 'offline',
  is_key_device TINYINT(1) NOT NULL DEFAULT 0,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  KEY idx_device_room_id (room_id),
  UNIQUE KEY uk_device_room_name (room_id, device_name),
  KEY idx_device_type (device_type),
  KEY idx_device_status (device_status),
  CONSTRAINT fk_device_room
    FOREIGN KEY (room_id) REFERENCES room_area(room_id)
    ON UPDATE CASCADE
    ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
