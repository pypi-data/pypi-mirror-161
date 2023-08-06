from setuptools import setup

setup(name='converter_package',
      version='0.3',
      description='This converter library is able to transform the ACCORDION application model to K3s configuration files',
      author='Giannis Korontanis',
      author_email='gkorod2@gmail.com',
      license='MIT',
      packages=['converter_package'],
      install_requires=[
          'pyyaml==5.3.1', 'kafka==1.3.5', 'hurry.filesize==0.9', 'oyaml==1.0'
      ],
      zip_safe=False)
