#pragma once

#include "models/Home.h"
#include <optional>
#include <vector>

namespace smart_home {

class HomeRepository {
public:
    virtual ~HomeRepository() = default;
    virtual Home save(const Home& home) = 0;
    virtual std::optional<Home> findById(long long homeId) = 0;
    virtual std::vector<Home> findByOwnerOrMember(long long userId) = 0;
    virtual bool update(const Home& home) = 0;
    virtual bool remove(long long homeId) = 0;
};

} // namespace smart_home

