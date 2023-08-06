// https://github.com/Mrs4s/MiraiGo/blob/master/binary/tea.go

#include <stdlib.h>
#include <string.h>

#ifdef _WIN32

#include "Windows.h"
#define __builtin_bswap64 _byteswap_uint64
#elif !__APPLE__

#include <endian.h>

#else
#include <machine/endian.h>
#endif

#include "simplecrypto.h"

const static uint32_t qqsumtable[0x10] = {
        0x9e3779b9,
        0x3c6ef372,
        0xdaa66d2b,
        0x78dde6e4,
        0x1715609d,
        0xb54cda56,
        0x5384540f,
        0xf1bbcdc8,
        0x8ff34781,
        0x2e2ac13a,
        0xcc623af3,
        0x6a99b4ac,
        0x08d12e65,
        0xa708a81e,
        0x454021d7,
        0xe3779b90,
};

int64_t tea_encrypt_qq(const uint32_t t[4], const uint8_t *src, int64_t src_len, uint8_t *out, int64_t out_len)
{
//    int64_t lens = src->len;
    int64_t fill = 10 - (src_len + 1) % 8;
    int64_t dstlen = fill + src_len + 7;
//    uint8_t *dstdat = (uint8_t *) malloc(dstlen);
    if (dstlen > out_len)
    {
        return -1;
    }
    ((uint32_t *) out)[0] = rand();
    ((uint32_t *) out)[1] = rand();
    ((uint32_t *) out)[2] = rand();
    out[0] = (fill - 3) | 0xF8; // 存储pad长度
    memcpy(out + fill, src, src_len);

    uint64_t iv1 = 0, iv2 = 0, holder;
    for (int64_t i = 0; i < dstlen / 8; i++)
    {
#ifdef WORDS_BIGENDIAN
        uint64_t block = ((uint64_t*)dstdat)[i];
#else
        uint64_t block = __builtin_bswap64(((uint64_t *) out)[i]);
#endif
        holder = block ^ iv1;

        iv1 = holder;
        uint32_t v1 = holder;
        iv1 >>= 32;
        uint32_t v0 = iv1;
        for (int i = 0; i < 0x10; i++)
        {
            v0 += (v1 + qqsumtable[i]) ^ ((v1 << 4) + t[0]) ^ ((v1 >> 5) + t[1]);
            v1 += (v0 + qqsumtable[i]) ^ ((v0 << 4) + t[2]) ^ ((v0 >> 5) + t[3]);
        }
        iv1 = ((uint64_t) v0 << 32) | (uint64_t) v1;

        iv1 = iv1 ^ iv2;
        iv2 = holder;
#ifdef WORDS_BIGENDIAN
        ((uint64_t*)dstdat)[i] = iv1;
#else
        ((uint64_t *) out)[i] = __builtin_bswap64(iv1);
#endif
    }

//    TEADAT *dst = (TEADAT *) malloc(sizeof(TEADAT));
    return dstlen;
//    dst->len = dstlen;
//    dst->data = out;
//    dst->ptr = out;
//    return dst;
}

int64_t
tea_encrypt(const uint32_t t[4], const uint32_t sumtable[0x10], const uint8_t *src, int64_t src_len, uint8_t *out,
            int64_t out_len)
{
//    int64_t lens = src->len;
    int64_t fill = 10 - (src_len + 1) % 8;
    int64_t dstlen = fill + src_len + 7;
    if (dstlen > out_len)
    {
        return -1;
    }
//    uint8_t *dstdat = (uint8_t *) malloc(dstlen);
    ((uint32_t *) out)[0] = rand();
    ((uint32_t *) out)[1] = rand();
    ((uint32_t *) out)[2] = rand();
    out[0] = (fill - 3) | 0xF8; // 存储pad长度
    memcpy(out + fill, src, src_len);

    uint64_t iv1 = 0, iv2 = 0, holder;
    for (int64_t i = 0; i < dstlen / 8; i++)
    {
#ifdef WORDS_BIGENDIAN
        uint64_t block = ((uint64_t*)dstdat)[i];
#else
        uint64_t block = __builtin_bswap64(((uint64_t *) out)[i]);
#endif
        holder = block ^ iv1;

        iv1 = holder;
        uint32_t v1 = holder;
        iv1 >>= 32;
        uint32_t v0 = iv1;
        for (int i = 0; i < 0x10; i++)
        {
            v0 += (v1 + sumtable[i]) ^ ((v1 << 4) + t[0]) ^ ((v1 >> 5) + t[1]);
            v1 += (v0 + sumtable[i]) ^ ((v0 << 4) + t[2]) ^ ((v0 >> 5) + t[3]);
        }
        iv1 = ((uint64_t) v0 << 32) | (uint64_t) v1;

        iv1 = iv1 ^ iv2;
        iv2 = holder;
#ifdef WORDS_BIGENDIAN
        ((uint64_t*)dstdat)[i] = iv1;
#else
        ((uint64_t *) out)[i] = __builtin_bswap64(iv1);
#endif
    }

//    TEADAT *dst = (TEADAT *) malloc(sizeof(TEADAT));
//    dst->len = dstlen;
//    dst->data = out;
//    dst->ptr = out;
    return dstlen;
}

