"""
Setup for UBA CalQlator
"""

from setuptools import setup
import pathlib

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(name='uba-calqlator',
      version='1.2.2',
      description='Functions to interact with the Seven2one TechStack via CalQlator',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='http://www.seven2one.de',
      author='Seven2one Informationssysteme GmbH',
      author_email='info@seven2one.de',
      license='MIT',
      packages=['uba_calqlator'],
      include_package_data=True,
      install_requires=[
            'pandas', 'seven2one>=2.34'
            ],
      classifiers =[
            'Development Status :: 3 - Alpha',
            'Natural Language :: English',
            'Operating System :: OS Independent',
            ],
      python_requires='>=3.7',
      zip_safe=False)
