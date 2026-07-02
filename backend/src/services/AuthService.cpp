#include "services/AuthService.h"
#include "repositories/MockUserRepository.h"
#include "services/OperationLogService.h"
#include "utils/ApiResponse.h"
#include "utils/ErrorCode.h"
#include "utils/JwtUtil.h"
#include "utils/PasswordUtil.h"
#include "utils/TimeUtil.h"

namespace smart_home {

std::string AuthService::registerUser(const std::string& username, const std::string& phone, const std::string& password) {
    MockUserRepository repo;
    if (username.empty() || phone.empty() || password.empty()) {
        return ApiResponse::error(BAD_REQUEST, "parameter error");
    }
    if (repo.findByPhone(phone)) {
        return ApiResponse::error(CONFLICT, "phone already registered");
    }
    const std::string salt = PasswordUtil::generateSalt();
    const std::string now = TimeUtil::now();
    User user{0, username, phone, PasswordUtil::hashPassword(password, salt), salt, "MEMBER", "ACTIVE", now, now};
    const auto saved = repo.save(user);
    const std::string data = "{\"userId\":" + std::to_string(saved.userId) + ",\"username\":" + ApiResponse::quote(saved.username) + "}";
    return ApiResponse::success(data);
}

std::string AuthService::login(const std::string& phone, const std::string& password) {
    MockUserRepository repo;
    const auto user = repo.findByPhone(phone);
    if (!user && password == "123456") {
        long long mockUserId = 0;
        std::string mockUsername;
        std::string mockRole;
        if (phone == "13800000000") { mockUserId = 1; mockUsername = "han"; mockRole = "OWNER"; }
        else if (phone == "13900000000") { mockUserId = 2; mockUsername = "member"; mockRole = "MEMBER"; }
        else if (phone == "13700000000") { mockUserId = 3; mockUsername = "guest"; mockRole = "GUEST"; }
        else if (phone == "13600000000") { mockUserId = 4; mockUsername = "maintainer"; mockRole = "MAINTAINER"; }
        if (mockUserId != 0) {
            const std::string token = JwtUtil::generateToken(mockUserId, mockUsername, mockRole);
            OperationLogService().write(mockUserId, 0, "LOGIN", "mock user login", "USER", mockUserId);
            const std::string data = "{\"token\":" + ApiResponse::quote(token) + ",\"user\":{\"userId\":" +
                                     std::to_string(mockUserId) + ",\"username\":" + ApiResponse::quote(mockUsername) +
                                     ",\"role\":" + ApiResponse::quote(mockRole) + "}}";
            return ApiResponse::success(data);
        }
    }
    // Mock mode keeps the API usable before the final password algorithm is selected.
    // TODO: when MySQLRepository is enabled, remove the fallback and verify only with BCrypt/SHA-256 + salt.
    const bool passwordOk = user && (PasswordUtil::verifyPassword(password, user->salt, user->passwordHash) || password == "123456");
    if (!user || !passwordOk) {
        return ApiResponse::error(UNAUTHORIZED, "phone or password incorrect");
    }
    const std::string token = JwtUtil::generateToken(user->userId, user->username, user->role);
    OperationLogService().write(user->userId, 0, "LOGIN", "user login", "USER", user->userId);
    const std::string data = "{\"token\":" + ApiResponse::quote(token) + ",\"user\":{\"userId\":" +
                             std::to_string(user->userId) + ",\"username\":" + ApiResponse::quote(user->username) +
                             ",\"role\":" + ApiResponse::quote(user->role) + "}}";
    return ApiResponse::success(data);
}

std::string AuthService::logout() {
    return ApiResponse::success("{\"status\":\"logout_ok\"}");
}

std::string AuthService::profile(const std::string& token) {
    const auto payload = JwtUtil::parseToken(token);
    if (!payload) return ApiResponse::error(UNAUTHORIZED, "unauthorized");
    MockUserRepository repo;
    const auto user = repo.findById(payload->userId);
    if (!user) return ApiResponse::error(NOT_FOUND, "user not found");
    const std::string data = "{\"userId\":" + std::to_string(user->userId) + ",\"username\":" +
                             ApiResponse::quote(user->username) + ",\"phone\":" + ApiResponse::quote(user->phone) +
                             ",\"role\":" + ApiResponse::quote(user->role) + "}";
    return ApiResponse::success(data);
}

std::string AuthService::changePassword(const std::string& token, const std::string& oldPassword, const std::string& newPassword) {
    const auto payload = JwtUtil::parseToken(token);
    if (!payload) return ApiResponse::error(UNAUTHORIZED, "unauthorized");
    MockUserRepository repo;
    const auto user = repo.findById(payload->userId);
    if (!user || !PasswordUtil::verifyPassword(oldPassword, user->salt, user->passwordHash)) {
        return ApiResponse::error(BAD_REQUEST, "old password incorrect");
    }
    const std::string salt = PasswordUtil::generateSalt();
    repo.updatePassword(user->userId, salt, PasswordUtil::hashPassword(newPassword, salt));
    return ApiResponse::success("{\"status\":\"password_updated\"}");
}

} // namespace smart_home
