from colorama import Fore

def colorget():
    from random import choice
    return choice([Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN,
    Fore.BLUE,Fore.LIGHTBLUE_EX, Fore.LIGHTCYAN_EX, Fore.LIGHTGREEN_EX,
    Fore.LIGHTMAGENTA_EX,Fore.LIGHTRED_EX,
    Fore.LIGHTYELLOW_EX])

def colorout(text):
    print(f"{colorget()}{text}{Fore.RESET}")

# color = "red" "yellow" "green" "cyan" "blue" 
# "lightblue_ex" "lightcyan_ex" "lightgreen_ex"
# "lightmagenta_ex" "lightred_ex" "lightyellow_ex"
def anycolorout(text, color):
    exec(f"print(Fore.{color.upper()} + '{text}' + Fore.RESET)")

def infoout(text):
    anycolorout(text, "blue")

def warningout(text):
    anycolorout(text, "yellow")

def errorout(text):
    anycolorout(text, "red")
