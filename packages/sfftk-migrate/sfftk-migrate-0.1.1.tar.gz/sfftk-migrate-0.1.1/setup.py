from setuptools import setup, find_packages

from sfftk_migrate import SFFTK_MIGRATIONS_VERSION

with open('README.rst') as f:
    LONG_DESCRIPTION = f.read()

setup(
    name='sfftk-migrate',
    version=SFFTK_MIGRATIONS_VERSION,
    packages=find_packages(),
    url='',
    license='Apache 2.0',
    author='Paul K. Korir, PhD',
    author_email='pkorir@ebi.ac.uk, paul.korir@gmail.com',
    description='Migrate older EMDB-SFF files to newer versions',
    long_description_content_type='text/x-rst',
    long_description=LONG_DESCRIPTION,
    install_requires=['lxml'],
    python_requires='>=3',
    classifiers=[
        # maturity
        u"Development Status :: 4 - Beta",
        # environment
        u"Environment :: Console",
        u"Intended Audience :: Developers",
        u"Intended Audience :: Science/Research",
        # license
        u"License :: OSI Approved :: Apache Software License",
        # os
        u"Operating System :: OS Independent",
        # python versions
        u"Programming Language :: Python :: 3",
        u"Programming Language :: Python :: 3.5",
        u"Programming Language :: Python :: 3.6",
        u"Programming Language :: Python :: 3.7",
        u"Programming Language :: Python :: 3.8",
        u"Programming Language :: Python :: 3.9",
        u"Programming Language :: Python :: 3.10",
        u"Topic :: Software Development :: Libraries :: Python Modules",
        u"Topic :: Terminals",
        u"Topic :: Text Processing",
        u"Topic :: Text Processing :: Markup",
        u"Topic :: Utilities",
    ],
    entry_points={
        'console_scripts': [
            'sff-migrate = sfftk_migrate.main:main',
        ]
    },
    package_data={
        'sfftk_migrate': [
            'stylesheets/*.xsl',
        ],
    }
)
