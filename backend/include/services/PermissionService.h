#pragma once

#include <string>

namespace smart_home {

class PermissionService {
public:
    bool isOwner(long long userId, long long homeId);
    bool isMemberOfHome(long long userId, long long homeId);
    bool canManageHome(long long userId, long long homeId);
    bool canManageMember(long long userId, long long homeId, long long targetMemberId);
    bool canUpdateSystemConfig(long long userId, long long homeId);
    bool canViewLogs(long long userId, long long homeId);
    bool hasRole(long long userId, long long homeId, const std::string& role);
};

} // namespace smart_home

