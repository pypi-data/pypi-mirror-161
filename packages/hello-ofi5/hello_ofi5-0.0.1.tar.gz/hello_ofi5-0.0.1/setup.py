from setuptools import setup, find_packages, Extension
from Cython.Build import cythonize
from Cython.Distutils import build_ext
import codecs
import os


VERSION = '0.0.1'
DESCRIPTION = 'A basic hello package'

extensions = [
    Extension(name='hello_pro',  # using dots!
              sources=['hello_pro.pyd'])]
# Setting up
setup(
    name="hello_ofi5",
    version=VERSION,
    author="Andrew (Florian Dedov)",
    author_email="<ablasi@bettercare.es>",
    description=DESCRIPTION,
    packages=find_packages(),
    ext_modules=cythonize(extensions),
    cmdclass= {'build_ext': build_ext},
    install_requires=[],
    keywords=['python', 'video', 'stream', 'video stream', 'camera stream', 'sockets'],
    include_package_data=True,
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)