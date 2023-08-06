#include "lua.h"
#include "lauxlib.h"

#include "simplecrypto.h"

#ifdef _WIN32
#define DLLEXPORT __declspec(dllexport)
#define swap_uint32 _byteswap_ulong
#elif
#define DLLEXPORT
#define swap_uint32 __builtin_bswap32
#endif /* _WIN32 */


int64_t encrypt_qq_len(int64_t src_len)
{
    int64_t fill = 10 - (src_len + 1) % 8;
    return fill + src_len + 7;
}


static int
lencrypt_qq(lua_State *L)
{
    if (lua_gettop(L) != 2)
    {
        luaL_error(L, "must be 2 args, key and data");
        return 0;
    }
    size_t key_len;
    const char *key = luaL_checklstring(L, 1, &key_len);
    luaL_argcheck(L, key_len == 16, 1, "key must be 16 bytes len!");
#ifdef WORDS_BIGENDIAN
    uint32_t *key_ = (uint32_t *)key;
#else
    uint32_t key_[4];
    key_[0] = swap_uint32(((uint32_t *) key)[0]);
    key_[1] = swap_uint32(((uint32_t *) key)[1]);
    key_[2] = swap_uint32(((uint32_t *) key)[2]);
    key_[3] = swap_uint32(((uint32_t *) key)[3]);
#endif
    size_t src_len;
    const char *src = luaL_checklstring(L, 2, &src_len);
    int64_t out_len = encrypt_qq_len((int64_t) src_len);
    uint8_t *out = (uint8_t *) lua_newuserdata(L, (size_t) out_len);
    int64_t buffer_updated = tea_encrypt_qq((uint32_t *) key_, (uint8_t *) src, (int64_t) src_len, out, out_len);
    if (buffer_updated < 0)
    {
        luaL_error(L, "encrypt wrong\n");
        return 0;
    }
    lua_pushlstring(L, (const char *) out, (size_t) buffer_updated);
    return 1;
}

static int
lencrypt(lua_State *L)
{
    if (lua_gettop(L) != 3)
    {
        luaL_error(L, "must be 3 args, key , sumtable and data");
        return 0;
    }
    size_t key_len;
    const char *key = luaL_checklstring(L, 1, &key_len);
    luaL_argcheck(L, key_len == 16, 1, "key must be 16 bytes len!");
#ifdef WORDS_BIGENDIAN
    uint32_t *key_ = (uint32_t *)key;
#else
    uint32_t key_[4];
    key_[0] = swap_uint32(((uint32_t *) key)[0]);
    key_[1] = swap_uint32(((uint32_t *) key)[1]);
    key_[2] = swap_uint32(((uint32_t *) key)[2]);
    key_[3] = swap_uint32(((uint32_t *) key)[3]);
#endif
    size_t sumtable_len;
    const char *sumtable = luaL_checklstring(L, 2, &sumtable_len);
    luaL_argcheck(L, sumtable_len == 64, 2, "sum table must be 64 bytes len!");
    size_t src_len;
    const char *src = luaL_checklstring(L, 3, &src_len);
    int64_t out_len = encrypt_qq_len((int64_t) src_len);
    uint8_t *out = (uint8_t *) lua_newuserdata(L, (size_t) out_len);

    int64_t buffer_updated = tea_encrypt((uint32_t *) key_, (uint32_t *) sumtable, (const uint8_t *) src,
                                         (int64_t) src_len, out, out_len);
    if (buffer_updated < 0)
    {
        luaL_error(L, "encrypt wrong\n");
        return 0;
    }
    lua_pushlstring(L, (const char *) out, (size_t) buffer_updated);
    return 1;
}

static int
lencrypt_native_endian(lua_State *L)
{
    if (lua_gettop(L) != 3)
    {
        luaL_error(L, "must be 3 args, key , sumtable and data");
        return 0;
    }
    size_t key_len;
    const char *key = luaL_checklstring(L, 1, &key_len);
    luaL_argcheck(L, key_len == 16, 1, "key must be 16 bytes len!");
#ifdef WORDS_BIGENDIAN
    uint32_t *key_ = (uint32_t *)key;
#else
    uint32_t key_[4];
    key_[0] = swap_uint32(((uint32_t *) key)[0]);
    key_[1] = swap_uint32(((uint32_t *) key)[1]);
    key_[2] = swap_uint32(((uint32_t *) key)[2]);
    key_[3] = swap_uint32(((uint32_t *) key)[3]);
#endif
    size_t sumtable_len;
    const char *sumtable = luaL_checklstring(L, 2, &sumtable_len);
    luaL_argcheck(L, sumtable_len == 64, 2, "sum table must be 64 bytes len!");

    size_t src_len;
    const char *src = luaL_checklstring(L, 3, &src_len);
    int64_t out_len = encrypt_qq_len((int64_t) src_len);
    uint8_t *out = (uint8_t *) lua_newuserdata(L, (size_t) out_len);

    int64_t buffer_updated = tea_encrypt_native_endian((uint32_t *) key_, (uint32_t *) sumtable, (const uint8_t *) src,
                                                       (int64_t) src_len, out, out_len);
    if (buffer_updated < 0)
    {
        luaL_error(L, "encrypt wrong\n");
        return 0;
    }
    lua_pushlstring(L, (const char *) out, (size_t) buffer_updated);
    return 1;
}

