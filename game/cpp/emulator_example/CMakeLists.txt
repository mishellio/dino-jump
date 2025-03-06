cmake_minimum_required(VERSION 3.10)

project(DinoJump VERSION 1.0)

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED True)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

include_directories(${PROJECT_SOURCE_DIR}/include)

file(GLOB SOURCES
    ${PROJECT_SOURCE_DIR}/src/*.cpp
)

add_executable(DinoJump ${SOURCES})

