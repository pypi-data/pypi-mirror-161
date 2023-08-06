#!/usr/bin/env python
# -*- coding: utf-8 -*-

# License Agreement
# This code is licensed under the outer restricted Tiss license:
#
#  Copyright [2014]-[2019] Thales Services under the Thales Inner Source Software License
#  (Version 1.0, InnerPublic -OuterRestricted the "License");
#
#  You may not use this file except in compliance with the License.
#
#  The complete license agreement can be requested at contact@punchplatform.com.
#
#  Refer to the License for the specific language governing permissions and limitations
#  under the License.


formatters: dict[str, str] = {
    "RED": "\033[91m",
    "ERROR": "\033[91m",
    "GREEN": "\033[92m",
    "SUCCESS": "\033[92m",
    "YELLOW": "\033[33m",
    "WARNING": "\033[33m",
    "WHITE": "\033[37m",
    "BLUE": "\033[34m",
    "INFO": "\033[34m",
    "CYAN": "\033[36m",
    "MAGENTA": "\033[35m",
    "BLACK": "\033[30m",
    "DARKWHITE": "\033[37m",
    "DARKYELLOW": "\033[33m",
    "DARKGREEN": "\033[32m",
    "DARKBLUE": "\033[34m",
    "DARKCYAN": "\033[36m",
    "DARKRED": "\033[31m",
    "DARKMAGENTA": "\033[35m",
    "END": "\033[0m",
}


def color(apply_color: str, message: str) -> str:
    """apply color to a given message when output to terminal

    .. warning::

        Although this method is accessible as public, it is tagged as an internal one
        Changes might occur without notice

    :param apply_color: color code you want to apply to your message
    :param message: the actual string message to be colored
    :return value: inputted message will have added colored ascii

    Available colors are:
        * RED
        * GREEN
        * WHITE
        * YELLOW
        * BLUE
        * CYAN
        * MAGENTA
        * BLACK
        * DARKWHITE
        * DARKYELLOW
        * DARKGREEN
        * DARKBLUE
        * DARKCYAN
        * DARKRED
        * DARKMAGENTA
    """

    prefix_colored_string: str = "{" + apply_color + "}"
    prefix_colored_string = prefix_colored_string.format(**formatters)
    suffix_colored_string = "{END}"
    suffix_colored_string = suffix_colored_string.format(**formatters)
    colored_string = prefix_colored_string + message + suffix_colored_string
    return colored_string


def print_debug(message: str) -> None:
    """Add debug color to message and then prints it on stdout

    :color value: No color is applied

    :param message: Debug colored message
    :return value: Display textual information on terminal without returning anything
    """
    print(message)


def print_error(message: str) -> None:
    """Add error color to message and then prints it on stdout

    :color value: RED

    :param message: Debug colored message
    :return value: Display textual information on terminal without returning anything
    """
    print(color("RED", "ERROR: %s" % message))


def print_message(message: str) -> None:
    """Add color to message and then prints it on stdout

    :color value: DARKBLUE

    :param message: Debug colored message
    :return value: Display textual information on terminal without returning anything
    """
    print(color("DARKBLUE", message))


def print_success(message: str) -> None:
    """Add success color to message and then prints it on stdout

    :color value: GREEN

    :param message: Debug colored message
    :return value: Display textual information on terminal without returning anything
    """
    print(color("GREEN", message))


def print_warning(message: str) -> None:
    """Add warning color to message and then prints it on stdout

    :color value: DARKYELLOW

    :param message: Debug colored message
    :return value: Display textual information on terminal without returning anything
    """
    print(color("DARKYELLOW", "WARNING: %s" % message))
