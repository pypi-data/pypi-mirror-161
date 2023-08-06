"""Python setup.py for iuser_i18n package"""
import io
import os
from setuptools import find_packages, setup


def read(*paths, **kwargs):
  """Read the contents of a text file safely.
    >>> read("iuser_i18n", "VERSION")
    '0.1.0'
    >>> read("README.md")
    ...
    """

  content = ""
  with io.open(
      os.path.join(os.path.dirname(__file__), *paths),
      encoding=kwargs.get("encoding", "utf8"),
  ) as open_file:
    content = open_file.read().strip()
  return content


setup(
    name="iuser_i18n",
    version=read("iuser_i18n", "VERSION"),
    description="iuser_i18n",
    url="https://github.com/iuser-dev/iuser-i18n-translate/",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=["tests", ".github"]),
    install_requires=["volcengine"],
    scripts=['iuser_i18n/i18n'],
    author='iuser',
    author_email='iuser.link@gmail.com',
)
