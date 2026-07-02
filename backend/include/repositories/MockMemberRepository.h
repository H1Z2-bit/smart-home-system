#pragma once

#include "repositories/MemberRepository.h"

namespace smart_home {

class MockMemberRepository : public MemberRepository {
public:
    HomeMember save(const HomeMember& member) override;
    std::optional<HomeMember> findById(long long memberId) override;
    std::optional<HomeMember> findByHomeAndUser(long long homeId, long long userId) override;
    std::vector<HomeMember> findByHome(long long homeId) override;
    bool update(const HomeMember& member) override;
    bool remove(long long memberId) override;
};

} // namespace smart_home

