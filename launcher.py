import os, sys

import requests as req
from tkinter import messagebox


url = "https://github.com/V0W4N/ADOFAI-Roulette/blob/bbda10c8e85719f07d5de592a08197d0ac43d5c9/dist/Roulette.exe?raw=true"
file = os.path.join(os.getenv('APPDATA'), "Roulette.exe")


def main():
    print("Requesting file...")
    try:
        data = req.get(url)
        if data.ok:
            with open(file, "wb+") as f:
                f.write(data.content)

        else:
            raise Exception
    except Exception:
        messagebox.showwarning("Failed to get executable",
                               "Failed to get executable from github, will attempt to launch previously installed version\n"
                               "Please report this issue")


    try:
        os.execv(file, ['h'])
        return 1
    except Exception:
        return 0


if __name__ == "__main__":
    executed = main()
    if not executed:
        messagebox.showerror("Execution failed!",
              "Execution failed! There's no previously downloaded Roulette.exe file in %appdata% or it has been corrupted\n"
              "Make sure you have access to the internet (if github is not down)\n"
              "or download the roulette and run it manually.\n"
              "!!!REPORT THIS IN ISSUES!!!")
    sys.exit()

