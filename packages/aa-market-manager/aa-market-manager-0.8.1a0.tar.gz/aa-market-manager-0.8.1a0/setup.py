import os

from setuptools import find_packages, setup

from marketmanager import __version__

# read the contents of your README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name="aa-market-manager",
    version=__version__,
    packages=find_packages(),
    include_package_data=True,
    license="MIT",
    description="AllianceAuth Market Management Tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Joel Falknau',
    author_email='ozirascal@gmail.com',
    url="https://gitlab.com/tactical-supremacy/aa-market-manager",
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 3.2',
        'Framework :: Django :: 4.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',

    ],
    python_requires="~=3.8",
    install_requires=[
        "allianceauth>=2.11.0",
        "django-eveuniverse",
        "py-cord>=2.0.0",
        "django-solo>=2.0.0"
        ],
)
