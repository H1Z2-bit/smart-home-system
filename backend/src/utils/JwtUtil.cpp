#include "utils/JwtUtil.h"
#include "utils/RsaUtil.h"
#include <sstream>
#include <vector>

namespace smart_home {

static std::vector<std::string> splitToken(const std::string& token) {
    std::vector<std::string> parts;
    std::stringstream ss(token);
    std::string item;
    while (std::getline(ss, item, '.')) {
        parts.push_back(item);
    }
    return parts;
}

std::string JwtUtil::generateToken(long long userId, const std::string& username, const std::string& globalRole) {
    const std::string payload = std::to_string(userId) + ":" + username + ":" + globalRole;
    const std::string signature = RsaUtil::sign(payload);
    return "mockjwt." + payload + "." + signature;
}

std::optional<JwtPayload> JwtUtil::parseToken(const std::string& token) {
    const auto parts = splitToken(token);
    if (parts.size() != 3 || parts[0] != "mockjwt") {
        return std::nullopt;
    }
    if (!RsaUtil::verify(parts[1], parts[2])) {
        return std::nullopt;
    }
    std::stringstream ss(parts[1]);
    std::string id, username, role;
    if (!std::getline(ss, id, ':') || !std::getline(ss, username, ':') || !std::getline(ss, role, ':')) {
        return std::nullopt;
    }
    JwtPayload payload;
    payload.userId = std::stoll(id);
    payload.username = username;
    payload.role = role;
    return payload;
}

bool JwtUtil::validateToken(const std::string& token) {
    return parseToken(token).has_value();
}

long long JwtUtil::getUserIdFromToken(const std::string& token) {
    const auto payload = parseToken(token);
    return payload ? payload->userId : 0;
}

std::string JwtUtil::extractBearerToken(const std::string& authorizationHeader) {
    const std::string prefix = "Bearer ";
    if (authorizationHeader.rfind(prefix, 0) == 0) {
        return authorizationHeader.substr(prefix.size());
    }
    return authorizationHeader;
}

} // namespace smart_home

