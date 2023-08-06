import random
from decrypt import *
from insert_password import *
from encrypt import *


def enter_password_button_event(key, window, values):
    password_list = []
    err = decrypt('../passwordFile.txt', key)
    if err:
        window['InvalidPasswordText'].Update(visible=True)
        values['EnterMasterPasswordInput'] = ''
    else:
        print(password_list)
        for x in range(int(values['PasswordFormInput'])):
            temp_list = []
            uppercase_letter = chr(random.randint(65, 90))
            temp_list.append(uppercase_letter)

            lowercase_letter = chr(random.randint(97, 122))
            temp_list.append(lowercase_letter)

            digit = chr(random.randint(48, 57))
            temp_list.append(digit)

            hashtag = chr(35)
            temp_list.append(hashtag)

            exclamation = chr(33)
            temp_list.append(exclamation)

            password_list.append(random.choice(temp_list))
            pass
        else:
            with open('../passwordFile.txt', 'a') as f:
                insert_password(values['UsernameFormInput'],
                                values['WebsiteFormInput'],
                                password_list,
                                f)
            encrypt('../passwordFile.txt', key)
            pass
