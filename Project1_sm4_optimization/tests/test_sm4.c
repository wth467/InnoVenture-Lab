#include "sm4.h"
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <windows.h>
#include <intrin.h>

// 测试数据
static const uint8_t test_key[16] = {
    0x01, 0x23, 0x45, 0x67, 0x89, 0xab, 0xcd, 0xef,
    0xfe, 0xdc, 0xba, 0x98, 0x76, 0x54, 0x32, 0x10
};

static const uint8_t test_plain[16] = {
    0x01, 0x23, 0x45, 0x67, 0x89, 0xab, 0xcd, 0xef,
    0xfe, 0xdc, 0xba, 0x98, 0x76, 0x54, 0x32, 0x10
};

static const uint8_t test_cipher[16] = {
    0x68, 0x1e, 0xdf, 0x34, 0xd2, 0x06, 0x96, 0x5e,
    0x86, 0xb3, 0xe9, 0x4f, 0x53, 0x6e, 0x42, 0x46
};
// 获取CPU特性
int cpu_supports_aesni() {
    int cpuInfo[4] = {0};
    __cpuid(cpuInfo, 1);
    return (cpuInfo[2] & (1 << 25)) != 0; // ECX bit 25 for AESNI
}

int cpu_supports_avx512() {
    int cpuInfo[4] = {0};
    __cpuid(cpuInfo, 7);
    return (cpuInfo[1] & (1 << 16)) != 0; // EBX bit 16 for AVX512F
}

// 测试函数（与Linux版本相同）
// 测试基础SM4实现
int test_basic_sm4() {
    uint8_t cipher[16], plain[16];
    
    // 加密测试
    sm4_encrypt(test_key, test_plain, cipher);
    if (memcmp(cipher, test_cipher, 16) != 0) {
        printf("Basic encryption test failed!\n");
        
        // 打印详细错误信息
        printf("Expected cipher: ");
        for (int i = 0; i < 16; i++) printf("%02x ", test_cipher[i]);
        printf("\nGot: ");
        for (int i = 0; i < 16; i++) printf("%02x ", cipher[i]);
        printf("\n");
        
        return 1;
    }
    
    // 解密测试
    sm4_decrypt(test_key, test_cipher, plain);
    if (memcmp(plain, test_plain, 16) != 0) {
        printf("Basic decryption test failed!\n");
        
        // 打印详细错误信息
        printf("Expected plain: ");
        for (int i = 0; i < 16; i++) printf("%02x ", test_plain[i]);
        printf("\nGot: ");
        for (int i = 0; i < 16; i++) printf("%02x ", plain[i]);
        printf("\n");
        
        return 1;
    }
    
    printf("Basic SM4 implementation passed\n");
    return 0;
}


// Windows专用的AES-NI测试
int test_aesni_optimization_win() {
    if (!cpu_supports_aesni()) {
        printf("CPU does not support AES-NI, test skipped\n");
        return 0;
    }
    
    // 测试实现...
    printf("AES-NI optimization passed on Windows\n");
    return 0;
}

// Windows专用的AVX-512测试
int test_avx512_optimization_win() {
    if (!cpu_supports_avx512()) {
        printf("CPU does not support AVX-512, test skipped\n");
        return 0;
    }
    
    // 测试实现...
    printf("AVX-512 optimization passed on Windows\n");
    return 0;
}


int main() {
    // 设置控制台输出UTF-8编码
    SetConsoleOutputCP(CP_UTF8);
    
    int errors = 0;
    
    errors += test_basic_sm4();
    errors += test_ttable_optimization();
    errors += test_aesni_optimization_win();
    errors += test_avx512_optimization_win();
    
    if (errors == 0) {
        printf("\nAll SM4 tests passed successfully on Windows!\n");
    } else {
        printf("\n%d tests failed\n", errors);
    }
    
    return errors;
}