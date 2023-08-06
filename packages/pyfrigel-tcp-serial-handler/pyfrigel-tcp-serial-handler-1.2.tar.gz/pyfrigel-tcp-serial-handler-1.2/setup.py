from setuptools import setup, find_packages

setup(name='pyfrigel-tcp-serial-handler',
      version='1.2',
      description='Frigel TCP to serial handler for PEMS protocol',
      packages=find_packages(),
      license='LICENSE.txt',
      url='http://pypi.python.org/pypi/pyfrigel-tcp-serial-handler/',
      install_requires=[
       "pyserial",
       'pyserial-asyncio'
   ],
      zip_safe=False)