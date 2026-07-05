<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'

type DeviceType = 'LIGHT' | 'PLUG' | 'CAMERA' | 'TEMP_SENSOR' | 'SMOKE_SENSOR' | 'GAS_SENSOR' | 'DOOR_SENSOR'
type DevicePower = 'ON' | 'OFF' | 'OPEN' | 'CLOSED' | 'NORMAL'
type AlarmStatus = 'NORMAL' | 'ALARM'

interface DeviceState {
  id: number
  backendId: number
  name: string
  room: string
  type: DeviceType
  status: 'ONLINE' | 'OFFLINE'
  power: DevicePower
  alarm: AlarmStatus
  value: string
  metric: string
  position: [number, number, number]
  endpoint: string
}

interface RoomArea {
  name: string
  x: number
  z: number
  width: number
  depth: number
  color: number
  border: number
}

interface DeviceRuntime {
  group: THREE.Group
  indicator: THREE.Mesh
  label: THREE.Sprite
  ring?: THREE.Mesh
}

const sceneHost = ref<HTMLDivElement | null>(null)
const selectedDevice = ref<DeviceState | null>(null)
const selectedRoom = ref('全部')
const currentTime = ref('')
const viewMode = ref<'overview' | 'alarm' | 'device'>('overview')

let renderer: THREE.WebGLRenderer | null = null
let scene: THREE.Scene | null = null
let camera: THREE.PerspectiveCamera | null = null
let controls: OrbitControls | null = null
let frameId = 0
let resizeObserver: ResizeObserver | null = null
let elapsed = 0
let clockTimer = 0

const raycaster = new THREE.Raycaster()
const pointer = new THREE.Vector2()
const deviceRuntime = new Map<number, DeviceRuntime>()
const alarmObjects: THREE.Object3D[] = []
const alarmMaterials: THREE.MeshStandardMaterial[] = []
const roomAlarmOverlays: THREE.Mesh[] = []
const labelSprites: THREE.Sprite[] = []

const rooms: RoomArea[] = [
  { name: '客厅', x: -2.55, z: -1.45, width: 3.9, depth: 2.85, color: 0xe3edf1, border: 0x8aa4b4 },
  { name: '厨房', x: 1.85, z: -1.45, width: 2.9, depth: 2.85, color: 0xf2e5d5, border: 0xb58b5f },
  { name: '卧室', x: -2.55, z: 1.75, width: 3.9, depth: 2.75, color: 0xe9e5f2, border: 0x978bb5 },
  { name: '玄关', x: 1.85, z: 1.75, width: 2.9, depth: 2.75, color: 0xe2eadc, border: 0x86a777 },
]

const devices: DeviceState[] = [
  { id: 1, backendId: 1, name: '客厅智能灯', room: '客厅', type: 'LIGHT', status: 'ONLINE', power: 'ON', alarm: 'NORMAL', value: '亮度 82%', metric: 'light=82', position: [-3.55, 1.08, -2.1], endpoint: 'POST /api/devices/1/control' },
  { id: 2, backendId: 2, name: '客厅智能插座', room: '客厅', type: 'PLUG', status: 'ONLINE', power: 'ON', alarm: 'NORMAL', value: '功率 430W', metric: 'power=430W', position: [-1.35, 0.38, -0.62], endpoint: 'POST /api/devices/2/control' },
  { id: 3, backendId: 3, name: '客厅摄像头', room: '客厅', type: 'CAMERA', status: 'ONLINE', power: 'ON', alarm: 'NORMAL', value: '在线', metric: 'video=online', position: [-4.1, 1.18, -2.78], endpoint: 'GET /api/homes/1/devices' },
  { id: 4, backendId: 4, name: '卧室智能灯', room: '卧室', type: 'LIGHT', status: 'ONLINE', power: 'OFF', alarm: 'NORMAL', value: '关闭', metric: 'light=off', position: [-3.3, 1.02, 1.2], endpoint: 'POST /api/devices/4/control' },
  { id: 5, backendId: 5, name: '卧室温度传感器', room: '卧室', type: 'TEMP_SENSOR', status: 'ONLINE', power: 'NORMAL', alarm: 'NORMAL', value: '26.4°C', metric: 'temperature=26.4', position: [-1.05, 0.55, 2.25], endpoint: 'GET /api/devices/5/simulations' },
  { id: 6, backendId: 6, name: '厨房烟雾传感器', room: '厨房', type: 'SMOKE_SENSOR', status: 'ONLINE', power: 'NORMAL', alarm: 'ALARM', value: '烟雾 91%', metric: 'smoke=91', position: [1.15, 0.6, -1.72], endpoint: 'POST /api/devices/6/simulate' },
  { id: 7, backendId: 7, name: '厨房燃气传感器', room: '厨房', type: 'GAS_SENSOR', status: 'ONLINE', power: 'NORMAL', alarm: 'NORMAL', value: '燃气 22%', metric: 'gas=22', position: [2.75, 0.58, -0.7], endpoint: 'POST /api/devices/7/simulate' },
  { id: 8, backendId: 8, name: '入户门磁传感器', room: '玄关', type: 'DOOR_SENSOR', status: 'ONLINE', power: 'OPEN', alarm: 'NORMAL', value: '门已打开', metric: 'door=open', position: [1.05, 0.55, 2.95], endpoint: 'GET /api/homes/1/devices' },
  { id: 9, backendId: 9, name: '玄关摄像头', room: '玄关', type: 'CAMERA', status: 'OFFLINE', power: 'OFF', alarm: 'NORMAL', value: '离线', metric: 'video=offline', position: [3.05, 1.18, 2.75], endpoint: 'GET /api/homes/1/devices' },
]

