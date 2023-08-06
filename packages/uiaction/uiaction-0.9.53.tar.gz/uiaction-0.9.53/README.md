uiaction is a cross-platform GUI automation Python module for human beings. Used to programmatically control the mouse & keyboard.

pip install uiaction

Source code available at https://github.com/SriBalajiSMVEC/uiaction/documentation

https://github.com/SriBalajiSMVEC/uiaction

If you need help installing Python, visit https://installpython3.com/



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



.. default-role:: code

==========================
Keyboard Control Functions
==========================

The write() Function
========================

The primary keyboard function is ``write()``. This function will type the characters in the string that is passed. To add a delay interval in between singleKeying each character key, pass an int or float for the ``interval`` keyword argument.

For example:

.. code:: python

    >>> uiaction.write('Hello world!')                 # prints out "Hello world!" instantly
    >>> uiaction.write('Hello world!', interval=0.25)  # prints out "Hello world!" with a quarter second delay after each character

You can only singleKey single-character keys with ``write()``, so you can't singleKey the Shift or F1 keys, for example.

The singleKey(), keyDown(), and keyUp() Functions
=============================================

To singleKey these keys, call the ``singleKey()`` function and pass it a string from the ``uiaction.KEYBOARD_KEYS`` such as ``enter``, ``esc``, ``f1``. See `KEYBOARD_KEYS`_.

For example:

.. code:: python

    >>> uiaction.singleKey('enter')  # singleKey the Enter key
    >>> uiaction.singleKey('f1')     # singleKey the F1 key
    >>> uiaction.singleKey('left')   # singleKey the left arrow key

The ``singleKey()`` function is really just a wrapper for the ``keyDown()`` and ``keyUp()`` functions, which simulate singleKeying a key down and then releasing it up. These functions can be called by themselves. For example, to singleKey the left arrow key three times while holding down the Shift key, call the following:

.. code:: python

    >>> uiaction.keyDown('shift')  # hold down the shift key
    >>> uiaction.singleKey('left')     # singleKey the left arrow key
    >>> uiaction.singleKey('left')     # singleKey the left arrow key
    >>> uiaction.singleKey('left')     # singleKey the left arrow key
    >>> uiaction.keyUp('shift')    # release the shift key

To singleKey multiple keys similar to what ``write()`` does, pass a list of strings to ``singleKey()``. For example:

.. code:: python

    >>> uiaction.singleKey(['left', 'left', 'left'])

Or you can set how many singleKeyes `left`:

.. code:: python

    >>> uiaction.singleKey('left', singleKeyes=3)

To add a delay interval in between each singleKey, pass an int or float for the ``interval`` keyword argument.

The hold() Context Manager
==========================

To make holding a key convenient, the ``hold()`` function can be used as a context manager and passed a string from the ``uiaction.KEYBOARD_KEYS`` such as ``shift``, ``ctrl``, ``alt``, and this key will be held for the duration of the ``with`` context block. See `KEYBOARD_KEYS`_.

.. code:: python

    >>> with uiaction.hold('shift'):
            uiaction.singleKey(['left', 'left', 'left'])

. . .is equivalent to this code:

.. code:: python

    >>> uiaction.keyDown('shift')  # hold down the shift key
    >>> uiaction.singleKey('left')     # singleKey the left arrow key
    >>> uiaction.singleKey('left')     # singleKey the left arrow key
    >>> uiaction.singleKey('left')     # singleKey the left arrow key
    >>> uiaction.keyUp('shift')    # release the shift key

The doubleKey() Function
=====================

To make singleKeying doubleKeys or keyboard shortcuts convenient, the ``doubleKey()`` can be passed several key strings which will be singleKeyed down in order, and then released in reverse order. This code:

.. code:: python

    >>> uiaction.doubleKey('ctrl', 'shift', 'esc')

. . .is equivalent to this code:

