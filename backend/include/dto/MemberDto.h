#pragma once

#include <string>

namespace smart_home {

struct MemberPermissionRequest {
    std::string role;
    std::string permissionScope;
    std::string validTo;
};

} // namespace smart_home

