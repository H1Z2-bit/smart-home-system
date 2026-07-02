#include "utils/ApiResponse.h"

namespace smart_home {

std::string ApiResponse::quote(const std::string& value) {
    std::ostringstream out;
    out << '"';
    for (char c : value) {
        switch (c) {
            case '\\': out << "\\\\"; break;
            case '"': out << "\\\""; break;
            case '\n': out << "\\n"; break;
            case '\r': out << "\\r"; break;
            case '\t': out << "\\t"; break;
            default: out << c; break;
        }
    }
    out << '"';
    return out.str();
}

std::string ApiResponse::success(const std::string& dataJson) {
    return "{\"code\":200,\"message\":\"success\",\"data\":" + dataJson + "}";
}

std::string ApiResponse::error(int code, const std::string& message) {
    return "{\"code\":" + std::to_string(code) + ",\"message\":" + quote(message) + ",\"data\":null}";
}

} // namespace smart_home

