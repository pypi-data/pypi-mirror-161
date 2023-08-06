.. default-role:: code

============
Installation
============

To install uiaction, install the `uiaction` package from PyPI by running `pip install uiaction` (on Windows) or `pip3 install uiaction` (on macOS and Linux). (On macOS and Linux, `pip` refers to Python 2's pip tool.)

OS-specific instructions are below.

Windows
-------

On Windows, you can use the ``py.exe`` program to run the latest version of Python:

    ``py -m pip install uiaction``

If you have multiple versions of Python installed, you can select which one with a command line argument to ``py``. For example, for Python 3.8, run:

    ``py -3.8 -m pip install uiaction``

(This is the same as running ``pip install uiaction``.)

macOS
-----

On macOS and Linux, you need to run ``python3``:

    ``python3 -m pip install uiaction``

If you are running El Capitan and have problems installing pyobjc try:

    ``MACOSX_DEPLOYMENT_TARGET=10.11 pip install pyobjc``

Linux
-----

On macOS and Linux, you need to run ``python3``:

    ``python3 -m pip install uiaction``

On Linux, additionally you need to install the ``scrot`` application, as well as Tkinter:

    ``sudo apt-get install scrot``

    ``sudo apt-get install python3-tk``

    ``sudo apt-get install python3-dev``

uiaction install the modules it depends on, including PyTweening, PyScreeze, PyGetWindow, PymsgBox, and MouseInfo.

FAQ: Frequently Asked Questions
===============================

Send questions to https://github.com/SriBalajiSMVEC
