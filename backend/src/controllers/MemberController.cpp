#include "controllers/MemberController.h"
#include "services/MemberService.h"
#include "utils/JwtUtil.h"
#include "utils/Validator.h"

namespace smart_home {

static std::string memberTokenFrom(const HttpRequest& request) {
    const auto it = request.headers.find("authorization");
    return it == request.headers.end() ? "" : JwtUtil::extractBearerToken(it->second);
}

HttpResponse MemberController::invite(const HttpRequest& request, long long homeId) {
    return {200, MemberService().invite(
        memberTokenFrom(request), homeId,
        Validator::getString(request.body, "phone").value_or(""),
        Validator::getString(request.body, "role").value_or("MEMBER"),
        Validator::getString(request.body, "validTo").value_or(""))};
}

HttpResponse MemberController::apply(const HttpRequest& request, long long homeId) {
    return {200, MemberService().apply(
        memberTokenFrom(request), homeId,
        Validator::getString(request.body, "applyReason").value_or(""))};
}

HttpResponse MemberController::approve(const HttpRequest& request, long long homeId, long long memberId) {
    return {200, MemberService().approve(
        memberTokenFrom(request), homeId, memberId,
        Validator::getBool(request.body, "approved", false),
        Validator::getString(request.body, "role").value_or("MEMBER"))};
}

HttpResponse MemberController::listMembers(const HttpRequest& request, long long homeId) {
    return {200, MemberService().listMembers(memberTokenFrom(request), homeId)};
}

HttpResponse MemberController::updatePermission(const HttpRequest& request, long long homeId, long long memberId) {
    return {200, MemberService().updatePermission(
        memberTokenFrom(request), homeId, memberId,
        Validator::getString(request.body, "role").value_or(""),
        Validator::getString(request.body, "permissionScope").value_or(""),
        Validator::getString(request.body, "validTo").value_or(""))};
}

HttpResponse MemberController::removeMember(const HttpRequest& request, long long homeId, long long memberId) {
    return {200, MemberService().removeMember(memberTokenFrom(request), homeId, memberId)};
}

} // namespace smart_home

