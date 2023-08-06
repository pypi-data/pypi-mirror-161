import os
import sys
from pathlib import Path

from pybind11.setup_helpers import Pybind11Extension
from setuptools import find_packages, setup

# Compiling requires Boost header files. The compiler can try and find Boost at the usual locations
# Alternatively the BOOST_DIR environment variable can be set, point to the directory with
# the Boost header files
BOOST_DIR = Path(os.environ.get("BOOST_DIR", "")).absolute().parent


def read_file_or_empty_str(file, comment_tag=None):
    try:
        with open(file) as fh:
            if comment_tag is not None:
                return "\n".join(
                    r.strip("\n") for r in fh.readlines() if not r.startswith(comment_tag)
                )
            return fh.read()
    except FileNotFoundError:
        return ""


REQUIREMENTS = read_file_or_empty_str("requirements.txt")
README = read_file_or_empty_str("README.rst")
VERSION = read_file_or_empty_str("VERSION", comment_tag="#")
CURRENT_DIR = Path(__file__).parent
SRC_DIR = CURRENT_DIR / "src"


_DEBUG = False
_DEBUG_LEVEL = 0
if sys.platform.startswith("win32"):
    extra_compile_args = []
else:
    extra_compile_args = ["-Wall", "-Wextra", "-std=c++17"]
    if _DEBUG:
        extra_compile_args += ["-g3", "-O0", f"-DDEBUG={_DEBUG_LEVEL}", "-UNDEBUG"]
    else:
        extra_compile_args += ["-DNDEBUG", "-O3"]

ext_modules = [
    Pybind11Extension(
        "_movici_geo_query",
        sorted(str(file.relative_to(CURRENT_DIR)) for file in SRC_DIR.glob("*.cpp")),
        include_dirs=[str(SRC_DIR), str(BOOST_DIR)],
        extra_compile_args=extra_compile_args,
    ),
]

setup(
    name="movici-geo-query",
    version=VERSION,
    description="Geospatial queries powered by Boost Geom",
    long_description=README,
    long_description_content_type="text/x-rst",
    ext_modules=ext_modules,
    author="NGinfra - Movici",
    author_email="movici@nginfra.nl",
    license="Movici Public License",
    packages=find_packages(),
    install_requires=REQUIREMENTS,
    python_requires=">=3.8",
    test_suite="tests",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "License :: Free for non-commercial use",
        "License :: Other/Proprietary License",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Software Development :: Libraries",
        "Topic :: Scientific/Engineering :: GIS",
    ],
    project_urls={"Documentation": "https://docs.movici.nl/"},
)
