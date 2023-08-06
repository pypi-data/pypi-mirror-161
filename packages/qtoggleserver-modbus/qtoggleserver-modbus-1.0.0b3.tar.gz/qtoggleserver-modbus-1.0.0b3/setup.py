
from setuptools import setup, find_namespace_packages


setup(
    name='qtoggleserver-modbus',
    version='1.0.0-beta.3',
    description='Modbus client/server for qToggleServer',
    author='Calin Crisan',
    author_email='ccrisan@gmail.com',
    license='Apache 2.0',

    packages=find_namespace_packages(),

    install_requires=[
        'pymodbus>=3.0.0.dev4',
        'pyserial-asyncio',
    ]
)
