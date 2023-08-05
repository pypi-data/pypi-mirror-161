from setuptools import setup
from setuptools import find_packages


VERSION = '0.1.1'

setup(
    name='semml',  # package name
    version=VERSION,  # package version
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*",
    install_requires=[
        'matplotlib==3.5.2',
        'numpy==1.21.6',
        'pandas==1.3.5',
        'psycopg2==2.9.3',
        'scikit_learn==1.1.1',
        'scipy==1.7.3',
        'seaborn==0.11.2',
        'setuptools==61.2.0',
        'statsmodels==0.13.2',
        'tqdm==4.64.0',
    ],
    description='Ship Energy Model Machine Learning',  # package description
    packages=find_packages(),
    zip_safe=False,
    url='https://github.com/shiningxy/shipEnergyML',
    author='Xiangyu Wang',
    author_email='codexy020999@163.com',
)