#pragma once

#include "models/User.h"
#include <optional>
#include <vector>

namespace smart_home {

class UserRepository {
public:
    virtual ~UserRepository() = default;
    virtual std::optional<User> findById(long long userId) = 0;
    virtual std::optional<User> findByPhone(const std::string& phone) = 0;
    virtual User save(const User& user) = 0;
    virtual bool updatePassword(long long userId, const std::string& salt, const std::string& passwordHash) = 0;
    virtual std::vector<User> findAll() = 0;
};

} // namespace smart_home

