#pragma once

#include "utils/HttpTypes.h"

namespace smart_home {

class UserController {
public:
    HttpResponse profile(const HttpRequest& request);
    HttpResponse changePassword(const HttpRequest& request);
};

} // namespace smart_home

