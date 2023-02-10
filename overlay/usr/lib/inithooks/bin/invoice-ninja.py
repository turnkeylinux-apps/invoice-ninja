#!/usr/bin/python3
"""Set Invoice Ninja admin password, email and domain

Option:
    --pass=     unless provided, will ask interactively
    --api-secret=
                when email, pass and domain are set, but not api-secret,
                it will be skipped. If api-secret unset plus any one or
                more of email, pass and/or domain unset, it will be asked
                interactively
    --email=    unless provided, will ask interactively
    --domain=   unless provided, will ask interactively
                DEFAULT=www.example.com
                if http desired, then include the schema; otherwise
                will default to https
"""

import sys
import getopt
import bcrypt
import subprocess
import string
import secrets
import re

from mysqlconf import MySQL
from libinithooks.dialog_wrapper import Dialog
from libinithooks import inithooks_cache

DEFAULT_DOMAIN = 'www.example.com'


def usage(s=None):
    if s:
        print("Error:", s, file=sys.stderr)
    print("Syntax: %s [options]" % sys.argv[0], file=sys.stderr)
    print(__doc__, file=sys.stderr)
    sys.exit(1)


def random_str(length=32):
    chars = string.ascii_letters + string.digits
    return "".join(secrets.choice(chars) for i in range(length))


def check_str(text):
    regex = r'^[a-zA-Z0-9]*$'
    if re.search(regex, text):
        return True
    else:
        return False


def main():
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], "h",
                                       ['help', 'pass=', 'email=',
                                        'api-secret=', 'domain='])
    except getopt.GetoptError as e:
        usage(e)

    email = ""
    password = ""
    api_secret = ""
    domain = ""
    for opt, val in opts:
        if opt in ('-h', '--help'):
            usage()
        elif opt == '--pass':
            password = val
        elif opt == '--api-secret':
            api_secret = val
        elif opt == '--email':
            email = val
        elif opt == '--domain':
            domain = val

    interactive = False if email and password and domain else True

    if not password:
        d = Dialog('TurnKey Linux - First boot configuration')
        password = d.get_password(
            "Invoice Ninja Password",
            "Enter new password for the Invoice Ninja 'admin' account.")

    if not api_secret and interactive:
        d = Dialog('TurnKey Linux - First boot configuration')
        set_api_secret = d.yesno(
            "Invoice Ninja API Secret",
            "Do you want to set an API secret?\n\n"
            "To use Invoice Ninja API, an API secret needs to be set."
            " Note that the secret will also be required when logging in via"
            " UI.",
            yes_label="Set API Secret", no_label="Skip")
        if set_api_secret:
            gen_secret = d.yesno(
                "Invoice Ninja API Secret",
                "Do you wish to generate an API secret, or set it manually?",
                yes_label="Generate", no_label="Enter Manually")
            if gen_secret:
                api_secret = random_str()
                d.msgbox("Invoice Ninja API Secret",
                         f"API secret is:\n\n{api_secret}\n\n"
                         "Note the API secret is stored in plain text in the"
                         " .env file.")
            else:
                while True:
                    api_secret = d.get_input(
                        "Invoice Ninja API Secret",
                        "Set an Invoice Ninja API secret.\n\n"
                        "Please use upper case, lower case and digits only,"
                        " the longer the better (32+ chars recommended).",
                        '')
                    if check_str(api_secret):
                        break
                    else:
                        d.error("Must only only contain upper case, lower"
                                " case and/or digits")

    if not email:
        if 'd' not in locals():
            d = Dialog('TurnKey Linux - First boot configuration')

        email = d.get_email(
            "Invoice Ninja Email",
            "Enter email address for the Invoice Ninja 'admin' account.",
            "admin@example.com")

    if not domain:
        if 'd' not in locals():
            d = Dialog('TurnKey Linux - First boot configuration')

        domain = d.get_input(
            "Invoice Ninja Domain",
            "Enter the domain to serve Invoice Ninja.\n\n"
            "To use plain HTTP - prefix with 'http://'",
            DEFAULT_DOMAIN)

    if domain == "DEFAULT":
        domain = DEFAULT_DOMAIN

    if domain.startswith('http://'):
        url = domain.rstrip('/')
        email_domain = domain.rstrip('/')[7:]
    elif domain.startswith('https://'):
        url = domain.rstrip('/')
        email_domain = domain.rstrip('/')[8:]
    else:
        url = f"https://{domain.rstrip('/')}"
        email_domain = domain.rstrip('/')
    if email_domain.startswith('www.'):
        email_domain = email_domain[4:]

    conf = "/var/www/invoiceninja/.env"
    lines = []
    with open(conf) as fob:
        for line in fob:
            if line.startswith('APP_URL='):
                line = f"APP_URL={url}\n"
            elif line.startswith('MAIL_FROM_ADDRESS='):
                line = f"MAIL_FROM_ADDRESS='ninja@{email_domain}'\n"
            elif line.startswith('API_SECRET='):
                line = f"API_SECRET={api_secret}\n"
            lines.append(line)
    with open(conf, 'w') as fob:
        fob.writelines(lines)

    inithooks_cache.write('APP_DOMAIN', domain)
    inithooks_cache.write('APP_EMAIL', email)

    salt = bcrypt.gensalt()
    hashpass = bcrypt.hashpw(password.encode('utf8'), salt).decode('utf8')

    m = MySQL()
    m.execute('UPDATE ninja.users SET password=%s WHERE id=1;', (hashpass,))
    m.execute('UPDATE ninja.users SET email=%s WHERE id=1;', (email,))

    subprocess.run(['turnkey-artisan', 'optimize'],
                   capture_output=True, text=True)
    subprocess.run(['systemctl', 'restart', 'apache2'])


if __name__ == "__main__":
    main()
