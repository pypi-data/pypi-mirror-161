import base64
from Crypto.Cipher import AES
from hashlib import blake2b
class AESCrypto():
    def __init__(self, key, iv, *salts, fill_word = '|', encrypt_delimiter = ',', encoding = 'utf-8'):
        self.encoding = encoding
        self.max_word_len = 64
        self.key_len = 32
        self.iv_len = 16
        self.fill_word = fill_word
        self.encrypt_delimiter = encrypt_delimiter
        self.key = key
        self.iv = iv
        self.salts = salts
        encryted_salts = []
        
        if len(key) > self.key_len:
            raise Exception("key의 길이는 32자리 이하로 설정")
        else:
            self.key = key.zfill(self.key_len).encode(self.encoding)
        
        if len(iv) > self.iv_len:
            raise Exception("iv의 길이는 16자리 이하로 설정")
        else:
            self.iv = iv.zfill(self.iv_len).encode(self.encoding)
        
        crypto = AES.new(self.key, AES.MODE_CBC, self.iv)
        for salt in salts:
            if len(salt) > self.key_len:
                raise Exception("salt의 길이는 32자리 이하로 설정")
            encryted_salts.append(crypto.encrypt(self._fill(salt).encode(self.encoding)))
        
        self.encryted_salts = tuple(encryted_salts)
    
    def encrypt(self, input:str):
        crypto = AES.new(self.key, AES.MODE_CBC, self.iv)
        for salt in self.salts:
            crypto.encrypt(self._fill(salt).encode(self.encoding))
        encrypted = crypto.encrypt(self._fill(input).encode(self.encoding))
        encoded_encrypted = base64.b64encode(encrypted)
        return encoded_encrypted.decode(self.encoding)

    def decrypt(self, encrypted):
        crypto = AES.new(self.key, AES.MODE_CBC, self.iv)
        for salt in self.encryted_salts:
            crypto.decrypt(salt)
        decoded_data = base64.b64decode(encrypted)
        decrypted = crypto.decrypt(decoded_data)
        return decrypted.decode(self.encoding)
    
    def _fill(self, word: str):
        word = str(word)
        word_length = len(word)
        if word_length < self.key_len:
            loop_cnt = self.key_len - word_length
            for i in range(loop_cnt):
                word = self.fill_word + word
        
        return word
    
__aes__: AESCrypto = None

def aes_init(key, iv, *salts, fill_word = '|', encrypt_delimiter = ',') -> AESCrypto:
    global __aes__
    if __aes__ is None:
        __aes__ = AESCrypto(key, iv, *salts, fill_word, encrypt_delimiter)
    return __aes__

def aes_encrypt(word: str, aes: AESCrypto = None):
    if aes is None:
        aes = __aes__
    
    word = str(word)
    word_size = len(word)
    
    if word_size > aes.max_word_len:
        raise Exception(f"글자 수 확인필요: {aes.max_word_len}이하 글자만 지원")
    
    loop_cnt = int(word_size / aes.key_len) + (1 if word_size % aes.key_len > 0 else 0)
    encrypt_list = []
    start_idx = 0
    
    for i in range(loop_cnt):
        if loop_cnt-1 == i :
            encrypt_list.append(aes.encrypt(word[start_idx:]))
        else:
            encrypt_list.append(aes.encrypt(word[start_idx:aes.key_len*(i+1)]))
        start_idx += aes.key_len
    return aes.encrypt_delimiter.join(encrypt_list)

def aes_decrypt(word: str, aes: AESCrypto = None):
    if aes is None:
        aes = __aes__
    
    word = str(word)
    dec_word = ''
    for w in word.split(aes.encrypt_delimiter):
        dec_word += aes.decrypt(w).lstrip(aes.fill_word)
    return dec_word

class BlakeCrypto():
    def __init__(self, key: str, person: str, salt: str, *message_salts: list, digest_size = 24, encoding = 'utf-8'):
        self.encoding = encoding
        self.key = key.encode(self.encoding)
        self.person = person.encode(self.encoding)
        self.salt = salt.encode(self.encoding)
        self.message_salts = tuple(map(lambda s: s.encode(self.encoding), message_salts))
        self.digest_size = digest_size
    
    def encrypt(self, input:str):
        crypto = blake2b(digest_size=self.digest_size, key=self.key, salt=self.salt, person=self.person)
        for salt in self.message_salts:
            crypto.update(salt)
        crypto.update(input.encode(self.encoding))
        return crypto.hexdigest()

__blake2b__: BlakeCrypto = None

def blake_init(key: str, person: str, salt: str, *message_salts: list, digest_size = 24, encoding = 'utf-8'):
    global __blake2b__
    if __blake2b__ is None:
        __blake2b__ = BlakeCrypto(key, person, salt, *message_salts, digest_size=digest_size, encoding=encoding)
    return __blake2b__

def blake_encrypt(word, blake: BlakeCrypto = None):
    if blake is None:
        blake = __blake2b__
    
    return blake.encrypt(word)

