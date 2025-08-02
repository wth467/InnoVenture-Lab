# SM4优化实现与GCM模式

## 项目概述
本项目提供了SM4加密算法的多种优化实现，包括：
- 基础C语言实现
- T-table优化
- AES-NI指令集优化
- AVX-512 + GFNI高级优化
- SM4-GCM认证加密模式

## 构建说明

### 依赖
- CMake 3.15+
- GCC 10+ 或 Clang 12+（支持AVX-512和GFNI）
- Windows用户需使用WSL2或MSYS2环境

### 构建步骤
```bash
# 克隆仓库
git clone https://github.com/your_username/SM4_Optimized.git
cd SM4_Optimized

# 创建构建目录
mkdir build
cd build

# 配置和构建
cmake -DCMAKE_BUILD_TYPE=Release ..
make -j8

# 运行测试
./tests/test_sm4
./tests/test_gcm

# 性能测试
./benchmarks/perf_test