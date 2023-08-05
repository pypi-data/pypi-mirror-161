#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import glob
from setuptools import find_packages, setup, Extension
'''
ext_modules = []
try:
    from pybind11.setup_helpers import Pybind11Extension, ParallelCompile, naive_recompile
    # `N` is to set the bumer of threads
    # `naive_recompile` makes it recompile only if the source file changes. It does not check header files!
    ParallelCompile("NPY_NUM_BUILD_JOBS", needs_recompile=naive_recompile, default=4).install()
    # could only be relative paths, otherwise the `build` command would fail if you use a MANIFEST.in to distribute your package
    # only source files (.cpp, .c, .cc) are needed
    source_files = glob.glob('thirdparty/streampuller/*.cpp', recursive=True)
    # If any libraries are used, e.g. libabc.so
    include_dirs = ["/usr/include/x86_64-linux-gnu/", "./thirdparty/streampuller/"]
    library_dirs = ["/usr/lib/x86_64-linux-gnu/"]
    # (optional) if the library is not in the dir like `/usr/lib/`
    # either to add its dir to `runtime_library_dirs` or to the env variable "LD_LIBRARY_PATH"
    # MUST be absolute path
    runtime_library_dirs = [os.path.abspath("LINK_DIR")]
    libraries = ["avformat", "avcodec", "avutil"]
    ext_modules = [
        Pybind11Extension(
            "ascend.StreamPuller", # depends on the structure of your package
            source_files,
            # Example: passing in the version to the compiled code
            define_macros=[('VERSION_INFO', 0.1)],
            include_dirs=include_dirs,
            library_dirs=library_dirs,
            runtime_library_dirs=runtime_library_dirs,
            libraries=libraries,
            cxx_std=14,
            language='c++'
        ),
    ]
except ImportError:
    pass
'''
long_description = None 
with open('./README.md', 'r', encoding="utf-8") as fr:
    long_description = fr.read()


setup(
    name='ascendfly',
    version='1.3',
    description='Ascend inference framework',
    keywords='ascend detection and classification',
    packages=find_packages(exclude=('configs', 'tools', 'cv2', 'tests', 'docs')),
    include_package_data=True,
    long_description= long_description,
    # ext_modules=ext_modules,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.7',
    ],
    url='https://gitee.com/ascend-fae/ascendfly',
    author='zhengguojian',
    author_email='kfengzheng@163.com',
    # setup_requires=["pybind11"],
    install_requires=['numpy>=1.14', 'av>=8.0.2', 'objgraph>=3.5.0', 'prettytable>=2.1.0'],
    # extras_requires = {'cv2':['opencv-python>=3.4.2'], 'pybind11':['pybind11>=2.10.0']},
    extras_requires = {'cv2':['opencv-python>=3.4.2']},
    zip_safe=False)
