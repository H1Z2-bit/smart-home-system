#pragma once

#include <string>

namespace smart_home {

struct HomeMember {
    long long memberId = 0;
    long long homeId = 0;
    long long userId = 0;
    std::string role;
    std::string status;
    std::string permissionScope;
    std::string validFrom;
    std::string validTo;
    std::string createdAt;
    std::string updatedAt;
};

} // namespace smart_home

