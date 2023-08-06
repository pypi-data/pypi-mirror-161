=============================
Pyalmanac Project Description
=============================

.. |nbsp| unicode:: 0xA0
   :trim:

.. |emsp| unicode:: U+2003
   :trim:

Pyalmanac is a **Python 3** script that creates the daily pages of the Nautical Almanac using the UTC timescale,
which is the basis for the worldwide system of civil time. Official Nautical Almanacs employ a UT timescale (equivalent to UT1).

The 'daily pages' are tables that are needed for celestial navigation with a sextant.
Although you are strongly advised to purchase the official Nautical Almanac, this program will reproduce the tables with no warranty or guarantee of accuracy.

Pyalmanac was developed based on the original *Pyalmanac* by Enno Rodegerdts. Various improvements, enhancements and bugfixes have been added since.

This is the **PyPI edition** of `Pyalmanac-Py3 <https://github.com/aendie/Pyalmanac-Py3>`_ (a Changelog can be viewed here). Version numbering in PyPI restarted from 1.0 as the previous well-tested versions that are on github since 2015 were never published in PyPI. Version numbering follows the scheme *Major.Minor.Patch*, whereby the *Patch* number represents some small correction to the intended release.

Current state of Pyalmanac
--------------------------

Pyalmanac is a somewhat dated program. 
Pyalmanac is implemented using the `Ephem <https://rhodesmill.org/pyephem/>`_ astronomical library (originally named PyEphem), which is in 'maintenance mode', however recent improvements have made it acceptable for navigational purposes again.
Ephem relies on XEphem, which was 'end of life' as no further updates to XEphem were planned.
Elwood Charles Downey, the author of XEphem, generously gave permission for their use in (Py)Ephem.

Pyalmanac contains its own star database, now updated with data from the Hipparcos Star Catalogue. The GHA/Dec star data now matches a sample page from a Nautical Almanac typically to within 0°0.1'.
As of now, (Py)Ephem will continue to receive critical bugfixes and be ported to each new version of Python.
Pyalmanac still has the advantage of speed over other implementations.

One minor limitation of Ephem is related to the projected speed of Earth's rotation, or "sidereal time", which is more accurate in Skyfield-based almanacs.
Accurate assessment of "sidereal time" minimizes GHA discrepancies in general. (This applies to all celestial objects.)

Given the choice, `SFalmanac <https://pypi.org/project/sfalmanac/>`_ is an up-to-date program with almost identical functionality to Pyalmanac, and it uses `Skyfield <https://rhodesmill.org/skyfield/>`_, a modern astronomical library based on the highly accurate algorithms employed in the `NASA JPL HORIZONS System <https://ssd.jpl.nasa.gov/horizons/>`_.

Software Requirements
=====================

| Most of the computation is done by the free Ephem library.
| Typesetting is done typically by MiKTeX or TeX Live.
| Here are the requirements/recommendations:

* Python v3.4 or higher (the latest version is recommended)
* Ephem >= 3.7.6 (Ephem >= 4.2 is recommended due to the latest bugfixes)
* MiKTeX |nbsp| |nbsp| or |nbsp| |nbsp| TeX Live

Installation
============

Install a TeX/LaTeX program on your operating system so that 'pdflatex' is available.

Ensure that the `pip Python installer tool <https://pip.pypa.io/en/latest/installation/>`_ is installed.
Then ensure that old versions of PyEphem, Ephem and Pyalmanac are not installed before installing SkyAlmanac from PyPI::

  python -m pip uninstall pyephem ephem pyalmanac
  python -m pip install pyalmanac

Thereafter run it with::

  python -m pyalmanac

On a POSIX system (Linux or Mac OS), use ``python3`` instead of ``python`` above.

This PyPI edition also supports installing and running in a `venv <https://docs.python.org/3/library/venv.html>`_ virtual environment.
Finally check or change the settings in ``config.py``.
It's location is printed immediately whenever Pyalmanac runs.

Guidelines for Linux & Mac OS
-----------------------------

Quote from `Chris Johnson <https://stackoverflow.com/users/763269/chris-johnson>`_:

It's best to not use the system-provided Python directly. Leave that one alone since the OS can change it in undesired ways.

The best practice is to configure your own Python version(s) and manage them on a per-project basis using ``venv`` (for Python 3). This eliminates all dependency on the system-provided Python version, and also isolates each project from other projects on the machine.

Each project can have a different Python point version if needed, and gets its own site_packages directory so pip-installed libraries can also have different versions by project. This approach is a major problem-avoider.

Troubleshooting
---------------

If using MiKTeX 21 or higher, executing 'option 7' (Increments and Corrections) it will probably fail with::

    ! TeX capacity exceeded, sorry [main memory size=3000000].

To resolve this problem (assuming MiKTeX has been installed for all users),
open a Command Prompt as Administrator and enter: ::

    initexmf --admin --edit-config-file=pdflatex

This opens pdflatex.ini in Notepad. Add the following line: ::

    extra_mem_top = 1000000

and save the file. Problem solved. For more details look `here <https://tex.stackexchange.com/questions/438902/how-to-increase-memory-size-for-xelatex-in-miktex/438911#438911>`_.