import setuptools

# deploy to turkcell pypi
# https://stash.turkcell.com.tr/git/projects/TBOT/repos/yas-py-sdk/browse/.pypirc-example
# twine upload --repository artifactory-dev --config-file ./.pyiprc dist/* --verbose

# install:
# pip install --index-url https://artifactory.turkcell.com.tr/artifactory/api/pypi/virtual-pypi/simple/ generic_crawler_sdk

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

with open('requirements.txt') as f:
    required = f.read().splitlines()

setuptools.setup(
    name="generic-crawler-sdk",
    version="0.0.5",
    author="Umut Alihan Dikel",
    author_email="alihan.dikel@turkcell.com.tr",
    description="Turkcell Generic Crawler Python SDK",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=None,
    packages=["generic_crawler"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent"
    ],
    python_requires='>=3.8',
    zip_safe=False,
    install_requires=required,
    setup_requires=['wheel'],
    # extras_require=get_extra_requires(),
    keywords=["generic_crawler"],
)
