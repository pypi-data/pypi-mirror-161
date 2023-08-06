

key,char = any_input () # wait for user input. returns ((char|key) or together)
char     = char_input() # wait for user input. returns char
key      = key_input () # wait for user input. returns key


password = password_input("Enter your password: ") # hide the input with (star="*")

type = amazing_input("enter a type: ") # returns a type "10"=>int("10")

cmd,laststr = commandline_input("enter a command>") # lex the command returns list,laststr "hello \"hi i am a big string\" more stuff" => (['hello', 'hi i am a big string', 'more', 'stuff'], None)

parserUrl,querys = urlparse_input("enter a url: ") # string to ParseUrl "https://google.com/kit?hi=1&yay=omg" => (ParseResult(scheme='https', netloc='google.com', path='/kit', params='', query='hi=1&yay=omg', fragment=''), {'hi': ['1'], 'yay': ['omg']})

# going to change the default check function
def check(i,x,y,z): # x is the input value
	if x.__class__.__name__== "int": # check if the type is int by name
		i.stop() # i = Input(); stop(the loop)
num = input_wait_for("int","enter a number",check=check) # wait for input type int,list,dict,etc  


def check(cls,input):
	input = input.lower()
	if input=="hello":
		print("hello")
	elif input=="yo":
		print("yo, bro")
	elif input=="good":
		print("me too")
	else:
		print("whats up?")
		return "no input" # return before we stop the input
	cls.stop() # stop the input loop
	return "bye"
output = check_input(prompt,check=check)
print(output) # output: bye

import re
def check_ragex(input,regex):
	if regex is None or re.match(regex,input) is not None:
		return True
	else:
		print("Invalid regex string")
		return False
regex_input(prompt="",regex=None,check_ragex=check_ragex)


limited_string = limit_input("prompt:",length=14) # Limit an input length return when the len(input) is equal to length

proc = subprocess_input("enter process command:") # run a child process. warpper for commandline_input
"""
another example subprocess_input(prompt="",process=None,*args,**kw):
	>>> subprocess_input("enter process command:",timeout=10,stdout=-1,process=subprocess.run)
	enter process command:python -c "print('Hello')"
	CompletedProcess(args=['python', '-c', "print('Hello')"], returncode=0, stdout=b'Hello\r\n')
"""

code = system_input("enter a command:") # run a commandline command returns the exit code

ignore_input() # a just input to ignore any inputs. help ("""ignore_input will wait for enter or ^C""")

f_t = yn_input("Do you want to eat some vegetables?(y/n):") # warpper for check_input """ yes|no input wait for the user to input ([yes,y,true] or [no,n,false]) returns booling"""
"""
another example yn_input(prompt=""):
	>>> yn_input("Do you want to eat some vegetables?(y/n):")
	Do you want to eat some vegetables?(y/n):what
	invalid option for (y/n). try again
	Do you want to eat some vegetables?(y/n):no
	False # returns False cuz i enter no
"""


{
'keys_': {'H': 'UP', 'P': 'DOWN', 'M': 'RIGHT', 'K': 'LEFT'},
'input_wait_for': <function input_wait_for at 0x000002075C30B9D0>,
'check_input': <function check_input at 0x000002075C30BA60>,
'limit_input': <function limit_input at 0x000002075C30BB80>,
'ignore_input': <function ignore_input at 0x000002075C30BC10>,
'subprocess_input': <function subprocess_input at 0x000002075C30BCA0>,
'system_input': <function system_input at 0x000002075C30BD30>,
'SubString': <function SubString at 0x000002075C2B1040>,
'cmdlexer': <function cmdlexer at 0x000002075C2B15E0>,
'input_': <function input at 0x000002075C263F70>, 
'any_input': <function any_input at 0x000002075C2B1160>,
'char_input': <function char_input at 0x000002075C2B11F0>, 
'key_input': <function key_input at 0x000002075C2B1280>,
'password_input_': <function password_input_ at 0x000002075C2B1310>,
'password_input': <function password_input at 0x000002075C2B14C0>,
'amazing_input': <function amazing_input at 0x000002075C2B1550>,
'commandline_input': <function commandline_input at 0x000002075C2B1670>,
'any_input_': <function any_input_ at 0x000002075C2B10D0>,
'String': <class 'inputkit.Input.String'>, 
'built_in_events_Input': <class 'inputkit.Input.built_in_events_Input'>,
'InputExit': <class 'inputkit.Input.InputExit'>, 
'InputDeadLock': <class 'inputkit.Input.InputDeadLock'>,
'Input': <class 'inputkit.Input.Input'>,
'urlparse_input': <function urlparse_input at 0x000002075C30B940>,
'urlparse_input_': <function urlparse_input_ at 0x000002075C30B8B0>,
'yn_input': <function yn_input at 0x000002075C30BAF0>
}



#_input = Input("Hello World!:",proxy_string=[],start=True)
#_input = Input("Hello World!:",proxy_string=[]).start()
#print(_input.input)

'''
# how to create attr 'proxy_string'
with Input("Hello World!:",proxy_string=[],extra_events=dict(),isdeadlock=True) as _input:
	_input.add_event("on_newline",built_in_events_Input.on_newline)
	@_input.event
	def on_update(cls,start="\x0D",deleted=False):
		if deleted:
			try:
				cls.proxy_string[len(cls)] = " "
				print(start+cls.prompt+"".join(cls.proxy_string),end="")
				del cls.proxy_string[len(cls)]
			except IndexError:
				cls.proxy_string = list(cls)
		print(start+cls.prompt+"".join(cls.proxy_string),end="")

	@_input.event
	def on_write(cls,module,prompt):
		cls.dispatch("update") # create an event
	@_input.event
	def on_start(cls):
		cls.running = True # start running

	@_input.event
	def on_read(cls,k,c):
		if c == b"\r": # pressed enter or ^M
			cls.stop() # stop running
		elif k == b"\x08":
			cls-=1
			cls.dispatch("update",deleted=True) # create an event
		elif k == b'\xe0' or k == b"\x00": # type ignore
			#key = parser_keys(c.decode())  # get key error if the key is not defind
			#print(key,"has been prassed")
			# Parser(UP = "H", DOWN = "P", RIGHT = "M", LEFT = "K")
			pass # we're going to ignore this.
		else:
			cls+=c.decode()
			cls.proxy_string=list(cls)
	@_input.event
	def on_close(cls,output):
		print(cls.proxy_string)

	output = _input.start()
	print()
	print(repr(output))
'''
