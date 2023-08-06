from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
   'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='DataCatalogPackage',
  version='0.0.1',
  description='Data Catalog package',
  long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
  url='',  
  author='Ammor Ayoub',
  author_email='ammorayoub5@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='Data Catalog', 
  packages=find_packages(),
  install_requires=[''] 
)