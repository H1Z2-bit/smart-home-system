#pragma once

#include "models/HomeMember.h"
#include <optional>
#include <vector>

namespace smart_home {

class MemberRepository {
public:
    virtual ~MemberRepository() = default;
    virtual HomeMember save(const HomeMember& member) = 0;
    virtual std::optional<HomeMember> findById(long long memberId) = 0;
    virtual std::optional<HomeMember> findByHomeAndUser(long long homeId, long long userId) = 0;
    virtual std::vector<HomeMember> findByHome(long long homeId) = 0;
    virtual bool update(const HomeMember& member) = 0;
    virtual bool remove(long long memberId) = 0;
};

} // namespace smart_home

