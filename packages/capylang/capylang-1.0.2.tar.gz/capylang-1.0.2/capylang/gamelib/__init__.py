from .randg import rand
from .hangman import hangman
from ..terminal import clear
from .uno import uno
from .wordle import wordle
from colorama import Fore as fore

def start():

  clear()
  
  def customisation():

    clear()

    style = int(input('''What colour would you like the game to be in?
    
[1] Red
[2] Blue
[3] Green
[4] Yellow
[5] White

'''))


    if style == 1:
      print(f'{fore.RED}')
    elif style == 2:
      print(f'{fore.BLUE}')
    elif style == 3:
      print(f'{fore.LIGHTGREEN_EX}')
    elif style == 4:
      print(f'{fore.LIGHTYELLOW_EX}')
    else:
      print(f'{fore.WHITE}')

  game = int(input('''What game would you like to play? 
  
[1] Uno
[2] Hangman
[3] Guess the Number
[4] Wordle
[5] Customization

'''))

  if game == 1:
    uno()
  if game == 2:
    hangman()
  if game == 3:
    rand()
  if game== 4:
   wordle()
  if game == 5:
    customisation()
    start()
  else:
    start()