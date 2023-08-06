#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''                                                                                                             
Author: penglinhan                                        
Email: 2453995079@qq.com                                
File: encryption_and_decryption.py
Date: 2022/7/28 4:42 下午
'''
import hashlib
import base64
import uuid
from Crypto.Cipher import DES,DES3
from Crypto.Cipher import AES,PKCS1_OAEP
from Crypto import Random
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA
from Crypto.Signature import PKCS1_v1_5 as PKCS1_signature
from Crypto.Cipher import PKCS1_v1_5 as PKCS1_cipher
from binascii import b2a_hex, a2b_hex
import Crypto
from ecies.utils import generate_eth_key, generate_key
import ecies



class EncDec:
    #固定加解密
    def base64_encode(sentence:str,type = 64):
        sentence = sentence.encode('utf-8')
        if type == 64:encode = base64.b64encode(sentence)
        elif type == 16:encode = base64.b16encode(sentence)
        elif type ==32:encode = base64.b32encode(sentence)
        else:return 'type参数内容只能为16、32、64'
        sentence = encode.decode('utf-8')
        return sentence
    def base64_decode(sentence:str,type=64):
        if type == 64:sentence =  base64.b64decode(sentence)
        elif type == 16:sentence = base64.b16decode(sentence)
        elif type == 32:sentence = base64.b32decode(sentence)
        else:return 'type参数内容只能为16、32、64'
        sentence = sentence.decode('utf-8')
        return sentence


    #对称加密算法
    def DES_encode(seentence:str,secret_key = 'bxddyg8w')->str:
        #必须8为或者16为的密钥
        if len(secret_key)!=8 and len(secret_key)!=16:
            return '密钥长度必须8位或者16位'
        DES.block_size = 32
        des_model = DES.new(secret_key.encode('utf8'), DES.MODE_ECB)
        while len(seentence) % DES.block_size != 0:
            seentence +=" "
        seentence = seentence.encode('utf8')
        return b2a_hex(des_model.encrypt(seentence)).decode('utf8')

    def DES_decode(seentence:bytes,secret_key = 'bxddyg8w')->str:
        if len(secret_key)!=8 and len(secret_key)!=16:
            return '密钥长度必须8位或者16位'
        seentence = a2b_hex(seentence)
        secret_key = secret_key.encode('utf8')
        des = DES.new(secret_key, DES.MODE_ECB)
        result = des.decrypt(seentence).decode().rstrip(' ')
        return result

    def AES_encode(seentence:str,secret_key = 'bxddyg8wdsfsafda')->str:
        if len(secret_key)!=32 and len(secret_key)!=16 and len(secret_key)!=24:
            return '密钥长度必须16位、24或者32位'
        pad = lambda s: s + (AES.block_size - len(s) % AES.block_size) * \
                        chr(AES.block_size - len(s) % AES.block_size)
        iv = Random.new().read(AES.block_size)
        aes_model = AES.new(secret_key.encode('utf8'), AES.MODE_CBC, iv)
        return b2a_hex(iv + aes_model.encrypt(pad(seentence).encode('utf8'))).decode('utf8')
    def AES_decode(seentence:bytes,secret_key = 'bxddyg8wdsfsafda')->str:
        if len(secret_key)!=32 and len(secret_key)!=16 and len(secret_key)!=24:
            return '密钥长度必须16位、24或者32位'
        seentence = a2b_hex(seentence)
        iv = seentence[:AES.block_size]
        aes_model =  AES.new(secret_key.encode('utf8'),AES.MODE_CBC, iv)
        unpad = lambda s: s[:-ord(s[len(s) - 1:])]
        return  unpad(aes_model.decrypt(seentence[AES.block_size:])).decode('utf8')

    def DES3_encode(seentence:str,secret_key = 'bxddyg8wdsfsafda')->str:
        if len(secret_key)!=32 and len(secret_key)!=16 and len(secret_key)!=24:
            return '密钥长度必须16位、24或者32位'
        pad = lambda s: s + (DES3.block_size - len(s) % DES3.block_size) * \
                        chr(DES3.block_size - len(s) % DES3.block_size)
        iv = Random.new().read(DES3.block_size)
        DES3_model = DES3.new(secret_key.encode("utf-8"), DES3.MODE_CBC, iv)
        return b2a_hex(iv + DES3_model.encrypt(pad(seentence).encode('utf8'))).decode('utf8')
    def DES3_decode(seentence:bytes,secret_key = 'bxddyg8wdsfsafda')->str:
        if len(secret_key)!=32 and len(secret_key)!=16 and len(secret_key)!=24:
            return '密钥长度必须16位、24或者32位'
        seentence = a2b_hex(seentence)
        iv = seentence[:DES3.block_size]
        DES3_model = DES3.new(secret_key.encode('utf8'), AES.MODE_CBC, iv)
        unpad = lambda s: s[:-ord(s[len(s) - 1:])]
        return unpad(DES3_model.decrypt(seentence[DES3.block_size:])).decode('utf8')

    #非堆成加密
    def save_key(key, url, name):
        with open(url + name + '.pem', 'wb')as f:
            f.write(key)
        return 'success'

    def load_key(url, name):
        with open(url + name) as f:
            key = f.read()
        return key
    def RSA_create_key():
        random_generator = Random.new().read
        rsa = RSA.generate(2048, random_generator)
        # 生成私钥
        private_key = rsa.exportKey()
        # 生成公钥
        public_key = rsa.publickey().exportKey()
        return public_key,private_key
    def RSA_encode(seentence:str,public_key):
        cipher_public = PKCS1_cipher.new(RSA.importKey(public_key))
        return b2a_hex(cipher_public.encrypt(seentence.encode('utf8'))).decode('utf8')
    def RSA_decode(seentence:str,private_key):
        cipher = PKCS1_cipher.new(RSA.importKey(private_key))
        back_text = cipher.decrypt(a2b_hex(seentence), 0)
        return back_text.decode('utf-8')

    def ECC_create_key():
        eth_k = generate_eth_key()
        sk_hex = eth_k.to_hex()  # hex string
        pk_hex = eth_k.public_key.to_hex()  # hex string
        return pk_hex,sk_hex
    def ECC_encode(seentence:str,public_key)->bytes:
        return ecies.encrypt(public_key,seentence.encode('utf8'))
    def ECC_decode(seentence:bytes,private_key)->str:
        return ecies.decrypt(private_key,seentence).decode('utf8')

    #散列加密算法
    def md5_encode(sentence: str) -> str:
        # 不可逆加密
        m = hashlib.md5()
        m.update(sentence.encode("utf8"))
        return m.hexdigest()

    def sha1_encode(sentence: str) -> str:
        # 不可逆加密
        sha1 = hashlib.sha1(sentence.encode('utf-8'))
        return sha1.hexdigest()

    def uuid_encode(sentence: str, secret_key='6ba7b811-9dad-11d1-80b4-00c04fd430c8') -> str:
        namespace = uuid.UUID(secret_key)
        return str(uuid.uuid5(namespace, sentence))

def test():
    s = EncDec.md5_encode('hello')
    print('md5：', s)
    s = EncDec.base64_encode('hello')
    print('base_enc', s)
    s = EncDec.base64_decode("aGVsbG8=")
    print('base_dec', s)
    s = EncDec.sha1_encode('hello')
    print('sha1:', s)
    s = EncDec.DES_encode('hello')
    print('des_enc:', s)
    s = EncDec.DES_decode(s)
    print('des_dec:', s)
    s = EncDec.AES_encode('hello')
    print('aes_enc', s)
    s = EncDec.AES_decode(s)
    print('aes_dec:', s)
    s = EncDec.DES3_encode('hello')
    print('des3_enc:', s)
    s = EncDec.DES3_decode(s)
    print('des3_dec:', s)
    pub_key, pri_key = EncDec.RSA_create_key()
    print(pub_key, pri_key)
    s = EncDec.RSA_encode('hello', pub_key)
    print('RSA_enc:', s)
    s = EncDec.RSA_decode(s, pri_key)
    print('RSA_dec:', s)
    pub_key, pri_key = EncDec.ECC_create_key()
    print(pub_key, pri_key)
    s = EncDec.ECC_encode('hello', pub_key)
    print('ECC_enc:', s)
    s = EncDec.ECC_decode(s, pri_key)
    print('ECC_dec:', s)
    s = EncDec.uuid_encode('hello')
    print('UUID_enc:',s)


if __name__ == '__main__':
    test()