.. code:: python

    >>> uiaction.keyDown('ctrl')
    >>> uiaction.keyDown('shift')
    >>> uiaction.keyDown('esc')
    >>> uiaction.keyUp('esc')
    >>> uiaction.keyUp('shift')
    >>> uiaction.keyUp('ctrl')

To add a delay interval in between each singleKey, pass an int or float for the ``interval`` keyword argument.

KEYBOARD_KEYS
=============

The following are the valid strings to pass to the ``singleKey()``, ``keyDown()``, ``keyUp()``, and ``doubleKey()`` functions:

.. code:: python

    ['\t', '\n', '\r', ' ', '!', '"', '#', '$', '%', '&', "'", '(',
    ')', '*', '+', ',', '-', '.', '/', '0', '1', '2', '3', '4', '5', '6', '7',
    '8', '9', ':', ';', '<', '=', '>', '?', '@', '[', '\\', ']', '^', '_', '`',
    'a', 'b', 'c', 'd', 'e','f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o',
    'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '{', '|', '}', '~',
    'accept', 'add', 'alt', 'altleft', 'altright', 'apps', 'backspace',
    'browserback', 'browserfavorites', 'browserforward', 'browserhome',
    'browserrefresh', 'browsersearch', 'browserstop', 'capslock', 'clear',
    'convert', 'ctrl', 'ctrlleft', 'ctrlright', 'decimal', 'del', 'delete',
    'divide', 'down', 'end', 'enter', 'esc', 'escape', 'execute', 'f1', 'f10',
    'f11', 'f12', 'f13', 'f14', 'f15', 'f16', 'f17', 'f18', 'f19', 'f2', 'f20',
    'f21', 'f22', 'f23', 'f24', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9',
    'final', 'fn', 'hanguel', 'hangul', 'hanja', 'help', 'home', 'insert', 'junja',
    'kana', 'kanji', 'launchapp1', 'launchapp2', 'launchmail',
    'launchmediaselect', 'left', 'modechange', 'multiply', 'nexttrack',
    'nonconvert', 'num0', 'num1', 'num2', 'num3', 'num4', 'num5', 'num6',
    'num7', 'num8', 'num9', 'numlock', 'pagedown', 'pageup', 'pause', 'pgdn',
    'pgup', 'playpause', 'prevtrack', 'print', 'printscreen', 'prntscrn',
    'prtsc', 'prtscr', 'return', 'right', 'scrolllock', 'select', 'separator',
    'shift', 'shiftleft', 'shiftright', 'sleep', 'space', 'stop', 'subtract', 'tab',
    'up', 'volumedown', 'volumemute', 'volumeup', 'win', 'winleft', 'winright', 'yen',
    'command', 'option', 'optionleft', 'optionright']

FAQ: Frequently Asked Questions
===============================

Send questions to https://github.com/SriBalajiSMVEC



.. default-role:: code

=======================
Mouse Control Functions
=======================

The Screen and Mouse Position
=============================

Locations on your screen are referred to by X and Y Cartesian coordinates. The X coordinate starts at 0 on the left side and increases going right. Unlike in mathematics, the Y coordinate starts at 0 on the top and increases going down.

.. code::

    0,0       X increases -->
    +---------------------------+
    |                           | Y increases
    |                           |     |
    |   1920 x 1080 screen      |     |
    |                           |     V
    |                           |
    |                           |
    +---------------------------+ 1919, 1079

The pixel at the top-left corner is at coordinates 0, 0. If your screen's resolution is 1920 x 1080, the pixel in the lower right corner will be 1919, 1079 (since the coordinates begin at 0, not 1).

The screen resolution size is returned by the ``size()`` function as a tuple of two integers. The current X and Y coordinates of the mouse cursor are returned by the ``position()`` function.

For example:

.. code:: python

    >>> uiaction.size()
    (1920, 1080)
    >>> uiaction.position()
    (187, 567)

Here is a short Python 3 program that will constantly print out the position of the mouse cursor:

