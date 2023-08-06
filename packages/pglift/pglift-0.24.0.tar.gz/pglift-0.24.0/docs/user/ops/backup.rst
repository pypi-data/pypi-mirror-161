Backup
======

Instances
---------

Backup
~~~~~~

The ``pglift instance`` command line entry point exposes ``backup`` and
``restore`` commands to respectively perform instance-level backup and
restoration using selected PITR tool, currently pgBackRest_.

Assuming we have a ``main`` instance running:

.. code-block:: console

    $ pglift instance status main
    running

The ``instance backup`` command can be used as follows:

.. code-block:: console

    $ pglift instance backup main
    INFO     backing up instance with pgBackRest

The type of backup (full, incremental or differential) can be specified
through ``--type [full|incr|diff]`` option. By default, an incremental backup
would be performed, unless no prior backup exists in which case pgBackRest
will switch to a full backup.

The ``backups`` command can be used to list available backups:

.. code-block:: console

    $ pglift instance backups main
                                                     Available backups for instance 14/main
    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┓
    ┃ label                             ┃ size    ┃ repo_size ┃ date_start                ┃ date_stop                 ┃ type ┃ databases              ┃
    ┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━┩
    │ 20220518-102816F_20220518-103636I │ 49.4MiB │ 5.1MiB    │ 2022-05-18 10:36:36+02:00 │ 2022-05-18 10:36:39+02:00 │ incr │ myapp, postgres        │
    │ 20220518-102816F_20220518-103527I │ 73.0MiB │ 7.0MiB    │ 2022-05-18 10:35:27+02:00 │ 2022-05-18 10:35:31+02:00 │ incr │ bench, myapp, postgres │
    │ 20220518-102816F                  │ 49.4MiB │ 5.1MiB    │ 2022-05-18 10:28:16+02:00 │ 2022-05-18 10:28:21+02:00 │ full │ bench, postgres        │
    └───────────────────────────────────┴─────────┴───────────┴───────────────────────────┴───────────────────────────┴──────┴────────────────────────┘


Restore
~~~~~~~

To restore the PostgreSQL instance, use ``instance restore`` command (the
instance must not be running):

.. code-block:: console

    $ pglift instance stop main
    $ pglift instance restore main
    INFO     restoring instance with pgBackRest

With no option, the ``restore`` action will use the latest backup and replay
all available WAL.

With ``--label`` option, the ``restore`` action does not replay WAL and the
instance is restored at its state targeted by specified label.

.. code-block:: console

    $ pglift instance restore main --label 20220518-102816F_20220518-103527I
    INFO     restoring instance with pgBackRest


.. code-block:: console

    $ pglift database list
    ┏━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┓
    ┃ name      ┃ owner    ┃ encoding ┃ collation ┃ ctype ┃ acls                    ┃ size    ┃ description             ┃ tablespace       ┃
    ┡━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━┩
    │ bench     │ postgres │ UTF8     │ C         │ C     │                         │ 23.6MiB │                         │ name: pg_default │
    │           │          │          │           │       │                         │         │                         │ location:        │
    │           │          │          │           │       │                         │         │                         │ size: 72.6MiB    │
    │ myapp     │ postgres │ UTF8     │ C         │ C     │                         │ 23.6MiB │                         │ name: pg_default │
    │           │          │          │           │       │                         │         │                         │ location:        │
    │           │          │          │           │       │                         │         │                         │ size: 72.6MiB    │
    │ postgres  │ postgres │ UTF8     │ C         │ C     │                         │ 8.6MiB  │ default administrative  │ name: pg_default │
    │           │          │          │           │       │                         │         │ connection database     │ location:        │
    │           │          │          │           │       │                         │         │                         │ size: 72.6MiB    │
    │ template1 │ postgres │ UTF8     │ C         │ C     │ =c/postgres,            │ 8.4MiB  │ default template for    │ name: pg_default │
    │           │          │          │           │       │ postgres=CTc/postgres   │         │ new databases           │ location:        │
    │           │          │          │           │       │                         │         │                         │ size: 72.6MiB    │
    └───────────┴──────────┴──────────┴───────────┴───────┴─────────────────────────┴─────────┴─────────────────────────┴──────────────────┘

.. note::
   Often when performing instance restore, it can be useful to examine
   pgBackRest command output. This can be achieved by setting the log-level to
   DEBUG in ``pglift`` command (e.g. ``pglift -L debug instance restore``).

.. _database-dumps:

Databases
---------

Dump
~~~~

`pglift` also provides a convenient way to backup a database for an instance.

Assuming we have a `main` instance running with a `myapp` database.

The `database dump` command can be used as follows:

.. code-block:: console

    $ pglift database -i main dump myapp
    INFO     backing up database 'myapp' on instance 14/main

