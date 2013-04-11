#!/usr/bin/env python
import os
import sys
from os.path import join, abspath, dirname

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "testapp.settings")

    sys.path.insert(0, join(dirname(abspath(__file__)), ".."))

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
