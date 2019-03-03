try:
    from numpy.distutils.core import setup, Extension
except ImportError:
    import warnings
    warnings.warn("numpy not installed, defaulting to setuptools.")
    try:
        from setuptools import setup, Extension
    except ImportError:
        warnings.warn("setuptools not installed, defaulting to distutils.")
        from distutils.core import setup, Extension

tricub = Extension('eqtools3._tricub',['eqtools3/_tricub.pyf','eqtools3/_tricub.c'])

setup(
    name='eqtools3',
    version='1.3.1',
    packages=['eqtools3',],
    install_requires=['scipy', 'numpy', 'matplotlib'],
    author=['Mark Chilenski','Ian Faust','John Walk'],
    author_email='psfcplasmatools@mit.edu',
    url='https://github.com/PSFCPlasmaTools/eqtools3/',
    description='Python tools for magnetic equilibria in tokamak plasmas',
    long_description=open('README.md', 'r').read(),
    ext_modules = [tricub,],
    license='GPL'
)
