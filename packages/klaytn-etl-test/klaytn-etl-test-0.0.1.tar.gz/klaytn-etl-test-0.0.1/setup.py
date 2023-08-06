import os

from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


long_description = read('README.md') if os.path.isfile("README.md") else ""

setup(
    name='klaytn-etl-test',
    version='0.0.1',
    author='Yongchan Hong',
    author_email='chan.hong@krustuniverse.com',
    description='Tools for exporting Klaytn blockchain data to JSON',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Krustuniverse-Klaytn-Group/klaytn-etl',
    packages=find_packages(exclude=['schemas', 'tests']),
    classifiers=[
        # 'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9'
    ],
    keywords=['klaytn', 'etl', 'batch', 'stream'],
    python_requires='>=3.7.2,<4',
    install_requires=[
        'web3>=5.29,<6',
        # eth-rlp is explicitly written to prevent dependency related issue
        'eth-rlp<0.3',
        'eth-utils==1.10',
        'eth-abi==2.1.1',
        # TODO: This has to be removed when "ModuleNotFoundError: No module named 'eth_utils.toolz'" is fixed at eth-abi
        'python-dateutil>=2.8.0,<3',
        'click==8.0.4',
        'ethereum-dasm==0.1.4',
        'pytz==2022.1',
        'base58',
        'requests',
    ],
    extras_require={
        'streaming': [
            'timeout-decorator==0.4.1',
            'google-cloud-pubsub==2.1.0',
            'google-cloud-storage==1.33.0',
            'kafka-python==2.0.2',
            'sqlalchemy==1.4',
            'pg8000==1.16.6',
            # This library is a dependency for google-cloud-pubsub, starting from 0.3.22 it requires Rust,
            # that's why we lock the version here
            'libcst==0.3.21'
        ],
        'dev': [
            'pytest~=4.3.0'
        ]
    },
    entry_points={
        'console_scripts': [
            'ethereumetl=ethereumetl.cli:cli',
            'klaytnetl=klaytnetl.cli:cli',
        ],
    },
    project_urls={
        'Bug Reports': 'https://github.com/Krustuniverse-Klaytn-Group/klaytn-etl/issues',
        'Source': 'https://github.com/Krustuniverse-Klaytn-Group/klaytn-etl/tree/klaytn-etl',
    },
)
