from random import randrange as rr
from string import ascii_letters as l
import sys
import subprocess
from webbrowser import open
import webbrowser
from time import sleep as sl
from subprocess import run

tabs = int(sys.argv[1])

def create_term():
    term = ""
    for i in range(9):
        term += l[rr(len(l) - 4)]

    return term

def open_tabs():
    base_url = "https://www.bing.com/search?q=como "
    end_url = "&form=TSASDS"

    for i in range(tabs):
        search = base_url + create_term() + end_url
        webbrowser.open(search)
        #print(f"ID: {i} -> {search}")
        sl(7)
    
    close_tabs()

def close_tabs():
    for i in range(tabs):
        #print(f"ID: {i} -> tab closed")
        subprocess.run(["ydotool" , "key", "29:1", "17:1", "17:0", "29:0"])
        sl(.5)
    print("TUDO FEITO")



open_tabs()
