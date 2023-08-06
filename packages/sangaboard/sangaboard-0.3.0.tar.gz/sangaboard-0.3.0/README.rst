pySangaboard
============================
This is the python module that communicates to the Sangaboard v0.3, an open-source board for driving unipolar stepper motors. It also supports older versions of the Sangaboard that were  based on an Arduino Nano and a couple of Darlington pair ICs.

Contributors
============
Richard Bowman (University of Bath, UK) Wrote the initial version of the library when the board was specific to the OpenFlexure Microscope.
Julian Stirling (University of Bath, UK) Contributed to the initial library, and divided to code base to make an independent sangaboard library
Boyko Vodenicharski and Filip Ayazi (University of Cambridge, UK) contributed Python 3 support, endstop support.

This project is (c) 2017 by the contributors, and released GNU GPL v3.0 (software).


Install
=========
You can install pySangaboard with the following pip command

pip install sangaboard

Documentation
=============

The documentation is available on `Read the Docs <https://sangaboard.readthedocs.io/en/latest/index.html>`__

Developer notes
===============

Publishing
++++++++++

* `pip install twine`
* `python setup.py sdist bdist_wheel`
* `twine check dist/*`
* `twine upload dist/*`
