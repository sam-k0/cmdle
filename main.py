import requests
import datetime
import json
import enum
from typing import Dict, List
from colorama import init as colorama_init
from colorama import Fore
from colorama import Style

ALLOWED_CHARS = "abcdefghijklmnopqrstuvwxyz"

class CharStatus(enum.Enum):
    UNCHECKED = 0
    ABSENT = 1
    PRESENT = 2
    CORRECT = 3

class GuessResult(enum.Enum):
    WIN = 0
    LOSE = 1
    CONTINUE = 2

def get_daily_word():
    today = datetime.date.today()
    url = f"https://wordle.ピケ.コム/words.php?date={today.year}-{today.month:02d}-{today.day:02d}&limit=1"
    resp = requests.get(url)
    return json.loads(resp.text), resp.status_code

def is_allowed(text:str, words:list):
    "Checks if console input is valid"
    if len(text) == 5 and all(c in ALLOWED_CHARS for c in text.lower()) and text in words:
        return True
    return False

def clear():
    print(chr(27) + "[2J")

def update_chars(chars:dict,inpt:str, correct:str)-> dict:

    for i,c in enumerate(inpt):
        # check for exact match
        if correct[i] == c:
            chars[c] = CharStatus.CORRECT 
        elif c in correct: # present but not correct
            if chars[c] != CharStatus.CORRECT: # do not set previously correct to present
                chars[c] = CharStatus.PRESENT 
        elif c not in correct:
            chars[c] = CharStatus.ABSENT

    return chars


def draw_chars(chars:dict, guesses:list, correct:str):
    colors = [Fore.LIGHTWHITE_EX, Fore.LIGHTBLACK_EX, Fore.LIGHTYELLOW_EX, Fore.LIGHTGREEN_EX]
    print("Characters: ",end="")
    for c,s in chars.items():
        print(f"{colors[s.value]}{c.upper()}",end=" ")
    print(f"{Style.RESET_ALL}")

    # draw guesses        
    for i,g in enumerate(guesses):
        print(f"{i+1}: ",end="")
        for j,c in enumerate(g):
            col = 0
            # check for exact match
            if correct[j] == c:
                col = CharStatus.CORRECT.value 
            elif c in correct: # present but not correct
                col = CharStatus.PRESENT.value
            elif c not in correct:
                col = CharStatus.ABSENT.value


            print(f"{colors[col]}{c.upper()}",end=" ")
        print(f"{Style.RESET_ALL}")
    # remaining
    for i in range(5-len(guesses)):
        print(f"{'_'*5}")
        
        

if __name__ == "__main__":
    colorama_init()
    # Load dictionary of possible words
    possible_dict = []
    with open("dict.txt", "r") as f:
        possible_dict = f.readlines()
        possible_dict = [x.strip() for x in possible_dict]

    # daily word
    info, status = get_daily_word() # solution, editor
    info = info[0]
    if status != 200:
        print("Could not get daily word.")
        
    print("Today's editor:",info["editor"])

    guesses = []
    win = False

    chars:Dict[str, int] = {}
    for c in ALLOWED_CHARS:
        chars[c] = CharStatus.UNCHECKED # type: ignore
    

    while True:
       
        draw_chars(chars,guesses, info["solution"].lower())
        text = input("Enter your guess: ").lower()
        if is_allowed(text,possible_dict):
            guesses.append(text.lower())
            chars = update_chars(chars, text, info["solution"].lower())  # type: ignore

            if text == info["solution"].lower():
                win = True
                break
            elif len(guesses) == 5:
                win = False
                break   
        clear()
        
    draw_chars(chars,guesses, info["solution"].lower())
    if win:
        print("Congratulations! You won!")
    else:
        print("Lost.")