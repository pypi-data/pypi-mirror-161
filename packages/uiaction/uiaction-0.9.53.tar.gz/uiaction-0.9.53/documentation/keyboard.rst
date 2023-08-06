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

