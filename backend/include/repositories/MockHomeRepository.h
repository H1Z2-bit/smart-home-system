#pragma once

#include "repositories/HomeRepository.h"

namespace smart_home {

class MockHomeRepository : public HomeRepository {
public:
    Home save(const Home& home) override;
    std::optional<Home> findById(long long homeId) override;
    std::vector<Home> findByOwnerOrMember(long long userId) override;
    bool update(const Home& home) override;
    bool remove(long long homeId) override;
};

} // namespace smart_home

