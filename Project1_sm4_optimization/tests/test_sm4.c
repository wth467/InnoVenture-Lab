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





int main() {
    // 设置控制台输出UTF-8编码
    SetConsoleOutputCP(CP_UTF8);
    
    int errors = 0;
    
    errors += test_basic_sm4();

    
    if (errors == 0) {
        printf("\nAll SM4 tests passed successfully on Windows!\n");
    } else {
        printf("\n%d tests failed\n", errors);
    }
    
    return errors;
}