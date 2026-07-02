#pragma once

#include <string>

namespace smart_home {

struct Home {
    long long homeId = 0;
    std::string homeName;
    std::string address;
    long long ownerUserId = 0;
    std::string createdAt;
    std::string updatedAt;
};

} // namespace smart_home

