from setuptools import setup

classifiers = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: GNU LESSER GENERAL PUBLIC LICENSE Version 3, 29 June 2007"
]

with open("README.md", "r") as fh:
    long_description = fh.read()

setup( 
    name="liblip",
    version="0.40",
    description="Library for multivariate scattered data interpolation",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="",
    author='Gleb Beliakov, Norbert Henseler',
    author_email='gleb.beliakov@deakin.edu.au, norbert.henseler@deakin.edu.au',
    license_file='LICENSE.txt',
    py_modules=['liblip'],
    package_dir={'': 'src'},
    install_requires=['cffi>=1.0.0'],
    setup_requires=['cffi>=1.0.0'],
    cffi_modules=['./src/build_liblip.py:ffibuilder'],
    include_package_data=True,
    package_data={'':['tests/test_wrapper.py', 'test/test_no_wrapper.py','test/test_wrapper_3d.ipynb']},
)

    
    