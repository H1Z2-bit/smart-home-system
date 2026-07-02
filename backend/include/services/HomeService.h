#pragma once

#include <string>

namespace smart_home {

class HomeService {
public:
    std::string createHome(const std::string& token, const std::string& homeName, const std::string& address);
    std::string listHomes(const std::string& token);
    std::string getHome(const std::string& token, long long homeId);
    std::string updateHome(const std::string& token, long long homeId, const std::string& homeName, const std::string& address);
    std::string deleteHome(const std::string& token, long long homeId);
};

} // namespace smart_home