const visibleDevices = computed(() =>
  selectedRoom.value === '全部' ? devices : devices.filter((device) => device.room === selectedRoom.value),
)
const onlineCount = computed(() => devices.filter((device) => device.status === 'ONLINE').length)
const alarmCount = computed(() => devices.filter((device) => device.alarm === 'ALARM').length)
const offlineCount = computed(() => devices.filter((device) => device.status === 'OFFLINE').length)
const currentAlarm = computed(() => devices.find((device) => device.alarm === 'ALARM') ?? null)

function makeMaterial(color: number, roughness = 0.55, metalness = 0.04) {
  return new THREE.MeshStandardMaterial({ color, roughness, metalness })
}

function makeTranslucent(color: number, opacity: number) {
  return new THREE.MeshStandardMaterial({ color, transparent: true, opacity, roughness: 0.65, depthWrite: false })
}

function makeBox(size: [number, number, number], color: number, position: [number, number, number], roughness = 0.55) {
  const mesh = new THREE.Mesh(new THREE.BoxGeometry(...size), makeMaterial(color, roughness))
  mesh.position.set(...position)
  mesh.castShadow = true
  mesh.receiveShadow = true
  return mesh
}

function makeCylinder(radius: number, height: number, color: number, position: [number, number, number], segments = 32) {
  const mesh = new THREE.Mesh(new THREE.CylinderGeometry(radius, radius, height, segments), makeMaterial(color))
  mesh.position.set(...position)
  mesh.castShadow = true
  mesh.receiveShadow = true
  return mesh
}

function makeLabel(text: string, color = '#18202a') {
  const canvas = document.createElement('canvas')
  canvas.width = 512
  canvas.height = 128
  const ctx = canvas.getContext('2d')
  if (!ctx) throw new Error('missing canvas context')
  ctx.clearRect(0, 0, canvas.width, canvas.height)
  ctx.fillStyle = 'rgba(255,255,255,0.9)'
  ctx.strokeStyle = 'rgba(96,111,128,0.45)'
  ctx.lineWidth = 3
  roundRect(ctx, 16, 18, 480, 90, 18)
  ctx.fill()
  ctx.stroke()
  ctx.fillStyle = color
  ctx.font = '600 34px Microsoft YaHei, Arial'
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  ctx.fillText(text, 256, 64)

  const texture = new THREE.CanvasTexture(canvas)
  texture.anisotropy = 4
  const sprite = new THREE.Sprite(new THREE.SpriteMaterial({ map: texture, transparent: true }))
  sprite.scale.set(1.18, 0.3, 1)
  labelSprites.push(sprite)
  return sprite
}

function roundRect(ctx: CanvasRenderingContext2D, x: number, y: number, width: number, height: number, radius: number) {
  ctx.beginPath()
  ctx.moveTo(x + radius, y)
  ctx.lineTo(x + width - radius, y)
  ctx.quadraticCurveTo(x + width, y, x + width, y + radius)
  ctx.lineTo(x + width, y + height - radius)
  ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height)
  ctx.lineTo(x + radius, y + height)
  ctx.quadraticCurveTo(x, y + height, x, y + height - radius)
  ctx.lineTo(x, y + radius)
  ctx.quadraticCurveTo(x, y, x + radius, y)
  ctx.closePath()
}

