#include "repositories/MockOperationLogRepository.h"
#include "utils/TimeUtil.h"

namespace smart_home {

static std::vector<OperationLog>& logs() {
    static std::vector<OperationLog> data;
    return data;
}

OperationLog MockOperationLogRepository::save(const OperationLog& log) {
    OperationLog copy = log;
    copy.logId = static_cast<long long>(logs().size()) + 1;
    copy.createdAt = TimeUtil::now();
    logs().push_back(copy);
    return copy;
}

std::vector<OperationLog> MockOperationLogRepository::findByHome(long long homeId) {
    std::vector<OperationLog> result;
    for (const auto& log : logs()) {
        if (log.homeId == homeId) result.push_back(log);
    }
    return result;
}

} // namespace smart_home

