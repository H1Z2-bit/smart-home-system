#include "services/HomeService.h"
#include "repositories/MockHomeRepository.h"
#include "repositories/MockMemberRepository.h"
#include "services/OperationLogService.h"
#include "services/PermissionService.h"
#include "utils/ApiResponse.h"
#include "utils/ErrorCode.h"
#include "utils/JwtUtil.h"
#include "utils/TimeUtil.h"

namespace smart_home {

static std::string homeJson(const Home& h) {
    return "{\"homeId\":" + std::to_string(h.homeId) + ",\"homeName\":" + ApiResponse::quote(h.homeName) +
           ",\"address\":" + ApiResponse::quote(h.address) + ",\"ownerUserId\":" + std::to_string(h.ownerUserId) + "}";
}

std::string HomeService::createHome(const std::string& token, const std::string& homeName, const std::string& address) {
    const auto payload = JwtUtil::parseToken(token);
    if (!payload) return ApiResponse::error(UNAUTHORIZED, "unauthorized");
    if (homeName.empty()) return ApiResponse::error(BAD_REQUEST, "homeName required");

    MockHomeRepository homeRepo;
    MockMemberRepository memberRepo;
    const std::string now = TimeUtil::now();
    const auto home = homeRepo.save(Home{0, homeName, address, payload->userId, now, now});
    memberRepo.save(HomeMember{0, home.homeId, payload->userId, "OWNER", "ACTIVE", "ALL", now, "", now, now});
    OperationLogService().write(payload->userId, home.homeId, "CREATE_HOME", "create home", "HOME", home.homeId);
    return ApiResponse::success(homeJson(home));
}

std::string HomeService::listHomes(const std::string& token) {
    const auto payload = JwtUtil::parseToken(token);
    if (!payload) return ApiResponse::error(UNAUTHORIZED, "unauthorized");
    MockHomeRepository repo;
    std::string data = "[";
    const auto homes = repo.findByOwnerOrMember(payload->userId);
    for (size_t i = 0; i < homes.size(); ++i) {
        if (i) data += ",";
        data += homeJson(homes[i]);
    }
    data += "]";
    return ApiResponse::success(data);
}

std::string HomeService::getHome(const std::string& token, long long homeId) {
    const auto payload = JwtUtil::parseToken(token);
    if (!payload) return ApiResponse::error(UNAUTHORIZED, "unauthorized");
    if (!PermissionService().isMemberOfHome(payload->userId, homeId)) return ApiResponse::error(FORBIDDEN, "permission denied");
    MockHomeRepository repo;
    const auto home = repo.findById(homeId);
    if (!home) return ApiResponse::error(NOT_FOUND, "home not found");
    return ApiResponse::success(homeJson(*home));
}

std::string HomeService::updateHome(const std::string& token, long long homeId, const std::string& homeName, const std::string& address) {
    const auto payload = JwtUtil::parseToken(token);
    if (!payload) return ApiResponse::error(UNAUTHORIZED, "unauthorized");
    if (!PermissionService().canManageHome(payload->userId, homeId)) return ApiResponse::error(FORBIDDEN, "permission denied");
    MockHomeRepository repo;
    const auto home = repo.findById(homeId);
    if (!home) return ApiResponse::error(NOT_FOUND, "home not found");
    Home updated = *home;
    updated.homeName = homeName.empty() ? updated.homeName : homeName;
    updated.address = address.empty() ? updated.address : address;
    repo.update(updated);
    OperationLogService().write(payload->userId, homeId, "UPDATE_HOME", "update home", "HOME", homeId);
    return ApiResponse::success(homeJson(updated));
}

std::string HomeService::deleteHome(const std::string& token, long long homeId) {
    const auto payload = JwtUtil::parseToken(token);
    if (!payload) return ApiResponse::error(UNAUTHORIZED, "unauthorized");
    if (!PermissionService().canManageHome(payload->userId, homeId)) return ApiResponse::error(FORBIDDEN, "permission denied");
    MockHomeRepository repo;
    if (!repo.remove(homeId)) return ApiResponse::error(NOT_FOUND, "home not found");
    OperationLogService().write(payload->userId, homeId, "DELETE_HOME", "delete home", "HOME", homeId);
    return ApiResponse::success("{\"status\":\"home_deleted\"}");
}

} // namespace smart_home

