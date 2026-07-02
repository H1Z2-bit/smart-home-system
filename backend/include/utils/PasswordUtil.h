#pragma once

#include <string>

namespace smart_home {

class PasswordUtil {
public:
    static std::string generateSalt();
    static std::string hashPassword(const std::string& password, const std::string& salt);
    static bool verifyPassword(const std::string& password, const std::string& salt, const std::string& passwordHash);
};

} // namespace smart_home

