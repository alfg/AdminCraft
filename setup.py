#!/usr/bin/env python

from setuptools import setup

setup(name='AdminCraft',
      version='0.3',
      description='Admin Web GUI Server Wrapper for Minecraft Servers',
      author='Alfred Gutierrez',
      author_email='alf.g.jr@gmail.com',
      url='https://github.com/Alf-/AdminCraft',
      packages=['admincraft'],
      install_requires=['Flask', 'APScheduler']
)

