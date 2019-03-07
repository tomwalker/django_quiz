#!/usr/bin/env python3

import os
import sys
os.environ['DJANGO_SETTINGS_MODULE'] = 'test_settings'
test_dir = os.path.dirname(__file__)
sys.path.insert(0, test_dir)

import django
from django.test.utils import get_runner
from django.conf import settings


def runtests():
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=1, interactive=True)
    failures = test_runner.run_tests(
        ['quiz', 'essay', 'multichoice', 'true_false']
    )
    sys.exit(bool(failures))

if __name__ == '__main__':
    runtests()
