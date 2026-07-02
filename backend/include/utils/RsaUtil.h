#pragma once

#include <string>

namespace smart_home {

class RsaUtil {
public:
    static std::string sign(const std::string& data);
    static bool verify(const std::string& data, const std::string& signature);
    static bool loadPrivateKey(const std::string& path);
    static bool loadPublicKey(const std::string& path);
};

} // namespace smart_home