function addRoom(room: RoomArea) {
  if (!scene) return
  const floor = new THREE.Mesh(new THREE.BoxGeometry(room.width, 0.05, room.depth), makeMaterial(room.color, 0.72))
  floor.position.set(room.x, 0, room.z)
  floor.receiveShadow = true
  scene.add(floor)

  const borderMaterial = new THREE.LineBasicMaterial({ color: room.border })
  const y = 0.062
  const x1 = room.x - room.width / 2
  const x2 = room.x + room.width / 2
  const z1 = room.z - room.depth / 2
  const z2 = room.z + room.depth / 2
  const points = [
    new THREE.Vector3(x1, y, z1),
    new THREE.Vector3(x2, y, z1),
    new THREE.Vector3(x2, y, z2),
    new THREE.Vector3(x1, y, z2),
    new THREE.Vector3(x1, y, z1),
  ]
  scene.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(points), borderMaterial))

  const roomLabel = makeLabel(room.name)
  roomLabel.position.set(room.x, 0.16, room.z - room.depth / 2 + 0.35)
  roomLabel.scale.set(0.9, 0.23, 1)
  scene.add(roomLabel)

  const overlay = new THREE.Mesh(new THREE.BoxGeometry(room.width, 0.035, room.depth), makeTranslucent(0xef4444, 0.0))
  overlay.position.set(room.x, 0.09, room.z)
  overlay.userData.roomName = room.name
  roomAlarmOverlays.push(overlay)
  scene.add(overlay)
}

function addWallsAndOpenings() {
  if (!scene) return
  const outer = 0xb9c5ce
  const inner = 0xcfd8df
  scene.add(makeBox([8.25, 1.22, 0.08], outer, [-0.15, 0.61, -2.92]))
  scene.add(makeBox([8.25, 1.22, 0.08], outer, [-0.15, 0.61, 3.18]))
  scene.add(makeBox([0.08, 1.22, 6.1], outer, [-4.55, 0.61, 0.13]))
  scene.add(makeBox([0.08, 1.22, 6.1], outer, [3.92, 0.61, 0.13]))
  scene.add(makeBox([0.08, 0.96, 6.1], inner, [-0.35, 0.48, 0.13]))
  scene.add(makeBox([8.25, 0.96, 0.08], inner, [-0.15, 0.48, 0.12]))

  addDoorway([0.72, 0.03, 3.16], 0)
  addDoorway([-0.35, 0.03, -0.18], Math.PI / 2)
  addWindow([-3.15, 0.9, -2.96], [1.2, 0.42, 0.04])
  addWindow([2.18, 0.9, -2.96], [1.0, 0.42, 0.04])
  addWindow([-4.58, 0.92, 1.72], [0.04, 0.42, 1.05])
}

function addDoorway(position: [number, number, number], rotationY: number) {
  if (!scene) return
  const frame = new THREE.Group()
  frame.position.set(...position)
  frame.rotation.y = rotationY
  frame.add(makeBox([0.78, 0.08, 0.08], 0x8b6d4f, [0, 0.06, 0]))
  frame.add(makeBox([0.08, 0.82, 0.08], 0x8b6d4f, [-0.42, 0.46, 0]))
  frame.add(makeBox([0.08, 0.82, 0.08], 0x8b6d4f, [0.42, 0.46, 0]))
  scene.add(frame)
}

function addWindow(position: [number, number, number], size: [number, number, number]) {
  if (!scene) return
  const glass = new THREE.Mesh(new THREE.BoxGeometry(...size), makeTranslucent(0x8ecae6, 0.38))
  glass.position.set(...position)
  scene.add(glass)
}

function addFurniture() {
  if (!scene) return
  addLivingRoomFurniture()
  addKitchenFurniture()
  addBedroomFurniture()
  addEntryFurniture()
}

function addLivingRoomFurniture() {
  if (!scene) return
  scene.add(makeBox([1.45, 0.26, 0.78], 0x78909c, [-3.35, 0.18, -0.82]))
  scene.add(makeBox([1.45, 0.55, 0.14], 0x607d8b, [-3.35, 0.43, -0.42]))
  scene.add(makeBox([0.28, 0.34, 0.78], 0x607d8b, [-4.22, 0.24, -0.82]))
  scene.add(makeBox([0.28, 0.34, 0.78], 0x607d8b, [-2.48, 0.24, -0.82]))
  scene.add(makeCylinder(0.38, 0.16, 0x9a7b64, [-3.2, 0.14, -1.65]))
  scene.add(makeBox([1.38, 0.08, 0.92], 0xbfd7ea, [-2.32, 0.07, -1.48], 0.9))
  scene.add(makeBox([1.04, 0.5, 0.08], 0x26323f, [-1.0, 0.48, -2.58]))
  scene.add(makeBox([1.25, 0.08, 0.32], 0x5f6f7c, [-1.0, 0.18, -2.44]))
}

