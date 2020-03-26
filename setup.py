from setuptools import setup, find_packages

install_requires = [
    'flask',
    'matplotlib',
    'seaborn',
    'scipy',
    'scikit-learn',
    'requests',
    'numpy',
    'pandas',
]

setup(
    name='Oogstvoorspellingen',
    version='1.0',
    description='Oogstvoorspellingen opzet',
    author='Hogeschool Utrecht V2A - 2020',
    author_email='martijn.knegt@student.hu.nl',
    package_dir={"": "."},
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
    dependency_links=[
        # "git+https://github.com/BB8-2020/<repo_name>#egg=<repo_name>",
    ],
)
