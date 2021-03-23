
from os import urandom
from sys import stdout
from random import choice
import re

from Excs.exceptions import UIDInvalid
from Flags.flags import USERNAME_UID_SEP

class Username():
    """
    Defines Appropiate identification variables
    """
    predefined_users = ['Romeo', 'Juliet']
    __uidlen = 8
    __pattern = re.compile(''.join(['[a-zA-Z0-9_]+\(', '[a-zA-Z0-9_]'*2*__uidlen, '\)']))

    def __init__(self, username: 'User Friendly Name'=None, UID: 'Define Username and UID'=None):
        if(not username): username = choice(self.predefined_users)
        if(UID): 
            self.__define(UID)
            return
        self._username = username
        self.__uid = urandom(self.__uidlen).hex()
        self.id = ''.join([str(self._username), '(', str(self.__uid), ')'])
        return

    def __repr__(self):
        # return ''.join(['<', 'user=', str(self._username), ' ', 'uid=', str(self.__uid), '>'])
        return self.id

    @property
    def uid(self)->None:
        return self.__uid
        
    @property
    def username(self)->None:
        return self._username

    @username.setter
    def username(self, value)->None:
        if(type(value) is str):
            if(value != ''):
                self._username = value
                self.__uid = urandom(self.__uidlen).hex()
                self.id = ''.join([str(self._username), '(', str(self.__uid), ')'])
        return

    def get(self):
        return ''.join([self._username, '(', self.__uid, ')'])

    def __define(self, define):
        try:
            __patt = self.__pattern.match(define)
            if(__patt is not None): 
                self._username, self.__uid = __patt.group().split('(')
                self.__uid = self.__uid[:-1]
                self.id = ''.join([str(self._username), '(', str(self.__uid), ')'])
                return
            raise UIDInvalid
        except:
            self._username, self.__uid = None, None
            stdout.write('Alloc Failed!')
            stdout.flush()
            return
    pass
