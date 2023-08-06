# this is a lib of python

you can use `syllib.__version__` to show the version

## for xueersi

uses `from syllib.xes import *` to use the api

### functions

#### in lib `syllib.xes.api`

function `get_cookies()`

**no arguments**

result: a string of cookies

function `get_run_token()`

**no arguments**

result: a string of token(in the cookies)


#### in lib `syllib.xes.msg`

function `send(mobile: int, content: str)`

mobile: the mobile number of who you want to send

content: a string of content what you want to send

result: a bool of success(True) or failed(False)

