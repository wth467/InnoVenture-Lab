cmake_minimum_required(VERSION 3.15)
project(SM4_Optimized)

# 设置C标准
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

# 配置选项
option(ENABLE_AESNI "Enable AES-NI optimizations" ON)
option(ENABLE_AVX512 "Enable AVX-512 optimizations" OFF)  # Windows默认禁用AVX-512
option(BUILD_TESTS "Build test programs" ON)
option(BUILD_BENCHMARKS "Build benchmark programs" ON)

# 包含目录
include_directories(include)

# 主库
add_library(sm4_optimized STATIC
    src/sm4_basic.c
    src/sm4_ttable.c
    src/sm4_gcm.c
)

# Windows平台特殊设置
if(WIN32)
    # 设置Windows特定的编译器选项
    if(MSVC)
        # MSVC编译器设置
        target_compile_options(sm4_optimized PRIVATE /W4 /WX)
        add_compile_options(/arch:AVX)
    
        # 启用AES指令集
        if(ENABLE_AESNI)
            target_compile_options(sm4_optimized PRIVATE /arch:AVX2)
            target_compile_definitions(sm4_optimized PRIVATE -D__AES__)
            message(STATUS "AES-NI optimizations enabled for MSVC")
        endif()
        
        # AVX-512在Windows上支持有限，默认禁用
        if(ENABLE_AVX512)
            target_compile_options(sm4_optimized PRIVATE /arch:AVX512)
            message(STATUS "AVX-512 optimizations enabled for MSVC")
        endif()
    else()
        # MinGW编译器设置
        target_compile_options(sm4_optimized PRIVATE -Wall -Wextra)
        add_compile_options(-mssse3 -msse4.1 -mpclmul -maes)
        
        # 检查并启用 AVX 如果支持
        include(CheckCXXCompilerFlag)
        check_cxx_compiler_flag(-mavx COMPILER_SUPPORTS_AVX)
        if(COMPILER_SUPPORTS_AVX)
            add_compile_options(-mavx)
        endif()
        
        if(ENABLE_AESNI)
            target_compile_options(sm4_optimized PRIVATE -maes -msse4.1)
            target_compile_definitions(sm4_optimized PRIVATE -D__AES__)
            message(STATUS "AES-NI optimizations enabled for MinGW")
        endif()
        
        if(ENABLE_AVX512)
            target_compile_options(sm4_optimized PRIVATE -mavx512f -mgfni -mavx512vl)
            target_compile_definitions(sm4_optimized PRIVATE -D__AVX512F__ -D__GFNI__)
            message(STATUS "AVX-512 optimizations enabled for MinGW")
        endif()
    endif()
    
    # 添加Windows特定源文件
    target_sources(sm4_optimized PRIVATE src/sm4_win.c)
    
    # 设置Windows SDK版本
    set(CMAKE_SYSTEM_VERSION 10.0.18362.0 CACHE STRING "Windows SDK Version")
endif()



# 测试程序
if(BUILD_TESTS)
    # SM4核心算法测试
    add_executable(test_sm4 tests/test_sm4.c)
    target_link_libraries(test_sm4 sm4_optimized)
    
    # GCM模式测试
    add_executable(test_gcm tests/test_gcm.c)
    target_link_libraries(test_gcm sm4_optimized)
    
    # 添加测试目标
    add_test(NAME test_sm4 COMMAND test_sm4)
    add_test(NAME test_gcm COMMAND test_gcm)
endif()

# 性能测试
if(BUILD_BENCHMARKS)
    add_executable(benchmark benchmarks/perf_test.c)
    target_link_libraries(benchmark sm4_optimized)
endif()

# 安装目标
install(TARGETS sm4_optimized ARCHIVE DESTINATION lib)
install(DIRECTORY include/ DESTINATION include)

# 支持调试和发布模式
set(CMAKE_BUILD_TYPE Release CACHE STRING "Choose the type of build")
set_property(CACHE CMAKE_BUILD_TYPE PROPERTY STRINGS "Debug" "Release")

# 在Debug模式下启用更多检查
if(CMAKE_BUILD_TYPE STREQUAL "Debug")
    target_compile_definitions(sm4_optimized PRIVATE -DDEBUG=1)
    if(MSVC)
        target_compile_options(sm4_optimized PRIVATE /Zi /Od)
    else()
        target_compile_options(sm4_optimized PRIVATE -g -O0)
    endif()
else()
    if(MSVC)
        target_compile_options(sm4_optimized PRIVATE /O2)
    else()
        target_compile_options(sm4_optimized PRIVATE -O3)
    endif()
endif()