#include "services/SystemConfigService.h"
#include "repositories/MockSystemConfigRepository.h"
#include "services/OperationLogService.h"
#include "services/PermissionService.h"
#include "utils/ApiResponse.h"
#include "utils/ErrorCode.h"
#include "utils/JwtUtil.h"
#include "utils/TimeUtil.h"

namespace smart_home {

static std::string configJson(const SystemConfig& c) {
    return "{\"configId\":" + std::to_string(c.configId) + ",\"homeId\":" + std::to_string(c.homeId) +
           ",\"configKey\":" + ApiResponse::quote(c.configKey) + ",\"configValue\":" + ApiResponse::quote(c.configValue) +
           ",\"configType\":" + ApiResponse::quote(c.configType) + ",\"description\":" + ApiResponse::quote(c.description) + "}";
}

std::string SystemConfigService::listConfig(const std::string& token, long long homeId) {
    const auto payload = JwtUtil::parseToken(token);
    if (!payload) return ApiResponse::error(UNAUTHORIZED, "unauthorized");
    if (!PermissionService().isMemberOfHome(payload->userId, homeId)) return ApiResponse::error(FORBIDDEN, "permission denied");
    MockSystemConfigRepository repo;
    const auto configs = repo.findByHome(homeId);
    std::string data = "[";
    for (size_t i = 0; i < configs.size(); ++i) {
        if (i) data += ",";
        data += configJson(configs[i]);
    }
    data += "]";
    return ApiResponse::success(data);
}

std::string SystemConfigService::updateConfig(const std::string& token, long long homeId, const std::string& key,
                                              const std::string& value, const std::string& description) {
    const auto payload = JwtUtil::parseToken(token);
    if (!payload) return ApiResponse::error(UNAUTHORIZED, "unauthorized");
    if (!PermissionService().canUpdateSystemConfig(payload->userId, homeId)) return ApiResponse::error(FORBIDDEN, "permission denied");
    MockSystemConfigRepository repo;
    const SystemConfig saved = repo.upsert(SystemConfig{0, homeId, key, value, "ALARM", description, payload->userId, TimeUtil::now()});
    OperationLogService().write(payload->userId, homeId, "UPDATE_SYSTEM_CONFIG", "update system config", "SYSTEM_CONFIG", saved.configId);
    return ApiResponse::success(configJson(saved));
}

} // namespace smart_home

