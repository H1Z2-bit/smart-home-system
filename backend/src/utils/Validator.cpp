#include "utils/Validator.h"
#include <sstream>

namespace smart_home {

std::optional<std::string> Validator::getString(const std::string& json, const std::string& key) {
    const std::string needle = "\"" + key + "\"";
    const auto keyPos = json.find(needle);
    if (keyPos == std::string::npos) return std::nullopt;
    const auto colon = json.find(':', keyPos + needle.size());
    if (colon == std::string::npos) return std::nullopt;
    const auto firstQuote = json.find('"', colon + 1);
    if (firstQuote == std::string::npos) return std::nullopt;
    const auto secondQuote = json.find('"', firstQuote + 1);
    if (secondQuote == std::string::npos) return std::nullopt;
    return json.substr(firstQuote + 1, secondQuote - firstQuote - 1);
}

bool Validator::getBool(const std::string& json, const std::string& key, bool defaultValue) {
    const std::string needle = "\"" + key + "\"";
    const auto keyPos = json.find(needle);
    if (keyPos == std::string::npos) return defaultValue;
    const auto colon = json.find(':', keyPos + needle.size());
    if (colon == std::string::npos) return defaultValue;
    const auto valueStart = json.find_first_not_of(" \t\r\n", colon + 1);
    if (valueStart == std::string::npos) return defaultValue;
    return json.rfind("true", valueStart) == valueStart;
}

std::vector<std::string> Validator::splitPath(const std::string& path) {
    std::vector<std::string> parts;
    std::stringstream ss(path);
    std::string item;
    while (std::getline(ss, item, '/')) {
        if (!item.empty()) parts.push_back(item);
    }
    return parts;
}

bool Validator::notBlank(const std::optional<std::string>& value) {
    return value.has_value() && !value->empty();
}

} // namespace smart_home

