from simplecrypt import encrypt, decrypt
from base64 import b64encode, b64decode

strKey = 'MyN3wK3Y5EncrYpt1-n'
strString = 'uid@example.com'

ciphertext = encrypt(strKey, strString)
strCipherText = b64encode(ciphertext)
print(strCipherText)
