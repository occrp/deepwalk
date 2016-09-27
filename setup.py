from setuptools import setup, find_packages


setup(
    name='deepwalk',
    version='0.1',
    description="Crawl a directory of files, handle archives transparently.",
    long_description="",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7'
    ],
    keywords='files walk index survey',
    author='OCCRP',
    author_email='tech@occrp.org',
    url='http://github.com/occrp/deepwalk',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples', 'test']),
    namespace_packages=[],
    package_data={},
    include_package_data=True,
    zip_safe=False,
    test_suite='nose.collector',
    install_requires=[
        'chardet',
        'rarfile',
        'six',
        'normality'
    ],
    tests_require=[
        'nose',
        'coverage',
    ],
    entry_points={
        'deepwalk.package': [
            'zip = deepwalk.types:ZipPackage',
            'rar = deepwalk.types:RarPackage',
            'tar = deepwalk.types:TarPackage',
            '7z = deepwalk.types:SevenZipPackage',
            'gzip = deepwalk.types:GzipPackage',
            'bz2 = deepwalk.types:BZ2Package',
        ]
    }
)
