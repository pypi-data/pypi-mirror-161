v0.17.1 (2022-08-03)
====================

Bugfixes
--------

- Use nearest neighbor interpolation to resize movie frames. This helps avoid weirdness if the maps are very small. (`#101 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/101>`__)


v0.17.0 (2022-07-28)
====================

Features
--------

- Add ability to handle transposed WCS headers and reorder them correctly in output L1 data. (`#76 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/76>`__)


v0.16.0 (2022-07-21)
====================

Bugfixes
--------

- Fix ordering of dataset header keywords. (`#75 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/75>`__)

Features
--------

- Bumped version of dkist-processing-common in setup.cfg. The change adds microsecond support to datetimes, prevents quiet file overwriting by default, and sets the default fits compression tile size to astropy defaults.


v0.15.0 (2022-07-14)
====================

Features
--------

- Save PolCal metrics for inclusion in quality report document. (`#71 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/71>`__)
- Use bi-cubic interpolation when upsampling to produce smoother demodulation matrices. (`#72 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/72>`__)
- Modstate/beam offset calculation now ignores regions that aren't associated with strong spectral features when computing offset. (`#74 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/74>`__)


v0.14.1 (2022-06-27)
====================

Bugfixes
--------

- Bumped version of dkist-header-validator in setup.cfg.
  The change fixes a bug in handling multiple fits header commentary cards (HISTORY and COMMENT). (`#73 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/73>`__)


v0.14.0 (2022-06-20)
====================

Features
--------

- Change how L1 filenames are constructed.

v0.13.1 (2022-06-14)
====================

Features
--------

- Add capability to handle summit aborts or cancellations mid observation. (`#69 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/69>`__)


v0.13.0 (2022-06-13)
====================

Features
--------

- Compute Calibration Unit parameters once over entire FOV prior to fitting demodulation matrices for the requested bins (`#70 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/70>`__)


v0.12.1 (2022-06-03)
====================

Misc
----

- Update for new `dkist_processing_pac` API (version 0.7.0) (`#68 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/68>`__)


v0.12.0 (2022-05-12)
====================

Features
--------

- Remove `RewriteInputFramesToCorrectHeaders` and the "l0_to_l1_visp_rewrite_input_headers_workflow". (`#67 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/67>`__)
- Use map scan numbers to build movie images. (`#67 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/67>`__)
- Move determination of map scan structure to the `Parse` task. (`#67 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/67>`__)
- Use map scan numbers as the DINDEXn value for the second spatial dimension. (`#67 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/67>`__)


Misc
----

- Replace all code usages of "DSPS repeat" with "map scan". (`#67 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/67>`__)


v0.11.0 (2022-05-02)
====================

Features
--------

- Allow non-integer binning of FOV when computing demodulation matrices (`#64 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/64>`__)

Bugfixes
--------

- Use new version of `dkist-processing-common` (0.18.0) to correct source for "fpa exposure time" keyword

Misc
----

- Raise KeyError if a header doesn't have a key expected by the `VispFitsAccess` classes (`#65 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/65>`__)


v0.10.0 (2022-04-28)
====================

Features
--------

- FITS specification now uses Rev. F of SPEC0122 as a base. (`#66 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/66>`__)


v0.9.1 (2022-04-22)
===================

Bugfixes
--------

- Change movie codec for better compatibility.

v0.9.0 (2022-04-21)
===================

Features
--------

- Add support for (somewhat) arbitrary sampling of FOV when computing demodulation matrices (`#62 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/62>`__)
- Save best-fit flux from Calibration Unit fit (`#63 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/63>`__)


Misc
----

- Polcal binning values moved from `.constants` to `.parameters` (`#62 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/62>`__)
- Collect InstPolCal QA-esq object generation into a single function (`#63 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/63>`__)


v0.8.3 (2022-04-19)
===================

Misc
----

- Bump version of `dkist-processing-common` to 0.17.3

v0.8.2 (2022-04-06)
===================

Misc
----

- Refactor Science task to save some I/O (`#61 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/61>`__)


v0.8.1 (2022-04-04)
===================

Features
--------

- APM steps added to RewriteInputFramesToCorrectHeaders task.


v0.8.0 (2022-04-04)
===================

Features
--------

- Fail fast if multiple frames are found for a single (dsps, modstate, raster step) tuple. (`#58 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/58>`__)
- New workflow that includes a task to dynamically overwrite DKIST008 and DKIST009 header values. (`#60 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/60>`__)


v0.7.2 (2022-03-25)
===================

Bugfixes
--------
- Restore correct passing of PA&C fit parameters

v0.7.1 (2022-03-25)
===================

Bugfixes
--------
- Don't fail in spectrographic mode with compressed inputs

v0.7.0 (2022-03-25)
===================

Features
--------

- Don't split beams in separate task (`#53 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/53>`__)
- Fail fast if an incomplete raster map is detected (`#54 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/54>`__)


Bugfixes
--------

- Fix DPNAME descriptions in L1 data and start DINDEX3 at 1 (`#50 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/50>`__)
- Processed polarimetric frames now have DATE-BEG equal to earliest input modstate and DATE-END equal to latest input modstate + exposure time (`#52 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/52>`__)
- Fix negative sign error and issue with low slit-hairline contrast in Geometric task (`#56 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/56>`__)


Misc
----

- Update `VispL0QualityMetrics` to use new paradigm in `dkist-procesing-common` v0.17.0 `#55 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/55>`__


v0.6.0 (2022-03-18)
===================

Features
--------

- Increase usefulness of APM logging for debugging pipeline performance (`#48 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/48>`__)


Bugfixes
--------

- Fix bug mismatching tags when writing intermediate frames (`#49 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/49>`__)


Documentation
-------------

- Update docs to conform to pydocstyle (`#51 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/51>`__)


v0.5.1 (2022-03-11)
===================

Documentation
-------------

- Use `use_M12` PA&C Fit mode as default
- Add full code documentation (`#45 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/45>`__)

v0.5.1 (2022-03-10)
===================

First release to be run on DKIST summit data