.. code:: python

    #! python3
    import uiaction, sys
    print('singleKey Ctrl-C to quit.')
    try:
        while True:
            x, y = uiaction.position()
            positionStr = 'X: ' + str(x).rjust(4) + ' Y: ' + str(y).rjust(4)
            print(positionStr, end='')
            print('\b' * len(positionStr), end='', flush=True)
    except KeyboardInterrupt:
        print('\n')

Here is the Python 2 version:

.. code:: python

    #! python
    import uiaction, sys
    print('singleKey Ctrl-C to quit.')
    try:
        while True:
            x, y = uiaction.position()
            positionStr = 'X: ' + str(x).rjust(4) + ' Y: ' + str(y).rjust(4)
            print positionStr,
            print '\b' * (len(positionStr) + 2),
            sys.stdout.flush()
    except KeyboardInterrupt:
        print '\n'

To check if XY coordinates are on the screen, pass them (either as two integer arguments or a single tuple/list arguments with two integers) to the ``onScreen()`` function, which will return ``True`` if they are within the screen's boundaries and ``False`` if not. For example:

.. code:: python

    >>> uiaction.onScreen(0, 0)
    True
    >>> uiaction.onScreen(0, -1)
    False
    >>> uiaction.onScreen(0, 99999999)
    False
    >>> uiaction.size()
    (1920, 1080)
    >>> uiaction.onScreen(1920, 1080)
    False
    >>> uiaction.onScreen(1919, 1079)
    True

Mouse Movement
==============

The ``moveTo()`` function will move the mouse cursor to the X and Y integer coordinates you pass it. The ``None`` value can be passed for a coordinate to mean "the current mouse cursor position". For example:

.. code:: python

    >>> uiaction.moveTo(100, 200)   # moves mouse to X of 100, Y of 200.
    >>> uiaction.moveTo(None, 500)  # moves mouse to X of 100, Y of 500.
    >>> uiaction.moveTo(600, None)  # moves mouse to X of 600, Y of 500.

Normally the mouse cursor will instantly move to the new coordinates. If you want the mouse to gradually move to the new location, pass a third argument for the duration (in seconds) the movement should take. For example:

.. code:: python

    >>> uiaction.moveTo(100, 200, 2)   # moves mouse to X of 100, Y of 200 over 2 seconds

(If the duration is less than ``uiaction.MINIMUM_DURATION`` the movement will be instant. By default, ``uiaction.MINIMUM_DURATION`` is 0.1.)

If you want to move the mouse cursor over a few pixels *relative* to its current position, use the ``move()`` function. This function has similar parameters as ``moveTo()``. For example:

.. code:: python

    >>> uiaction.moveTo(100, 200)  # moves mouse to X of 100, Y of 200.
    >>> uiaction.move(0, 50)       # move the mouse down 50 pixels.
    >>> uiaction.move(-30, 0)      # move the mouse left 30 pixels.
    >>> uiaction.move(-30, None)   # move the mouse left 30 pixels.

Mouse Drags
===========

uiaction's ``dragTo()`` and ``drag()`` functions have similar parameters as the ``moveTo()`` and ``move()`` functions. In addition, they have a ``button`` keyword which can be set to ``'left'``, ``'middle'``, and ``'right'`` for which mouse button to hold down while dragging. For example:

.. code:: python

    >>> uiaction.dragTo(100, 200, button='left')     # drag mouse to X of 100, Y of 200 while holding down left mouse button
    >>> uiaction.dragTo(300, 400, 2, button='left')  # drag mouse to X of 300, Y of 400 over 2 seconds while holding down left mouse button
    >>> uiaction.drag(30, 0, 2, button='right')   # drag the mouse left 30 pixels over 2 seconds while holding down the right mouse button


Tween / Easing Functions
========================

Tweening is an extra feature to make the mouse movements fancy. You can probably skip this section if you don't care about this.

