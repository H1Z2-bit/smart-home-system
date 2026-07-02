#include "controllers/UserController.h"
#include "services/AuthService.h"
#include "utils/JwtUtil.h"
#include "utils/Validator.h"

namespace smart_home {

static std::string tokenFrom(const HttpRequest& request) {
    const auto it = request.headers.find("authorization");
    return it == request.headers.end() ? "" : JwtUtil::extractBearerToken(it->second);
}

HttpResponse UserController::profile(const HttpRequest& request) {
    return {200, AuthService().profile(tokenFrom(request))};
}

HttpResponse UserController::changePassword(const HttpRequest& request) {
    return {200, AuthService().changePassword(
        tokenFrom(request),
        Validator::getString(request.body, "oldPassword").value_or(""),
        Validator::getString(request.body, "newPassword").value_or(""))};
}

} // namespace smart_home

