from setuptools import setup, find_packages

with open('README.rst') as fp:
    long_description = fp.read()

CLASSIFIERS = """
Development Status :: 3 - Alpha
Intended Audience :: Education
License :: OSI Approved :: BSD License
Programming Language :: Python :: 3.5
Programming Language :: Python :: 3.6
Programming Language :: Python :: 3.7
Programming Language :: Python :: 3.8
Operating System :: POSIX
Operating System :: Unix
"""

setup(
    name='practicon',
    version='0.3',
    author='Rene van Paassen',
    author_email='rene.vanpaassen@gmail.com',
    url='https://gitlab.tudelft.nl/rvanpaassen/practicon',
    description='Control theory and matrix calculation Moodle/CodeRunner plugin',
    long_description=long_description,
    packages=find_packages(),
    classifiers=[f for f in CLASSIFIERS.split('\n') if f],
    install_requires=('numpy', 'scipy', 'control', 'slycot', 'json5',
                      'pyparsing'),
    tests_require=('pytest'),
    test_suite='pytest'
)
