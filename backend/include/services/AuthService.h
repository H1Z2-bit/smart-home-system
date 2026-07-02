#pragma once

#include <string>

namespace smart_home {

class AuthService {
public:
    std::string registerUser(const std::string& username, const std::string& phone, const std::string& password);
    std::string login(const std::string& phone, const std::string& password);
    std::string logout();
    std::string profile(const std::string& token);
    std::string changePassword(const std::string& token, const std::string& oldPassword, const std::string& newPassword);
};

} // namespace smart_home

