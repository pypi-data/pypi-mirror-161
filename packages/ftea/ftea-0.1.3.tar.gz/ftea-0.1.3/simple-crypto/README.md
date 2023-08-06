# simple-crypto

Simple C lib of the MD5 & TEA algorithm

# Install

```bash
git clone https://github.com/fumiama/simple-crypto.git
cd simple-crypto
mkdir build
cd build
cmake ..
make
make install
```

# Usage

1. Include `simplecrypto.h` in your c program.
```c
#include <simplecrypto.h>
```
2. Call functions. Don't forget to `free` the returned digest.
```c
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
```
3. Optional lua binding
```lua
local tea = require("tea")


local encoded = tea.encrypt_qq("32107654BA98FEDC", "hahaha")
print(encoded)

print(tea.decrypt_qq("32107654BA98FEDC",encoded))


tea.encrypt("32107654BA98FEDC", sumtableof64bits,"hahaha")
tea.decrypt("32107654BA98FEDC", sumtableof64bits,"hahaha")

tea.encrypt_native_endian("32107654BA98FEDC", sumtableof64bits,"hahaha")
tea.decrypt_native_endian("32107654BA98FEDC", sumtableof64bits,"hahaha")

```
