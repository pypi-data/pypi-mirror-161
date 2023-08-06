from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))

LONG_DESCRIPTION = '''
## UMAHTLIB

umathlib is a simple math library that can perform simple mathemetical operations.
'''
    
setup(
    name='umathlib',
    version='0.0.1',
    author='mr-cob',
    author_email='mr.cob.004@gmail.com',
    description='A simple math library',
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    keywords=['python', 'math', 'science'],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
    ]
)