#pragma once

#include <string>

namespace smart_home {

struct OperationLog {
    long long logId = 0;
    long long userId = 0;
    long long homeId = 0;
    std::string actionType;
    std::string actionDesc;
    std::string targetType;
    long long targetId = 0;
    std::string ipAddress;
    std::string createdAt;
};

} // namespace smart_home

