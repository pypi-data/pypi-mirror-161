from setuptools import find_packages, setup

try:
    with open("README.rst", 'r') as fp:
        long_description = fp.read()
except IOError:
    print("Could not read README.rst, long_description will be empty.")
    long_description = ""

setup(
    name='hazwaz',
    version='0.0.2',
    packages=find_packages(),
    test_suite='tests',
    install_requires=[],
    python_requires='>=3',
    # Metadata
    author="Elena ``of Valhalla'' Grandi",
    author_email='valhalla@trueelena.org',
    description='write command line scripts',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    license='AGPLv3+',
    keywords='cli',
    url='https://hazwaz.trueelena.org/',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',  # noqa: E501
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: User Interfaces',
    ],
    project_urls={
        'Source': 'https://git.sr.ht/~valhalla/hazwaz',
        'Documentation': 'https://hazwaz.trueelena.org/',
        'Tracker': 'https://todo.sr.ht/~valhalla/hazwaz',
    },
)