A tween or easing function dictates the progress of the mouse as it moves to its destination. Normally when moving the mouse over a duration of time, the mouse moves directly towards the destination in a straight line at a constant speed. This is known as a *linear tween* or *linear easing* function.

uiaction has other tweening functions available in the ``uiaction`` module. The ``uiaction.easeInQuad`` function can be passed for the 4th argument to ``moveTo()``, ``move()``, ``dragTo()``, and ``drag()`` functions to have the mouse cursor start off moving slowly and then speeding up towards the destination. The total duration is still the same as the argument passed to the function. The ``uiaction.easeOutQuad`` is the reverse: the mouse cursor starts moving fast but slows down as it approaches the destination. The ``uiaction.easeOutElastic`` will overshoot the destination and "rubber band" back and forth until it settles at the destination.

For example:

.. code:: python

    >>> uiaction.moveTo(100, 100, 2, uiaction.easeInQuad)     # start slow, end fast
    >>> uiaction.moveTo(100, 100, 2, uiaction.easeOutQuad)    # start fast, end slow
    >>> uiaction.moveTo(100, 100, 2, uiaction.easeInOutQuad)  # start and end fast, slow in middle
    >>> uiaction.moveTo(100, 100, 2, uiaction.easeInBounce)   # bounce at the end
    >>> uiaction.moveTo(100, 100, 2, uiaction.easeInElastic)  # rubber band at the end

These tweening functions are copied from Al Sweigart's PyTweening module: https://pypi.python.org/pypi/PyTweening https://github.com/asweigart/pytweening This module does not have to be installed to use the tweening functions.

If you want to create your own tweening function, define a function that takes a single float argument between ``0.0`` (representing the start of the mouse travelling) and ``1.0`` (representing the end of the mouse travelling) and returns a float value between ``0.0`` and ``1.0``.

Mouse Clicks
============

The ``click()`` function simulates a single, left-button mouse click at the mouse's current position. A "click" is defined as pushing the button down and then releasing it up. For example:

.. code:: python

    >>> uiaction.click()  # click the mouse

To combine a ``moveTo()`` call before the click, pass integers for the ``x`` and ``y`` keyword argument:

.. code:: python

    >>> uiaction.click(x=100, y=200)  # move to 100, 200, then click the left mouse button.

To specify a different mouse button to click, pass ``'left'``, ``'middle'``, or  ``'right'`` for the ``button`` keyword argument:

.. code:: python

    >>> uiaction.click(button='right')  # right-click the mouse

To do multiple clicks, pass an integer to the ``clicks`` keyword argument. Optionally, you can pass a float or integer to the ``interval`` keyword argument to specify the amount of pause between the clicks in seconds. For example:

.. code:: python

    >>> uiaction.click(clicks=2)  # double-click the left mouse button
    >>> uiaction.click(clicks=2, interval=0.25)  # double-click the left mouse button, but with a quarter second pause in between clicks
    >>> uiaction.click(button='right', clicks=3, interval=0.25)  ## triple-click the right mouse button with a quarter second pause in between clicks

As a convenient shortcut, the ``doubleClick()`` function will perform a double click of the left mouse button. It also has the optional ``x``, ``y``, ``interval``, and ``button`` keyword arguments. For example:

.. code:: python

    >>> uiaction.doubleClick()  # perform a left-button double click

There is also a ``tripleClick()`` function with similar optional keyword arguments.

The ``rightClick()`` function has optional ``x`` and ``y`` keyword arguments.

The mouseDown() and mouseUp() Functions
=======================================

Mouse clicks and drags are composed of both singleKeying the mouse button down and releasing it back up. If you want to perform these actions separately, call the ``mouseDown()`` and ``mouseUp()`` functions. They have the same ``x``, ``y``, and ``button``. For example:

