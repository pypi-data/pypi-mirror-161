from distutils.core import setup
from setuptools import find_packages


with open("README.rst", "r") as f:
  long_description = f.read()


setup(name='pymdocx',  # 包名
      version='0.4.0',  # 版本号
      description='pydocx is a Python library for merging revised and commented Microsoft Word files.',
      long_description=long_description,
      author='mirrornight',
      author_email='mirrornighth@gmail.com',
      url='https://github.com/mirrornight/pydocx',
      install_requires=['bayoo-docx==0.2.17'],
      license='MIT License',
      packages=find_packages(),
      platforms=["all"],
      classifiers=[
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
      ],
      )