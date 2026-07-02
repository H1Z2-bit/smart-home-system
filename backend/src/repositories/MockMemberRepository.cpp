#include "repositories/MockMemberRepository.h"
#include "utils/TimeUtil.h"
#include <algorithm>

namespace smart_home {

static std::vector<HomeMember>& members() {
    static std::vector<HomeMember> data = [] {
        const std::string now = TimeUtil::now();
        return std::vector<HomeMember>{
            {1, 1, 1, "OWNER", "ACTIVE", "ALL", now, "", now, now},
            {2, 1, 2, "MEMBER", "ACTIVE", "ALL", now, "", now, now},
            {3, 1, 3, "GUEST", "ACTIVE", "ROOM:1,DEVICE:2", now, "2026-07-10 23:59:59", now, now}
        };
    }();
    return data;
}

HomeMember MockMemberRepository::save(const HomeMember& member) {
    HomeMember copy = member;
    copy.memberId = static_cast<long long>(members().size()) + 1;
    members().push_back(copy);
    return copy;
}

std::optional<HomeMember> MockMemberRepository::findById(long long memberId) {
    const auto it = std::find_if(members().begin(), members().end(), [&](const HomeMember& m) { return m.memberId == memberId; });
    if (it == members().end()) return std::nullopt;
    return *it;
}

std::optional<HomeMember> MockMemberRepository::findByHomeAndUser(long long homeId, long long userId) {
    const auto it = std::find_if(members().begin(), members().end(), [&](const HomeMember& m) {
        return m.homeId == homeId && m.userId == userId && m.status != "REMOVED";
    });
    if (it == members().end()) return std::nullopt;
    return *it;
}

std::vector<HomeMember> MockMemberRepository::findByHome(long long homeId) {
    std::vector<HomeMember> result;
    for (const auto& member : members()) {
        if (member.homeId == homeId && member.status != "REMOVED") {
            result.push_back(member);
        }
    }
    return result;
}

bool MockMemberRepository::update(const HomeMember& member) {
    for (auto& item : members()) {
        if (item.memberId == member.memberId) {
            item = member;
            item.updatedAt = TimeUtil::now();
            return true;
        }
    }
    return false;
}

bool MockMemberRepository::remove(long long memberId) {
    for (auto& item : members()) {
        if (item.memberId == memberId) {
            item.status = "REMOVED";
            item.updatedAt = TimeUtil::now();
            return true;
        }
    }
    return false;
}

} // namespace smart_home

