#pragma once

#include <sstream>
#include <string>

namespace smart_home {

class ApiResponse {
public:
    static std::string success(const std::string& dataJson = "{}");
    static std::string error(int code, const std::string& message);
    static std::string quote(const std::string& value);
};

} // namespace smart_home

