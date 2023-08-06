from setuptools import setup, Extension
from Cython.Distutils import build_ext

src = [
    'mp2hudcolor/mp2hudcolor_wrapper.pyx'
]

extensions = [
    Extension("mp2hudcolor", src)
]

setup(
    ext_modules=extensions,
    cmdclass={'build_ext': build_ext},
    package_data={'mp2hudcolor': ['mp2hudcolor.c']}
)
