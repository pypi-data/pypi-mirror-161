from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize
from numpy import get_include

extensions = [
    Extension("cythLeastR", ['src/cythLeastR.pyx', 'src/ep21R.c', 'src/epph.c'], include_dirs=['src', get_include()]),
    Extension("cythKronPlus", ["src/cythKronPlus.pyx"]),
]

setup(
    name="pySPaRTAN-helper",
    version="0.0.0",
    packages=['pySPaRTAN-helper'],
    package_dir={'pySPaRTAN-helper': 'src/'},
    ext_modules=cythonize(extensions),
    include_dirs=get_include(),
    install_requires=[
        'numpy>=1.19.2',
    ]
)