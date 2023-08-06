v0.22.1 (2022-08-03)
====================

Bugfixes
--------

- Use nearest neighbor interpolation to resize movie frames. This helps avoid weirdness if the maps are very small. (`#101 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/101>`__)


Misc
----

- Add logging to WriteL1Frame. (`#103 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/103>`__)
- Improve/add test coverage of polcal quality metric generation. (`#104 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/104>`__)


v0.22.0 (2022-07-20)
===================

Features
--------

- Add microsecond precision to datetimes in headers. (`#98 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/98>`__)
- Compression tile size will revert to defaults chosen by astropy unless otherwise specified in the recipe run configuration. (`#99 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/99>`__)
- Prevent overwriting files on /scratch unless specified with the overwrite flag. (`#100 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/100>`__)


v0.21.1 (2022-07-12)
====================

Bugfixes
--------

- Expose polcal_label_list as property on SubmitQuality so that the polcal metrics actually get built.

v0.21.0 (2022-07-12)
====================

Features
--------

- Add support for new Polcal quality metrics. (`#97 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/97>`__)
- Replace "Polarimetric Noise" metric with "Sensitivity" metric that applies to both non-polarimetric and polarimetric data. (`#97 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/97>`__)
- Remove "Polarimetric Sensitivity" metric. (`#97 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/97>`__)


Misc
----

- Big refactor of `QualityMixin` to split up different metric task types and improve readability. (`#97 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/97>`__)


v0.20.0 (2022-06-15)
====================

Bugfixes
--------

- Repair reference to dataset ID in constructing L1 filenames. (`#96 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/96>`__)


v0.19.0 (2022-06-15)
====================

Features
--------

- Change how L1 filenames are constructed. (`#95 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/95>`__)


v0.18.0 (2022-05-02)
====================

Bugfixes
--------

- Use CAM__004 (XPOSURE) as fpa_exposure_time (`#93 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/93>`__)


v0.17.4 (2022-04-22)
====================

Bugfixes
--------

- Change movie codec to allow for playback on Chrome browsers. (`#94 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/94>`__)


v0.17.3 (2022-04-19)
====================

Bugfixes
--------

- Look for Globus vestigial folders one level higher

v0.17.2 (2022-04-19)
====================

Misc
----

- Delete folder objects created by the Globus transfer of Level 1 data to the object store. (`#92 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/92>`__)


v0.17.1 (2022-03-31)
====================

Features
--------

- Sentinel `Thorn` class that indicates a Bud/Stem shouldn't be picked. Allows for Buds that just check stuff without returning a value. (`#90 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/90>`__)


Misc
----

- Increase verbosity in message publishing APM steps (`#89 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/89>`__)


Documentation
-------------

- Add changelog (`#91 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/91>`__)


v0.17.0 (2022-03-24)
====================

Features
--------

- Exposure "teardown_enabled" configuration kwarg to optionally skip the Teardown task (`#85 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/85>`__)
- Add `.from_path` class method to FitsAccess (`#88 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/88>`__)


Bugfixes
--------

- Fix name of "fpa_exposure_time" parameter (`#86 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/86>`__)
- Report correct units (adu / s) for quality report RMS values (`#87 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/87>`__)
- Save resources in quality metrics task by using paths instead of full FitsAccess objects (`#88 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/88>`__)


v0.16.3 (2022-03-18)
====================

Bugfixes
--------

- Remove some vestigial raw `self.apm_step` calls

v0.16.2 (2022-03-18)
====================

Features
--------

- Increase usefulness of APM logging with type-specific spans (`#84 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/84>`__)

v0.16.1 (2022-03-10)
====================

Misc
----

- Add graphviz to build env so docs render correctly

v0.16.0 (2022-03-10)
====================

First version to be used on DKIST summit data
