#!/usr/bin/python3
"""Set Invoice Ninja admin password and email

Option:
    --pass=     unless provided, will ask interactively
    --email=    unless provided, will ask interactively
"""

import sys
import getopt
import bcrypt
from mysqlconf import MySQL

from dialog_wrapper import Dialog
import inithooks_cache


def usage(s=None):
    if s:
        print("Error:", s, file=sys.stderr)
    print("Syntax: %s [options]" % sys.argv[0], file=sys.stderr)
    print(__doc__, file=sys.stderr)
    sys.exit(1)


def main():
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], "h",
                                       ['help', 'pass=', 'email='])
    except getopt.GetoptError as e:
        usage(e)

    email = ""
    password = ""
    for opt, val in opts:
        if opt in ('-h', '--help'):
            usage()
        elif opt == '--pass':
            password = val
        elif opt == '--email':
            email = val

    if not password:
        d = Dialog('TurnKey Linux - First boot configuration')
        password = d.get_password(
            "Invoice Ninja Password",
            "Enter new password for the Invoice Ninja 'admin' account.")

    if not email:
        if 'd' not in locals():
            d = Dialog('TurnKey Linux - First boot configuration')

        email = d.get_email(
            "Invoice Ninja Email",
            "Enter email address for the Invoice Ninja 'admin' account.",
            "admin@example.com")

    inithooks_cache.write('APP_EMAIL', email)

    salt = bcrypt.gensalt()
    hashpass = bcrypt.hashpw(password.encode('utf8'), salt).decode('utf8')
    
    m = MySQL()
    m.execute('UPDATE ninja.user SET password=%s WHERE id=1;', (hashpass,))
    m.execute('UPDATE ninja.user SET username=%s WHERE id=1;', (email,))
    m.execute('UPDATE ninja.user SET email=%s WHERE id=1;', (email,))


if __name__ == "__main__":
    main()
