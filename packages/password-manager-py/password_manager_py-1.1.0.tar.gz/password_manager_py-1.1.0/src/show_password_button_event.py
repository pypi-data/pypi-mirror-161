from decrypt import *
import subprocess as sp
from encrypt import *


def show_password_button_event(key, window, values):
    with open('./../passwordFile.txt') as f:
        err = decrypt('./../passwordFile.txt', key)
        if err:
            window['InvalidPasswordText'].Update(visible=True)
            values['EnterMasterPasswordInput'] = ''
        else:
            program_name = "notepad.exe"
            file_name = "./../passwordFile.txt"
            process = sp.Popen([program_name, file_name])
            exitcode = process.wait()
            if exitcode == 0:
                encrypt('./../passwordFile.txt', key)