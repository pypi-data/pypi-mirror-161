from setuptools import find_packages, setup

setup(
    name='cosmoplib',
    packages=find_packages(include=['cosmoplib']),
    version='0.1.0',
    description='COSMOP Library',
    author='Luke Lorentzatos',
    license='UH',
    install_requires=['pandas', 'numpy'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest==4.4.1'],
    test_suite='tests',
)