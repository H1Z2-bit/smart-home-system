#pragma once

#include "repositories/UserRepository.h"

namespace smart_home {

class MockUserRepository : public UserRepository {
public:
    std::optional<User> findById(long long userId) override;
    std::optional<User> findByPhone(const std::string& phone) override;
    User save(const User& user) override;
    bool updatePassword(long long userId, const std::string& salt, const std::string& passwordHash) override;
    std::vector<User> findAll() override;
};

} // namespace smart_home

