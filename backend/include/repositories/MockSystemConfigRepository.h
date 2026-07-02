#pragma once

#include "repositories/SystemConfigRepository.h"

namespace smart_home {

class MockSystemConfigRepository : public SystemConfigRepository {
public:
    std::vector<SystemConfig> findByHome(long long homeId) override;
    std::optional<SystemConfig> findByHomeAndKey(long long homeId, const std::string& key) override;
    SystemConfig upsert(const SystemConfig& config) override;
};

} // namespace smart_home

