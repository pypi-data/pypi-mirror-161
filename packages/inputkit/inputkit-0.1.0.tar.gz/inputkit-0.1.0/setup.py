from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  "Intended Audience :: Developers",
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'Operating System :: Microsoft :: Windows',
  "Intended Audience :: Developers",
  'Programming Language :: Python :: 3',
  'License :: OSI Approved :: MIT License'
]
__version__ = "0.1.0"
__author__ = 'Alawi Hussein Adnan Al Sayegh'
__description__ = 'library of input functions. and an input API'
__license__ = """
Copyright 2022 "Alawi Hussein Adnan Al Sayegh"
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
and the names are copyrighted
"""
setup(
  name='inputkit',
  version=__version__,
  description=__description__,
  long_description=open('README.md').read() + "\n\n" + open("CHANGELOG.txt").read(),
  long_description_content_type='text/markdown',
  url='',  
  author=__author__,
  author_email='programming.laboratorys@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='inputs,inputing,inputed,input,inputtools,tools,toolkit,tooling,useful_input,useful', 
  packages=find_packages(),
  install_requires=['stopit','psutil'] 
)