import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mini-pickle-db",
    version="0.1.0",
    author="Marin Dragolov",
    author_email="murrou13@gmail.com",
    description="Mini pickle database",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/murrou-cell/mini_pickle_db",
    project_urls={
        "Bug Tracker": "https://github.com/murrou-cell/mini_pickle_db/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)