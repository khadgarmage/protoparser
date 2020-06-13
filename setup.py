import setuptools

with open("README.md", "r") as fh:
  long_description = fh.read()

setuptools.setup(
  name="proto3parser",
  version="0.0.1",
  author="xiaochun.liu",
  author_email="liuxiaochun@apache.org",
  description="A package for parsing proto3 files",
  long_description=long_description,
  long_description_content_type="text/markdown",
  url="https://github.com/khadgarmage/proto3parser",
  packages=setuptools.find_packages(),
  classifiers=[
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: Apache2.0 License",
    "Operating System :: OS Independent",
    "Topic :: Proto",
    "Topic :: Software Development :: Libraries :: Python Modules",
  ],
  install_requires=[
    'pandas>=0.20.0',
    'numpy>=1.14.0'
  ],
)
