import sys
import msvcrt
from .inputlib import any_input_
from .inputlib import any_input


inputs  = ['input', 'input_', 'any_input', 'char_input', 'key_input', 'password_input_', 'password_input', 'amazing_input', 'commandline_input','any_input_']
__all__ = ['SubString', 'cmdlexer']+inputs
__description__ = "methods to collect user inputs in an easier"
try:
    __all__.remove("input")
except ValueError:
    pass

##########################
# input
##########################

def input(value="",*args,end="",sep=" ",stdout=sys.stdout,stdin=sys.stdin):
    """ input from scratch """
    sub = SubString(value,*args,end=end,sep=sep)
    stdout.write(("\r")+sub)
    stdout.flush()
    line = stdin.readline()
    if line[-1:] == '\n':
        line = line[:-1]
    return line


# alias for input function
input_ = input

def SubString(value="",*args,start="",end="\n",sep=" ",default=""): #SS = SubString
    string = str(value)
    string+=str(start)
    if len(args) != 0:
        for obj in list(args):
            string += sep+str(obj)
    else:
        string += default
    string+=str(end)
    return string

##########################
# end of input
##########################



##########################
# end of Input
##########################


##########################
# char_input
##########################
def char_input():
    while True:
        key,char = any_input()
        if char:
            return char

##########################
# end of char_input
##########################


##########################
# key_input
##########################
def key_input():
    while True:
        key,char = any_input()
        if key:
            return key,char
##########################
# end of key_input
##########################


##########################
# password_input
##########################
def password_input_(prompt='',*,star="*",space=" ",refesh="",end="\n",newline=True,encoding='cp1256'):
    unicodeble = {}
    password = ''
    proxy_string = [""]
    while True:
        sys.stdout.write('\x0D' + prompt + (''.join(proxy_string)) + refesh)
        c = msvcrt.getch()
        if c == b'\r':
            break
        elif c == b'\x08':
            CharInd = len(password)-1
            password = password[:-1]
            proxy_string = ["*"]*(len(password))
            if CharInd in unicodeble:del unicodeble[CharInd]
            sys.stdout.write('\x0D' + prompt + (''.join(proxy_string+list(space))) + refesh)
        else:
            try: proxy_string[len(password)] = star
            except IndexError: proxy_string += star
            try:
                if repr(c)[2:-1].startswith("\\x"): password += c.decode(encoding);raise UnicodeDecodeError("utf-8",c,len(password)-1,len(password),"invild input")
                else: password += c.decode()
            except UnicodeDecodeError as unicodeError:
                args = list(unicodeError.args)
                args[2] = len(password)-1
                args[3] = len(password)
                unicodeError.args = tuple(args)
                handler = []
                handler+= c
                unicodeError.handler = handler.copy()
                unicodeble[len(password)-1] = (unicodeError)
                proxy_string = ["*"]*(len(password))
    if newline: sys.stdout.write(end)
    return password,unicodeble
def filter(input,unicodes=None):
    if unicodes is None and len(input) == 2:
        unicodes = input[1]
        input = input[0]
    input = list(input)
    chars = []
    for index,value in enumerate(input):
        if index in unicodes and not (index <= -1):
            pass
        else:
            chars.append(value)
    return chars,unicodes
def join(listInput,unicodes=None,*,strInput="",sep=""):
    if unicodes is None and len(listInput) == 2:
        unicodes  = listInput[1]
        listInput = listInput[0]
    for char in listInput:
        strInput += str(sep)+str(char)
    return strInput
def password_input(*args,**kw):
    return join(filter(password_input_(*args,**kw)))
##########################
# end of password_input
##########################

##########################
# amazing_input
##########################
def amazing_input(object="",globals=None,locals=None,**kw):
    content = input(object)
    eval_  = kw.get("eval",eval)
    kw["kw"]=kw.get("kw",{}).update(dict(globals=globals,locals=locals))
    try:
        evaled = eval_(content,globals,locals) if (eval_==eval)\
         else eval_(content,*kw.get("args",[]),**kw.get("kw",{}))
        return evaled,type(evaled),None
    except Exception as e:
        try:   
            return content,type(evaled),e
        except NameError:
            return content,None,e
##########################
# end of amazing_input
##########################


##########################
# commandline_input
##########################

def cmdlexer(content,qutes=False,error=True,append=False):
    tokens = []
    get = 0
    index = 0
    tok = ""
    string = ""
    strend = ""
    #content = " "+content
    content+= " "
    for char in list(content):
        tok += char
        if char == " " and not get:
            if tok[:-1] and tok.strip(): tokens.append(tok[:-1])
            tok = ""
        elif (char == "\"" or char == "\'") and not get and content[index-1] != "\\":
            if (char == "\'" or char == "\"") and qutes: string += char;
            if tok.strip() and tok[:len(tok)-1] and not get:tokens.append(tok[:len(tok)-1])
            if get:
                get = 0
            else:
                strend = char
                get = 1
        elif get:
            if (char == "\'" or char == "\"") and qutes and char == strend and (content[index-1] != "\\"): string += char;
            if char == "\'" and strend == "'" and content[index-1] != "\\":
                tokens.append(string)
                get = 0
                string = ""
            elif char == "\"" and strend == "\"" and (content[index-1] != "\\"):
                tokens.append(string)
                get = 0
                string = ""
            else:
                string += char
            tok = ""
        index += 1
    if string.strip() and error: raise SyntaxError(f"EOL while scanning string literal: {string}")
    elif append and not error and string.strip(): tokens.append(string)
    return tokens,(string if string.strip() else None)

def commandline_input(prompt="",qutes=False,error=False,append=True):
    return cmdlexer(input(prompt),qutes=qutes,error=error,append=append)

##########################
# end of commandline_input
##########################