#pragma once

#include <string>

namespace smart_home {

class SystemConfigService {
public:
    std::string listConfig(const std::string& token, long long homeId);
    std::string updateConfig(const std::string& token, long long homeId, const std::string& key,
                             const std::string& value, const std::string& description);
};

} // namespace smart_home