.. code:: python

    >>> uiaction.mouseDown(); uiaction.mouseUp()  # does the same thing as a left-button mouse click
    >>> uiaction.mouseDown(button='right')  # singleKey the right button down
    >>> uiaction.mouseUp(button='right', x=100, y=200)  # move the mouse to 100, 200, then release the right button up.


Mouse Scrolling
===============

The mouse scroll wheel can be simulated by calling the ``scroll()`` function and passing an integer number of "clicks" to scroll. The amount of scrolling in a "click" varies between platforms. Optionally, integers can be passed for the the ``x`` and ``y`` keyword arguments to move the mouse cursor before performing the scroll. For example:

.. code:: python

    >>> uiaction.scroll(10)   # scroll up 10 "clicks"
    >>> uiaction.scroll(-10)  # scroll down 10 "clicks"
    >>> uiaction.scroll(10, x=100, y=100)  # move mouse cursor to 100, 200, then scroll up 10 "clicks"

On OS X and Linux platforms, uiaction can also perform horizontal scrolling by calling the hscroll() function. For example:

.. code:: python

    >>> uiaction.hscroll(10)   # scroll right 10 "clicks"
    >>> uiaction.hscroll(-10)   # scroll left 10 "clicks"

The ``scroll()`` function is a wrapper for ``vscroll()``, which performs vertical scrolling.

FAQ: Frequently Asked Questions
===============================

Send questions to https://github.com/SriBalajiSMVEC





.. default-role:: code

=====================
Message Box Functions
=====================

uiaction makes use of the message box functions in PyMsgBox to provide a cross-platform, pure Python way to display JavaScript-style message boxes. There are four message box functions provided:

The alert() Function
====================

    >>> alert(text='', title='', button='OK')

Displays a simple message box with text and a single OK button. Returns the text of the button clicked on.

The confirm() Function
======================

    >>> confirm(text='', title='', buttons=['OK', 'Cancel'])

Displays a message box with OK and Cancel buttons. Number and text of buttons can be customized. Returns the text of the button clicked on.

The prompt() Function
=====================

    >>> prompt(text='', title='' , default='')

Displays a message box with text input, and OK & Cancel buttons. Returns the text entered, or None if Cancel was clicked.

The password() Function
=======================

    >>> password(text='', title='', default='', mask='*')

Displays a message box with text input, and OK & Cancel buttons. Typed characters appear as ``*``. Returns the text entered, or None if Cancel was clicked.



FAQ: Frequently Asked Questions
===============================

Send questions to https://github.com/SriBalajiSMVEC


.. default-role:: code

===========
Cheat Sheet
===========

This is a quickstart reference to using uiaction. uiaction is cross-platform GUI automation module that works on Python 2 & 3. You can control the mouse and keyboard as well as perform basic image recognition to automate tasks on your computer.

**All the keyword arguments in the examples on this page are optional.**

    >>> import uiaction

uiaction works on Windows/Mac/Linux and on Python 2 & 3. Install from PyPI with `pip install uiaction`.

General Functions
-----------------

    >>> uiaction.position()  # current mouse x and y
    (968, 56)
    >>> uiaction.size()  # current screen resolution width and height
    (1920, 1080)
    >>> uiaction.onScreen(x, y)  # True if x & y are within the screen.
    True

Fail-Safes
----------

Set up a 2.5 second pause after each uiaction call:

    >>> import uiaction
    >>> uiaction.PAUSE = 2.5

When fail-safe mode is `True`, moving the mouse to the upper-left will raise a `uiaction.FailSafeException` that can abort your program:

    >>> import uiaction
    >>> uiaction.FAILSAFE = True

Mouse Functions
---------------

XY coordinates have 0, 0 origin at top left corner of the screen. X increases going right, Y increases going down.

    >>> uiaction.moveTo(x, y, duration=num_seconds)  # move mouse to XY coordinates over num_second seconds
    >>> uiaction.moveRel(xOffset, yOffset, duration=num_seconds)  # move mouse relative to its current position

