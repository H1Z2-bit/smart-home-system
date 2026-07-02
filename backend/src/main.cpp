#include "controllers/AuthController.h"
#include "controllers/HomeController.h"
#include "controllers/MemberController.h"
#include "controllers/SystemConfigController.h"
#include "controllers/UserController.h"
#include "utils/ApiResponse.h"
#include "utils/ErrorCode.h"
#include "utils/Validator.h"

#include <algorithm>
#include <cctype>
#include <iostream>
#include <map>
#include <sstream>
#include <string>

#ifdef _WIN32
#include <winsock2.h>
#include <ws2tcpip.h>
#else
#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <unistd.h>
#define closesocket close
#endif

using namespace smart_home;

static std::string lower(std::string value) {
    std::transform(value.begin(), value.end(), value.begin(), [](unsigned char c) { return static_cast<char>(std::tolower(c)); });
    return value;
}

static HttpRequest parseRequest(const std::string& raw) {
    HttpRequest request;
    const auto headerEnd = raw.find("\r\n\r\n");
    const std::string headerText = raw.substr(0, headerEnd);
    request.body = headerEnd == std::string::npos ? "" : raw.substr(headerEnd + 4);

    std::istringstream headers(headerText);
    std::string line;
    if (std::getline(headers, line)) {
        if (!line.empty() && line.back() == '\r') line.pop_back();
        std::istringstream first(line);
        first >> request.method >> request.path;
    }
    while (std::getline(headers, line)) {
        if (!line.empty() && line.back() == '\r') line.pop_back();
        const auto colon = line.find(':');
        if (colon != std::string::npos) {
            std::string key = lower(line.substr(0, colon));
            std::string value = line.substr(colon + 1);
            while (!value.empty() && value.front() == ' ') value.erase(value.begin());
            request.headers[key] = value;
        }
    }
    return request;
}

static long long toId(const std::string& text) {
    try {
        return std::stoll(text);
    } catch (...) {
        return 0;
    }
}

static HttpResponse route(const HttpRequest& request) {
    const auto parts = Validator::splitPath(request.path);
    AuthController auth;
    UserController user;
    HomeController home;
    MemberController member;
    SystemConfigController system;

    if (request.method == "OPTIONS") return {200, "{}"};
    if (request.method == "GET" && request.path == "/api/health") {
        return {200, ApiResponse::success("{\"status\":\"ok\"}")};
    }
    if (request.method == "POST" && request.path == "/api/auth/register") return auth.registerUser(request);
    if (request.method == "POST" && request.path == "/api/auth/login") return auth.login(request);
    if (request.method == "POST" && request.path == "/api/auth/logout") return auth.logout(request);
    if (request.method == "GET" && request.path == "/api/users/profile") return user.profile(request);
    if (request.method == "PUT" && request.path == "/api/users/password") return user.changePassword(request);
    if (request.method == "POST" && request.path == "/api/homes") return home.createHome(request);
    if (request.method == "GET" && request.path == "/api/homes") return home.listHomes(request);

    if (parts.size() >= 3 && parts[0] == "api" && parts[1] == "homes") {
        const long long homeId = toId(parts[2]);
        if (parts.size() == 3 && request.method == "GET") return home.getHome(request, homeId);
        if (parts.size() == 3 && request.method == "PUT") return home.updateHome(request, homeId);
        if (parts.size() == 3 && request.method == "DELETE") return home.deleteHome(request, homeId);
        if (parts.size() == 5 && parts[3] == "members" && parts[4] == "invite" && request.method == "POST") return member.invite(request, homeId);
        if (parts.size() == 5 && parts[3] == "members" && parts[4] == "apply" && request.method == "POST") return member.apply(request, homeId);
        if (parts.size() == 4 && parts[3] == "members" && request.method == "GET") return member.listMembers(request, homeId);
        if (parts.size() == 6 && parts[3] == "members" && parts[5] == "approve" && request.method == "POST") return member.approve(request, homeId, toId(parts[4]));
        if (parts.size() == 6 && parts[3] == "members" && parts[5] == "permission" && request.method == "PUT") return member.updatePermission(request, homeId, toId(parts[4]));
        if (parts.size() == 5 && parts[3] == "members" && request.method == "DELETE") return member.removeMember(request, homeId, toId(parts[4]));
        if (parts.size() == 5 && parts[3] == "system" && parts[4] == "config" && request.method == "GET") return system.listConfig(request, homeId);
        if (parts.size() == 5 && parts[3] == "system" && parts[4] == "config" && request.method == "PUT") return system.updateConfig(request, homeId);
        if (parts.size() == 4 && parts[3] == "logs" && request.method == "GET") return system.listLogs(request, homeId);
    }
    return {404, ApiResponse::error(NOT_FOUND, "route not found")};
}

