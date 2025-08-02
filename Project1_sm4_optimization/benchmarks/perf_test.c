#include "sm4.h"
#include "sm4_gcm.h"
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define BUFFER_SIZE (1 << 24) // 16MB

void performance_test() {
    uint8_t key[16] = {0};
    uint8_t iv[12] = {0};
    uint8_t *data = malloc(BUFFER_SIZE);
    uint8_t *out = malloc(BUFFER_SIZE);
    uint8_t tag[16];
    
    // 初始化数据
    for (size_t i = 0; i < BUFFER_SIZE; i++) {
        data[i] = rand() & 0xFF;
    }
    
    // SM4基础实现性能
    clock_t start = clock();
    for (size_t i = 0; i < BUFFER_SIZE; i += 16) {
        sm4_encrypt(key, data + i, out + i);
    }
    double basic_time = (double)(clock() - start) / CLOCKS_PER_SEC;
    
    // SM4-GCM性能
    start = clock();
    sm4_gcm_encrypt(key, iv, 12, NULL, 0, data, BUFFER_SIZE, out, tag, 16);
    double gcm_time = (double)(clock() - start) / CLOCKS_PER_SEC;
    
    printf("Performance Results:\n");
    printf("SM4 Basic: %.2f MB/s\n", BUFFER_SIZE / (basic_time * 1e6));
    printf("SM4-GCM: %.2f MB/s\n", BUFFER_SIZE / (gcm_time * 1e6));
    
    free(data);
    free(out);
}

int main() {
    performance_test();
    return 0;
}