#pragma once

#include <optional>
#include <string>
#include <vector>

namespace smart_home {

class Validator {
public:
    static std::optional<std::string> getString(const std::string& json, const std::string& key);
    static bool getBool(const std::string& json, const std::string& key, bool defaultValue = false);
    static std::vector<std::string> splitPath(const std::string& path);
    static bool notBlank(const std::optional<std::string>& value);
};

} // namespace smart_home

