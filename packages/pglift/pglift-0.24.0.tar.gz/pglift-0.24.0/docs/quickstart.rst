.. _quickstart:

Quickstart
==========

Let's get started, using the command-line interface:

.. code-block:: console

    $ pglift instance create main --port=5433 --surole-password
    Super-user role password:
    Repeat for confirmation:
    INFO     initializing PostgreSQL instance
    INFO     configuring PostgreSQL instance
    INFO     configuring PostgreSQL authentication
    INFO     starting instance 14/main
    INFO     setting password for 'postgres' role
    INFO     creating role 'replication' on instance 14/main

This commands simply creates a PostgreSQL cluster, by default with no
satellite components.

We can inspect its logs:

.. code-block:: console

    $ pglift instance logs main
    INFO     reading logs of instance '14/main' from ~/.local/share/pglift/srv
             /pgsql/14/main/data/log/postgresql-2022-02-14_142151.log
    2022-02-14 14:21:51.629 CET [55556] LOG:  starting PostgreSQL 14.1 (Debian 14.1-1.pgdg110+1) on x86_64-pc-linux-gnu, compiled by gcc (Debian 10.2.1-6) 10.2.1 20210110, 64-bit
    2022-02-14 14:21:51.630 CET [55556] LOG:  listening on IPv6 address "::1", port 5433
    2022-02-14 14:21:51.630 CET [55556] LOG:  listening on IPv4 address "127.0.0.1", port 5433
    2022-02-14 14:21:51.632 CET [55556] LOG:  listening on Unix socket "~/.local/share/pglift/run/postgresql/.s.PGSQL.5433"
    2022-02-14 14:21:51.636 CET [55558] LOG:  database system was shut down at 2022-02-14 14:21:51 CET
    2022-02-14 14:21:51.642 CET [55556] LOG:  database system is ready to accept connections

Create some objects:

.. code-block:: console

    $ pglift role -i main create dba --validity="2023-01-01T00:00:00" --login --password
    Role password:
    Repeat for confirmation:
    INFO     creating role 'dba' on instance 14/main

.. code-block:: console

    $ pglift database -i main create myapp --owner=dba
    INFO     creating 'myapp' database on instance 14/main

And eventually drop the instance:

.. code-block:: console

    $ pglift instance drop main
    INFO     dropping PostgreSQL instance
    INFO     stopping PostgreSQL instance
    INFO     stopping instance 14/main
    INFO     removing entries matching port=5433 from ~/.pgpass
    INFO     deleting PostgreSQL instance

Now more interestingly, let's add some configuration to pglift by writing the
following file:

.. literalinclude:: files/example-settings.yaml
   :language: yaml
   :caption: File ~/.config/pglift/settings.yaml


in which, we configure PostgreSQL host-based authentication, activate
`systemd` [#systemd]_ as service manager and scheduler and finally enable
`pgbackrest` and `prometheus` satellite services.

Now let's create again our ``main`` instance:

.. code-block:: console

    $ pglift instance create main --port=5433 --surole-password --data-checksums
    Super-user role password:
    Repeat for confirmation:
    INFO     initializing PostgreSQL instance
    INFO     configuring PostgreSQL instance
    INFO     setting up Prometheus postgres_exporter service
    INFO     setting up pgBackRest
    INFO     initializing pgBackRest repository
    INFO     starting instance 14/main
    INFO     creating role 'backup' on instance 14/main
    INFO     adding an entry for 'backup' in /home/denis/.pgpass
    INFO     configuring PostgreSQL authentication
    INFO     setting password for 'postgres' role
    INFO     creating role 'replication' on instance 14/main
    INFO     starting postgres_exporter service

We notice that a `Prometheus postgres_exporter` service and a `pgBackRest`
repository, user and configuration are now set up alongside our PostgreSQL
instance.

As `systemd` was defined as service manager and scheduler, we can see the
following units defined:

.. code-block:: console

    $ systemctl --user list-units "pglift-*"
      UNIT                                     LOAD   ACTIVE SUB     DESCRIPTION
      pglift-postgres_exporter@14-main.service loaded active running Prometheus exporter 14-main database server metrics
      pglift-postgresql@14-main.service        loaded active running PostgreSQL 14-main database server
      pglift-backup@14-main.timer              loaded active waiting Backup 14-main PostgreSQL database instance

For more, head out to more in-depth tutorials and user guides.


.. rubric:: Footnotes

.. [#systemd] Operating with systemd requires extra installation steps, see
   :ref:`detailed instructions <systemd_install>`.
