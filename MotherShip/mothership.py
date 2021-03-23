
'''
 __  __       _   _               ____  _     _       
|  \/  | ___ | |_| |__   ___ _ __/ ___|| |__ (_)_ __  
| |\/| |/ _ \| __| '_ \ / _ \ '__\___ \| '_ \| | '_ \ 
| |  | | (_) | |_| | | |  __/ |   ___) | | | | | |_) |
|_|  |_|\___/ \__|_| |_|\___|_|  |____/|_| |_|_| .__/ 
                                               |_|    
'''

from __future__ import unicode_literals, print_function
import sys
import argparse
import os
import getpass
import crypt
from Crypto.Hash import SHA512

from prompt_toolkit import print_formatted_text, HTML
from prompt_toolkit.shortcuts import prompt
from prompt_toolkit.styles import Style
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.completion import NestedCompleter
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from pygments.lexers.python import PythonLexer
from prompt_toolkit.lexers import PygmentsLexer
import string
import inspect
import traceback
import random
from pyfiglet import figlet_format

from Prompt import custom_completer
import Chromos
o = Chromos.Chromos()

debug = False

print('\n')
print(o.blue(figlet_format("MotherShip")))

def custinput(st)->str:
    return input(o.blue(st))

class Login():
    """
    Structure for login mechanism
    """
    def __init__(self, token, master, data_file_name="login.ch", i_username=None, i_password=None):
        super(Login, self).__init__()

        raise NotImplementedError
        self.__username = None
        self.__login_chk_comp = False
        self.__token = SHA512.new(str(token).encode()).hexdigest()
        self.__secret_key = None
        self.master = master
        self.__data_file_name = data_file_name

        if(i_username):
            if(os.path.isfile(self.__data_file_name)):
                self.__checker(str(i_username), str(i_password) or getpass.getpass(o.blue("Password:")))
                return
            self.__create_pass(str(i_username), str(i_password) or getpass.getpass(o.blue("Password:")))
            return
        
        if(os.path.isfile(self.__data_file_name)==False):
            self.__create_pass(custinput("Username:"), getpass.getpass(o.blue("Password:")))
            return

        self.__checker(custinput("Username: "), getpass.getpass(o.blue("Password: ")))

    def __checker(self, __interim_username, __interim_password):
        with open(self.__data_file_name, mode="r") as file_:
            self.__username = file_.readline()[:-1]
            __password = file_.readline()[:-1]
            __secret_sauce = file_.readline()[:-1]
            if(SHA512.new(''.join([self.__username, '.', self.master, '.', __password])).hexdigest() == __secret_sauce):
                pass
            else:
                if(debug): o.error_info("Integrity check Failed!")
                sys.exit(-1)

        __salt = "$" + self.__username.split("$")[1] + "$" + self.__username.split("$")[2]
        __interim_username = crypt.crypt(__interim_username, __salt)

        if(self.__username==__interim_username):
            __salt = "$" + __password.split("$")[1] + "$" + __password.split("$")[2]
            if(__password==crypt.crypt(__interim_password, __salt)):
                __salt_u = "$" + self.__username.split("$")[1] + "$" + self.__username.split("$")[2]
                __salt = self.__salt_adder(__salt_u, __salt)
                
                self.__secret_key = crypt.crypt(self.__username+__password, __salt)
                self.__login_chk_comp = True
        
                self.__go([self.__data_file_name, self.__secret_key])

                return True

            else:
                if(debug): o.error_info("Incorrect Username or Password")
                sys.exit(-1)
                return False
        else:
            if(debug): o.error_info("Incorrect Username or Password")
            sys.exit(-1)

        return False

    def __create_pass(self, i_username, i_password):
        """
        Create User Ident!
        """
        with open(self.__data_file_name, mode="w") as file_:
            self.__username = i_username
            __password = i_password
            self.__username = crypt.crypt(self.__username, salt=crypt.mksalt(method=crypt.METHOD_SHA512))
            __password = crypt.crypt(__password, salt=crypt.mksalt(method=crypt.METHOD_SHA512))
            
            __secret_sauce = ''.join([self.__username, ".CliSer.", __password])
            __secret_sauce = SHA512.new(__secret_sauce)

            file_.write(self.__username)
            file_.write("\n")

            file_.write(__password)
            file_.write("\n")

            file_.write(__secret_sauce.hexdigest())
            file_.write("\n")

            if(debug): o.info_y("User Created!")

            return

    def __salt_adder(self, salt_1, salt_2):
        _salt_ = ""
        if(len(salt_1)!=len(salt_2)):
            print(o.error_info("Length Mismatch"))
            return
        _salt_ += salt_1[0:3]
        for i in range(3, len(salt_1)):
            _salt_ += chr(int((ord(salt_1[i]) + ord(salt_2[i]))/2))

        return _salt_

    def __go(self):
        return self.token

