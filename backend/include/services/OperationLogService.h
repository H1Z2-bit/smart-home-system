#pragma once

#include "models/OperationLog.h"
#include <string>
#include <vector>

namespace smart_home {

class OperationLogService {
public:
    OperationLog write(long long userId, long long homeId, const std::string& actionType,
                       const std::string& actionDesc, const std::string& targetType,
                       long long targetId, const std::string& ipAddress = "127.0.0.1");
    std::vector<OperationLog> listByHome(long long homeId);
};

} // namespace smart_home

