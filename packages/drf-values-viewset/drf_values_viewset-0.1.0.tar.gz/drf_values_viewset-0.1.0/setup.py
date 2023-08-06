import io
import os
from setuptools import setup


def read(*paths, **kwargs):
    """Read the contents of a text file safely.
    >>> read("drf_values_viewset", "VERSION")
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
    name="drf_values_viewset",
    version=read("drf_values_viewset", "VERSION"),
    description="A Viewset and Mixins for Django Rest Framework that attempts to prevent the N+1 query problem",
    url="https://github.com/learningequality/drf-values-viewset",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    author="Learning Equality",
    packages=[str("drf_values_viewset")],
    install_requires=["djangorestframework"],
)
