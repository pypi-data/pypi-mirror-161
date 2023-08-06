cmake_minimum_required(VERSION 3.3)
project(pycryptonight)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11 -maes -g -O0 ") # -fdeclspec
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -maes -g -O0  -DDUMP_JIT=1 -DDEBUG_JIT=1") # -DSTATIC_JIT=1

set(SOURCE_FILES
        aesb.c
        blake256.c
        CryptonightR_JIT.c
        CryptonightR_template.c
        groestl.c
        hash.c
        hash-extra-blake.c
        hash-extra-groestl.c
        hash-extra-jh.c
        hash-extra-skein.c
        jh.c
        keccak.c
        oaes_lib.c
        skein.c
        slow-hash.c
        main.c
        )

add_executable(pycryptonight ${SOURCE_FILES})