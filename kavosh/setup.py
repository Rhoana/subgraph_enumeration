import os



import numpy as np



from distutils.core import setup, Extension
from Cython.Build import cythonize



home_dir = os.path.expanduser('~')
nauty_dir = '{}/software/nauty'.format(home_dir)



extensions = [
    Extension(
        name = 'enumerate',
        include_dirs = [np.get_include(), nauty_dir],
        libraries = ['bz2'],
        library_dirs = [nauty_dir],
        sources = ['enumerate.pyx', 'cpp-enumerate.cpp', 'cpp-nauty.cpp', 'cpp-graph.cpp'],
        extra_objects = [
            nauty_dir + '/' + 'nauty.o',
            nauty_dir + '/' + 'nautil.o',
            nauty_dir + '/' + 'naugraph.o',
            nauty_dir + '/' + 'schreier.o',
            nauty_dir + '/' + 'naurng.o',
        ],
        extra_compile_args = ['-O4', '-fPIC', '-std=c++0x'],
        language = 'c++'
    )
]



setup(
    name = 'enumerate',
    ext_modules = cythonize(extensions, language_level=3)
)
