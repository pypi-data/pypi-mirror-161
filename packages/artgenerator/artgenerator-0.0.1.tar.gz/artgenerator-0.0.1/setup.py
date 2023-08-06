from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  "Operating System :: Unix",
  "Operating System :: MacOS :: MacOS X",
  "Operating System :: Microsoft :: Windows",
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='artgenerator',
  version='0.0.1',
  description='Basic random image effects with Python.',
  long_description=open('README.md').read() + '\n\n' + open('CHANGELOG.txt').read(),
  url='https://github.com/owardlaw',  
  author='Owen Wardlaw',
  author_email='owen.wardlaw2017@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='calculator', 
  packages=find_packages(),
  install_requires=['numpy', 'opencv-python'] 
)