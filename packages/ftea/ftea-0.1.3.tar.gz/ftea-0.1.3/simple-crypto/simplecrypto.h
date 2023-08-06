#ifndef _SIMPLECRYPTO_H_
#define _SIMPLECRYPTO_H_
#include <stdio.h>
#include <stdint.h>

// ---------------MD5 area---------------

// return 128bit(16bytes) digest
uint8_t* md5(const uint8_t *data, size_t data_len, uint8_t digest[16]);

// ---------------MD5 area---------------


// ---------------TEA area---------------
int64_t tea_encrypt_qq(const uint32_t t[4], const uint8_t *src, int64_t src_len, uint8_t *out, int64_t out_len);
int64_t tea_encrypt(const uint32_t t[4], const uint32_t sumtable[0x10], const uint8_t *src, int64_t src_len, uint8_t *out,
                    int64_t out_len);
int64_t tea_encrypt_native_endian(const uint32_t t[4], const uint32_t sumtable[0x10], const uint8_t *src, int64_t src_len,
                          uint8_t *out, int64_t out_len);
int64_t tea_decrypt_qq(const uint32_t t[4], const uint8_t *src, int64_t src_len, uint8_t *out, int64_t out_len);
int64_t tea_decrypt(const uint32_t t[4], const uint32_t sumtable[0x10], const uint8_t *src, int64_t src_len, uint8_t *out,
            int64_t out_len);
int64_t tea_decrypt_native_endian(const uint32_t t[4], const uint32_t sumtable[0x10], const uint8_t *src, int64_t src_len,
                          uint8_t *out, int64_t out_len);

// ---------------TEA area---------------

#endif