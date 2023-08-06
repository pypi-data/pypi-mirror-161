def check_for_salt(os, window):
    if os.path.exists('./../salt.salt'):
        window['EnterMasterPasswordText'].Update(visible=True)
        window['EnterMasterPasswordInput'].Update(visible=True)
        window['EnterExistingMasterPasswordButton'].Update(visible=True)
    else:
        window['CreateMasterPasswordText'].Update(visible=True)
        window['CreateMasterPasswordInput'].Update(visible=True)
        window['CreateMasterPasswordButton'].Update(visible=True)