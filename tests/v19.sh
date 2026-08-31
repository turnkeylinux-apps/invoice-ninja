#!/bin/bash
set -euo pipefail

result=${TKL_TEST_RESULT:?}
password=${TKL_TEST_APP_PASS:?}
work=/run/tkl-v19-tests/invoice-ninja
mkdir -p "$work"

systemctl --quiet is-active apache2.service mariadb.service supervisor.service
grep -q '\[40invoice-ninja\] successfully completed' /var/log/inithooks.log
curl -kfsS --resolve www.example.com:443:127.0.0.1 \
    https://www.example.com/ >"$work/home.html"
grep -Eqi 'invoice|ninja|login' "$work/home.html"

printf '%s' "$password" | python3 -c '
import json
import ssl
import sys
import urllib.request

secret = ""
for line in open("/var/www/invoiceninja/.env"):
    if line.startswith("API_SECRET="):
        secret = line.split("=", 1)[1].strip().strip("\"\047")
request = urllib.request.Request(
    "https://127.0.0.1/api/v1/login",
    data=json.dumps({"email": "admin@example.invalid", "password": sys.stdin.read()}).encode(),
    headers={"Content-Type": "application/json", "X-API-SECRET": secret,
             "Host": "www.example.com"},
)
context = ssl._create_unverified_context()
with urllib.request.urlopen(request, context=context) as response:
    assert response.status == 200
    open(sys.argv[1], "wb").write(response.read())
' "$work/login.json"
grep -Eq 'token|user|account' "$work/login.json"

test "$(cat /var/www/invoiceninja/VERSION.txt)" = 5.13.36
runuser -u www-data -- test ! -w /var/www/invoiceninja/artisan
runuser -u www-data -- test ! -w /var/www/invoiceninja/.env
runuser -u www-data -- touch /var/www/invoiceninja/storage/.tkl-v19-write-test
runuser -u www-data -- rm /var/www/invoiceninja/storage/.tkl-v19-write-test
runuser -u www-data -- /var/www/invoiceninja/vendor/bin/snappdf convert \
    --html '<h1>TurnKey QA</h1>' /var/www/invoiceninja/storage/qa-v19.pdf
test -s /var/www/invoiceninja/storage/qa-v19.pdf
rm -f /var/www/invoiceninja/storage/qa-v19.pdf

systemctl restart mariadb.service apache2.service supervisor.service
curl -kfsS --resolve www.example.com:443:127.0.0.1 \
    https://www.example.com/ >/dev/null
! grep -R -F -- "$password" /var/log/inithooks.log /var/log/invoiceninja 2>/dev/null

cat >"$result" <<EOF
package_source=official Invoice Ninja v5.13.36 and Snappdf Chromium archives pinned by SHA-256
installed_version=5.13.36
runtime_checks=Apache, MariaDB and worker services, firstboot completion, HTTPS page, API admin login, PDF generation, restart, ownership boundaries, password log hygiene
updater_command=supervised official Invoice Ninja release replacement
updater_result=installed version unchanged during QA
updater_channel=official Invoice Ninja stable releases
integrity_evidence=Invoice Ninja e10bea262a57b947c4f6b3a3c29bbe54e9efa09322f34dc3c0294bf8ca8007b8 and Snappdf bc241a3a17df91dff21d57326ce5c8bf6f8ef55b8384d94e0c1007892fba2868
EOF
