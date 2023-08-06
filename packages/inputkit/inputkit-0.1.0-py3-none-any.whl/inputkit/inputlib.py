import sys
import msvcrt
import traceback
from .inputs import *
byte__ = '\\x'

__all__ = ["String","built_in_events_Input","InputExit","InputDeadLock","Input"]


##########################
# any_input
##########################

def any_input_():
    """ any_input_ returns ((char|key) or together) as bytes """
    key = None
    char = None
    input = Input()
    inp = msvcrt.getch()
    char = input.CharIsByte(inp)
    key = input.KeyIsByte(inp)
    if key in [b"\xe0",b"\x00"]:
        char = msvcrt.getch()
    return key,char

def any_input():
    """ any_input returns ((char|key) or together). try to decode bytes """
    key,char = any_input_()
    try:
        return key.decode(),char.decode()
    except (UnicodeDecodeError,AttributeError):
        try:
            return key,char.decode()
        except (UnicodeDecodeError,AttributeError):
            return key,char

##########################
# end of any_input
##########################

##########################
# Input
##########################


class String:
    """ String class for more useg of str object """
    def __init__(self,string):
            self.string = string
    def __iter__(self):
        return iter(self.string)
    def __add__(self,other):
        self.string += other
        return self
    def __sub__(self,other):
        self.string = self.string[:other*-1]
        return self
    def __str__(self):
        return self.string
    def __getitem__(self,index):
        return self.string[index]
    def __getattr__(self,name):
        return getattr(self.string,name)
    def __len__(self):
        return len(self.string)
    def __repr__(self):
            return repr(self.string)

class built_in_events_Input(object):
	""" events made for Input handling """
	def on_write(self,msvcrt,prompt):
		for c in prompt:
			msvcrt.putwch(c)
		return prompt
	def on_newline(self,newline):
		if self.newline is not False:
			for c in self.newline:
				msvcrt.putwch(c)
	def on_start(cls):
		cls.run()
	def on_read(cls,k,c):
		if c == b"\r":
			cls.stop()
		elif k == b'\003' or k == b'\x03':
			raise KeyboardInterrupt
		elif k == b'\x1a':
			raise EOFError()
		elif k == b"\x08": # k == b"\b"
			cls-=1
			cls.dispatch("update",deleted=True)
		elif k == b'\xe0' or k == b"\x00": # type ignore
			#key = parser_keys(c.decode())
			#print(key,"has been prassed")
			# Parser(UP = "H", DOWN = "P", RIGHT = "M", LEFT = "K")
			pass # we're going to ignore this cuz its need time to make
		elif k is not None and c is None: # to ignore None char that can't be decoded
			return # type ignore
		else:
			cls+=c.decode()
			cls.proxy_string=list(cls)
	def on_update(cls,start="\x0D",deleted=False):
		if deleted:
			try:
				cls.proxy_string[len(cls)] = " "
				print(start+cls.prompt+"".join(cls.proxy_string),end="")
				del cls.proxy_string[len(cls)]
			except IndexError:
				cls.proxy_string = list(cls)
		print(start+cls.prompt+"".join(cls.proxy_string),end="")


class InputExit(Exception):
	""" when Input Exit unexceptly """
	def __init__(self,message,**kw):
		self.__dict__.update(kw)
		super(Exception,self).__init__(message)
	def __repr__(self):
	    try:
	        input = self.Input
	    except AttributeError:
	        input = ""
	    return f"InputExit({repr(input)})"
class InputDeadLock(InputExit):
	""" raise when Input class is not on deadlock mode """
	pass

