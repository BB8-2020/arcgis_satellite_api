from setuptools import find_packages, setup

install_requires = [
    'pillow',
    'pytest',
    'requests',
    'numpy'
]

setup(
    name='Arcgis Satellite API',
    version='1.0',
    description='Arcgis Satellite API',
    author='Hogeschool Utrecht V2A - 2020',
    author_email='berry.hijwegen@student.hu.nl',
    package_dir={"": "."},
    packages=find_packages(),
    package_data={'arcgis_satellite_api': ['satellite/data/not_found_base64.txt']},
    include_package_data=True,
    install_requires=install_requires,
)
