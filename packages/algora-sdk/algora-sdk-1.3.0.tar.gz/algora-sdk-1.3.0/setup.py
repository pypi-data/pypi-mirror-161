import sys
import subprocess
import setuptools


try:
    import pypandoc
    long_description = pypandoc.convert_file('README.md', 'rst')
except(IOError, ImportError):
    long_description = open('README.md').read()


def get_tag():
    tag = subprocess.getoutput('git tag --sort=version:refname | tail -n1')
    commits = subprocess.getoutput(f'git rev-list {tag}..HEAD --count')
    return f'{tag}.{commits}'


def is_public():
    if '--public' in sys.argv:
        sys.argv.remove('--public')
        return True
    return False


def get_packages_arguments():
    default_args = {
        'include': ['algora*'],
        'exclude': ['tests.*']
    }

    if is_public():
        default_args.update({
            'exclude': ['tests.*', '*quant*']
        })

    return default_args


setuptools.setup(
    name="algora-sdk",
    version=get_tag(),
    author="Algora Labs",
    author_email="hello@algoralabs.com",
    description="Algora Labs Python SDK",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://docs.algoralabs.com",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    python_requires=">=3.7",
    packages=setuptools.find_packages(**get_packages_arguments()),
    install_requires=[
        "requests",
        "pandas",
        "cachetools",
        "pydash",
        "PyYaml",
        "pydantic",
        "asyncio",
        "aiohttp",
        "aiocache",
        "fastparquet",
        "scipy",
        "pandas-market-calendars"
    ]
)
