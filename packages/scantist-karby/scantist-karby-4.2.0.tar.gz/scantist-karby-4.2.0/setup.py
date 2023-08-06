import setuptools
from karby.util.constants import version

with open("README.md", "r") as fh:
  long_description = fh.read()

requirement = [
  'requests',
  'lxml'
]

setuptools.setup(
  name="scantist-karby",
  version=version,
  author="scantist",
  author_email="lida@scantist.com",
  description="scan the provided projects by using whitesource or scantist,"
              " and convert the result into scantist's format",
  install_requires=requirement,
  long_description=long_description,
  long_description_content_type="text/markdown",
  packages=setuptools.find_packages(),
  entry_points={
    'console_scripts': [
      'karby = karby.sca_tool_scan:main',
    ]
  },
  classifiers=[
      "Programming Language :: Python :: 3",
      "License :: OSI Approved :: MIT License",
      "Operating System :: OS Independent",
    ]
)

