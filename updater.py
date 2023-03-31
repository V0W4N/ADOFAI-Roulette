import os, sys

import requests as req
from tkinter import messagebox


url = "https://github.com/V0W4N/ADOFAI-Roulette/releases/download/ADOFAI/Roulette.exe"
file = os.path.join(os.curdir, "Roulette.exe")


def main():
    print("Requesting file...")
    try:
        data = req.get(url)
        if data.ok:
            with open(file, "wb+") as f:
                f.write(data.content)
                return 1

        else:
            raise Exception
    except Exception:
        return 0



if __name__ == "__main__":
    executed = main()
    if not executed:
        messagebox.showwarning("Failed to get executable",
                               "Failed to get executable from github, you may need to download and launch it manually.\n"
                               "!!!REPORT THIS PLEASE!!!")
    else:
        messagebox.showinfo("Success!",
                             f"Successful update! The file now is in this directory.\n"
                             "Unfortunately, to avoid false-flagging by windows defender, i had to disable autoexecuting.\n"
                             "You will now need to launch Roulette.exe manually.")
    sys.exit()

