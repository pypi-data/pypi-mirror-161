def insert_password(usernameforminput,
                    websiteforminput,
                    password_list,
                    f):
    if len(usernameforminput.strip()) > 0:
        f.write('Username: ' + usernameforminput + ' ')
    else:
        f.write('Username: N/A ')
    if len(websiteforminput.strip()) > 0:
        f.write('Website: ' + websiteforminput + ' ')
    else:
        f.write('Website:  N/A ')

    f.write('Password: ' + ''.join(password_list))
    f.write('\n')