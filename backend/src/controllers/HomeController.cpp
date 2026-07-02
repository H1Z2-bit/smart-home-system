#include "controllers/HomeController.h"
#include "services/HomeService.h"
#include "utils/JwtUtil.h"
#include "utils/Validator.h"

namespace smart_home {

static std::string homeTokenFrom(const HttpRequest& request) {
    const auto it = request.headers.find("authorization");
    return it == request.headers.end() ? "" : JwtUtil::extractBearerToken(it->second);
}

HttpResponse HomeController::createHome(const HttpRequest& request) {
    return {200, HomeService().createHome(
        homeTokenFrom(request),
        Validator::getString(request.body, "homeName").value_or(""),
        Validator::getString(request.body, "address").value_or(""))};
}

HttpResponse HomeController::listHomes(const HttpRequest& request) {
    return {200, HomeService().listHomes(homeTokenFrom(request))};
}

HttpResponse HomeController::getHome(const HttpRequest& request, long long homeId) {
    return {200, HomeService().getHome(homeTokenFrom(request), homeId)};
}

HttpResponse HomeController::updateHome(const HttpRequest& request, long long homeId) {
    return {200, HomeService().updateHome(
        homeTokenFrom(request), homeId,
        Validator::getString(request.body, "homeName").value_or(""),
        Validator::getString(request.body, "address").value_or(""))};
}

HttpResponse HomeController::deleteHome(const HttpRequest& request, long long homeId) {
    return {200, HomeService().deleteHome(homeTokenFrom(request), homeId)};
}

} // namespace smart_home

