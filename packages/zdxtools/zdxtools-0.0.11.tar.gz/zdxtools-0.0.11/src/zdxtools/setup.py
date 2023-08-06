import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="zdxtools",
    version="0.0.12",
    author="zhou",
    author_email="1057129097@qq.com",
    description="来自21世纪最伟大的科学家",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    project_urls={
        "Bug Tracker": "https://github.com/pypa/sampleproject/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    package_data={"": ["*.txt", "*.rst"]},
    # include_package_data=True,
    # packages=['zdxtools'],
    python_requires=">=3.6",
)