local tea = require("tea")


local encoded = tea.encrypt_qq("32107654BA98FEDC", "hahaha")
print(encoded)

print(tea.decrypt_qq("32107654BA98FEDC",encoded))


