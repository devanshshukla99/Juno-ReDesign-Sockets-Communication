
from numpy import array, zeros, mean, sin, cos, tan
from scipy import fftpack
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
import struct
from base64 import b64encode, b64decode
from TSE.encoder_function_6 import encf6
from typing import List

class Key(encf6):
    """
    Transport Security Encryption Key Class
    """
    from os import urandom
    def __init__(self, aeskey: 'AES Encryption Key', key:'Symmetric Key'=None):
        self.__key = None
        if(key): self.retrieveKey(key)
        else: self.genKey()

        super().__init__(key=self.__processKey(), aeskey=aeskey)
        return

    def __repr__(self):
        return ''.join(['<', 'TSE', ' ', 'Instance w/ AES @', str(hex(id(self))), ' n(', str(len(self.__key)), ')', '>'])

    def genKey(self) -> None:
        """
        Generate 1024-byte length Random binary string.
        """
        self.__key = self.urandom(1024)
        return

    def exportKey(self) -> None:
        """
        Dump Key base64.
        """
        return b64encode(self.__key).decode()

    def retrieveKey(self, __s) -> None:
        """
        Retrieve Key from base64 dump.
        """
        if(type(__s) is str): __s = __s.encode()
        self.__key = b64decode(__s)
        return

    def __processKey(self) -> List[int]:
        """
        actual_key will be the fft of the sin, cos(permutes) of the original key
        """
        __key_s2i = array(struct.unpack('>' + 'B'*1024, self.__key))
        __mean = int(mean(__key_s2i))

        __actual_key = zeros(2048, dtype=int)

        for i in range(0, __key_s2i.size):
            __actual_key[2*i] = sin(__key_s2i[i])*__mean
            __actual_key[2*i + 1] = cos(__key_s2i[i])*__mean

        __actual_key = array(fftpack.fft(__actual_key).real/10, dtype=int)

        return __actual_key

    def RelayKey(self, public_key):
        """
        Args:
            public_key
        
        Returns:
            AES Key, TSE Key, Nonce, Tag
        """

        aeskey = self.urandom(16)
        cipher = AES.new(aeskey, AES.MODE_OCB)
        tsekey, tag = cipher.encrypt_and_digest(self.exportKey().encode())
        nonce = cipher.nonce
        
        tsekey = b64encode(tsekey)
        nonce = b64encode(nonce)
        tag = b64encode(tag)

        __rsa = RSA.importKey(public_key)
        __enc = PKCS1_OAEP.new(__rsa)
        aeskey = __enc.encrypt(aeskey)
        
        return b64encode(aeskey), tsekey, nonce, tag
                
    def DeRelayKey(self, aeskey, tsekey, nonce, tag, private_key):
        """
        Args:
            aeskey
            tsekey
            nonce
            tag
            private_key
        Returns:
            <Key Instance>
        """
        aeskey =  b64decode(aeskey)
        tsekey =  b64decode(tsekey)
        nonce =  b64decode(nonce)
        tag =  b64decode(tag)

        __rsa = RSA.importKey(private_key)
        __enc = PKCS1_OAEP.new(__rsa)
        aeskey = __enc.decrypt(aeskey)
        
        cipher = AES.new(aeskey, AES.MODE_OCB, nonce=nonce)
        tsekey = cipher.decrypt_and_verify(tsekey, tag)

        return Key(aeskey=aeskey, key=tsekey)

    pass

def encode_RSA(data, cpub):
    __rsa = RSA.importKey(cpub)
    __enc = PKCS1_OAEP.new(__rsa)
    return __enc.encrypt(data)

def decode_RSA(data, cpri):
    __rsa = RSA.importKey(cpri)
    __enc = PKCS1_OAEP.new(__rsa)
    return __enc.decrypt(data)
