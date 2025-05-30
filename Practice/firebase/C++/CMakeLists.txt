cmake_minimum_required(VERSION 3.10)
project(FirebaseCppDemo)

# Firebase C++ SDK 경로
set(FIREBASE_CPP_SDK_PATH "/path/to/firebase_cpp_sdk")

# include 경로
include_directories(${FIREBASE_CPP_SDK_PATH}/include)

# 링크할 라이브러리
set(FIREBASE_LIB_DIR ${FIREBASE_CPP_SDK_PATH}/lib)
link_directories(${FIREBASE_LIB_DIR})

add_executable(main main.cpp)

# Firebase Core, Auth, Firestore (원하는 모듈만 추가)
target_link_libraries(main
    firebase_app
    firebase_auth
    firebase_firestore
    # firebase_database  # Realtime DB 사용 시
)