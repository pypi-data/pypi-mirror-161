import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="RiceXL",
    version="0.6.3",
    author="SNAKE",
    author_email="admin@wangbaishi.com",
    description="A tool for handling Excel easily. Handle both xls and xlsx in the same way.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wbsabc/RiceXL",
    project_urls={
        "Bug Tracker": "https://github.com/wbsabc/RiceXL/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    requires=['xlrd', 'xlwt', 'xlutils', 'openpyxl', 'os', 're', 'tempfile']
)