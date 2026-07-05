from fastapi import APIRouter

from app.api.v1 import (
    alarms,
    auth,
    debug,
    device_simulations,
    devices,
    health,
    homes,
    linkages,
    logs,
    members,
    rooms,
    scenes,
    schedules,
    self_checks,
    system,
)

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(debug.router)
api_router.include_router(auth.router)
api_router.include_router(auth.user_router)
api_router.include_router(homes.router)
api_router.include_router(members.router)
api_router.include_router(rooms.router)
api_router.include_router(devices.router)
api_router.include_router(device_simulations.router)
api_router.include_router(logs.router)
api_router.include_router(scenes.router)
api_router.include_router(schedules.router)
api_router.include_router(linkages.router)
api_router.include_router(alarms.router)
api_router.include_router(self_checks.router)
api_router.include_router(system.router)
