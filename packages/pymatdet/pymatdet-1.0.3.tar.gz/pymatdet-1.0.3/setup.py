from setuptools import setup, find_packages

classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]


setup(
    name='pymatdet',
    version='1.0.3',
    description="This is a module which can be used for performing matrix operations",
    license='MIT',
    author="Viren Tanti",
    author_email='virentanti16@gmail.com',
    classifiers=classifiers,
    packages=["pymatdet"],
    # packages=find_packages('pymatdet',"pymatdet.*"),
    # py_modules=['__init__'],
    # package_dir={'': 'pymatdet'},
    url='https://github.com/Virentanti/MatrixObject',
    long_description_content_type="text/markdown",
    long_description=open('README.md').read(),
    keywords=['matrix','MATRIX','matrix-object','matrix_object','matrixobject','MatrixObject', 'mat', "determinant","det"],


)