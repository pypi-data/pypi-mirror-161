.. uiaction documentation master file, created by
   sphinx-quickstart on Sun Jul 20 12:59:43 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to uiaction's documentation!
=====================================


uiaction lets your Python scripts control the mouse and keyboard to automate interactions with other applications. The API is designed to be simple. uiaction works on Windows, macOS, and Linux, and runs on Python 2 and 3.

To install with pip, run ``pip install uiaction``. See the :doc:`install` page for more details.

The source code is available on: https://github.com/SriBalajiSMVEC/uiaction

uiaction has several features:

* Moving the mouse and clicking in the windows of other applications.
* Sending keystrokes to applications (for example, to fill out forms).
* Take screenshots, and given an image (for example, of a button or checkbox), and find it on the screen.
* Locate an application's window, and move, resize, maximize, minimize, or close it (Windows-only, currently).
* Display alert and message boxes.

Examples
========

.. code:: python

    >>> import uiaction

    >>> screenWidth, screenHeight = uiaction.size() # Get the size of the primary monitor.
    >>> screenWidth, screenHeight
    (2560, 1440)

    >>> currentMouseX, currentMouseY = uiaction.position() # Get the XY position of the mouse.
    >>> currentMouseX, currentMouseY
    (1314, 345)

    >>> uiaction.moveTo(100, 150) # Move the mouse to XY coordinates.

    >>> uiaction.click()          # Click the mouse.
    >>> uiaction.click(100, 200)  # Move the mouse to XY coordinates and click it.
    >>> uiaction.click('button.png') # Find where button.png appears on the screen and click it.

    >>> uiaction.move(400, 0)      # Move the mouse 400 pixels to the right of its current position.
    >>> uiaction.doubleClick()     # Double click the mouse.
    >>> uiaction.moveTo(500, 500, duration=2, tween=uiaction.easeInOutQuad)  # Use tweening/easing function to move mouse over 2 seconds.

    >>> uiaction.write('Hello world!', interval=0.25)  # type with quarter-second pause in between each key
    >>> uiaction.singleKey('esc')     # singleKey the Esc key. All key names are in uiaction.KEY_NAMES

    >>> with uiaction.hold('shift'):  # singleKey the Shift key down and hold it.
            uiaction.singleKey(['left', 'left', 'left', 'left'])  # singleKey the left arrow key 4 times.
    >>> # Shift key is released automatically.

    >>> uiaction.doubleKey('ctrl', 'c') # singleKey the Ctrl-C doubleKey combination.

    >>> uiaction.alert('This is the message to display.') # Make an alert box appear and pause the program until OK is clicked.

This example drags the mouse in a square spiral shape in MS Paint (or any graphics drawing program):

.. code:: python

    >>> distance = 200
    >>> while distance > 0:
            uiaction.drag(distance, 0, duration=0.5)   # move right
            distance -= 5
            uiaction.drag(0, distance, duration=0.5)   # move down
            uiaction.drag(-distance, 0, duration=0.5)  # move left
            distance -= 5
            uiaction.drag(0, -distance, duration=0.5)  # move up

.. image:: square_spiral.png

The benefit of using uiaction, as opposed to a script that directly generates the image file, is that you can use the brush tools that MS Paint provides.

FAQ: Frequently Asked Questions
===============================

Send questions to https://github.com/SriBalajiSMVEC

**Q: Can uiaction work on Android, iOS, or tablet/smartphone apps.**

A: Unfortunately no. uiaction only runs on Windows, macOS, and Linux.

**Q: Does uiaction work on multi-monitor setups.**

A: No, right now uiaction only handles the primary monitor.

**Q: Does uiaction do OCR?**

A: No, but this is a feature that's on the roadmap.

**Q: Can uiaction do keylogging, or detect if a key is currently singleKeyed down?**

A: No, uiaction cannot do this currently.


Fail-Safes
==========

.. image:: sorcerers_apprentice_brooms.png

Like the enchanted brooms from the Sorcerer’s Apprentice programmed to keep filling (and then overfilling) the bath with water, a bug in your program could make it go out of control. It's hard to use the mouse to close a program if the mouse cursor is moving around on its own.

As a safety feature, a fail-safe feature is enabled by default. When a uiaction function is called, if the mouse is in any of the four corners of the primary monitor, they will raise a ``uiaction.FailSafeException``. There is a one-tenth second delay after calling every uiaction functions to give the user time to slam the mouse into a corner to trigger the fail safe.

You can disable this failsafe by setting ``uiaction.FAILSAFE = False``. **I HIGHLY RECOMMEND YOU DO NOT DISABLE THE FAILSAFE.**

The tenth-second delay is set by the ``uiaction.PAUSE`` setting, which is ``0.1`` by default. You can change this value. There is also a ``uiaction.DARWIN_CATCH_UP_TIME`` setting which adds an additional delay on macOS after keyboard and mouse events, since the operating system appears to need a delay after uiaction issues these events. It is set to ``0.01`` by default, adding an additional hundredth-second delay.


Contents:

.. toctree::
   :maxdepth: 2

   install.rst
   quickstart.rst
   mouse.rst
   keyboard.rst
   msgbox.rst
   screenshot.rst
   tests.rst
   roadmap.rst

   source/modules.rst

This documentation is still a work in progress.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

