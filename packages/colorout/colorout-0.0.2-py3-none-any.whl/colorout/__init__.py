def colorget():
    from colorama import Fore
    from random import choice
    return choice([Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN,
    Fore.BLUE,Fore.LIGHTBLUE_EX, Fore.LIGHTCYAN_EX, Fore.LIGHTGREEN_EX,
    Fore.LIGHTMAGENTA_EX,Fore.LIGHTRED_EX,
    Fore.LIGHTYELLOW_EX])

def colorout(text):
    from colorama import Fore
    print(f"{colorget()}{text}{Fore.RESET}")
