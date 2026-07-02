#pragma once

#include <string>

namespace smart_home {

class MemberService {
public:
    std::string invite(const std::string& token, long long homeId, const std::string& phone,
                       const std::string& role, const std::string& validTo);
    std::string apply(const std::string& token, long long homeId, const std::string& reason);
    std::string approve(const std::string& token, long long homeId, long long memberId, bool approved, const std::string& role);
    std::string listMembers(const std::string& token, long long homeId);
    std::string updatePermission(const std::string& token, long long homeId, long long memberId,
                                 const std::string& role, const std::string& permissionScope,
                                 const std::string& validTo);
    std::string removeMember(const std::string& token, long long homeId, long long memberId);
};

} // namespace smart_home

