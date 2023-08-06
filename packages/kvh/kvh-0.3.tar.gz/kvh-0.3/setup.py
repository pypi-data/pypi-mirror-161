import sys

from pybind11 import get_cmake_dir
# Available at setup time due to pyproject.toml
from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import setup, find_packages

sys.path.insert(0, "kvh")
from version import __version__

# The main interface is through Pybind11Extension.
# * You can add cxx_std=11/14/17, and then build_ext can be removed.
# * You can set include_pybind11=false to add the include directory yourself,
#   say from a submodule.
#
# Note:
#   Sort input source files if you glob sources to ensure bit-for-bit
#   reproducible builds (https://github.com/pybind/python_example/pull/53)
ext_modules = [
    Pybind11Extension("kvh.ckvh",
        ["kvh/ckvh.cpp"],
        # Example: passing in the version to the compiled code
        define_macros = [('VERSION_INFO', __version__)],
        cxx_std=11,
        ),
]
setup(
   name="kvh",
   version=__version__,
   author="Serguei Sokol",
   author_email="sokol@insa-toulouse.fr",
   url="https://forgemia.inra.fr/mathscell/kvh",
   description="KVH format reader/writer",
   keywords="key-value hierarchy",
   license="GNU General Public License v2 or later (GPLv2+)",
   long_description="KVH format reader/writer",
   packages=find_packages(),
   #package_data={"kvh": ["*.txt"]},
   #py_modules=["kvh"],
   ext_modules=ext_modules,
   extras_require={"test": "pytest"},
   # Currently, build_ext only provides an optional "highest supported C++
   # level" feature, but in the future it may provide more features.
   #cmdclass={"build_ext": build_ext},
   python_requires=">=3.6",
   classifiers=[
      "Environment :: Console",
      "Intended Audience :: End Users/Desktop",
      "License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)",
      "Operating System :: OS Independent",
      "Programming Language :: Python :: 3",
      "Programming Language :: C++",
      "Topic :: Scientific/Engineering",
      "Topic :: Text Processing",
   ],
   project_urls={
      "Source": "https://forgemia.inra.fr/mathscell/kvh",
      "Tracker": "https://forgemia.inra.fr/mathscell/kvh/-/issues",
   },
)
