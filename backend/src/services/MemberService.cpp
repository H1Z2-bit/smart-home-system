#include "services/MemberService.h"
#include "repositories/MockMemberRepository.h"
#include "repositories/MockUserRepository.h"
#include "services/OperationLogService.h"
#include "services/PermissionService.h"
#include "utils/ApiResponse.h"
#include "utils/ErrorCode.h"
#include "utils/JwtUtil.h"
#include "utils/TimeUtil.h"

namespace smart_home {

static std::string memberJson(const HomeMember& m) {
    return "{\"memberId\":" + std::to_string(m.memberId) + ",\"homeId\":" + std::to_string(m.homeId) +
           ",\"userId\":" + std::to_string(m.userId) + ",\"role\":" + ApiResponse::quote(m.role) +
           ",\"status\":" + ApiResponse::quote(m.status) + ",\"permissionScope\":" + ApiResponse::quote(m.permissionScope) +
           ",\"validTo\":" + ApiResponse::quote(m.validTo) + "}";
}

std::string MemberService::invite(const std::string& token, long long homeId, const std::string& phone, const std::string& role, const std::string& validTo) {
    const auto payload = JwtUtil::parseToken(token);
    if (!payload) return ApiResponse::error(UNAUTHORIZED, "unauthorized");
    if (!PermissionService().canManageHome(payload->userId, homeId)) return ApiResponse::error(FORBIDDEN, "permission denied");
    MockUserRepository userRepo;
    const auto user = userRepo.findByPhone(phone);
    if (!user) return ApiResponse::error(NOT_FOUND, "user not found");
    MockMemberRepository memberRepo;
    const std::string now = TimeUtil::now();
    const auto member = memberRepo.save(HomeMember{0, homeId, user->userId, role.empty() ? "MEMBER" : role, "ACTIVE", "ALL", now, validTo, now, now});
    OperationLogService().write(payload->userId, homeId, "INVITE_MEMBER", "invite member", "MEMBER", member.memberId);
    return ApiResponse::success(memberJson(member));
}

std::string MemberService::apply(const std::string& token, long long homeId, const std::string&) {
    const auto payload = JwtUtil::parseToken(token);
    if (!payload) return ApiResponse::error(UNAUTHORIZED, "unauthorized");
    MockMemberRepository memberRepo;
    const std::string now = TimeUtil::now();
    const auto member = memberRepo.save(HomeMember{0, homeId, payload->userId, "MEMBER", "PENDING", "", now, "", now, now});
    return ApiResponse::success(memberJson(member));
}

std::string MemberService::approve(const std::string& token, long long homeId, long long memberId, bool approved, const std::string& role) {
    const auto payload = JwtUtil::parseToken(token);
    if (!payload) return ApiResponse::error(UNAUTHORIZED, "unauthorized");
    if (!PermissionService().canManageMember(payload->userId, homeId, memberId)) return ApiResponse::error(FORBIDDEN, "permission denied");
    MockMemberRepository repo;
    auto member = repo.findById(memberId);
    if (!member) return ApiResponse::error(NOT_FOUND, "member not found");
    member->status = approved ? "ACTIVE" : "REJECTED";
    if (!role.empty()) member->role = role;
    repo.update(*member);
    OperationLogService().write(payload->userId, homeId, "APPROVE_MEMBER", "approve member", "MEMBER", memberId);
    return ApiResponse::success(memberJson(*member));
}

std::string MemberService::listMembers(const std::string& token, long long homeId) {
    const auto payload = JwtUtil::parseToken(token);
    if (!payload) return ApiResponse::error(UNAUTHORIZED, "unauthorized");
    if (!PermissionService().isMemberOfHome(payload->userId, homeId)) return ApiResponse::error(FORBIDDEN, "permission denied");
    MockMemberRepository repo;
    const auto members = repo.findByHome(homeId);
    std::string data = "[";
    for (size_t i = 0; i < members.size(); ++i) {
        if (i) data += ",";
        data += memberJson(members[i]);
    }
    data += "]";
    return ApiResponse::success(data);
}

std::string MemberService::updatePermission(const std::string& token, long long homeId, long long memberId,
                                            const std::string& role, const std::string& permissionScope, const std::string& validTo) {
    const auto payload = JwtUtil::parseToken(token);
    if (!payload) return ApiResponse::error(UNAUTHORIZED, "unauthorized");
    if (!PermissionService().canManageMember(payload->userId, homeId, memberId)) return ApiResponse::error(FORBIDDEN, "permission denied");
    MockMemberRepository repo;
    auto member = repo.findById(memberId);
    if (!member) return ApiResponse::error(NOT_FOUND, "member not found");
    if (!role.empty()) member->role = role;
    if (!permissionScope.empty()) member->permissionScope = permissionScope;
    if (!validTo.empty()) member->validTo = validTo;
    repo.update(*member);
    OperationLogService().write(payload->userId, homeId, "UPDATE_MEMBER_PERMISSION", "update member permission", "MEMBER", memberId);
    return ApiResponse::success(memberJson(*member));
}

std::string MemberService::removeMember(const std::string& token, long long homeId, long long memberId) {
    const auto payload = JwtUtil::parseToken(token);
    if (!payload) return ApiResponse::error(UNAUTHORIZED, "unauthorized");
    if (!PermissionService().canManageMember(payload->userId, homeId, memberId)) return ApiResponse::error(FORBIDDEN, "permission denied");
    MockMemberRepository repo;
    if (!repo.remove(memberId)) return ApiResponse::error(NOT_FOUND, "member not found");
    OperationLogService().write(payload->userId, homeId, "REMOVE_MEMBER", "remove member", "MEMBER", memberId);
    return ApiResponse::success("{\"status\":\"member_removed\"}");
}

} // namespace smart_home

