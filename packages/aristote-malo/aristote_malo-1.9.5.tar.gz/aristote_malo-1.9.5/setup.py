import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="aristote_malo",
    version="1.9.5",
    author="Malo FRACKOWIAK",
    author_email="malo.frackowiak.sta@sylfen.com",
    description="Programme de prévision de production électrique d'une centrale PV",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    # packages=setuptools.find_packages(),
    packages=['aristotePV'],
    # packages=setuptools.find_packages(exclude=["quickTest"]),
    package_data={'': ['confFiles/*']},
    data_files=[("my_data", ["data/DataPrevision.pkl"])],
    # include_package_data=True,
    install_requires=['dorianUtils==5.1.2','geopy==2.2.0','tzwhere==3.0.3','requests==2.28.1','urllib3==1.26.10','pygrib==2.1.4','numpy==1.23.1','scikit-learn==1.1.1'],
    python_requires=">=3.8"
)
