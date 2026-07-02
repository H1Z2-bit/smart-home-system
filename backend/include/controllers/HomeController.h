#pragma once

#include "utils/HttpTypes.h"

namespace smart_home {

class HomeController {
public:
    HttpResponse createHome(const HttpRequest& request);
    HttpResponse listHomes(const HttpRequest& request);
    HttpResponse getHome(const HttpRequest& request, long long homeId);
    HttpResponse updateHome(const HttpRequest& request, long long homeId);
    HttpResponse deleteHome(const HttpRequest& request, long long homeId);
};

} // namespace smart_home

