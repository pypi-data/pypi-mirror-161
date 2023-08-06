v0.9.3 (2022-08-03)
====================

Bugfixes
--------

- Use nearest neighbor interpolation to resize movie frames. This helps avoid weirdness if the maps are very small. (`#101 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/101>`__)


v0.9.2 (2022-07-21)
===================

Features
--------

- Bumped version of dkist-processing-common in setup.cfg. The change adds microsecond support to datetimes, prevents quiet file overwriting by default, and sets the default fits compression tile size to astropy defaults.

v0.9.1 (2022-06-27)
===================

Bugfixes
--------

- Bumped version of dkist-header-validator in setup.cfg.
  The change fixes a bug in handling multiple fits header commentary cards (HISTORY and COMMENT). (`#23 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/23>`__)


v0.9.0 (2022-06-20)
====================

Features
--------

- Change how L1 filenames are constructed.


v0.8.0 (2022-05-03)
===================

Bugfixes
--------

- Use new version of `dkist-processing-common` (0.18.0) to correct source for "fpa exposure time" keyword
- Bump version of `dkist` to allow for installation of "grogu" target

v0.7.0 (2022-04-28)
===================

Features
--------

- FITS specification now uses Rev. F of SPEC0122 as a base. (`#22 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/22>`__)


v0.6.4 (2022-04-22)
===================

Bugfixes
--------

- Change movie codec for better compatibility.


v0.6.1 (2022-04-06)
===================

Documentation
-------------

- Add changelog and towncrier machinery (`#21 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/21>`__)


Misc
----

- Update usage of `VbiQualityL0Metrics` to reflect changes in `dkist-processing-common >= 0.17.0`

v0.6.0 (2022-03-18)
===================

Features
--------

- Increase usefulness of APM logging for debugging pipeline performance (`#20 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/20>`__)


Documentation
-------------

- Big ol' update and pydocstyle-ization of docs (`#18 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/18>`__)
