#include "services/PermissionService.h"
#include "repositories/MockHomeRepository.h"
#include "repositories/MockMemberRepository.h"

namespace smart_home {

bool PermissionService::isOwner(long long userId, long long homeId) {
    MockHomeRepository homeRepo;
    const auto home = homeRepo.findById(homeId);
    return home && home->ownerUserId == userId;
}

bool PermissionService::isMemberOfHome(long long userId, long long homeId) {
    MockMemberRepository memberRepo;
    const auto member = memberRepo.findByHomeAndUser(homeId, userId);
    return member && member->status == "ACTIVE";
}

bool PermissionService::canManageHome(long long userId, long long homeId) {
    return isOwner(userId, homeId);
}

bool PermissionService::canManageMember(long long userId, long long homeId, long long targetMemberId) {
    if (!isOwner(userId, homeId)) return false;
    MockMemberRepository memberRepo;
    const auto target = memberRepo.findById(targetMemberId);
    return target && target->homeId == homeId;
}

bool PermissionService::canUpdateSystemConfig(long long userId, long long homeId) {
    return isOwner(userId, homeId) || hasRole(userId, homeId, "MAINTAINER");
}

bool PermissionService::canViewLogs(long long userId, long long homeId) {
    return isOwner(userId, homeId);
}

bool PermissionService::hasRole(long long userId, long long homeId, const std::string& role) {
    MockMemberRepository memberRepo;
    const auto member = memberRepo.findByHomeAndUser(homeId, userId);
    return member && member->status == "ACTIVE" && member->role == role;
}

} // namespace smart_home

