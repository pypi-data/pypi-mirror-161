from setuptools import setup
from io import open
import re

def read(filename):
    with open(filename, encoding='utf-8') as file:
        return file.read()


setup(name='Kuchizu',
      version='1.0.0',
      description='Kuchizu api.',
      long_description='Just the Kuchizu api.',
      long_description_content_type="text/markdown",
      author='Kuchizu',
      author_email='Kuchizu@bk.ru',
      url='https://github.com/eternnoir/pyTelegramBotAPI',
      packages = ['Kuchizu'],
      license='GPL2',
      keywords='Kuchizu',
      install_requires=['requests'],
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Programming Language :: Python :: 3',
          'Environment :: Console',
          'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
      ],

      )
