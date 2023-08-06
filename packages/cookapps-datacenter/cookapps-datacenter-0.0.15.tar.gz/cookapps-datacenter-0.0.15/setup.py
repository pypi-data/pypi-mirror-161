from setuptools import setup, find_packages

setup(
    name             = 'cookapps-datacenter',
    version          = '0.0.15',
    description      = 'CookApps DATACENTER SDK',
    author           = 'synoh',
    author_email     = 'syno@cookapps.com',
    install_requires = ['pandas', 'boto3'],
    packages         = find_packages(exclude = ['tests*']),
    keywords         = ['cookapps', 'aws', 'datacenter'],
    python_requires  = '>=3',
    classifiers      = [
        'Programming Language :: Python :: 3.7'
    ]
)