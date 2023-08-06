"""
setup file for python package
"""
import setuptools

with open("README.md", "r") as fh:
    description = fh.read()

setuptools.setup(
    name="niqe",
    version="0.1.1",
    author="tapan",
    author_email="tapan5356@gmail.com",
    packages=setuptools.find_packages(),
    description="read",
    long_description=description,
    long_description_content_type="text/markdown",
    license='MIT',
    keywords=[''],
    python_requires='>=3',
    install_requires=['numpy', 'opencv-python', 'scipy','scikit-image']
)

classifiers = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
]
