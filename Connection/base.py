# Program for Connection Setup
'''
Konnect In Server Sequence
'''
from os import urandom, mkdir
from os.path import isfile, isdir
from Crypto import Random
from Crypto.PublicKey import RSA
from hashlib import md5
from Crypto.Cipher import PKCS1_OAEP, AES

class NegotiationBase():
    def load_keys(self, path, prefix='')->None:
        if(isdir(path) is False): mkdir(path)
        path = ''.join([path, '/', prefix])
        if(isfile(''.join([path, 'public.key',])) is False or isfile(''.join([path, 'private.key',])) is False): self.generate_key(path=path)
        with open(''.join([path, 'public.key',]), 'r') as f:
            public = f.read().encode()
        with open(''.join([path, 'private.key',]), 'r') as f: 
            private = f.read().encode()
        return public, private

    def load_key(self, keypath)->bytearray:
        with open(keypath, 'rb') as f:
            return f.read()    

    def generate_key(self, path)->bool:
        random = Random.new().read
        RSAKey = RSA.generate(1024, random)
        public = RSAKey.publickey().exportKey()
        private = RSAKey.exportKey()

        with open(''.join([path, 'public.key']), 'wb') as f:
            f.write(public)
            f.flush()
        with open(''.join([path, 'private.key']), 'wb') as f:
            f.write(private)
            f.flush()

        return True

    def rand_gen(self, n)->str:
        return str(int.from_bytes(urandom(n), byteorder='big'))

    def osurandom(self, n)->bytes:
        return urandom(n)

    def ret_hash(self, __data)->bytearray:
        return md5(__data).hexdigest().encode()

    def ret_enc(self, __key):
        __RSAKey = RSA.importKey(__key)
        return PKCS1_OAEP.new(__RSAKey)

    pass
