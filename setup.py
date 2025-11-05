import glob

from pybind11 import get_include
from pybind11.setup_helpers import Pybind11Extension
from setuptools import setup

matching_sources = glob.glob("cpp/src/matching/**/*.cpp", recursive=True)

ext_modules = [
    Pybind11Extension(
        "py4swiss.matching_computer",
        [
            "python_bindings/computer_bindings.cpp",
            *matching_sources,
        ],
        include_dirs=[
            "cpp/include",
            "cpp/include/matching",
            "cpp/include/swisssystems",
            "cpp/include/tournament",
            "cpp/include/utility",
            get_include(),
        ],
        language="c++",
        cxx_std=14,
    ),
    Pybind11Extension(
        "py4swiss.dynamicuint",
        [
            "python_bindings/dynamicuint_bindings.cpp",
            *matching_sources,
        ],
        include_dirs=[
            "cpp/include",
            "cpp/include/matching",
            "cpp/include/swisssystems",
            "cpp/include/tournament",
            "cpp/include/utility",
            get_include(),
        ],
        language="c++",
        cxx_std=14,
    ),
]

setup(ext_modules=ext_modules)
