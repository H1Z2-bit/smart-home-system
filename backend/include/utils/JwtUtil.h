#pragma once

#include <optional>
#include <string>

namespace smart_home {

struct JwtPayload {
    long long userId = 0;
    std::string username;
    std::string role;
};

class JwtUtil {
public:
    static std::string generateToken(long long userId, const std::string& username, const std::string& globalRole);
    static std::optional<JwtPayload> parseToken(const std::string& token);
    static bool validateToken(const std::string& token);
    static long long getUserIdFromToken(const std::string& token);
    static std::string extractBearerToken(const std::string& authorizationHeader);
};

} // namespace smart_home

