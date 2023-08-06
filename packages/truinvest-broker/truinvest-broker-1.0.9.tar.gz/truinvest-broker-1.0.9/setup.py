import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="truinvest-broker",
    version="1.0.9",
    author="Anukkrit Shanker",
    author_email="anukkrit@rebal.tech",
    description="Broker client Lib",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://truinvest.ai/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
    install_requires=[
        'gitpython',
        'kiteconnect',
        'djangorestframework',
        'requests',
        'pandas'
    ],
    keywords='truinvest truinvest-broker',
    project_urls={
        'Homepage': 'https://truinvest.ai/',
    },
)