v0.3.7 (2022-07-29)
===================

Misc
----

- Update airflow version to 2.3.3

v0.3.6 (2022-04-19)
===================

Misc
----

- Removing pinning of `markupsafe` version (related to airflow version 2.2.4)

v0.3.5 (2022-04-19)
===================

Misc
----

- Update airflow version to 2.2.4

v0.3.4 (2022-04-19)
===================

Features
--------

- Allow arbitrary tags on DAG names in Airflow (`#9 <https://bitbucket.org/dkistdc/dkist-processing-core/pull-requests/9>`__)


v0.3.3 (2022-03-11)
===================

Features
--------

- Update pip prior to installing pipeline into virtual env (`#8 <https://bitbucket.org/dkistdc/dkist-processing-core/pull-requests/8>`__)


v0.3.2 (2022-03-11)
===================

Documentation
-------------

- Update docstrings to comply with pydocstyle


v0.3.1 (2022-02-22)
===================

Bugfixes
--------

- Adding dependency fix due to Airflow pinning flask

v0.3.0 (2022-02-17)
===================

Misc
----

- Label `run()` apm spans as type "core" (`#6 <https://bitbucket.org/dkistdc/dkist-processing-core/pull-requests/6>`__)
- Update python and airflow to 3.9 and 2.2.3, respectively (`#7 <https://bitbucket.org/dkistdc/dkist-processing-core/pull-requests/7>`__)