function addKitchenFurniture() {
  if (!scene) return
  scene.add(makeBox([2.3, 0.5, 0.44], 0x9ca3af, [2.0, 0.28, -2.28]))
  scene.add(makeBox([2.3, 0.08, 0.48], 0x475569, [2.0, 0.58, -2.28]))
  scene.add(makeBox([0.52, 0.08, 0.34], 0x1f2937, [1.35, 0.64, -2.35]))
  scene.add(makeBox([0.42, 0.06, 0.28], 0x93c5fd, [2.2, 0.65, -2.35]))
  scene.add(makeBox([0.9, 1.05, 0.62], 0xd7dee8, [3.02, 0.55, -1.08]))
  scene.add(makeBox([0.78, 0.32, 0.58], 0xa1a1aa, [1.15, 0.22, -0.72]))
  scene.add(makeBox([1.1, 0.06, 0.78], 0xf3f4f6, [1.72, 0.56, -0.72]))
}

function addBedroomFurniture() {
  if (!scene) return
  scene.add(makeBox([1.55, 0.26, 1.05], 0x9b7a65, [-3.38, 0.2, 1.78]))
  scene.add(makeBox([1.5, 0.14, 0.98], 0xd6c7b8, [-3.38, 0.42, 1.78]))
  scene.add(makeBox([0.62, 0.12, 0.34], 0xf8fafc, [-3.75, 0.55, 1.36]))
  scene.add(makeBox([0.62, 0.12, 0.34], 0xf8fafc, [-2.98, 0.55, 1.36]))
  scene.add(makeBox([0.42, 0.38, 0.42], 0x7c6f64, [-1.22, 0.22, 1.1]))
  scene.add(makeBox([1.0, 1.05, 0.45], 0x8b735f, [-1.0, 0.56, 2.82]))
}

function addEntryFurniture() {
  if (!scene) return
  scene.add(makeBox([0.9, 0.32, 0.42], 0x7b8794, [1.15, 0.22, 1.02]))
  scene.add(makeBox([0.72, 0.84, 0.12], 0x9ca3af, [3.55, 0.54, 1.15]))
  const door = makeBox([0.12, 0.94, 0.62], 0x8b5e3c, [0.78, 0.53, 3.02])
  door.rotation.y = -0.62
  scene.add(door)
}

function addGridAndLegendBase() {
  if (!scene) return
  const grid = new THREE.GridHelper(9, 18, 0xb8c2cc, 0xd9e2ea)
  grid.position.y = -0.005
  scene.add(grid)
}

function deviceColor(device: DeviceState) {
  if (device.alarm === 'ALARM') return 0xef4444
  if (device.status === 'OFFLINE') return 0x8b96a3
  if (device.type === 'LIGHT' && device.power === 'ON') return 0xffd447
  if (device.type === 'LIGHT') return 0x64748b
  if (device.type === 'PLUG' && device.power === 'ON') return 0x38bdf8
  if (device.type === 'CAMERA') return 0x3f6b80
  if (device.type === 'TEMP_SENSOR') return 0x23b26d
  if (device.type === 'DOOR_SENSOR') return device.power === 'OPEN' ? 0xf97316 : 0x2563eb
  return 0x10b981
}

