import random
import string
import crc32c
import time

 
def random_string_generator(str_size, allowed_chars):
    return (''.join(random.choice(allowed_chars) for x in range(str_size))).encode('utf8')
 
chars = string.ascii_letters + string.punctuation

data = random_string_generator(10**7, chars)

s = time.time()
for i in range(10):
    x = crc32c.crc32c(data)
print(time.time() - s)
print(x)
