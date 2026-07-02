#pragma once

#include <map>
#include <string>

namespace smart_home {

struct HttpRequest {
    std::string method;
    std::string path;
    std::string body;
    std::map<std::string, std::string> headers;
};

struct HttpResponse {
    int status = 200;
    std::string body;
};

} // namespace smart_home

