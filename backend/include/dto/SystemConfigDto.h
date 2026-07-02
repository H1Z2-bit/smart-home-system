#pragma once

#include <string>

namespace smart_home {

struct SystemConfigRequest {
    std::string configKey;
    std::string configValue;
    std::string description;
};

} // namespace smart_home