int64_t
tea_encrypt_native_endian(const uint32_t t[4], const uint32_t sumtable[0x10], const uint8_t *src, int64_t src_len,
                          uint8_t *out, int64_t out_len)
{
//    int64_t lens = src->len;
    int64_t fill = 10 - (src_len + 1) % 8;
    int64_t dstlen = fill + src_len + 7;
    if (dstlen > out_len)
    {
        return -1;
    }
//    uint8_t *dstdat = (uint8_t *) malloc(dstlen);
    ((uint32_t *) out)[0] = rand();
    ((uint32_t *) out)[1] = rand();
    ((uint32_t *) out)[2] = rand();
    out[0] = (fill - 3) | 0xF8; // 存储pad长度
    memcpy(out + fill, src, src_len);

    uint64_t iv1 = 0, iv2 = 0, holder;
    for (int64_t i = 0; i < dstlen / 8; i++)
    {
        uint64_t block = ((uint64_t *) out)[i];
        holder = block ^ iv1;

        iv1 = holder;
        uint32_t v1 = holder;
        iv1 >>= 32;
        uint32_t v0 = iv1;
        for (int i = 0; i < 0x10; i++)
        {
            v0 += (v1 + sumtable[i]) ^ ((v1 << 4) + t[0]) ^ ((v1 >> 5) + t[1]);
            v1 += (v0 + sumtable[i]) ^ ((v0 << 4) + t[2]) ^ ((v0 >> 5) + t[3]);
        }
        iv1 = ((uint64_t) v0 << 32) | (uint64_t) v1;

        iv1 = iv1 ^ iv2;
        iv2 = holder;
        ((uint64_t *) out)[i] = iv1;
    }

//    TEADAT *dst = (TEADAT *) malloc(sizeof(TEADAT));
//    dst->len = dstlen;
//    dst->data = out;
//    dst->ptr = out;
    return dstlen;
}

int64_t tea_decrypt_qq(const uint32_t t[4], const uint8_t *src, int64_t src_len, uint8_t *out, int64_t out_len)
{
    if (src_len < 16 || (src_len) % 8 != 0)
    {
        return -1;
    }
    if (src_len > out_len)
    {
        return -1;
    }
//    uint8_t *dstdat = (uint8_t *) malloc(src_len);

    uint64_t iv1, iv2 = 0, holder = 0;
    for (int64_t i = 0; i < src_len / 8; i++)
    {
#ifdef WORDS_BIGENDIAN
        iv1 = ((uint64_t*)(src->data))[i];
#else
        iv1 = __builtin_bswap64(((uint64_t *) (src))[i]);
#endif

        iv2 ^= iv1;

        uint32_t v1 = iv2;
        iv2 >>= 32;
        uint32_t v0 = iv2;
        for (int i = 0x0f; i >= 0; i--)
        {
            v1 -= (v0 + qqsumtable[i]) ^ ((v0 << 4) + t[2]) ^ ((v0 >> 5) + t[3]);
            v0 -= (v1 + qqsumtable[i]) ^ ((v1 << 4) + t[0]) ^ ((v1 >> 5) + t[1]);
        }
        iv2 = ((uint64_t) v0 << 32) | (uint64_t) v1;

#ifdef WORDS_BIGENDIAN
        ((uint64_t*)dstdat)[i] = iv2^holder;
#else
        ((uint64_t *) out)[i] = __builtin_bswap64(iv2 ^ holder);
#endif

        holder = iv1;
    }

//    TEADAT *dst = (TEADAT *) malloc(sizeof(TEADAT));
    int start = (out[0] & 7) + 3;
    int64_t buffer_updated = src_len - 7 - start;
//    dst->len = src_len - 7 - start;
//    dst->data = out + start;
    memmove(out, out + start, (size_t) buffer_updated);
//    dst->ptr = out;
    return buffer_updated;
}

