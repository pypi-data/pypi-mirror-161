from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='AlphaDigits',
  version='0.0.1',
  description='find total number of character and numberical in a srting ',
  long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
  url='',  
  author='Bala shanmuga veeran',
  author_email='veeranbalashanmuga@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='AlphaDigits', 
  packages=find_packages(),
  install_requires=[''] 
)