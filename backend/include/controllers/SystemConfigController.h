#pragma once

#include "utils/HttpTypes.h"

namespace smart_home {

class SystemConfigController {
public:
    HttpResponse listConfig(const HttpRequest& request, long long homeId);
    HttpResponse updateConfig(const HttpRequest& request, long long homeId);
    HttpResponse listLogs(const HttpRequest& request, long long homeId);
};

} // namespace smart_home

