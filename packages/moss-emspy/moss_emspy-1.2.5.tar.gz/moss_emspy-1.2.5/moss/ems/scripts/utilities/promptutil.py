# -*- coding: utf-8 -*-
#
# Copyright (c) 2020  by M.O.S.S. Computer Grafik Systeme GmbH
#                         Hohenbrunner Weg 13
#                         D-82024 Taufkirchen
#                         http://www.moss.de#

# -*- coding: utf-8 -*-

import sys
from getpass import getpass

this = sys.modules[__name__]

this.default_max_try = 5
this.default_interactive = True
this.default_clear_before_return = False
this.default_is_secure = False
this.default_required = True


def set_prompt_defaults(
    max_try=this.default_max_try,
    required=this.default_required,
    is_secure=this.default_is_secure,
    interactive=this.default_interactive,
    clear_before_return=this.default_clear_before_return,
):
    this.default_max_try = max_try
    this.default_required = required
    this.default_is_secure = is_secure
    this.default_interactive = interactive
    this.default_clear_before_return = clear_before_return


def prompt(
    message,
    default=None,
    max_try=None,
    required=None,
    is_secure=None,
    is_bool=False,
    interactive=None,
    clear_before_return=None,
):
    if max_try is None:
        max_try = this.default_max_try

    if required is None:
        required = this.default_required

    if is_secure is None:
        is_secure = this.default_is_secure

    if interactive is None:
        interactive = this.default_interactive

    if clear_before_return is None:
        clear_before_return = this.default_clear_before_return

    result = None

    if interactive is False:
        if required:
            exit_when_empty(
                result,
                "Expected Parameter {parameter} to be defined:".format(
                    parameter=message
                ),
            )

        return default

    if default is not None:
        message = "{message} ({default})".format(message=message, default=default)

    message = message + ": "

    while max_try > 0 and result is None:
        max_try = max_try - 1

        if is_secure:
            result = getpass(message)
        else:
            result = input(message)

            if result == "" and default is not None:
                result = default
            elif is_bool:
                result = result.lower() in ["y", "true", "yes"]

        result = result.strip()

        if required and result == "":
            result = None

    if clear_before_return:
        print("\033[A                                   \033[A")

    return result


def exit_when_empty(value, message):
    if value is None or value == "":
        print(message)
        sys.exit(1)
