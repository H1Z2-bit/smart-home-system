#pragma once

#include <string>

namespace smart_home {

struct User {
    long long userId = 0;
    std::string username;
    std::string phone;
    std::string passwordHash;
    std::string salt;
    std::string role;
    std::string status;
    std::string createdAt;
    std::string updatedAt;
};

} // namespace smart_home

