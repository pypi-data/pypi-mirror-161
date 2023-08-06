from urllib.parse import urlparse, parse_qs
from .inputs import *
from .inputlib  import Input,InputExit
import subprocess
import os
import sys
import re
from typing import Callable,Any

dataTypes_ = [ str, int, float, list, dict, tuple, set, bool ]
dataTypes  = {                                               } 

for datatype in dataTypes_:
	dataTypes[datatype.__name__] = datatype

keys_ = dict(H = "UP", P = "DOWN", M = "RIGHT", K = "LEFT")

__all__ = ["keys_","input_wait_for","check_input","limit_input","ignore_input","subprocess_input","system_input","urlparse_input","urlparse_input_","yn_input","regex_input"]

def parser_keys(key:str):
	""" parser_keys for Input class. dict(H = "UP", P = "DOWN", M = "RIGHT", K = "LEFT")"""
	return keys_[key]

def urlparse_input_(URL:str):
	""" perse str as url """
	parsed_url = urlparse(URL)
	querys = parse_qs(parsed_url.query)
	return parsed_url,querys
def urlparse_input(value:str="",input:Callable=input,*args,**kw):
	""" perse input as url """
	return urlparse_input_(input(value,*args,**kw))

def input_wait_for(wait_for:str,prompt:str="",*,check:Callable=None,globals=None,locals=None,**kw):
	""" wait for input type int,list,dict,etc """ 
	if wait_for not in dataTypes and kw.get("exception",True):
		raise ValueError(f"Invalid type {wait_for}")
	if check is None:
		def check(i,x,y,z):
			if x.__class__.__name__== wait_for:
				i.running=False
	input = Input(input="",isdeadlock=True)
	input.running = True
	amazing_input = kw.get('input',amazing_input)
	while input.running:
		evaled,type_,err = amazing_input(prompt,globals,locals)
		check(input,evaled,type_,err)
	return evaled

def check_input(prompt:str="",check:Callable=None,input:Callable=input):
	""" when enter an input. the check function will be called """
	if check is None:
		raise TypeError("check is a required argument")
	input_class = Input(input="",isdeadlock=True)
	input_class.running = True
	while input_class.running:
		C_input = input(prompt)
		evaled = check(input_class,C_input)
	return evaled

def yn_input(prompt:str=""):
	""" yes|no input wait for the user to input ([yes,y,true] or [no,n,false]) returns booling """
	def check(cls,input):
		input = input.lower().strip()
		if   input in ["y","true","yes"]:
			cls.stop()
			return True
		elif input in ["n","false","no"]:
			cls.stop()
			return False
		else:
			print("invalid option for (y/n). try again")
		return False
	return check_input(prompt,check=check)

def regex_input(prompt:Any="",regex:str=None,check_ragex:Callable=None):
	""" regex with input """
	if check_ragex is None:
		def check_ragex(input,regex):
			if regex is None:
				return True
			return re.fullmatch(regex, str(input)) is not None
	def check(cls,input,regex):
		if check_ragex(input,regex):
			cls.stop()
			return input
	return check_input(prompt,check=lambda cls, input: check(cls,input,regex))


try:
	pass
except Exception as e:
	raise e
def limit_input(prompt:str="",length:int=None,end:str="\n"): # Test input
	""" Limit an input length return when the input is equal to length """
	if length is None:
		raise TypeError("length is required argument")
	string = ""
	point_zore = 0
	keys = []
	sys.stdout.write('\x0D' + prompt + (string))
	while len(string) != int(length):
			key,char = any_input()
			if str(char) == "\r":
				break
			elif key in [b'\x03', b'\x1a']:
				raise InputExit("exit keys have been passed {key}".format(key=key),key=key,input=string)
			elif key == b"\x08":
				string=string[:-1]
				if string.strip():
					sys.stdout.write('\x0D'+ prompt + (string) + " ")
					point_zore = 1
				elif point_zore:
					sys.stdout.write('\x0D' + prompt + (string) + " ")
					point_zore = 0
			elif isinstance(char,str) and key is None:
				string+=str(char)
			sys.stdout.write('\x0D' + prompt + (string))
	sys.stdout.write('\x0D' + prompt + (string)+end)
	return string

def ignore_input(): # Test input
	""" ignore_input will wait for enter or ^C """
	char = None
	key  = None
	while char != b"\r" or key == b"\003":
		key,char = any_input_()

def subprocess_input(prompt:Any="",process=None,*args,**kw):
	""" create a subprocess returns process """
	if process is None: process = subprocess.run
	return process(commandline_input(prompt)[0],*args,**kw)

def system_input(prompt:Any=""):
	""" normal input with os.system """
	return os.system(input(prompt))
