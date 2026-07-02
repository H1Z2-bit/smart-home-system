#pragma once

#include "models/OperationLog.h"
#include <vector>

namespace smart_home {

class OperationLogRepository {
public:
    virtual ~OperationLogRepository() = default;
    virtual OperationLog save(const OperationLog& log) = 0;
    virtual std::vector<OperationLog> findByHome(long long homeId) = 0;
};

} // namespace smart_home

