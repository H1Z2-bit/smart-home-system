cmake_minimum_required(VERSION 3.16)
project(smart_home_backend LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

file(GLOB_RECURSE BACKEND_SOURCES CONFIGURE_DEPENDS
    "${CMAKE_CURRENT_SOURCE_DIR}/src/*.cpp"
)

add_executable(smart_home_backend ${BACKEND_SOURCES})
target_include_directories(smart_home_backend PRIVATE
    "${CMAKE_CURRENT_SOURCE_DIR}/include"
)

if (WIN32)
    target_link_libraries(smart_home_backend PRIVATE ws2_32)
endif()

