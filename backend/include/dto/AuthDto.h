#pragma once

#include <string>

namespace smart_home {

struct RegisterRequest {
    std::string username;
    std::string phone;
    std::string password;
};

struct LoginRequest {
    std::string phone;
    std::string password;
};

} // namespace smart_home

