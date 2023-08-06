"""Setup for the package."""
import subprocess

import setuptools

vue_package_version = \
    subprocess.run(["git", "describe", "--tags"], stdout=subprocess.PIPE)\
    .stdout.decode("utf-8").strip()

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name='vue-cinema',
    author='Flonc',
    description='A library to access information about vue cinemas',
    keywords='package, vue, cinema, api',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/DevFlock/vue-cinema',
    project_urls={
        'Documentation': 'https://github.com/DevFlock/vue-cinema',
        'Bug Reports':
        'https://github.com/DevFlock/vue-cinema/issues',
        'Source Code': 'https://github.com/DevFlock/vue-cinema'
    },
    package_dir={'': 'src'},
    packages=setuptools.find_packages(where='src'),
    classifiers=[
        # see https://pypi.org/classifiers/
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',

        'Programming Language :: Python :: 3.10',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',
    install_requires=[
        "requests~=2.28.1"
    ],
    version=vue_package_version
)