function addDevice(device: DeviceState) {
  if (!scene) return
  const group = new THREE.Group()
  group.position.set(...device.position)
  group.userData.deviceId = device.id
  group.userData.selectable = true

  const color = deviceColor(device)
  let indicator: THREE.Mesh

  if (device.type === 'LIGHT') {
    const shade = new THREE.Mesh(new THREE.ConeGeometry(0.22, 0.26, 32), makeMaterial(0xf8fafc, 0.35))
    shade.rotation.x = Math.PI
    group.add(shade)
    const bulb = new THREE.Mesh(new THREE.SphereGeometry(0.14, 24, 16), makeMaterial(color, 0.28, 0.04))
    bulb.position.y = -0.18
    bulb.castShadow = true
    indicator = bulb
    group.add(bulb)
    group.add(makeBox([0.06, 0.28, 0.06], 0x334155, [0, 0.24, 0]))
    if (device.power === 'ON') {
      const glow = new THREE.PointLight(0xffd447, 2.4, 3.0)
      glow.position.set(0, -0.08, 0)
      group.add(glow)
      const cone = new THREE.Mesh(new THREE.ConeGeometry(0.78, 1.0, 32, 1, true), makeTranslucent(0xffd447, 0.14))
      cone.position.y = -0.64
      cone.rotation.x = Math.PI
      group.add(cone)
    }
  } else if (device.type === 'PLUG') {
    indicator = makeBox([0.34, 0.26, 0.16], color, [0, 0, 0])
    group.add(indicator)
    group.add(makeBox([0.05, 0.12, 0.035], 0x17212b, [-0.07, 0.02, -0.11]))
    group.add(makeBox([0.05, 0.12, 0.035], 0x17212b, [0.07, 0.02, -0.11]))
    group.add(makeBox([0.5, 0.035, 0.035], 0x1f2937, [0.36, -0.02, 0]))
  } else if (device.type === 'CAMERA') {
    indicator = makeBox([0.34, 0.22, 0.22], color, [0, 0, 0])
    group.add(indicator)
    const lens = new THREE.Mesh(new THREE.CylinderGeometry(0.095, 0.095, 0.12, 24), makeMaterial(0x111827, 0.25, 0.4))
    lens.rotation.x = Math.PI / 2
    lens.position.z = -0.17
    group.add(lens)
    const cone = new THREE.Mesh(new THREE.ConeGeometry(0.22, 0.72, 28, 1, true), makeTranslucent(0x6ee7f9, device.status === 'ONLINE' ? 0.2 : 0.04))
    cone.rotation.x = Math.PI / 2
    cone.position.z = -0.52
    group.add(cone)
  } else if (device.type === 'DOOR_SENSOR') {
    indicator = makeBox([0.08, 0.18, 0.08], color, [0.16, 0.12, -0.18])
    group.add(indicator)
  } else {
    indicator = new THREE.Mesh(new THREE.SphereGeometry(0.17, 24, 16), makeMaterial(color))
    indicator.castShadow = true
    group.add(indicator)
    group.add(makeBox([0.28, 0.06, 0.28], 0x334155, [0, -0.19, 0]))
  }

  const statusRing = new THREE.Mesh(
    new THREE.TorusGeometry(0.28, 0.012, 8, 52),
    makeTranslucent(device.alarm === 'ALARM' ? 0xef4444 : device.status === 'ONLINE' ? 0x22c55e : 0x94a3b8, 0.6),
  )
  statusRing.rotation.x = Math.PI / 2
  statusRing.position.y = -0.28
  group.add(statusRing)

  if (device.alarm === 'ALARM') {
    addAlarmBeacon(group)
    alarmObjects.push(group)
  }

  const label = makeLabel(device.name, device.alarm === 'ALARM' ? '#9f1239' : '#18202a')
  label.position.set(0, 0.48, 0)
  group.add(label)

  deviceRuntime.set(device.id, { group, indicator, label, ring: statusRing })
  scene.add(group)
}

function addAlarmBeacon(group: THREE.Group) {
  const beaconMat = makeTranslucent(0xef4444, 0.18)
  alarmMaterials.push(beaconMat)
  const beacon = new THREE.Mesh(new THREE.SphereGeometry(0.52, 32, 18), beaconMat)
  beacon.position.y = 0.05
  group.add(beacon)

  const waveMat = makeTranslucent(0xef4444, 0.35)
  alarmMaterials.push(waveMat)
  const wave = new THREE.Mesh(new THREE.TorusGeometry(0.42, 0.016, 8, 64), waveMat)
  wave.rotation.x = Math.PI / 2
  wave.position.y = -0.25
  group.add(wave)
}

function setSelected(device: DeviceState | null) {
  selectedDevice.value = device
  if (device) selectedRoom.value = device.room
  deviceRuntime.forEach((runtime, id) => {
    const active = id === device?.id
    runtime.group.scale.setScalar(active ? 1.22 : 1)
    const ringMaterial = runtime.ring?.material as THREE.MeshStandardMaterial | undefined
    if (ringMaterial) ringMaterial.opacity = active ? 0.95 : 0.55
  })
  if (device && viewMode.value === 'device') focusDevice(device)
}

function selectRoom(roomName: string) {
  selectedRoom.value = roomName
  const next = roomName === '全部' ? devices[0] : devices.find((device) => device.room === roomName) ?? null
  setSelected(next)
}

function focusDevice(device: DeviceState) {
  if (!camera || !controls) return
  const [x, y, z] = device.position
  controls.target.set(x, y * 0.45, z)
  camera.position.set(x + 2.4, 3.1, z + 3.0)
}

function switchView(mode: 'overview' | 'alarm' | 'device') {
  viewMode.value = mode
  if (!camera || !controls) return
  if (mode === 'overview') {
    controls.target.set(-0.25, 0.12, 0.1)
    camera.position.set(4.9, 5.4, 6.9)
  } else if (mode === 'alarm' && currentAlarm.value) {
    setSelected(currentAlarm.value)
    controls.target.set(1.55, 0.2, -1.45)
    camera.position.set(4.3, 3.3, 1.2)
  } else if (mode === 'device' && selectedDevice.value) {
    focusDevice(selectedDevice.value)
  }
}