class colors():
    
    def __init__(self):
        super(colors, self).__init__()

        self.base_attr = "\x1b[1;"

        self.black = '30'
        self.red = '31'
        self.green = '32'
        self.yellow = '33'
        self.blue = '34'
        self.purple = '35'
        self.cyan = '36'
        self.white = '37'
        return

class MotherShip():
    """
    Structure for MotherShip
    """
    def __init__(self, 
        username:str='',
        host:str='localhost',
        port:int=45284,
        stdin=None,
        stdout=None,
        init_server=False):

        super(MotherShip, self).__init__()
        
        if stdin is not None: self.stdin = stdin
        else: self.stdin = sys.stdin
        if stdout is not None: self.stdout = stdout
        else: self.stdout = sys.stdout
        
        self._cliser_ = None
        self.HOST = host
        self.PORT = port
        self.identchars = string.ascii_letters + string.digits + '_'
        self.username = username
        if(self.username == ''):
            self.username = input("\x1b[1;34musername\x1b[1;31m> \x1b[0m\x1b[1;32m")  
            if(self.username): pass
            else: self.username = ["Romeo", "Juliet"][random.randint(0,1)]

        if(init_server):
            self.start.server(self)
            self.connect()
        return

    def __repr__(self):
        return '<[\x1b[1;34m%s\x1b[0m] username=[\x1b[1;34m%s\x1b[0m] _cliser=[\x1b[1;34m%s\x1b[0m] host=[\x1b[1;34m%s\x1b[0m] port=[\x1b[1;34m%d\x1b[0m]>' % ('MotherShip Instance', str(self.username), str(self._cliser_), self.HOST, self.PORT)

    class start:
        def __init__(self, obj):
            __style = Style.from_dict({
                '': '#00eb00 bold',
                'username':'#0091ff',
                'at':'white',
                'host':'#ed9a00',
                'port':'#b244fc',
                'colon':'white',
                'prompt': '#ff0000 bold',
                'msg': "blue bold",
                'rprompt': 'bg:#ff0066 #ffffff',
                'precmd': '#00eb00 bold',
            })
            message = [
                ('class:username', obj.username),
                ('class:at',       '@'),
                ('class:host',     obj.HOST),
                ('class:prompt',    '> '),
                ('class:precmd',    '\start'),
                ('class:prompt',    '> '),
            ]
            __startcompleter = custom_completer.MyNestedCompleter.from_nested_dict({"server":None, "client":None, "exit":None})
            postcmd = obj.session.prompt(message=message, style=__style, completer=__startcompleter)
            if(postcmd):
                if(postcmd == "exit"):
                    pass
                elif(postcmd == "server"):
                    obj.start.server(obj)
                else:
                    obj.start.client(obj)
            return
        
        def server(self)->None:
            from Server import server
            print_formatted_text(FormattedText([("green bold", "Starting Server!")]))
            self._cliser_ = "server"
            self.setip()
            self.server = server.server(username=self.username, HOST=self.HOST, PORT=self.PORT)
            return

        def client(self)->None:
            from Client import client
            print_formatted_text(FormattedText([("green bold", "Starting Client!")]))
            self._cliser_ = "client"
            self.setip()
            self.client = client.client(username=self.username, HOST=self.HOST, PORT=self.PORT)
            return
    
    def setip(self, *args)->None:
        __style = Style.from_dict({
            '': '#00eb00 bold',
            'username':'#0091ff',
            'at':'white',
            'host':'#fc4444',
            'port':'#b244fc',
            'colon':'white',
            'prompt': '#ff0000 bold',
            'msg': "blue bold",
        })
        message = [
            ('class:username', self.username),
            ('class:at',       '@'),
            ('class:host',     self.HOST),
            ('class:colon', ":"),
            ('class:port', str(self.PORT)),
            ('class:prompt',    '>'),
            ('class:host', 'ip'),
            ('class:colon', ':'),
            ('class:port', 'port'),
            ('class:prompt', '> '),
        ]

        HOST = prompt(message=message, style=__style, default='%s' % self.HOST + ':' +str(self.PORT))

        try:
            self.HOST, self.PORT = HOST.split(":")
            self.PORT = int(self.PORT)
            self.__define_prompt()
        except Exception as exc:
            traceback.print_exc()

    def connect(self, *args):
        if(self._cliser_):
            if(self._cliser_ == "server"):
                self.server.connect()
            else:
                if(self.client.connect()):
                    self.session = PromptSession(self.__message, style=self.__style)
                    
        return

    def disconnect(self, *args)->None:
        if(self._cliser_):
            if(self._cliser_ == "server"):
                self.server.stop()
            else:
                self.client.stop()
        return

    def stop(self, *args)->None:
        if(self._cliser_):
            func = getattr(self, self._cliser_)
            func.stop()
        return

    def devid(self, *args)->None:
        if(self._cliser_): print(o.yellow(str(getattr(self, self._cliser_).username)))
        return

    def whoami(self, *args)->None:
        self.stdout.write(''.join(['This is the ', self.username, '\n']))
        self.stdout.flush()
        return

    def whoisthis(self, *args)->None:
        self.stdout.write(''.join(['Hi! This is the ', 'MotherShip', '\n']))
        self.stdout.flush()
        return

    def who(self, *args)->None:
        self.__send_('/who')
        return

    def __send_(self, text)->None:
        """
        Only valid for self._cliser_ = "client"
        """
        if(self._cliser_):
            if(self._cliser_ == "client"):
                self.client.send(text)
                return

    def __execute_py(self, line)->None:
        print(line)
        if(debug): eval(line) # Dangerous keep debug False
        return

    def print(*args)->None:
        print(args)
    
    def __parseline(self, line)->str:
        """Parse the line into a command name and a string containing
        the arguments.  Returns a tuple containing (command, args, line).
        'command' and 'args' may be None if the line couldn't be parsed.
        """
        line = line.strip()
        if not line:
            return None, None, line
        elif line[0] == '?':
            line = 'help ' + line[1:]
        # i, n = 0, len(line)
        # while i < n and line[i] in identchars: i = i+1
        # cmd, arg = line[:i], line[i:].strip()
        # cmd = line.split(" ")[0]
        # arg = line.split(" ")[1:]
        args = None
        if("(" in line and ")" in line):
            # mo1 = re.search("\(", line)
            # mo2 = re.search("\)", line)
            # args = line[mo1.start(): mo2.start() + 1]
            args = line[line.find("("): line.find(")") + 1]
            line = line.split(args)[0]
            args = args[1:-1]
        try:
            cmds = line.split(" ")
        except:
            print_formatted_text(FormattedText([("#ff0000 bold", "Invalid COM!")]))
        
        return cmds, args, line

    def __execute_com(self, text):
        cmds, args, line = self.__parseline(text)
        func = self
        # print(cmds)
        try:
            for cmd in cmds:
                func = getattr(func, cmd)
        except AttributeError:
            return self.stdout.write('\x1b[1;31m*** Unknown syntax: %s\n\x1b[0m'%line)

        # print("func:" + str(func))

        if(inspect.getmodule(func)):
            if(inspect.getmodule(func).__name__=="MotherShip.mothership"):
                return func(self)
        if(args):
            return func(eval(args)[0])
        return func()

    def exit(self, *args)->None:
        print_formatted_text(FormattedText([('red bold', 'Exiting.....')]))
        if(self._cliser_):
            try:
                func = getattr(self, self._cliser_)
                func.stop()
            except AttributeError:
                pass
            except RuntimeError:
                pass
            except Exception as exc:
                traceback.print_exc()
        sys.exit(0)

    def __get_rprompt(self)->str:
        return 'CliSer'

    def __define_prompt(self, *args)->None:
        self.__style = Style.from_dict({
            '': '#00eb00 bold',
            'username':'#0091ff',
            'at':'white',
            'host':'#ed9a00',
            'prompt': '#ff0000 bold',
            'msg': "blue bold",
            'rprompt': 'bg:#ff0066 #ffffff',
        })
        self.__message = [
            ('class:username', self.username),
            ('class:at',       '@'),
            ('class:host',     self.HOST),
            # ('white',    ':'),
            ('class:prompt',    '> '),
        ]

        __custom_coms = {
            # '|/who': None,
            '|/clients': None,
            '|/connect': {'to': None},
            '\start server': None,
            '\start client': None,
            }

        __predefined_coms = self.__commandify(self.__getmembers(self))
        __predefined_coms.update(__custom_coms)

        # self.my_completer = custom_completer.MyNestedCompleter.from_nested_dict({
        #     '\\start':{
        #         'server': None,
        #         'client': None,
        #     },
        #     '\\connect': None,
        #     '\\setip': None,
        #     '\\exit': None,
        #     '|/clients': None,
        #     '|/connect': {
        #         'to': None
        #     },
        #     '\disconnect': None,
        #     '\__define_prompt': None,

        # })
        self.my_completer = custom_completer.MyNestedCompleter.from_nested_dict(__predefined_coms)
        self.session = PromptSession(self.__message, style=self.__style, enable_history_search=True) # lexer=PygmentsLexer(PythonLexer)

        return

    def __commandify(self, dict1)->dict:
        keys = list(dict1.keys())
        return {"\\" + key: dict1[key] for key in keys}

    def __getmembers(self, obj)->dict:
        def Merge(dict1, dict2):
            if(dict1 is None):
                dict1 = {}
            dict1.update(dict2 or {})    
        allowed_methods = [__method[0] for __method in inspect.getmembers(obj, inspect.ismethod) if ''.join(['_', obj.__class__.__name__, "__"]) not in __method[0]]
        allowed_classes = [__class[0] for __class in inspect.getmembers(obj, inspect.isclass)]
        allowed_functions = [__function[0] for __function in inspect.getmembers(obj, inspect.isfunction)]
        if('__init__' in allowed_methods): allowed_methods.remove('__init__')
        if('__repr__' in allowed_methods): allowed_methods.remove('__repr__')
        if('__init__' in allowed_functions): allowed_functions.remove('__init__')
        if('__repr__' in allowed_functions): allowed_functions.remove('__repr__')
        if('__base__' in allowed_classes): allowed_classes.remove('__base__')
        if('__class__' in allowed_classes): allowed_classes.remove('__class__')
        com_m = {key: None for key in allowed_methods}
        com_f = {key: None for key in allowed_functions}
        com_c = {}
        if(allowed_classes): com_c = {key: self.__getmembers(getattr(obj, key)) for key in allowed_classes}
        Merge(com_m, com_c)
        Merge(com_m, com_f)
        return com_m

    def deck(self):
        # Shell
        self.__define_prompt()

        while True:
            try:
                text = self.session.prompt(self.__message, completer=self.my_completer, rprompt='', auto_suggest=AutoSuggestFromHistory())
            
                if(text==''):
                    pass
                elif(text[0] == '|'):
                    self.__send_(text.strip('|'))
                elif(text[0] == '\\'):
                    self.__execute_com(text.strip('\\'))
                elif(text[0] == '/'):
                    self.__execute_py(text.strip('/'))
                else:
                    self.__send_(text)
            except SystemExit:
                sys.exit(0)
                pass
            except KeyboardInterrupt:
                pass
            except EOFError:
                self.exit()
                sys.exit(-1)
            except Exception as exc:
                traceback.print_exc()
                pass

# parser = argparse.ArgumentParser(description="CliSer")
# parser.add_argument("--bind", "-b", dest="bind_ip", required=False, action="store", type=str, default="localhost", help="Bind IP")
# parser.add_argument("--port", "-p", dest="bind_port", required=False, action="store", type=int, default=45284, help="Bind Port")
# parser.add_argument("--timeout", "-t", dest="timeout", required=False, action="store", type=int, default=30, help="Timeout [30s]")
# parser.add_argument("--username", "-u", dest="username", required=False, action="store", type=str, default="", help="Username")
# parser.add_argument("--server", "-s", dest="server", required=False, action="store_true", help="Initiate a server instance")
# args = parser.parse_args()

# m = MotherShip(username=args.username, host=args.bind_ip, port=args.bind_port, init_server=args.server)
# m.deck()
