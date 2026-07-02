#pragma once

#include "utils/HttpTypes.h"

namespace smart_home {

class AuthController {
public:
    HttpResponse registerUser(const HttpRequest& request);
    HttpResponse login(const HttpRequest& request);
    HttpResponse logout(const HttpRequest& request);
};

} // namespace smart_home

