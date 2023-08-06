from decrypt import *
from show_form import *
from encrypt import *


def enter_existing_master_password_button(key, values, window):
    err = decrypt('../passwordFile.txt', key)

    if err:
        window['InvalidPasswordText'].Update(visible=True)
        values['EnterMasterPasswordInput'] = ''
    else:
        encrypt('../passwordFile.txt', key)

        show_form(window)

        window['EnterMasterPasswordText'].Update(visible=False)
        window['EnterMasterPasswordInput'].Update(visible=False)
        window['EnterExistingMasterPasswordButton'].Update(visible=False)
        window['showPasswordsButton'].Update(visible=True)

        window['InvalidPasswordText'].Update(visible=False)