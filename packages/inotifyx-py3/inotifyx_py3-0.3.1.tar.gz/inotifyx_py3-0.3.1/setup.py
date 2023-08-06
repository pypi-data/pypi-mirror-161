#!/usr/bin/env python

# Author: Forest Bond
# This file is in the public domain.

import os, sys, subprocess
# from distutils.core import Extension
from setuptools import Extension


sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))


from setuplib import setup


def get_version(release_file):
    try:
        f = open(release_file, 'r')
        try:
            return f.read().strip()
        finally:
            f.close()
    except (IOError, OSError):
        status, output = subprocess.getstatusoutput('bzr revno')
        if status == 0:
            return 'bzr%s' % output.strip()
    return 'unknown'


version = get_version('release')

setup(
  name = 'inotifyx_py3',
  distinfo_module = 'inotifyx.distinfo',
  version = version,
  description = 'Simple Linux inotify bindings',
  author = 'Forest Bond',
  author_email = 'forest@forestbond.com',
  url = 'https://launchpad.net/inotifyx/',
  packages = ['inotifyx'],
  ext_modules = [
    Extension(
      'inotifyx.binding',
      sources = [os.path.join('inotifyx', 'binding.c')],
    ),
  ],
)
