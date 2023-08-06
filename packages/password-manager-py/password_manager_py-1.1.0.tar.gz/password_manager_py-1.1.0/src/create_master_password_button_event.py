from encrypt import *
from show_form import *


def create_master_password_button_event(key, window, os):
    if not os.path.exists('../passwordFile.txt'):
        open('../passwordFile.txt', 'w')

    encrypt('../passwordFile.txt', key)

    show_form(window)

    window['CreateMasterPasswordText'].Update(visible=False)
    window['CreateMasterPasswordInput'].Update(visible=False)
    window['CreateMasterPasswordButton'].Update(visible=False)
    window['showPasswordsButton'].Update(visible=True)