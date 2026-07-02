#include "utils/PasswordUtil.h"
#include <functional>

namespace smart_home {

std::string PasswordUtil::generateSalt() {
    return "mock_salt";
}

std::string PasswordUtil::hashPassword(const std::string& password, const std::string& salt) {
    // TODO: replace simple hash with BCrypt or SHA-256 + salt.
    return std::to_string(std::hash<std::string>{}(salt + ":" + password));
}

bool PasswordUtil::verifyPassword(const std::string& password, const std::string& salt, const std::string& passwordHash) {
    return hashPassword(password, salt) == passwordHash;
}

} // namespace smart_home