If `duration` is 0 or unspecified, movement is immediate. Note: dragging on Mac can't be immediate.

    >>> uiaction.dragTo(x, y, duration=num_seconds)  # drag mouse to XY
    >>> uiaction.dragRel(xOffset, yOffset, duration=num_seconds)  # drag mouse relative to its current position

Calling `click()` just clicks the mouse once with the left button at the mouse's current location, but the keyword arguments can change that:

    >>> uiaction.click(x=moveToX, y=moveToY, clicks=num_of_clicks, interval=secs_between_clicks, button='left')

The `button` keyword argument can be `'left'`, `'middle'`, or `'right'`.

All clicks can be done with `click()`, but these functions exist for readability. Keyword args are optional:

    >>> uiaction.rightClick(x=moveToX, y=moveToY)
    >>> uiaction.middleClick(x=moveToX, y=moveToY)
    >>> uiaction.doubleClick(x=moveToX, y=moveToY)
    >>> uiaction.tripleClick(x=moveToX, y=moveToY)

Positive scrolling will scroll up, negative scrolling will scroll down:

    >>> uiaction.scroll(amount_to_scroll, x=moveToX, y=moveToY)

Individual button down and up events can be called separately:

    >>> uiaction.mouseDown(x=moveToX, y=moveToY, button='left')
    >>> uiaction.mouseUp(x=moveToX, y=moveToY, button='left')

Keyboard Functions
------------------

Key singleKeyes go to wherever the keyboard cursor is at function-calling time.

    >>> uiaction.typewrite('Hello world!\n', interval=secs_between_keys)  # useful for entering text, newline is Enter

A list of key names can be passed too:

    >>> uiaction.typewrite(['a', 'b', 'c', 'left', 'backspace', 'enter', 'f1'], interval=secs_between_keys)

The full list of key names is in `uiaction.KEYBOARD_KEYS`.

Keyboard doubleKeys like Ctrl-S or Ctrl-Shift-1 can be done by passing a list of key names to `doubleKey()`:

    >>> uiaction.doubleKey('ctrl', 'c')  # ctrl-c to copy
    >>> uiaction.doubleKey('ctrl', 'v')  # ctrl-v to paste

Individual button down and up events can be called separately:

    >>> uiaction.keyDown(key_name)
    >>> uiaction.keyUp(key_name)


Message Box Functions
---------------------

If you need to pause the program until the user clicks OK on something, or want to display some information to the user, the message box functions have similar names that JavaScript has:

    >>> uiaction.alert('This displays some text with an OK button.')
    >>> uiaction.confirm('This displays text and has an OK and Cancel button.')
    'OK'
    >>> uiaction.prompt('This lets the user type in a string and singleKey OK.')
    'This is what I typed in.'

The `prompt()` function will return `None` if the user clicked Cancel.

Screenshot Functions
--------------------

uiaction uses Pillow/PIL for its image-related data.

On Linux, you must run `sudo apt-get install scrot` to use the screenshot features.

    >>> uiaction.screenshot()  # returns a Pillow/PIL Image object
    <PIL.Image.Image image mode=RGB size=1920x1080 at 0x24C3EF0>
    >>> uiaction.screenshot('foo.png')  # returns a Pillow/PIL Image object, and saves it to a file
    <PIL.Image.Image image mode=RGB size=1920x1080 at 0x31AA198>

If you have an image file of something you want to click on, you can find it on the screen with `locateOnScreen()`.

    >>> uiaction.locateOnScreen('looksLikeThis.png')  # returns (left, top, width, height) of first place it is found
    (863, 417, 70, 13)

