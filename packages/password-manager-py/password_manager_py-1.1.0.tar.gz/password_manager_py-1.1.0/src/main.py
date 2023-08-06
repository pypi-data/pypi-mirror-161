import os.path
import PySimpleGUI as sg

from generate_key import *
from check_for_salt import *
from show_password_button_event import *
from enter_existing_master_password_button import *
from create_master_password_button_event import *
from enter_password_button_event import *
from build_layout import *

global key

sg.theme('DarkAmber')

layout = build_layout(sg)

window = sg.Window('Password Manager', layout, finalize=True)

check_for_salt(os, window)

while True:
    global masterPassword
    event, values = window.read()

    if event == sg.WIN_CLOSED or event == 'Cancel':  # if user closes window or clicks cancel
        break

    if event == 'showPasswordsButton':
        show_password_button_event(key, window, values)

    if event == 'EnterExistingMasterPasswordButton':
        key = generate_key(values['EnterMasterPasswordInput'], load_existing_salt=True)
        enter_existing_master_password_button(key, values, window)

    if event == 'CreateMasterPasswordButton':
        key = generate_key(values['CreateMasterPasswordInput'])
        create_master_password_button_event(key, window, os)

    if event == 'EnterPasswordButton':
        enter_password_button_event(key, window, values)