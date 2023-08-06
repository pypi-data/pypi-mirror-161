import setuptools
from distutils.core import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
setup(
    name="aifund",
    version="0.0.4",
    author="yebaige",
    author_email="silence_tiano@163.com",
    description="A AI fund",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/silenceTiano/aifund",
    project_urls={
        "Bug Tracker": "https://github.com/silenceTiano/aifund/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=['aifund'],
    python_requires=">=3.7",
)
