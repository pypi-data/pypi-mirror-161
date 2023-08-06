from distutils.core import setup

setup(
    name = 'satellite_images_fusion',
    packages = ['satellite_images_fusion', 'satellite_images_fusion.algorithms', 'satellite_images_fusion.metrics', 'satellite_images_fusion.utils'],
    version = '1.1.2',  # Ideally should be same as your GitHub release tag varsion
    description = 'Package for satellite image fusion',
    author = 'ParallUD',
    author_email = 'aorestrepor@correo.udistrital.edu.co',
    url = 'https://github.com/AndresRestrepoRodriguez/satellite_images_fusion',
    download_url = 'https://github.com/AndresRestrepoRodriguez/satellite_images_fusion/archive/refs/tags/1.1.2.tar.gz',
    keywords = ['fusion', 'satellite image'],
    classifiers = [],
)