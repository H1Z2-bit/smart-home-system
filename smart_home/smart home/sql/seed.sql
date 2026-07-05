USE smart_home;

INSERT INTO room_area (home_id, room_name, room_type, remark)
VALUES
  (1, '客厅', 'living_room', '用于智能灯、插座、门磁演示'),
  (1, '主卧', 'bedroom', '用于温度传感器演示'),
  (1, '厨房', 'kitchen', '用于烟雾和燃气报警演示')
ON DUPLICATE KEY UPDATE
  room_type = VALUES(room_type),
  remark = VALUES(remark);

INSERT INTO device (room_id, device_name, device_type, device_status, is_key_device)
SELECT room_id, '客厅灯', 'light', 'off', 0
FROM room_area
WHERE home_id = 1 AND room_name = '客厅'
ON DUPLICATE KEY UPDATE device_name = device_name;

INSERT INTO device (room_id, device_name, device_type, device_status, is_key_device)
SELECT room_id, '客厅插座', 'socket', 'off', 0
FROM room_area
WHERE home_id = 1 AND room_name = '客厅'
ON DUPLICATE KEY UPDATE device_name = device_name;

INSERT INTO device (room_id, device_name, device_type, device_status, is_key_device)
SELECT room_id, '主卧温度传感器', 'temperature_sensor', 'online', 0
FROM room_area
WHERE home_id = 1 AND room_name = '主卧'
ON DUPLICATE KEY UPDATE device_name = device_name;

INSERT INTO device (room_id, device_name, device_type, device_status, is_key_device)
SELECT room_id, '厨房烟雾传感器', 'smoke_sensor', 'online', 1
FROM room_area
WHERE home_id = 1 AND room_name = '厨房'
ON DUPLICATE KEY UPDATE device_name = device_name;

INSERT INTO device (room_id, device_name, device_type, device_status, is_key_device)
SELECT room_id, '厨房燃气传感器', 'gas_sensor', 'online', 1
FROM room_area
WHERE home_id = 1 AND room_name = '厨房'
ON DUPLICATE KEY UPDATE device_name = device_name;

INSERT INTO device (room_id, device_name, device_type, device_status, is_key_device)
SELECT room_id, '入户门磁', 'door_sensor', 'online', 1
FROM room_area
WHERE home_id = 1 AND room_name = '客厅'
ON DUPLICATE KEY UPDATE device_name = device_name;
