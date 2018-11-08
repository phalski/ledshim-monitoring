from setuptools import setup

setup(
    name='ledshim-monitoring',
    version='0.0.1',
    packages=['ledshim_monitoring'],
    url='',
    license='',
    author='phalski',
    author_email='mail@phalski.com',
    description='Monitor toolkit to display node stats on the Pimoroni LED SHIM',
    install_requires=[
        'phalski-ledshim>=0.1.1',
        'psutil',
        'docker'
    ]
)
