from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='ledshim-monitoring',
    version='0.0.1',
    packages=['ledshim_monitoring'],
    url='https://github.com/phalski/ledshim-monitoring',
    author='phalski',
    author_email='mail@phalski.com',
    description='Monitor toolkit to display node stats on the Pimoroni LED SHIM',
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        'phalski-ledshim>=0.2.2',
        'psutil',
        'docker'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
