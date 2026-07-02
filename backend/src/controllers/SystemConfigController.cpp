#include "controllers/SystemConfigController.h"
#include "services/OperationLogService.h"
#include "services/PermissionService.h"
#include "services/SystemConfigService.h"
#include "utils/ApiResponse.h"
#include "utils/ErrorCode.h"
#include "utils/JwtUtil.h"
#include "utils/Validator.h"

namespace smart_home {

static std::string systemTokenFrom(const HttpRequest& request) {
    const auto it = request.headers.find("authorization");
    return it == request.headers.end() ? "" : JwtUtil::extractBearerToken(it->second);
}

HttpResponse SystemConfigController::listConfig(const HttpRequest& request, long long homeId) {
    return {200, SystemConfigService().listConfig(systemTokenFrom(request), homeId)};
}

HttpResponse SystemConfigController::updateConfig(const HttpRequest& request, long long homeId) {
    return {200, SystemConfigService().updateConfig(
        systemTokenFrom(request), homeId,
        Validator::getString(request.body, "configKey").value_or(""),
        Validator::getString(request.body, "configValue").value_or(""),
        Validator::getString(request.body, "description").value_or(""))};
}

HttpResponse SystemConfigController::listLogs(const HttpRequest& request, long long homeId) {
    const auto token = systemTokenFrom(request);
    const auto payload = JwtUtil::parseToken(token);
    if (!payload) return {200, ApiResponse::error(UNAUTHORIZED, "unauthorized")};
    if (!PermissionService().canViewLogs(payload->userId, homeId)) {
        return {200, ApiResponse::error(FORBIDDEN, "permission denied")};
    }
    const auto logs = OperationLogService().listByHome(homeId);
    std::string data = "[";
    for (size_t i = 0; i < logs.size(); ++i) {
        const auto& log = logs[i];
        if (i) data += ",";
        data += "{\"logId\":" + std::to_string(log.logId) + ",\"userId\":" + std::to_string(log.userId) +
                ",\"homeId\":" + std::to_string(log.homeId) + ",\"actionType\":" + ApiResponse::quote(log.actionType) +
                ",\"actionDesc\":" + ApiResponse::quote(log.actionDesc) + ",\"targetType\":" + ApiResponse::quote(log.targetType) +
                ",\"targetId\":" + std::to_string(log.targetId) + ",\"createdAt\":" + ApiResponse::quote(log.createdAt) + "}";
    }
    data += "]";
    return {200, ApiResponse::success(data)};
}

} // namespace smart_home

