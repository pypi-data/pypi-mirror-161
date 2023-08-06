from distutils.core import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
setup(
    name="aifund",
    packages=['aifund'],
    version="0.0.7",
    license='MIT',
    description="A AI fund",
    author="yebaige",
    author_email="silence_tiano@163.com",
    url="https://github.com/silenceTiano/aifund",
    long_description=long_description,
    long_description_content_type="text/markdown",
    project_urls={
        "Bug Tracker": "https://github.com/silenceTiano/aifund/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