static std::string httpText(const HttpResponse& response) {
    std::ostringstream out;
    out << "HTTP/1.1 " << response.status << " OK\r\n";
    out << "Content-Type: application/json; charset=utf-8\r\n";
    out << "Access-Control-Allow-Origin: *\r\n";
    out << "Access-Control-Allow-Headers: Content-Type, Authorization\r\n";
    out << "Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS\r\n";
    out << "Content-Length: " << response.body.size() << "\r\n\r\n";
    out << response.body;
    return out.str();
}

int main() {
#ifdef _WIN32
    WSADATA wsaData;
    if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0) {
        std::cerr << "WSAStartup failed\n";
        return 1;
    }
#endif
    const int serverFd = static_cast<int>(socket(AF_INET, SOCK_STREAM, 0));
    if (serverFd < 0) {
        std::cerr << "socket failed\n";
        return 1;
    }

    sockaddr_in address{};
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(8080);

    if (bind(serverFd, reinterpret_cast<sockaddr*>(&address), sizeof(address)) < 0) {
        std::cerr << "bind failed, port 8080 may be occupied\n";
        return 1;
    }
    if (listen(serverFd, 16) < 0) {
        std::cerr << "listen failed\n";
        return 1;
    }

    std::cout << "Smart home backend started at http://127.0.0.1:8080\n";
    std::cout << "Health check: GET http://127.0.0.1:8080/api/health\n";

    while (true) {
        sockaddr_in client{};
        socklen_t len = sizeof(client);
        const int clientFd = static_cast<int>(accept(serverFd, reinterpret_cast<sockaddr*>(&client), &len));
        if (clientFd < 0) continue;
        std::string raw;
        char buffer[4096] = {0};
        int received = static_cast<int>(recv(clientFd, buffer, sizeof(buffer), 0));
        if (received > 0) {
            raw.append(buffer, received);
            auto headerEnd = raw.find("\r\n\r\n");
            size_t contentLength = 0;
            if (headerEnd != std::string::npos) {
                const std::string headerText = raw.substr(0, headerEnd);
                const std::string key = "content-length:";
                const auto lowerHeaders = lower(headerText);
                const auto pos = lowerHeaders.find(key);
                if (pos != std::string::npos) {
                    const auto valueStart = pos + key.size();
                    const auto valueEnd = lowerHeaders.find("\r\n", valueStart);
                    const auto value = lowerHeaders.substr(valueStart, valueEnd == std::string::npos ? std::string::npos : valueEnd - valueStart);
                    try { contentLength = static_cast<size_t>(std::stoul(value)); } catch (...) { contentLength = 0; }
                }
            }
            while (headerEnd != std::string::npos && raw.size() < headerEnd + 4 + contentLength) {
                received = static_cast<int>(recv(clientFd, buffer, sizeof(buffer), 0));
                if (received <= 0) break;
                raw.append(buffer, received);
            }
            const auto request = parseRequest(raw);
            const auto response = httpText(route(request));
            send(clientFd, response.c_str(), static_cast<int>(response.size()), 0);
        }
        closesocket(clientFd);
    }

#ifdef _WIN32
    WSACleanup();
#endif
    return 0;
}
