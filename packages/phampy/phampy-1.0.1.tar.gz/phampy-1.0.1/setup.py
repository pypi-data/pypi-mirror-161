import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="phampy",
    version="1.0.1",
    author="Loc Ha",
    author_email='haducloc13@gmail.com',
    description="Python Libraries",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/haducloc/phampy",
    packages=setuptools.find_packages('src'),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8.0',
    py_modules=["phampy"],
    package_dir={'':'src'},
    install_requires=[]
)