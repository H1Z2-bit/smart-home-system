#include "utils/TimeUtil.h"
#include <chrono>
#include <ctime>
#include <iomanip>
#include <sstream>

namespace smart_home {

std::string TimeUtil::now() {
    const auto now = std::chrono::system_clock::now();
    const auto t = std::chrono::system_clock::to_time_t(now);
    std::tm tm{};
#ifdef _WIN32
    localtime_s(&tm, &t);
#else
    localtime_r(&t, &tm);
#endif
    std::ostringstream out;
    out << std::put_time(&tm, "%Y-%m-%d %H:%M:%S");
    return out.str();
}

} // namespace smart_home

