#include "services/OperationLogService.h"
#include "repositories/MockOperationLogRepository.h"
#include "utils/TimeUtil.h"

namespace smart_home {

OperationLog OperationLogService::write(long long userId, long long homeId, const std::string& actionType,
                                        const std::string& actionDesc, const std::string& targetType,
                                        long long targetId, const std::string& ipAddress) {
    MockOperationLogRepository repo;
    OperationLog log;
    log.userId = userId;
    log.homeId = homeId;
    log.actionType = actionType;
    log.actionDesc = actionDesc;
    log.targetType = targetType;
    log.targetId = targetId;
    log.ipAddress = ipAddress;
    log.createdAt = TimeUtil::now();
    return repo.save(log);
}

std::vector<OperationLog> OperationLogService::listByHome(long long homeId) {
    MockOperationLogRepository repo;
    return repo.findByHome(homeId);
}

} // namespace smart_home