function setupScene() {
  const host = sceneHost.value
  if (!host) return

  scene = new THREE.Scene()
  scene.background = new THREE.Color(0xeef3f7)
  scene.fog = new THREE.Fog(0xeef3f7, 9, 18)

  camera = new THREE.PerspectiveCamera(45, host.clientWidth / host.clientHeight, 0.1, 100)
  camera.position.set(4.9, 5.4, 6.9)

  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false, preserveDrawingBuffer: true })
  renderer.setSize(host.clientWidth, host.clientHeight)
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
  renderer.shadowMap.enabled = true
  renderer.shadowMap.type = THREE.PCFShadowMap
  host.appendChild(renderer.domElement)

  controls = new OrbitControls(camera, renderer.domElement)
  controls.enableDamping = true
  controls.target.set(-0.25, 0.12, 0.1)
  controls.maxPolarAngle = Math.PI * 0.48
  controls.minDistance = 4.2
  controls.maxDistance = 12.5

  scene.add(new THREE.HemisphereLight(0xffffff, 0x8aa0b5, 1.75))
  const sun = new THREE.DirectionalLight(0xffffff, 2.4)
  sun.position.set(3.5, 6.5, 4.2)
  sun.castShadow = true
  sun.shadow.mapSize.set(2048, 2048)
  sun.shadow.camera.near = 0.5
  sun.shadow.camera.far = 16
  scene.add(sun)

  addGridAndLegendBase()
  rooms.forEach(addRoom)
  addWallsAndOpenings()
  addFurniture()
  devices.forEach(addDevice)
  setSelected(devices[0])

  renderer.domElement.addEventListener('pointerdown', handlePointerDown)
  resizeObserver = new ResizeObserver(resizeScene)
  resizeObserver.observe(host)
  animate()
}

function handlePointerDown(event: PointerEvent) {
  if (!renderer || !camera) return
  const rect = renderer.domElement.getBoundingClientRect()
  pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1
  pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1
  raycaster.setFromCamera(pointer, camera)
  const intersections = raycaster.intersectObjects([...deviceRuntime.values()].map((item) => item.group), true)
  const hit = intersections.find((item) => {
    let object: THREE.Object3D | null = item.object
    while (object) {
      if (object.userData.selectable) return true
      object = object.parent
    }
    return false
  })
  if (!hit) return

  let object: THREE.Object3D | null = hit.object
  while (object && !object.userData.selectable) object = object.parent
  const device = devices.find((item) => item.id === object?.userData.deviceId) ?? null
  setSelected(device)
}

function resizeScene() {
  const host = sceneHost.value
  if (!host || !renderer || !camera) return
  const width = Math.max(host.clientWidth, 1)
  const height = Math.max(host.clientHeight, 1)
  camera.aspect = width / height
  camera.updateProjectionMatrix()
  renderer.setSize(width, height)
}

function animate() {
  if (!renderer || !scene || !camera) return
  elapsed += 0.018
  controls?.update()

  const pulse = 0.7 + Math.sin(elapsed * 7) * 0.3
  alarmObjects.forEach((object) => {
    const selected = object.userData.deviceId === selectedDevice.value?.id
    object.scale.setScalar((selected ? 1.2 : 1) + pulse * 0.13)
  })
  alarmMaterials.forEach((mat, index) => {
    mat.opacity = index % 2 === 0 ? 0.12 + pulse * 0.14 : 0.18 + pulse * 0.2
  })
  roomAlarmOverlays.forEach((overlay) => {
    const hasAlarm = devices.some((device) => device.room === overlay.userData.roomName && device.alarm === 'ALARM')
    const mat = overlay.material as THREE.MeshStandardMaterial
    mat.opacity = hasAlarm ? 0.12 + pulse * 0.1 : 0
  })
  labelSprites.forEach((sprite) => {
    sprite.quaternion.copy(camera!.quaternion)
  })

  renderer.render(scene, camera)
  frameId = requestAnimationFrame(animate)
}

function updateClock() {
  currentTime.value = new Intl.DateTimeFormat('zh-CN', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  }).format(new Date())
}

onMounted(() => {
  updateClock()
  clockTimer = window.setInterval(updateClock, 1000)
  setupScene()
})

onBeforeUnmount(() => {
  window.clearInterval(clockTimer)
  cancelAnimationFrame(frameId)
  resizeObserver?.disconnect()
  if (renderer) {
    renderer.domElement.removeEventListener('pointerdown', handlePointerDown)
    renderer.dispose()
  }
  scene?.traverse((object) => {
    const mesh = object as THREE.Mesh
    mesh.geometry?.dispose?.()
    const mat = mesh.material as THREE.Material | THREE.Material[] | undefined
    if (Array.isArray(mat)) mat.forEach((item) => item.dispose())
    else mat?.dispose?.()
  })
})
</script>

