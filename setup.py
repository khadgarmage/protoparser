import setuptools

with open("README.md", "r") as fh:
  long_description = fh.read()

setuptools.setup(
  name="proto-parser",
  version="1.6.3",
  author="xiaochun.liu",
  author_email="liuxiaochun@apache.org",
  description="A package for parsing proto files",
  long_description_content_type="text/markdown",
  url="https://github.com/khadgarmage/protoparser",
  packages=setuptools.find_packages(),
  classifiers=[
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: Apache Software License",
    "Operating System :: OS Independent",
    "Topic :: Software Development :: Libraries :: Python Modules",
  ],
  install_requires=[
    'lark-parser>=0.8.6',
    'numpy>=1.14.0'
  ],
)
