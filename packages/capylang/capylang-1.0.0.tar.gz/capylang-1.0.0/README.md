# Capylang
### Capylang is a pretty simple language.
### Here is an example of using Capylang.
```python
from capylang import capy
a = 5
b = 2
capy.help() # Prints the functions down
capy.log(str(capy.add(a,b))) # Prints 7 (also uses the add function)
capy.log(str(capy.sub(a,b))) # Prints 3 (also uses the subtract function)
capy.log(str(capy.multi(a,b))) # Prints 10 (also uses the multiply function)
capy.log(str(capy.div(a,b))) # Prints 2.5 (also uses the divide function)
capy.log(str(capy.hyp(a,b))) # Try this yourself for more info, check capy.help()
capy.log(str(capy.opp(a,b))) # Try this yourself for more info, check capy.help()
capy.log(str(capy.adj(a,b))) # Try this yourself for more info, check capy.help()
capy.auto_update(True) # Turns on auto updating. Auto updating is set to False by default.
```
### That's pretty much it for a basic tutorial of Capylang.