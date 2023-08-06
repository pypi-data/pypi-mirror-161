import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="kaskada",
    version="0.0.20",
    author="Kaskada",
    author_email="support@kaskada.com",
    description="A client library for the Kaskada time travel machine learning service",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://kaskada.com",
    project_urls={
        "Documentation": "https://docs.kaskada.com/",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: Jupyter",
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
    ],
    package_dir={"": "src"},
    packages=["kaskada"],
    package_data={"kaskada": ["formatters.css", "formatters.js"]},
    python_requires=">=3.6",
    install_requires=[
        'certifi',
        'domonic',
        'googleapis-common-protos',
        'grpcio~=1.47.0',
        'grpcio-status',
        'html5lib',
        'ipython',
        'kaskada_grpc==0.0.14',
        'pandas',
        'protobuf',
        'pyarrow',
        'requests',
    ],
)
