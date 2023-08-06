from setuptools import setup

import bioblu

setup(
    name='bioblu',
    version=bioblu.__version__,
    packages=['bioblu', 'bioblu.ds_manage', 'bioblu.unittests', 'bioblu.detectron'],
    install_requires=[
        "ExifRead",
        "Pillow",
        "matplotlib",
        "numpy",
        "opencv-python",
        "pandas",
        "piexif",
        "pyexiv2",
        "scikit-learn",
        "setuptools",
        "tensorflow",
        "termcolor",
        "torch",
        "torchvision",
    ],
    url='https://dsrg-ict.research.um.edu.mt/gianluca/bioblu',
    license='',
    author='Roland Pfeiffer',
    author_email='landpfeiffer@gmail.com',
    description="!!! PACKAGE IS IN DEVELOPMENT !!! Contains scripts used within the scope of the BIOBLU project. No warranty or guaranteed functionality."
)
