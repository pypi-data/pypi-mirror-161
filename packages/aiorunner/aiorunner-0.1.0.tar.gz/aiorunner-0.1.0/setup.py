import re
from pathlib import Path

from setuptools import setup

path = Path(__file__).parent
txt = (path / "aiorunner" / "__init__.py").read_text("utf-8")
version = re.findall(r"^__version__ = \"([^\"]+)\"\r?$", txt, re.M)[0]
readme = (path / "README.rst").read_text("utf-8")

setup(
    name="aiorunner",
    version=version,
    description="Handle signals and cleanup context",
    long_description=readme,
    long_description_content_type="text/x-rst",
    url="https://github.com/gleb-chipiga/aiorunner",
    license="MIT",
    author="Gleb Chipiga",
    # author_email='',
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 3 - Alpha",
        "Operating System :: POSIX",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Topic :: Internet",
        "Framework :: AsyncIO",
    ],
    packages=["aiorunner"],
    package_data={"aiorunner": ["py.typed"]},
    python_requires=">=3.8,<3.11",
    tests_require=[
        "pytest",
        "pytest-asyncio",
        "pytest-cov",
    ],
)
