from distutils.core import setup
from setuptools import find_packages

setup(
    classifiers=[
        'Development Status :: 5 - Production/Stable',

        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',

        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',

        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    description='Convert from Delaunay tesselation to Voronoi triangulation.',
    entry_points={
    },
    url='https://gitlab.com/dfki/ra/ni/ol/iml/vr/vr.delaunay_to_voronoi/',
    author='Bengt Lüers',
    author_email='bengt.lueers@gmail.com',
    include_package_data=True,
    install_requires=[
    ],
    long_description=(
        open('README.md').read()
    ),
    long_description_content_type='text/markdown',
    maintainer='Bengt Lüers',
    maintainer_email='bengt.lueers@gmail.com',
    name='vr_delaunay-to-voronoi',
    packages=find_packages(exclude=['test', 'tests']),
    package_data={
        'vr_delaunay_to_voronoi': ['py.typed'],
    },
    setup_requires=[
    ],
    version='1.0.12',
)
