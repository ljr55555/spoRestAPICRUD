from cryptography.fernet import Fernet

key = Fernet.generate_key()
print("Save this key for future decryption: %s" % key)

f = Fernet(key)

ciphertext = f.encrypt(b"uid@example.com")
print("The crypted version is %s" % ciphertext)
strCipherText = f.decrypt(ciphertext)
print("Decrypted version is %s" % strCipherText)