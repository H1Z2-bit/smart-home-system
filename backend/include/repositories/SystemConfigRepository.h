#pragma once

#include "models/SystemConfig.h"
#include <optional>
#include <vector>

namespace smart_home {

class SystemConfigRepository {
public:
    virtual ~SystemConfigRepository() = default;
    virtual std::vector<SystemConfig> findByHome(long long homeId) = 0;
    virtual std::optional<SystemConfig> findByHomeAndKey(long long homeId, const std::string& key) = 0;
    virtual SystemConfig upsert(const SystemConfig& config) = 0;
};

} // namespace smart_home