<template>
  <main class="visual-shell">
    <section class="scene-wrap" aria-label="智能家居 3D 可视化">
      <div class="topbar">
        <div>
          <h1>演示家庭</h1>
          <p>智能家居 3D 状态总览</p>
        </div>
        <div class="metrics">
          <span><strong>{{ onlineCount }}</strong> 在线</span>
          <span><strong>{{ alarmCount }}</strong> 报警</span>
          <span><strong>{{ offlineCount }}</strong> 离线</span>
          <span>{{ currentTime }}</span>
        </div>
      </div>

      <div class="scene-actions" aria-label="视角切换">
        <button type="button" :class="{ active: viewMode === 'overview' }" @click="switchView('overview')">总览</button>
        <button type="button" :class="{ active: viewMode === 'alarm' }" @click="switchView('alarm')">报警定位</button>
        <button type="button" :class="{ active: viewMode === 'device' }" @click="switchView('device')">设备跟随</button>
      </div>

      <div ref="sceneHost" class="scene-host"></div>

      <div v-if="currentAlarm" class="alarm-strip">
        <strong>{{ currentAlarm.room }}异常</strong>
        <span>{{ currentAlarm.name }}，{{ currentAlarm.value }}，已触发报警联动。</span>
      </div>
    </section>

    <aside class="inspector">
      <div class="inspector-head">
        <span class="eyebrow">Device</span>
        <h2>{{ selectedDevice?.name ?? '未选择设备' }}</h2>
        <p v-if="selectedDevice">{{ selectedDevice.endpoint }}</p>
      </div>

      <dl v-if="selectedDevice" class="device-list">
        <div>
          <dt>房间</dt>
          <dd>{{ selectedDevice.room }}</dd>
        </div>
        <div>
          <dt>类型</dt>
          <dd>{{ selectedDevice.type }}</dd>
        </div>
        <div>
          <dt>连接</dt>
          <dd :class="selectedDevice.status === 'ONLINE' ? 'ok' : 'muted'">{{ selectedDevice.status }}</dd>
        </div>
        <div>
          <dt>状态</dt>
          <dd>{{ selectedDevice.power }}</dd>
        </div>
        <div>
          <dt>读数</dt>
          <dd>{{ selectedDevice.value }}</dd>
        </div>
        <div>
          <dt>指标</dt>
          <dd>{{ selectedDevice.metric }}</dd>
        </div>
        <div>
          <dt>告警</dt>
          <dd :class="selectedDevice.alarm === 'ALARM' ? 'danger' : 'ok'">{{ selectedDevice.alarm }}</dd>
        </div>
      </dl>

      <section class="room-summary">
        <h3>房间筛选</h3>
        <button type="button" :class="{ active: selectedRoom === '全部' }" @click="selectRoom('全部')">
          全部设备
        </button>
        <button
          v-for="room in rooms"
          :key="room.name"
          type="button"
          :class="{ active: selectedRoom === room.name }"
          @click="selectRoom(room.name)"
        >
          <span>{{ room.name }}</span>
          <small>{{ devices.filter((device) => device.room === room.name).length }} 个设备</small>
        </button>
      </section>

      <section class="device-table">
        <h3>当前列表</h3>
        <button
          v-for="device in visibleDevices"
          :key="device.id"
          type="button"
          :class="{ active: selectedDevice?.id === device.id, alarm: device.alarm === 'ALARM' }"
          @click="setSelected(device)"
        >
          <span>{{ device.name }}</span>
          <small>{{ device.value }}</small>
        </button>
      </section>
    </aside>
  </main>
</template>

<style scoped>
.visual-shell {
  width: 100%;
  min-height: 100svh;
  display: grid;
  grid-template-columns: minmax(0, 1fr) 360px;
  background: #eef3f7;
  color: #17212b;
}

.scene-wrap {
  position: relative;
  min-width: 0;
  min-height: 100svh;
  overflow: hidden;
}

.scene-host {
  width: 100%;
  height: 100svh;
}

.scene-host :deep(canvas) {
  display: block;
  width: 100%;
  height: 100%;
}

.topbar,
.scene-actions,
.alarm-strip {
  position: absolute;
  z-index: 3;
}

.topbar {
  inset: 22px 24px auto 24px;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  pointer-events: none;
}

h1,
h2,
h3,
p,
dl {
  margin: 0;
}

h1 {
  font-size: 28px;
  line-height: 1.1;
  letter-spacing: 0;
}

