#include "repositories/MockUserRepository.h"
#include "utils/PasswordUtil.h"
#include "utils/TimeUtil.h"
#include <algorithm>

namespace smart_home {

static std::vector<User>& users() {
    static std::vector<User> data = [] {
        const std::string salt = PasswordUtil::generateSalt();
        const std::string hash = PasswordUtil::hashPassword("123456", salt);
        const std::string now = TimeUtil::now();
        return std::vector<User>{
            {1, "han", "13800000000", hash, salt, "OWNER", "ACTIVE", now, now},
            {2, "member", "13900000000", hash, salt, "MEMBER", "ACTIVE", now, now},
            {3, "guest", "13700000000", hash, salt, "GUEST", "ACTIVE", now, now},
            {4, "maintainer", "13600000000", hash, salt, "MAINTAINER", "ACTIVE", now, now}
        };
    }();
    return data;
}

std::optional<User> MockUserRepository::findById(long long userId) {
    const auto it = std::find_if(users().begin(), users().end(), [&](const User& u) { return u.userId == userId; });
    if (it == users().end()) return std::nullopt;
    return *it;
}

std::optional<User> MockUserRepository::findByPhone(const std::string& phone) {
    const auto it = std::find_if(users().begin(), users().end(), [&](const User& u) { return u.phone == phone; });
    if (it == users().end()) return std::nullopt;
    return *it;
}

User MockUserRepository::save(const User& user) {
    User copy = user;
    copy.userId = static_cast<long long>(users().size()) + 1;
    users().push_back(copy);
    return copy;
}

bool MockUserRepository::updatePassword(long long userId, const std::string& salt, const std::string& passwordHash) {
    for (auto& user : users()) {
        if (user.userId == userId) {
            user.salt = salt;
            user.passwordHash = passwordHash;
            user.updatedAt = TimeUtil::now();
            return true;
        }
    }
    return false;
}

std::vector<User> MockUserRepository::findAll() {
    return users();
}

} // namespace smart_home

