import setuptools

requirements = ["aiohttp"]

with open("README.md", "r", encoding="utf-8") as f:
    long_desc = f.read()

version = "v0.0.1.dev"


name = "pyrunaway"

classifiers = [
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    "Operating System :: OS Independent",
]


setuptools.setup(
    name=name,
    version=version,
    author="",
    author_email="",
    description="",
    long_description=long_desc,
    long_description_content_type="text/markdown",
    url="",
    project_urls={},
    license="",
    keywords=[],
    packages=setuptools.find_packages(),
    install_requires=requirements,
    classifiers=classifiers,
    python_requires=">3.7, <3.11",
)
