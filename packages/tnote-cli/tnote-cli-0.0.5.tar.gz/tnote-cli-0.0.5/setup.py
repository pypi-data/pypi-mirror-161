from setuptools import find_packages, setup
from pathlib import Path
from setuptools import setup

VERSION = "v0.0.5"

dependencies = ["click", "rich"]


this_directory = Path(__file__).parent
long_description = (this_directory / 'README.md').read_text()

setup(
    name='tnote-cli',
    packages=find_packages(exclude='tests'),
    version=VERSION,
    description='A simple Terminal-based notes app',
    author='Carson Henrich',
    author_email='contact@carsonhenrich.com',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='MIT',
    project_urls={
        'github': 'https://github.com/carsonhenrich/tnote-cli',
    },
    classifiers=[
        'Environment :: Console',
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Information Technology',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License ',
        'Operating System :: MacOS',
        'Operating System :: POSIX',
        'Natural Language :: English',
        'Topic :: Utilities',
    ],
    #package_data=[('~/tnote-cli/notes/', ['notes/index.txt'])],
    install_requires=dependencies,
    setup_requires=['pytest-runner'],
    tests_require=['pytest==4.4.1'],
    test_suite='tests',
    entry_points={
        'console_scripts': [
            'tn = tnote.__main__:cli',
            'tnote = tnote.__main__:cli',
        ],
    },
)
