#pragma once

#include "utils/HttpTypes.h"

namespace smart_home {

class MemberController {
public:
    HttpResponse invite(const HttpRequest& request, long long homeId);
    HttpResponse apply(const HttpRequest& request, long long homeId);
    HttpResponse approve(const HttpRequest& request, long long homeId, long long memberId);
    HttpResponse listMembers(const HttpRequest& request, long long homeId);
    HttpResponse updatePermission(const HttpRequest& request, long long homeId, long long memberId);
    HttpResponse removeMember(const HttpRequest& request, long long homeId, long long memberId);
};

} // namespace smart_home

