#pragma once

#include "repositories/OperationLogRepository.h"

namespace smart_home {

class MockOperationLogRepository : public OperationLogRepository {
public:
    OperationLog save(const OperationLog& log) override;
    std::vector<OperationLog> findByHome(long long homeId) override;
};

} // namespace smart_home