.topbar p {
  margin-top: 7px;
  color: #52606f;
  font-size: 14px;
}

.metrics {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.metrics span,
.alarm-strip,
.scene-actions {
  background: rgba(255, 255, 255, 0.84);
  border: 1px solid rgba(141, 154, 168, 0.45);
  box-shadow: 0 14px 34px rgba(60, 72, 88, 0.12);
  backdrop-filter: blur(12px);
}

.metrics span {
  min-width: 76px;
  padding: 10px 12px;
  border-radius: 8px;
  color: #3b4652;
  font-size: 13px;
  text-align: center;
}

.metrics strong {
  color: #17212b;
  font-size: 18px;
}

.scene-actions {
  left: 24px;
  top: 108px;
  display: flex;
  gap: 6px;
  padding: 6px;
  border-radius: 8px;
}

button {
  font: inherit;
}

.scene-actions button,
.room-summary button,
.device-table button {
  border: 1px solid transparent;
  border-radius: 8px;
  cursor: pointer;
}

.scene-actions button {
  min-height: 34px;
  padding: 0 12px;
  background: transparent;
  color: #334155;
}

.scene-actions button.active {
  background: #1d4ed8;
  color: #ffffff;
}

.alarm-strip {
  left: 24px;
  bottom: 22px;
  display: grid;
  gap: 4px;
  max-width: min(520px, calc(100% - 48px));
  padding: 13px 16px;
  border-radius: 8px;
  border-color: rgba(239, 68, 68, 0.38);
  color: #8a1f1f;
  background: rgba(255, 241, 241, 0.9);
}

.alarm-strip span {
  color: #9f3a3a;
  font-size: 13px;
}

.inspector {
  min-height: 100svh;
  padding: 28px 24px;
  border-left: 1px solid #ccd5df;
  background: #f8fafc;
  display: flex;
  flex-direction: column;
  gap: 22px;
}

.eyebrow {
  display: block;
  margin-bottom: 10px;
  color: #64748b;
  font-size: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.inspector h2 {
  font-size: 22px;
  line-height: 1.2;
  letter-spacing: 0;
}

.inspector-head p {
  margin-top: 9px;
  color: #64748b;
  font-size: 12px;
  word-break: break-word;
}

.device-list {
  display: grid;
  gap: 10px;
}

.device-list div {
  display: grid;
  grid-template-columns: 76px minmax(0, 1fr);
  align-items: center;
  min-height: 38px;
  padding: 0 0 9px;
  border-bottom: 1px solid #dbe3ea;
}

.device-list dt {
  color: #64748b;
  font-size: 13px;
}

.device-list dd {
  color: #17212b;
  font-size: 14px;
  word-break: break-word;
}

.ok {
  color: #16834b !important;
}

.danger {
  color: #d92d20 !important;
}

.muted {
  color: #7b8794 !important;
}

.room-summary,
.device-table {
  display: grid;
  gap: 9px;
}

.room-summary h3,
.device-table h3 {
  font-size: 15px;
  color: #334155;
}

.room-summary button,
.device-table button {
  width: 100%;
  min-height: 42px;
  padding: 8px 10px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  background: #ffffff;
  color: #243241;
  border-color: #c7d1dc;
  text-align: left;
}

.device-table {
  min-height: 0;
  overflow: auto;
}

.device-table button {
  min-height: 48px;
  align-items: flex-start;
  flex-direction: column;
  gap: 4px;
}

.room-summary button.active,
.device-table button.active {
  border-color: #2563eb;
  color: #1d4ed8;
  background: #eff6ff;
}

.device-table button.alarm {
  border-color: rgba(217, 45, 32, 0.45);
  background: #fff1f1;
}

.room-summary small,
.device-table small {
  color: #64748b;
  font-size: 12px;
}

@media (max-width: 900px) {
  .visual-shell {
    grid-template-columns: 1fr;
  }

  .scene-wrap,
  .scene-host {
    min-height: 68svh;
    height: 68svh;
  }

  .topbar {
    inset: 14px 14px auto 14px;
    flex-direction: column;
  }

  .scene-actions {
    left: 14px;
    top: 132px;
    max-width: calc(100% - 28px);
    overflow-x: auto;
  }

  .metrics {
    justify-content: flex-start;
  }

  .metrics span {
    min-width: 70px;
    padding: 8px 10px;
  }

  h1 {
    font-size: 23px;
  }

  .inspector {
    min-height: auto;
    border-left: none;
    border-top: 1px solid #ccd5df;
  }

  .alarm-strip {
    left: 14px;
    bottom: 14px;
    max-width: calc(100% - 28px);
  }
}
</style>
