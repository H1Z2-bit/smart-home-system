#include "controllers/AuthController.h"
#include "services/AuthService.h"
#include "utils/Validator.h"

namespace smart_home {

HttpResponse AuthController::registerUser(const HttpRequest& request) {
    return {200, AuthService().registerUser(
        Validator::getString(request.body, "username").value_or(""),
        Validator::getString(request.body, "phone").value_or(""),
        Validator::getString(request.body, "password").value_or(""))};
}

HttpResponse AuthController::login(const HttpRequest& request) {
    return {200, AuthService().login(
        Validator::getString(request.body, "phone").value_or(""),
        Validator::getString(request.body, "password").value_or(""))};
}

HttpResponse AuthController::logout(const HttpRequest&) {
    return {200, AuthService().logout()};
}

} // namespace smart_home