The `locateAllOnScreen()` function will return a generator for all the locations it is found on the screen:

    >>> for i in uiaction.locateAllOnScreen('looksLikeThis.png')
    ...
    ...
    (863, 117, 70, 13)
    (623, 137, 70, 13)
    (853, 577, 70, 13)
    (883, 617, 70, 13)
    (973, 657, 70, 13)
    (933, 877, 70, 13)

    >>> list(uiaction.locateAllOnScreen('looksLikeThis.png'))
    [(863, 117, 70, 13), (623, 137, 70, 13), (853, 577, 70, 13), (883, 617, 70, 13), (973, 657, 70, 13), (933, 877, 70, 13)]

The `locateCenterOnScreen()` function just returns the XY coordinates of the middle of where the image is found on the screen:

    >>> uiaction.locateCenterOnScreen('looksLikeThis.png')  # returns center x and y
    (898, 423)

These functions return `None` if the image couldn't be found on the screen.

Note: The locate functions are slow and can take a full second or two.

FAQ: Frequently Asked Questions
===============================

Send questions to https://github.com/SriBalajiSMVEC




=======
Roadmap
=======

uiaction is planned as a replacement for other Python GUI automation scripts, such as PyUserInput, PyKeyboard, PyMouse, pykey, etc. Eventually it would be great to offer the same type of features that Sikuli_ offers.

For now, the primary aim for uiaction is cross-platform mouse and keyboard control and a simple API.

Future features planned (specific versions not planned yet):

- A tool for determining why an image can't be found in a particular screenshot. (This is a common source of questions for users.)
- Full compatibility on Raspberry Pis.
- "Wave" function, which is used just to see where the mouse is by shaking the mouse cursor a bit. A small helper function.
- locateNear() function, which is like the other locate-related screen reading functions except it finds the first instance near an xy point on the screen.
- Find a list of all windows and their captions.
- Click coordinates relative to a window, instead of the entire screen.
- Make it easier to work on systems with multiple monitors.
- GetKeyState() type of function
- Ability to set global doubleKey on all platforms so that there can be an easy "kill switch" for GUI automation programs.
- Optional nonblocking uiaction calls.
- "strict" mode for keyboard - passing an invalid keyboard key causes an exception instead of silently skipping it.
- rename keyboardMapping to KEYBOARD_MAPPING
- Ability to convert png and other image files into a string that can be copy/pasted directly in the source code, so that they don't have to be shared separately with people's uiaction scripts.
- Test to make sure uiaction works in Windows/mac/linux VMs.
- A way to compare two images and highlight differences between them (good for pointing out when a UI changes, etc.)

Window handling features:
 - uiaction.getWindows()      # returns a dict of window titles mapped to window IDs
 - uiaction.getWindow(str_title_or_int_id)   # returns a "Win" object
 - win.move(x, y)
 - win.resize(width, height)
 - win.maximize()
 - win.minimize()
 - win.restore()
 - win.close()
 - win.position()  # returns (x, y) of top-left corner
 - win.moveRel(x=0, y=0)   # moves relative to the x, y of top-left corner of the window
 - win.clickRel(x=0, y=0, clicks=1, interval=0.0, button='left')  # click relative to the x, y of top-left corner of the window
 - Additions to screenshot functionality so that it can capture specific windows instead of full screen.

FAQ: Frequently Asked Questions
===============================

Send questions to https://github.com/SriBalajiSMVEC




.. default-role:: code

=======
Testing
=======

The unit tests for uiaction are currently not comprehensive. The tests (in basicTests.py) cover the following:

- onScreen()
- size()
- position()
- moveTo()
- moveRel()
- typewrite()
- PAUSE

Platforms Tested
================

- Python 3.4, 3.3, 3.2, 3.1, 2.7, 2.6, 2.5
- Windows
- OS X
- Raspberry Pi

(If you have run the unit tests successfully on other platforms, please tell https://github.com/SriBalajiSMVEC.)

uiaction is not compatible with Python 2.4 or before.

The keyboard functions do not work on Ubuntu when run in VirtualBox on Windows.

FAQ: Frequently Asked Questions
===============================

Send questions to https://github.com/SriBalajiSMVEC