By default, this command runs the pg_dump_ utility and creates a dump in the
`dumps_directory` (with a name including the current date and time).

The `dumps_directory` and `dump_commands` can be adjusted in the site settings
(see :doc:`/user/setup/settings`):

.. code-block:: yaml

   dumps_directory: dumps/{instance.version}-{instance.name}
   dump_commands:
     -
       - "{bindir}/pg_dump"
       - -Fc
       - -f
       - "{path}/{dbname}_{date}.dump"
       - -d
       - "{conninfo}"

Here's an example of a command that simply dumps the database in SQL format:

.. code-block:: yaml

   dump_commands:
     -
       - "{bindir}/pg_dump"
       - -f
       - "{path}/{dbname}_{date}.sql"
       - -d
       - "{conninfo}"

When using pg_dump_, some important information is not dumped (for example
roles or tablespaces definitions). If this is a limitation, pg_back_ can be
used instead:

.. code-block:: yaml

   dump_commands:
     -
       - /path/to/pg_back
       - -B
       - "{bindir}"
       - -b
       - "{path}"
       - -d
       - "{conninfo}"
       - "{dbname}"

List dumps
~~~~~~~~~~

Database dumps can be listed with the following command:

.. code-block:: console

    $ pglift database -i main dumps
    ┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
    ┃ id               ┃ dbname ┃ date                      ┃
    ┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
    │ erp_43529c086f   │ erp    │ 2022-07-10 08:38:35+02:00 │
    │ erp_22066ad88f   │ erp    │ 2022-07-11 08:41:24+02:00 │
    │ myapp_12b04d9d56 │ myapp  │ 2022-07-06 10:01:32+02:00 │
    │ myapp_529a0223cb │ myapp  │ 2022-07-06 10:31:58+02:00 │
    │ myapp_e18e6661c8 │ myapp  │ 2022-07-08 11:24:47+02:00 │
    └──────────────────┴────────┴───────────────────────────┘

This list can be limited to one database:

.. code-block:: console

    $ pglift database -i main dumps erp
    ┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
    ┃ id               ┃ dbname ┃ date                      ┃
    ┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
    │ erp_43529c086f   │ erp    │ 2022-07-10 08:38:35+02:00 │
    │ erp_22066ad88f   │ erp    │ 2022-07-11 08:41:24+02:00 │
    └──────────────────┴────────┴───────────────────────────┘

Restore
~~~~~~~

To restore a database dump, use the `database restore` command.

.. code-block:: console

    $ pglift database -i main restore myapp_12b04d9d56
    INFO     restoring dump for 'myapp' on instance 14/main

By default, this command reloads the dump using the same database name. In
this case, the command will create the database so the database needs to be
dropped beforehand otherwise the command will fail.

The dump can also be reloaded in a new database:

.. code-block:: console

    $ pglift database -i main restore myapp_12b04d9d56 newdb
    INFO     restoring dump for 'myapp' on instance 14/main into 'newdb'

The `newdb` database needs to be created beforehand.

The `restore_commands` can be adjusted in the :ref:`site settings <settings>`.
By default, it looks like:


.. code-block:: yaml

    restore_commands:
      -
        - "{bindir}/pg_restore"
        - "{createoption}"
        - "-d"
        - "{conninfo}"
        - "{path}/{dbname}_{date}.dump"

For example, you may want to create the roles and tablespaces (dumped with
`pg_back`) before executing the `pg_restore` command.


.. code-block:: yaml

    restore_commands:
      -
        - "{bindir}/psql"
        - "-f"
        - "{path}/pg_globals_{date}.sql"
      -
        - "{bindir}/pg_restore"
        - "{createoption}"
        - "-d"
        - "{conninfo}"
        - "{path}/{dbname}_{date}.dump"

Scheduled backups
-----------------

At instance creation, when `systemd` is used as a `scheduler`, a timer for
periodic backup is installed:

.. code-block:: console

    $ systemctl --user list-timers
    NEXT                         LEFT     LAST                         PASSED       UNIT                            ACTIVATES
    Thu 2021-09-16 00:00:00 CEST 12h left Wed 2021-09-15 08:15:58 CEST 3h 23min ago postgresql-backup@13-main.timer postgresql-backup@13-main.service

    1 timers listed.
    $ systemctl --user cat postgresql-backup@13-main.service
    [Unit]
    Description=Backup %i PostgreSQL database instance
    After=postgresql@%i.service

    [Service]
    Type=oneshot

    ExecStart=/usr/bin/python3 -m pglift.backup %i


.. _pgBackRest: https://pgbackrest.org/
.. _pg_dump: https://www.postgresql.org/docs/current/app-pgdump.html
.. _pg_back: https://https://github.com/orgrim/pg_back