static int
ldecrypt_qq(lua_State *L)
{
    if (lua_gettop(L) != 2)
    {
        luaL_error(L, "must be 2 args, key and data");
        return 0;
    }
    size_t key_len;
    const char *key = luaL_checklstring(L, 1, &key_len);
    luaL_argcheck(L, key_len == 16, 1, "key must be 16 bytes len!");
#ifdef WORDS_BIGENDIAN
    uint32_t *key_ = (uint32_t *)key;
#else
    uint32_t key_[4];
    key_[0] = swap_uint32(((uint32_t *) key)[0]);
    key_[1] = swap_uint32(((uint32_t *) key)[1]);
    key_[2] = swap_uint32(((uint32_t *) key)[2]);
    key_[3] = swap_uint32(((uint32_t *) key)[3]);
#endif
    size_t src_len;
    const char *src = luaL_checklstring(L, 2, &src_len);
    uint8_t *out = (uint8_t *) lua_newuserdata(L, (size_t) src_len);

    int64_t buffer_updated = tea_decrypt_qq((uint32_t *) key_, (const uint8_t *) src, (int64_t) src_len, out,
                                            (int64_t) src_len);
    if (buffer_updated < 0)
    {
        luaL_error(L, "decrypt wrong\n");
        return 0;
    }
    lua_pushlstring(L, (const char *) out, (size_t) buffer_updated);
    return 1;
}

static int
ldecrypt(lua_State *L)
{
    if (lua_gettop(L) != 3)
    {
        luaL_error(L, "must be 3 args, key , sumtable and data");
        return 0;
    }
    size_t key_len;
    const char *key = luaL_checklstring(L, 1, &key_len);
    luaL_argcheck(L, key_len == 16, 1, "key must be 16 bytes len!");
#ifdef WORDS_BIGENDIAN
    uint32_t *key_ = (uint32_t *)key;
#else
    uint32_t key_[4];
    key_[0] = swap_uint32(((uint32_t *) key)[0]);
    key_[1] = swap_uint32(((uint32_t *) key)[1]);
    key_[2] = swap_uint32(((uint32_t *) key)[2]);
    key_[3] = swap_uint32(((uint32_t *) key)[3]);
#endif
    size_t sumtable_len;
    const char *sumtable = luaL_checklstring(L, 2, &sumtable_len);
    luaL_argcheck(L, sumtable_len == 64, 2, "sum table must be 64 bytes len!");
    size_t src_len;
    const char *src = luaL_checklstring(L, 3, &src_len);
    uint8_t *out = (uint8_t *) lua_newuserdata(L, (size_t) src_len);
    int64_t buffer_updated = tea_decrypt((uint32_t *) key_, (uint32_t *) sumtable, (const uint8_t *) src,
                                         (int64_t) src_len, out, (int64_t) src_len);
    if (buffer_updated < 0)
    {
        luaL_error(L, "decrypt wrong\n");
        return 0;
    }
    lua_pushlstring(L, (const char *) out, (size_t) buffer_updated);
    return 1;
}

static int
ldecrypt_native_endian(lua_State *L)
{
    if (lua_gettop(L) != 3)
    {
        luaL_error(L, "must be 3 args, key , sumtable and data");
        return 0;
    }
    size_t key_len;
    const char *key = luaL_checklstring(L, 1, &key_len);
    luaL_argcheck(L, key_len == 16, 1, "key must be 16 bytes len!");
#ifdef WORDS_BIGENDIAN
    uint32_t *key_ = (uint32_t *)key;
#else
    uint32_t key_[4];
    key_[0] = swap_uint32(((uint32_t *) key)[0]);
    key_[1] = swap_uint32(((uint32_t *) key)[1]);
    key_[2] = swap_uint32(((uint32_t *) key)[2]);
    key_[3] = swap_uint32(((uint32_t *) key)[3]);
#endif
    size_t sumtable_len;
    const char *sumtable = luaL_checklstring(L, 2, &sumtable_len);
    luaL_argcheck(L, sumtable_len == 64, 2, "sum table must be 64 bytes len!");
    size_t src_len;
    const char *src = luaL_checklstring(L, 3, &src_len);
    uint8_t *out = (uint8_t *) lua_newuserdata(L, (size_t) src_len);
    int64_t buffer_updated = tea_decrypt_native_endian((uint32_t *) key_, (uint32_t *) sumtable, (const uint8_t *) src,
                                                       (int64_t) src_len, out, (int64_t) src_len);
    if (buffer_updated < 0)
    {
        luaL_error(L, "decrypt wrong\n");
        return 0;
    }
    lua_pushlstring(L, (const char *) out, (size_t) buffer_updated);
    return 1;
}

static luaL_Reg lua_funcs[] = {
        {"encrypt_qq",            &lencrypt_qq},
        {"encrypt",               &lencrypt},
        {"encrypt_native_endian", &lencrypt_native_endian},
        {"decrypt_qq",            &ldecrypt_qq},
        {"decrypt",               &ldecrypt},
        {"decrypt_native_endian", &ldecrypt_native_endian},
        {NULL, NULL}
};

DLLEXPORT int luaopen_tea(lua_State *L)
{
    luaL_newlib(L, lua_funcs);
    return 1;
}