int64_t
tea_decrypt(const uint32_t t[4], const uint32_t sumtable[0x10], const uint8_t *src, int64_t src_len, uint8_t *out,
            int64_t out_len)
{
    if (src_len < 16 || (src_len) % 8 != 0)
    {
        return -1;
    }
    if (src_len > out_len)
    {
        return -1;
    }
//    uint8_t *dstdat = (uint8_t *) malloc(src->len);

    uint64_t iv1, iv2 = 0, holder = 0;
    for (int64_t i = 0; i < src_len / 8; i++)
    {
#ifdef WORDS_BIGENDIAN
        iv1 = ((uint64_t*)(src->data))[i];
#else
        iv1 = __builtin_bswap64(((uint64_t *) (src))[i]);
#endif

        iv2 ^= iv1;

        uint32_t v1 = iv2;
        iv2 >>= 32;
        uint32_t v0 = iv2;
        for (int i = 0x0f; i >= 0; i--)
        {
            v1 -= (v0 + sumtable[i]) ^ ((v0 << 4) + t[2]) ^ ((v0 >> 5) + t[3]);
            v0 -= (v1 + sumtable[i]) ^ ((v1 << 4) + t[0]) ^ ((v1 >> 5) + t[1]);
        }
        iv2 = ((uint64_t) v0 << 32) | (uint64_t) v1;

#ifdef WORDS_BIGENDIAN
        ((uint64_t*)dstdat)[i] = iv2^holder;
#else
        ((uint64_t *) out)[i] = __builtin_bswap64(iv2 ^ holder);
#endif

        holder = iv1;
    }

//    TEADAT *dst = (TEADAT *) malloc(sizeof(TEADAT));
    int start = (out[0] & 7) + 3;
    int64_t buffer_updated = src_len - 7 - start;
//    dst->len = src_len - 7 - start;
//    dst->data = out + start;
    memmove(out, out + start, (size_t) buffer_updated);
//    dst->ptr = out;
    return buffer_updated;
}

int64_t
tea_decrypt_native_endian(const uint32_t t[4], const uint32_t sumtable[0x10], const uint8_t *src, int64_t src_len,
                          uint8_t *out, int64_t out_len)
{
    if (src_len < 16 || (src_len) % 8 != 0)
    {
        return -1;
    }
    if (src_len > out_len)
    {
        return -1;
    }
//    uint8_t *dstdat = (uint8_t *) malloc(src_len);

    uint64_t iv1, iv2 = 0, holder = 0;
    for (int64_t i = 0; i < src_len / 8; i++)
    {
        iv1 = ((uint64_t *) (src))[i];

        iv2 ^= iv1;

        uint32_t v1 = iv2;
        iv2 >>= 32;
        uint32_t v0 = iv2;
        for (int i = 0x0f; i >= 0; i--)
        {
            v1 -= (v0 + sumtable[i]) ^ ((v0 << 4) + t[2]) ^ ((v0 >> 5) + t[3]);
            v0 -= (v1 + sumtable[i]) ^ ((v1 << 4) + t[0]) ^ ((v1 >> 5) + t[1]);
        }
        iv2 = ((uint64_t) v0 << 32) | (uint64_t) v1;

        ((uint64_t *) out)[i] = iv2 ^ holder;

        holder = iv1;
    }

//    TEADAT *dst = (TEADAT *) malloc(sizeof(TEADAT));
    int start = (out[0] & 7) + 3;
    int64_t buffer_updated = src_len - 7 - start;
//    dst->len = src_len - 7 - start;
//    dst->data =  out + start;
    memmove(out, out + start, (size_t) buffer_updated);
//    dst->ptr =  out;
    return buffer_updated;
}

#ifdef TEST_SIMPLE_CRYPTO
int main(int argc, char **argv)
{
//    TEADAT* td = (TEADAT*)malloc(sizeof(TEADAT));
    uint32_t *t = (uint32_t *) "32107654BA98FEDC";
    uint8_t *buff = malloc(1000);
    if (buff == NULL)
    {
        return -1;
    }
    if (argc != 3)
    {
        printf("usage: %s -[e|d] 'string'\n", argv[0]);
        return 1;
    }
    switch (argv[1][1])
    {
        case 'e':
        {
            //            td->data = (uint8_t *) (argv[2]);
            //            td->len = strlen(argv[2]);
            int64_t buffer_updated = tea_encrypt_qq(t, (const uint8_t *) argv[2], (int64_t) strlen(argv[2]),
                                                    (uint8_t *) buff, 1000);
            if (buffer_updated < 0)
            {
                fprintf(stderr, "sth wrong\n");
                return -1;
            }
            // display result
            for (int i = 0; i < buffer_updated; i++) printf("%02x", buff[i]);
            putchar('\n');
            free(buff);
            //            free(tde->ptr);
            //            free(tde);
            break;
        }
        case 'd':
        {
            //            td->len = strlen(argv[2]) / 2;
            // printf("decode input len: %lld\n", td->len);
            //            td->data = malloc(td->len);
            int64_t len = strlen(argv[2]) / 2;
            uint8_t *data = malloc(len);
            int i = len;
            while (i--)
            {
                uint8_t x;
                sscanf(argv[2] + i * 2, "%02x", &x);
                data[i] = x;
                argv[2][i * 2] = 0;
            }
            int64_t buffer_updated = tea_decrypt_qq(t, data, len, (uint8_t *) buff, 1000);
            if (buffer_updated < 0)
            {
                return -1;
            }

            if (buffer_updated)
            {
//                tdd->data[tdd->len] = 0;
                // printf("decode output len: %lld\n", tdd->len);
                for (int i = 0; i < buffer_updated; i++)
                {
                    putchar(buff[i]);
                }
                putchar('\n');
            }
            else
            {
                puts("decode error!");
            }
            free(buff);
            break;
        }
        default:
            break;
    }
    return 0;
}
#endif
