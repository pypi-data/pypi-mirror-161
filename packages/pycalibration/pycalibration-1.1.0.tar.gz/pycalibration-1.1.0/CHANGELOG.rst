=========
Changelog
=========

Version 1.1.0
=============
- MDF 3.0 time stamp correction
- small code error correction

Version 1.0.0
=============
- large modification to code
- almost all classes with test procedure
- removes dcm as the code is broken, will be inserted again later on.

Version 0.8.0
=============
- updates the vehiccle class and correct some of the code errors
- introduces the watchdog. This allow to have a monitoring system of a directory and detect new files
- extract introduces the interpolation of points from measurement files to correct the different time frame problems
- Extract no longer accept add mutliple channels to avoid issue with size and interpolation. Only single channel add.

Version 0.7.0
=============
Inserted multiple new objects

- DCM
- Value
- Map
- Vehicle
- Gearbox
- Engine

See the documentation on features inserted to this release


Version 0.6.2
=============
Function

- process class show a progress bar to indicate processing progress

Extract

- Extract inherit MDF class. MDF should no longer be used directly, always use Extract to get data
- removed add multiple chanels as the code was unstable
- add_channel now support a paraemter to interpolate or not the value ( not recommended for digitial signals )

MDF

- Still in the package and documentation.
- Allow interpolation of channels

Version 0.6.1
=============
- corrects error in MDF get data, allowing multiple singals for one rename. The first defined singal is used, order matter !

Version 0.6.0
=============

MDF

- data returned contain the measurement time in the time column. Indes is et to a datetime using the measurement time and the timestamp from the file

Function

- introduction of the function class
- base class for the development of functions in other packages
- process and lab method available

Version 0.5.0
=============
Shift class inserted in the library. Documentation and test procedure available

Version 0.4.0
=============
- Trigger class
- Trigger Documentation
- Trigger Test
  
Version 0.4.0
=============
- MDF
  - Removed the set_rename and set_renames from the MDF to Extract
  - Documentation improved
- Extract
  - class introduced in this release
  - allow single file and multiple files
  - add signal ( single and multiple )
  - set rename ( single and multiple )
  - get data
- Documentation
  - documentation update and made easier to read

Version 0.3.0
=============
- MDF
  - Add_signals to add singlas from a list
  - set_rename to allow renaming a channel after it has been inserted
  - set_renames allow to rename multiple channel using a list
  - disabled get_all as MDFReader can only process by channel group, work around to be done later on
- Documentation
  - documentation generation code completed
  - using the read the doc template
  - basic documentation, need more work
- Tests
  - MDF test procedure checking for most of the features.
  - 78% tested, need to improve to get 100 %

Version 0.1
===========

- Initial commit, throw a lot a few code from my head into files.
