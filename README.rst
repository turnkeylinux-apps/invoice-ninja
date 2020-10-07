Invoice Ninja - Open Source Invoicing
=====================================

`Invoice Ninja`_ provides a platform for invoicing, quotes, expenses &
time-tracking. It is built on top of Laravel; a well known and highly
respected PHP framework, backed by MySQL.

Invoice Ninja handles:

- Client management
- Invoices
- Payments
- Recurring Invoices
- Credits
- Quotes
- Proposals
- Tasks
- Expenses
- Vendors
- Reports

Invoice Ninja is `extensively doumented`_. This TurnKey appliance also
includes all the standard features in `TurnKey Core`_, and on top of that:

- SSL support out of the box.
- `Adminer`_ administration frontend for MySQL (MariaDB) (listening on port
  12322 - uses SSL).
- `Postfix`_ MTA (bound to localhost) to allow sending of email.
- Webmin modules for configuring Apache2, PHP, MySQL and Postfix.

Credentials *(passwords set at first boot)*
-------------------------------------------

-  Webmin, SSH, MySQL: username **root**

-  Adminer: username **adminer**

- Invoice Ninja: username is email - set at firstboot

.. _Invoice Ninja: https://www.invoiceninja.org/
.. _extensively doumented: https://docs.invoiceninja.com/index.html
.. _TurnKey Core: https://www.turnkeylinux.org/core
.. _Adminer: https://www.adminer.org/
.. _Postfix: https://www.postfix.org/
