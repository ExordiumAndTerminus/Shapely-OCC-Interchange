from setuptools import setup

setup(
    name='Shapely_OCC_Interchange',
    version='0.0.1',
    author='Maximillian Merritts',
    author_email='merrittsmax@gmail.com',
    packages=['Shapely_OCC_Interchange'],
    py_modules=[],
    scripts=[],
    url='https://github.com/ExordiumAndTerminus/Shapely-OCC-Interchange',
    license='LICENSE.txt',
    description='An un-described package.',
    long_description=open('README.md').read(),
    install_requires=[
        'shapely',
        'OCC',
        'UnitAlg'
        
    ],
    python_requires='~=3.7'
)