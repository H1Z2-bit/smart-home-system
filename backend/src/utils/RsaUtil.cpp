#include "utils/RsaUtil.h"
#include <functional>

namespace smart_home {

std::string RsaUtil::sign(const std::string& data) {
    // TODO: replace mock signature with real RSA RS256 implementation.
    return std::to_string(std::hash<std::string>{}("mock-rsa-private-key:" + data));
}

bool RsaUtil::verify(const std::string& data, const std::string& signature) {
    // TODO: replace mock verification with real RSA RS256 implementation.
    return sign(data) == signature;
}

bool RsaUtil::loadPrivateKey(const std::string&) {
    return true;
}

bool RsaUtil::loadPublicKey(const std::string&) {
    return true;
}

} // namespace smart_home

