#pragma once

#include <string>

namespace smart_home {

struct SystemConfig {
    long long configId = 0;
    long long homeId = 0;
    std::string configKey;
    std::string configValue;
    std::string configType;
    std::string description;
    long long updatedBy = 0;
    std::string updatedAt;
};

} // namespace smart_home

