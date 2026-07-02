#include "repositories/MockSystemConfigRepository.h"
#include "utils/TimeUtil.h"
#include <algorithm>

namespace smart_home {

static std::vector<SystemConfig>& configs() {
    static std::vector<SystemConfig> data = [] {
        const std::string now = TimeUtil::now();
        return std::vector<SystemConfig>{
            {1, 1, "smoke_threshold", "80", "ALARM", "Smoke alarm threshold", 1, now},
            {2, 1, "temperature_threshold", "38", "ALARM", "High temperature alarm threshold", 1, now},
            {3, 1, "communication_mode", "MOCK", "COMM", "Device communication mode", 1, now}
        };
    }();
    return data;
}

std::vector<SystemConfig> MockSystemConfigRepository::findByHome(long long homeId) {
    std::vector<SystemConfig> result;
    for (const auto& config : configs()) {
        if (config.homeId == homeId) result.push_back(config);
    }
    return result;
}

std::optional<SystemConfig> MockSystemConfigRepository::findByHomeAndKey(long long homeId, const std::string& key) {
    const auto it = std::find_if(configs().begin(), configs().end(), [&](const SystemConfig& c) {
        return c.homeId == homeId && c.configKey == key;
    });
    if (it == configs().end()) return std::nullopt;
    return *it;
}

SystemConfig MockSystemConfigRepository::upsert(const SystemConfig& config) {
    for (auto& item : configs()) {
        if (item.homeId == config.homeId && item.configKey == config.configKey) {
            item.configValue = config.configValue;
            item.description = config.description;
            item.updatedBy = config.updatedBy;
            item.updatedAt = TimeUtil::now();
            return item;
        }
    }
    SystemConfig copy = config;
    copy.configId = static_cast<long long>(configs().size()) + 1;
    configs().push_back(copy);
    return copy;
}

} // namespace smart_home

