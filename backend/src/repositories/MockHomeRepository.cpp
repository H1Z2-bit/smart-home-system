#include "repositories/MockHomeRepository.h"
#include "repositories/MockMemberRepository.h"
#include "utils/TimeUtil.h"
#include <algorithm>

namespace smart_home {

static std::vector<Home>& homes() {
    static std::vector<Home> data = [] {
        const std::string now = TimeUtil::now();
        return std::vector<Home>{{1, "Smart Home", "Beijing", 1, now, now}};
    }();
    return data;
}

Home MockHomeRepository::save(const Home& home) {
    Home copy = home;
    copy.homeId = static_cast<long long>(homes().size()) + 1;
    homes().push_back(copy);
    return copy;
}

std::optional<Home> MockHomeRepository::findById(long long homeId) {
    const auto it = std::find_if(homes().begin(), homes().end(), [&](const Home& h) { return h.homeId == homeId; });
    if (it == homes().end()) return std::nullopt;
    return *it;
}

std::vector<Home> MockHomeRepository::findByOwnerOrMember(long long userId) {
    MockMemberRepository memberRepo;
    std::vector<Home> result;
    for (const auto& home : homes()) {
        if (home.ownerUserId == userId || memberRepo.findByHomeAndUser(home.homeId, userId).has_value()) {
            result.push_back(home);
        }
    }
    return result;
}

bool MockHomeRepository::update(const Home& home) {
    for (auto& item : homes()) {
        if (item.homeId == home.homeId) {
            item.homeName = home.homeName;
            item.address = home.address;
            item.updatedAt = TimeUtil::now();
            return true;
        }
    }
    return false;
}

bool MockHomeRepository::remove(long long homeId) {
    const auto oldSize = homes().size();
    homes().erase(std::remove_if(homes().begin(), homes().end(), [&](const Home& h) { return h.homeId == homeId; }), homes().end());
    return homes().size() != oldSize;
}

} // namespace smart_home

