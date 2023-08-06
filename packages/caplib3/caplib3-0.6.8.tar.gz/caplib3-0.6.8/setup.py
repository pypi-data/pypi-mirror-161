import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(
    name="caplib3", # Replace with your own username
    version="0.6.8",
    author="Damien Marsic",
    author_email="damien.marsic@aliyun.com",
    description="NGS data analysis of capsid libraries",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/damienmarsic/caplib3",
    package_dir={'': 'caplib3'},
    packages=setuptools.find_packages(),
    py_modules=["caplib3"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
    python_requires='>=3.6',
)
