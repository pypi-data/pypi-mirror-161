from operator import sub, truediv
from functools import reduce
from math import sqrt, prod
import os
from .http import check
from .cjson import set_config
global __version__, __functions__
__version__ = "1.0.1"
#Functions
__functions__ = f'''
Capylang v{__version__} help.
Running Capylang directly results in invalid class usage. To be provided with assistance while using Capylang, run capy.help() or see the commands below.

capy.auto_update()
Sets the auto update setting. True or False.

capy.help()
1. The function prints out all the functions in the current module.

capy.log()
1. The function takes in one argument: text, the text to be printed
2. The function then prints the text to the console.

capy.add()
1. The function takes in any number of arguments.
2. The function then returns the product of the addition.

capy.sub()
1. The function takes in any number of arguments.
2. The function subtracts all arguments from each other in chronological order.
3. The function then returns the product of the subtraction.

capy.multi()
1. The function takes in any number of arguments.
2. The function multiplies all the arguments together in chronological order.
3. The function then returns the product of this multiplication.
to get these explanations right click on a selection and click explain code

capy.hyp()
1. The function takes 2 arguments, opposite and adjacent.
2. The function adds the squared value of the 2 sides together.
3. The function then returns the square root of this value.

capy.opp()
1. The function takes 2 arguments, hypotenuse and adjacent.
2. The function subtracts the squared value of the 2 sides from eachother.
3. The function then returns the square root of this value.

capy.adj()
1. The function takes 2 arguments, hypotenuse and opposite.
2. The function subtracts the squared value of the 2 sides from eachother.
3. The function then returns the square root of this value.

capy.div()
1. The function takes in a variable number of arguments.
2. The function then divides the first argument by the second argument, then divides the result by the third argument, and so on.
3. The function then returns the result.
'''
print(f"Capylang v{__version__}. Made by Anistick. capylang.anistick.com.")
print("Use capy.help() for commands.")
class capy(object):
  
  def __init__(self):
    print("Please do not call Capylang directly. Use capy.help() for more info.")
    
  def help():
    print(__functions__)
    
  def log(text):
    print(text)

  def add(*args):
    return sum(args)
  
  def sub(*args):
    return reduce(sub, args)
  
  def multi(*args):
    return prod(args)
  
  def div(*args):
    return reduce(truediv, args)

  def hyp(opp, adj):
    return sqrt(opp ** 2 + adj ** 2)

  def opp(hyp, adj):
    return sqrt(hyp ** 2 + adj ** 2)
    
  def adj(hyp, opp):
    return sqrt(hyp ** 2 + opp ** 2)
  
  def update():
    os.system(f"pip install --upgrade capylang")

  def auto_update(value):
    set_config("AUTO_UPDATE",value)
    print("Success.")

if check(__version__) == True:
  capy.update()
else:
  check(__version__)