class Input:
    """ Input API class for button listening. listen for button pressing in the console """
    def __init__(self,prompt="",start=False,**kw) -> None:
        self.__dict__.update(kw)
        self.input= kw.get("input",String(''))
        self.newline = kw.get("newline","\r\n")
        self.prompt = prompt
        self.extra_events = kw.get("extra_events",
        	{
            "on_write":[built_in_events_Input.on_write],
            "on_newline":[built_in_events_Input.on_newline],
            "on_start":[built_in_events_Input.on_start],
            })
        self.typed = False
        self.running = False
        self.isdeadlock = kw.get("isdeadlock",False)
        if start:
        	self.add_event("on_update",built_in_events_Input.on_update)
        	self.add_event("on_read",built_in_events_Input.on_read)
        	self.start()
    def IsByte(self,char):
        """ check if char is byte or char returns None if char is byte else char """
        if len(char) > 1 or len(char) < 0:
            raise ValueError(f"invalid char expected len of 1 but get {len(char)}")
        elif not isinstance(char,bytes):
            raise TypeError(f"invalid char expected to be bytes (not {char})."\
                .format(char=char.__class__.__name__))
        if (repr(char)[2:-1].startswith(byte__)): return None
        else: return char
    def CharIsByte(self,char):
        """ alies for IsByte """
        return self.IsByte(char)
    def KeyIsByte(self,key):
        """ check if key is byte or char returns None if key is not byte else key """
        c = self.IsByte(key)
        if c is None: return key
        else: return None
    def __enter__(self):
    	""" returns self """
    	return self
    def __exit__(self,cls,error,tracebacks):
    	""" if error raise InputExit else self """
    	if error is not None:
    		print(cls,error)
    		self.stop(1)
    		traceback.print_tb(tracebacks)
    		raise InputExit(f"input exited {repr(error)}",error=error,traceback=tracebacks,Input=self)
    	else:
    		return self
    def __iter__(self):
    	""" returns self input iter """
    	return iter(self.input)
    def __str__(self):
        """ returns self input str """
        return str(self.input)
    def __len__(self):
        """ returns self input len """
        return len(self.input)
    def __bool__(self):
        """ returns running """
        return self.running
    def __getitem__(self, item):
        """ get index of self input """
        return self.input[item]
    def __tuple__(self):
        """ returns tuple of self running and typed """
        return self.running,self.typed
    def __add__(self,other):
        """ add to self input """
        self.input += other
        return self
    def __sub__(self,other):
    	""" sub from self input """
    	self.input-=other
    	return self
    @property
    def tuple(self):
        """ alies for __tuple__ """
        return self.__tuple__()
    # event handle 
    def event(self,func,*args,**kw):
        """ add an event """
        return self.listen(*args,**kw)(func)
    def listen(self,*args,**kw):
    	""" add an event """
    	def inner(func):
    		name = func.__name__ if kw.get("name",None) is None else kw.get("name")
    		if name in self.extra_events:
    			self.extra_events[name].append(func)
    		else:
    			self.extra_events[name] = [func]
    	return inner
    def add_event(self,name=None,func=None):
    	""" add an event """
    	if func is None:
    		raise TypeError("Invalid function")
    	return self.event(func,name=name)
    def Eventhandle(self,function,*args,**kw):
    	""" event handler calling. that can be replaced safely """
    	return function(self,*args,**kw)
    def dispatch(self, event_name, *args,**kw):
    	""" dispatch events """
    	if "on_read" not in self.extra_events and not self.isdeadlock:
    		raise InputDeadLock("input is a dead lock")
    	ev = "on_"+event_name
    	for event in self.extra_events.get(ev,[]):
    		self.Eventhandle(event,*args,**kw)
    def start(self,*,any_input=any_input_,module=msvcrt):
        """ start inputing """
        self.dispatch("start")
        self.dispatch("write",module,self.prompt)
        while self.running:
            self.typed = False
            char,key = any_input()
            self.dispatch("read",char,key)
            self.dispatch("update")
            self.typed = True
        self.dispatch("newline",self.newline)
        self.dispatch("close",self.input)
        return self.input
    def stop(self,code=0):
        """ stop inputing """
        if self.running:
            self.running = False
            self.dispatch("stop",code,self.input)
    def run(self):
        if not self.running:
            self.running = True
            self.dispatch("run")
    def __repr__(self):
        """ repr of Input """
        repr_ = "Input("
        if self.input:
            repr_+= "input="+repr(self.input)
        if self.running:
            if self.input:
                repr_+= ","
            repr_+= "running="+str(self.running)
        repr_ += ")"
        return repr_

##########################
# end of Input
##########################