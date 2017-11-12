from setuptools import setup, find_packages


def readme():
    with open('README.rst') as f:
        return f.read()


setup(
    name='Xenops',
    version="0.0.1",
    description="Xenops is a simple program to sync data like (customers/products) between different systems",
    long_description=readme(),
    packages=find_packages(),
    include_package_data=True,
    classifiers = [
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
    ],
    author="Maikel Martens",
    author_email = 'maikel@martens.me',
    license='GPL3',
    url = 'https://github.com/krukas/Xenops',
    download_url = 'https://github.com/krukas/Xenops/releases/tag/0.0.1',
    keywords = ['Xenops', 'Connector', 'Enterprise Service Bus', 'ESB'],
    install_requires = [],
)
