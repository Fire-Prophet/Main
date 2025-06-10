import hashlib

text = input("암호화할 문자열: ")
hash = hashlib.sha256(text.encode()).hexdigest()
print("SHA256 해시값:", hash)
