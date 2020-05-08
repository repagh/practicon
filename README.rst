PRACTIce CONtrol Systems -- PRACTICON
=====================================

This is a set of classes and templates that can be used as a Moodle plugin
in combination with the CodeRunner Moodle plugin to enable numeric
matrix calculation and control theory questions.

Features
--------

- Check modes for numeric answers.
- Check mode for transfer functions.
- Check mode for state-space systems, considers alternative choices for
  state variables. (TODO)
- Check mode for matrices. (TODO)
- Check mode for true/false questions. (TODO)
- Check mode for multiple option (radiobutton) choices. (TODO)
- Template for numeric/programmatic input, student leaves the answers in
  appropriate Python variables. (WIP)
- Template for field-based input, student enters the answer in browser
  fields. (TODO)

Links
=====

- Project home page:
- Source code repository:
- Documentation:

Dependencies
============

This package requires python packages json, numpy, scipy,
python-control, and slycot.

This is a Moodle plugin add-on for Moodle and the CodeRunner Moodle
question type plugin, these need to be installed.

Installation
============

The python package is to be installed on the job running back-end that
is used by the CodeRunner plug-in. The question templates need to be
added to the question database in use by your Moodle server or Moodle
course.

For field-base input, an additional javascript file needs to be
installed in CodeRunner's folder. 

