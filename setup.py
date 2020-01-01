from setuptools import setup, find_packages

setup(
    name='dupfinder',
    version='0.2',
    url='https://github.com/jirih/dupfinder',
    packages=find_packages(),
    license='GPLv3',
    author='jirih',
    author_email='',
    description='Duplicates finder',
    long_description='Duplicates finder',
    long_description_content_type="text/markdown",
    python_requires='>=3.8',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'dupfinder = dupfinder.dupfinder:main'
        ]
    }, install_requires=[
        'progressbar',
    ],

)
